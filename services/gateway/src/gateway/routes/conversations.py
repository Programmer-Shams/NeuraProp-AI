"""Conversation management endpoints."""

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from neuraprop_core.logging import get_logger
from neuraprop_core.models.conversation import Conversation, Message
from neuraprop_core.models.trader import Trader

from gateway.deps import DB, FirmId

logger = get_logger(__name__)
router = APIRouter()


@router.get("/conversations")
async def list_conversations(
    firm_id: FirmId,
    db: DB,
    status: str | None = Query(None),
    channel: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """List conversations for the firm with optional filters."""
    query = select(Conversation).where(Conversation.firm_id == firm_id)

    if status:
        query = query.where(Conversation.status == status)
    if channel:
        query = query.where(Conversation.channel == channel)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Conversation.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    conversations = result.scalars().all()

    return {
        "items": [
            {
                "id": str(c.id),
                "trader_id": str(c.trader_id) if c.trader_id else None,
                "channel": c.channel,
                "status": c.status,
                "current_agent": c.current_agent,
                "started_at": c.started_at.isoformat() if c.started_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in conversations
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    firm_id: FirmId,
    db: DB,
) -> dict:
    """Get conversation details with messages."""
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    msg_query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    result = await db.execute(msg_query)
    messages = result.scalars().all()

    return {
        "id": str(conv.id),
        "firm_id": str(conv.firm_id),
        "trader_id": str(conv.trader_id) if conv.trader_id else None,
        "channel": conv.channel,
        "status": conv.status,
        "current_agent": conv.current_agent,
        "satisfaction": conv.satisfaction,
        "started_at": conv.started_at.isoformat() if conv.started_at else None,
        "resolved_at": conv.resolved_at.isoformat() if conv.resolved_at else None,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "agent_name": m.agent_name,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
    }
