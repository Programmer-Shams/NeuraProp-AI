"""Inbound message handling — the core endpoint that receives trader messages."""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from neuraprop_core.config import get_settings
from neuraprop_core.logging import get_logger
from neuraprop_core.sqs import publish_message

from gateway.deps import DB, FirmId

logger = get_logger(__name__)
router = APIRouter()


class InboundMessageRequest(BaseModel):
    channel: str = Field(pattern="^(discord|web_chat|email)$")
    sender_channel_id: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=10000)
    attachments: list[dict] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    conversation_id: str | None = None


class InboundMessageResponse(BaseModel):
    message_id: str
    conversation_id: str | None
    status: str = "queued"


@router.post("/messages", response_model=InboundMessageResponse)
async def receive_message(
    body: InboundMessageRequest,
    firm_id: FirmId,
    db: DB,
) -> InboundMessageResponse:
    """
    Receive an inbound message from any channel.

    This endpoint normalizes the message into a UnifiedMessage
    and publishes it to the processing queue.
    """
    message_id = str(uuid.uuid4())
    settings = get_settings()

    unified_message = {
        "id": message_id,
        "firm_id": firm_id,
        "channel": body.channel,
        "direction": "inbound",
        "sender_type": "trader",
        "sender_channel_id": body.sender_channel_id,
        "trader_id": None,  # Resolved by the agent pipeline
        "content": body.content,
        "attachments": body.attachments,
        "metadata": body.metadata,
        "conversation_id": body.conversation_id,
        "reply_to_message_id": None,
        "created_at": datetime.now(UTC).isoformat(),
        "channel_timestamp": datetime.now(UTC).isoformat(),
    }

    # Publish to SQS inbound queue
    await publish_message(
        queue_url=settings.sqs_inbound_queue_url,
        message=unified_message,
        message_group_id=firm_id,
    )

    logger.info(
        "message_queued",
        message_id=message_id,
        firm_id=firm_id,
        channel=body.channel,
    )

    return InboundMessageResponse(
        message_id=message_id,
        conversation_id=body.conversation_id,
        status="queued",
    )
