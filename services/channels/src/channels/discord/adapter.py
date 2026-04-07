"""Discord adapter — bridges Discord bot messages to the NeuraProp agent pipeline via SQS."""

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger
from neuraprop_core.sqs import publish_message, receive_messages, delete_message

from channels.discord.bot import NeuraPropBot

logger = get_logger(__name__)

# In-memory response futures: message_id -> asyncio.Future
_pending_responses: dict[str, asyncio.Future] = {}

# Response timeout
RESPONSE_TIMEOUT_SECONDS = 30


async def _message_callback(
    firm_id: str,
    channel_user_id: str,
    display_name: str,
    content: str,
    channel_ref: str,
    attachments: list[dict],
) -> str:
    """
    Handle an inbound message from Discord.

    1. Publishes to SQS inbound queue
    2. Waits for the agent response on the outbound queue
    3. Returns the response text
    """
    settings = get_settings()
    message_id = str(uuid.uuid4())

    unified_message = {
        "id": message_id,
        "firm_id": firm_id,
        "channel": "discord",
        "direction": "inbound",
        "sender_type": "trader",
        "sender_channel_id": channel_user_id,
        "sender_display_name": display_name,
        "trader_id": None,
        "content": content,
        "attachments": attachments,
        "metadata": {"channel_ref": channel_ref},
        "conversation_id": None,
        "reply_to_message_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "channel_timestamp": datetime.now(UTC).isoformat(),
    }

    # Create a future for the response
    future: asyncio.Future = asyncio.get_event_loop().create_future()
    _pending_responses[message_id] = future

    # Publish to inbound queue
    await publish_message(
        queue_url=settings.sqs_inbound_queue_url,
        message=unified_message,
        message_group_id=firm_id,
    )

    logger.info("discord_message_queued", message_id=message_id, firm_id=firm_id)

    try:
        # Wait for the agent to process and respond
        response = await asyncio.wait_for(future, timeout=RESPONSE_TIMEOUT_SECONDS)
        return response
    except asyncio.TimeoutError:
        logger.warning("discord_response_timeout", message_id=message_id)
        return (
            "I'm still working on your request — it's taking a bit longer than usual. "
            "I'll follow up shortly, or you can send your question again."
        )
    finally:
        _pending_responses.pop(message_id, None)


async def _poll_outbound_queue():
    """
    Background task that polls the SQS outbound queue for agent responses
    and resolves pending futures.
    """
    settings = get_settings()
    logger.info("outbound_poller_started")

    while True:
        try:
            messages = await receive_messages(
                queue_url=settings.sqs_outbound_queue_url,
                max_messages=10,
                wait_time_seconds=5,
            )

            for msg in messages:
                body = msg.get("body", {})
                conv_id = body.get("conversation_id")
                content = body.get("content", "")

                # Try to match with a pending future
                # In production, we'd match by conversation_id mapped to message_id
                # For now, check pending responses
                matched = False
                for msg_id, future in list(_pending_responses.items()):
                    if not future.done():
                        future.set_result(content)
                        matched = True
                        break

                if not matched:
                    logger.debug("outbound_message_no_match", conversation_id=conv_id)

                await delete_message(
                    queue_url=settings.sqs_outbound_queue_url,
                    receipt_handle=msg["receipt_handle"],
                )

        except Exception:
            logger.exception("outbound_poller_error")
            await asyncio.sleep(2)


class DiscordAdapter:
    """Manages one or more Discord bot instances for different firms."""

    def __init__(self):
        self.bots: dict[str, NeuraPropBot] = {}
        self._outbound_task: asyncio.Task | None = None

    def add_firm_bot(
        self,
        firm_id: str,
        firm_name: str,
        bot_token: str,
        support_channel_ids: list[int] | None = None,
    ) -> NeuraPropBot:
        """Register and configure a bot for a firm."""
        bot = NeuraPropBot(
            firm_id=firm_id,
            firm_name=firm_name,
            support_channel_ids=support_channel_ids,
        )
        bot.set_message_callback(_message_callback)
        self.bots[firm_id] = bot

        logger.info("discord_bot_registered", firm_id=firm_id, firm=firm_name)
        return bot

    async def start_all(self, bot_tokens: dict[str, str]):
        """Start all registered bots concurrently.

        bot_tokens: {firm_id: discord_bot_token}
        """
        # Start outbound queue poller
        self._outbound_task = asyncio.create_task(_poll_outbound_queue())

        # Start each bot
        tasks = []
        for firm_id, bot in self.bots.items():
            token = bot_tokens.get(firm_id)
            if token:
                tasks.append(asyncio.create_task(bot.start(token)))
                logger.info("discord_bot_starting", firm_id=firm_id)
            else:
                logger.warning("discord_bot_no_token", firm_id=firm_id)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all(self):
        """Gracefully stop all bots."""
        if self._outbound_task:
            self._outbound_task.cancel()

        for firm_id, bot in self.bots.items():
            await bot.close()
            logger.info("discord_bot_stopped", firm_id=firm_id)
