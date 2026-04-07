"""Outbound response consumer — delivers agent responses back to the correct channel."""

import asyncio
import signal
from typing import Any

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger, setup_logging
from neuraprop_core.sqs import receive_messages, delete_message

from channels.webchat.adapter import deliver_response as webchat_deliver
from channels.email.adapter import send_agent_response_email

logger = get_logger(__name__)


async def handle_outbound_message(message: dict[str, Any]) -> bool:
    """
    Route an outbound agent response to the correct channel adapter.

    Returns True if delivery was successful.
    """
    channel = message.get("channel")
    content = message.get("content", "")
    firm_id = message.get("firm_id", "")
    metadata = message.get("metadata", {})

    if not content:
        logger.warning("empty_outbound_message", channel=channel)
        return True  # Ack and discard

    if channel == "web_chat":
        session_id = metadata.get("webchat_session_id")
        if session_id:
            return await webchat_deliver(session_id, content, message.get("agent_name"))
        logger.warning("webchat_no_session_id")
        return False

    elif channel == "discord":
        # Discord responses are handled by the Discord adapter's outbound poller
        # This consumer just needs to ensure the message stays in the queue
        # for the Discord adapter to pick up. In production, use separate queues.
        logger.info("discord_outbound_delegated", firm_id=firm_id)
        return True

    elif channel == "email":
        to_address = metadata.get("email_from", "")
        if not to_address:
            logger.warning("email_no_reply_address")
            return False

        result = await send_agent_response_email(
            to_address=to_address,
            agent_response=content,
            firm_id=firm_id,
            subject=f"Re: {metadata.get('email_subject', 'Your Support Request')}",
            in_reply_to=metadata.get("email_message_id"),
            references=metadata.get("email_references"),
        )
        return result.get("success", False)

    else:
        logger.warning("unknown_outbound_channel", channel=channel)
        return True


async def run_outbound_consumer():
    """
    Main loop for the outbound response consumer.

    Polls SQS outbound queue and delivers responses to channels.
    """
    setup_logging()
    settings = get_settings()
    running = True

    def shutdown():
        nonlocal running
        running = False
        logger.info("outbound_consumer_stopping")

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    logger.info("outbound_consumer_started")

    while running:
        try:
            messages = await receive_messages(
                queue_url=settings.sqs_outbound_queue_url,
                max_messages=10,
                wait_time_seconds=10,
            )

            for msg in messages:
                body = msg.get("body", {})
                success = await handle_outbound_message(body)

                if success:
                    await delete_message(
                        queue_url=settings.sqs_outbound_queue_url,
                        receipt_handle=msg["receipt_handle"],
                    )
                else:
                    logger.warning(
                        "outbound_delivery_failed",
                        channel=body.get("channel"),
                        conversation_id=body.get("conversation_id"),
                    )

        except Exception:
            logger.exception("outbound_consumer_error")
            await asyncio.sleep(2)

    logger.info("outbound_consumer_stopped")


if __name__ == "__main__":
    asyncio.run(run_outbound_consumer())
