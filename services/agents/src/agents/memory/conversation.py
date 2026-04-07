"""Conversation memory — load/save conversation state and message history."""

from typing import Any

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.logging import get_logger

logger = get_logger(__name__)

# Rolling window: keep last N messages in context
MAX_CONTEXT_MESSAGES = 20


async def load_conversation_history(
    conversation_id: str,
    firm_id: str,
    session: AsyncSession,
    limit: int = MAX_CONTEXT_MESSAGES,
) -> list[dict[str, Any]]:
    """
    Load recent message history for a conversation.

    Returns messages in chronological order, limited to the rolling window.
    """
    result = await session.execute(
        sql_text("""
            SELECT role, content, agent_name, tool_calls, created_at
            FROM messages
            WHERE conversation_id = :conv_id AND firm_id = :firm_id
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {"conv_id": conversation_id, "firm_id": firm_id, "limit": limit},
    )
    rows = result.mappings().all()

    messages = [
        {
            "role": row["role"],
            "content": row["content"],
            "agent_name": row.get("agent_name"),
            "timestamp": str(row["created_at"]),
        }
        for row in reversed(rows)  # Reverse to chronological order
    ]

    logger.info("conversation_loaded", conversation_id=conversation_id, messages=len(messages))
    return messages


async def save_message(
    conversation_id: str,
    firm_id: str,
    role: str,
    content: str,
    session: AsyncSession,
    agent_name: str | None = None,
    tool_calls: dict | None = None,
    llm_model: str | None = None,
    llm_tokens: dict | None = None,
    llm_latency_ms: int | None = None,
) -> str:
    """Save a message to the conversation history. Returns message ID."""
    import uuid

    msg_id = str(uuid.uuid4())

    await session.execute(
        sql_text("""
            INSERT INTO messages (id, conversation_id, firm_id, role, content, agent_name, tool_calls, llm_model, llm_tokens, llm_latency_ms)
            VALUES (:id, :conv_id, :firm_id, :role, :content, :agent_name, :tool_calls::jsonb, :llm_model, :llm_tokens::jsonb, :llm_latency_ms)
        """),
        {
            "id": msg_id,
            "conv_id": conversation_id,
            "firm_id": firm_id,
            "role": role,
            "content": content,
            "agent_name": agent_name,
            "tool_calls": str(tool_calls) if tool_calls else None,
            "llm_model": llm_model,
            "llm_tokens": str(llm_tokens) if llm_tokens else None,
            "llm_latency_ms": llm_latency_ms,
        },
    )

    return msg_id


async def get_or_create_conversation(
    firm_id: str,
    channel: str,
    channel_ref: str | None,
    trader_id: str | None,
    session: AsyncSession,
) -> str:
    """
    Get existing active conversation or create a new one.

    Matches on firm_id + channel + channel_ref for continuity.
    """
    import uuid

    if channel_ref:
        result = await session.execute(
            sql_text("""
                SELECT id FROM conversations
                WHERE firm_id = :firm_id AND channel = :channel AND channel_ref = :channel_ref
                  AND status = 'active'
                ORDER BY updated_at DESC
                LIMIT 1
            """),
            {"firm_id": firm_id, "channel": channel, "channel_ref": channel_ref},
        )
        row = result.first()
        if row:
            return str(row[0])

    # Create new conversation
    conv_id = str(uuid.uuid4())
    await session.execute(
        sql_text("""
            INSERT INTO conversations (id, firm_id, trader_id, channel, channel_ref, status)
            VALUES (:id, :firm_id, :trader_id, :channel, :channel_ref, 'active')
        """),
        {
            "id": conv_id,
            "firm_id": firm_id,
            "trader_id": trader_id,
            "channel": channel,
            "channel_ref": channel_ref,
        },
    )

    logger.info("conversation_created", conversation_id=conv_id, firm_id=firm_id, channel=channel)
    return conv_id
