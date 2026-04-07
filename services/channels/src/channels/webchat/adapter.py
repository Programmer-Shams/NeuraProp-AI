"""Web chat adapter — WebSocket handler for the embeddable chat widget."""

import asyncio
import json
import uuid
from datetime import UTC, datetime
from typing import Any

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger
from neuraprop_core.sqs import publish_message

logger = get_logger(__name__)

# Active WebSocket sessions: session_id -> WebChatSession
_active_sessions: dict[str, "WebChatSession"] = {}


class WebChatSession:
    """Represents a single web chat session with a trader."""

    def __init__(
        self,
        session_id: str,
        firm_id: str,
        websocket: Any,
    ):
        self.session_id = session_id
        self.firm_id = firm_id
        self.websocket = websocket
        self.conversation_id: str | None = None
        self.trader_id: str | None = None
        self.created_at = datetime.now(UTC)

    async def send(self, data: dict):
        """Send a message to the client."""
        await self.websocket.send_text(json.dumps(data))

    async def send_agent_response(self, content: str, agent_name: str | None = None):
        """Send an agent response to the client."""
        await self.send({
            "type": "agent_message",
            "content": content,
            "agent_name": agent_name,
            "conversation_id": self.conversation_id,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    async def send_typing(self, is_typing: bool = True):
        """Send typing indicator."""
        await self.send({"type": "typing", "is_typing": is_typing})

    async def send_error(self, message: str):
        """Send an error message to the client."""
        await self.send({"type": "error", "message": message})


async def handle_websocket(websocket: Any, firm_id: str):
    """
    Handle a WebSocket connection from the chat widget.

    Protocol:
    - Client sends: {"type": "message", "content": "...", "session_id": "..."}
    - Server sends: {"type": "agent_message", "content": "...", "agent_name": "..."}
    - Server sends: {"type": "typing", "is_typing": true/false}
    - Server sends: {"type": "error", "message": "..."}
    - Client sends: {"type": "init", "session_id": "...", "metadata": {...}}
    """
    session_id = str(uuid.uuid4())
    session = WebChatSession(
        session_id=session_id,
        firm_id=firm_id,
        websocket=websocket,
    )
    _active_sessions[session_id] = session

    logger.info("webchat_connected", session_id=session_id, firm_id=firm_id)

    # Send welcome
    await session.send({
        "type": "connected",
        "session_id": session_id,
    })

    try:
        async for raw_message in websocket.iter_text():
            try:
                data = json.loads(raw_message)
                msg_type = data.get("type")

                if msg_type == "init":
                    # Client initialization with metadata (e.g., page URL, user info)
                    session.trader_id = data.get("trader_id")
                    session.conversation_id = data.get("conversation_id")
                    await session.send({"type": "init_ack", "session_id": session_id})

                elif msg_type == "message":
                    content = data.get("content", "").strip()
                    if not content:
                        continue

                    await session.send_typing(True)
                    await _process_webchat_message(session, content, data.get("attachments", []))

                else:
                    logger.debug("webchat_unknown_type", type=msg_type, session=session_id)

            except json.JSONDecodeError:
                await session.send_error("Invalid message format")
            except Exception:
                logger.exception("webchat_message_error", session=session_id)
                await session.send_error("An error occurred processing your message")

    except Exception:
        logger.info("webchat_disconnected", session_id=session_id)
    finally:
        _active_sessions.pop(session_id, None)


async def _process_webchat_message(
    session: WebChatSession,
    content: str,
    attachments: list[dict],
):
    """Publish a web chat message to the agent pipeline via SQS."""
    settings = get_settings()
    message_id = str(uuid.uuid4())

    unified_message = {
        "id": message_id,
        "firm_id": session.firm_id,
        "channel": "web_chat",
        "direction": "inbound",
        "sender_type": "trader",
        "sender_channel_id": session.session_id,
        "trader_id": session.trader_id,
        "content": content,
        "attachments": attachments,
        "metadata": {"webchat_session_id": session.session_id},
        "conversation_id": session.conversation_id,
        "reply_to_message_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "channel_timestamp": datetime.now(UTC).isoformat(),
    }

    await publish_message(
        queue_url=settings.sqs_inbound_queue_url,
        message=unified_message,
        message_group_id=session.firm_id,
    )

    logger.info("webchat_message_queued", message_id=message_id, session=session.session_id)


async def deliver_response(session_id: str, content: str, agent_name: str | None = None):
    """Deliver an agent response to a web chat session.

    Called by the outbound queue consumer when a response is ready.
    """
    session = _active_sessions.get(session_id)
    if not session:
        logger.warning("webchat_session_not_found", session_id=session_id)
        return False

    await session.send_typing(False)
    await session.send_agent_response(content, agent_name)
    return True


def get_active_session_count() -> int:
    return len(_active_sessions)
