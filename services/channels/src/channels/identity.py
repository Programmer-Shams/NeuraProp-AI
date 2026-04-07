"""Cross-channel identity resolution — maps Discord ID, email, widget sessions to trader records."""

from typing import Any

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.logging import get_logger

logger = get_logger(__name__)


async def resolve_trader_identity(
    firm_id: str,
    channel: str,
    sender_channel_id: str,
    session: AsyncSession,
) -> dict[str, Any] | None:
    """
    Resolve a trader from their channel-specific identity.

    Looks up trader_channel_identities to find the trader record.
    Returns trader dict or None if no match found.
    """
    result = await session.execute(
        sql_text("""
            SELECT tci.trader_id, t.email, t.display_name, t.kyc_status, t.risk_tier
            FROM trader_channel_identities tci
            JOIN traders t ON t.id = tci.trader_id
            WHERE tci.firm_id = :firm_id
              AND tci.channel = :channel
              AND tci.channel_user_id = :channel_user_id
        """),
        {"firm_id": firm_id, "channel": channel, "channel_user_id": sender_channel_id},
    )
    row = result.mappings().first()

    if row:
        logger.info(
            "trader_resolved",
            firm_id=firm_id,
            channel=channel,
            trader_id=str(row["trader_id"]),
        )
        return dict(row)

    logger.debug(
        "trader_not_resolved",
        firm_id=firm_id,
        channel=channel,
        sender_id=sender_channel_id[:20],
    )
    return None


async def link_channel_identity(
    firm_id: str,
    trader_id: str,
    channel: str,
    channel_user_id: str,
    display_name: str | None,
    session: AsyncSession,
) -> bool:
    """
    Link a channel identity to an existing trader.

    Used when a trader verifies their identity on a new channel
    (e.g., links their Discord to their account).
    """
    import uuid

    try:
        await session.execute(
            sql_text("""
                INSERT INTO trader_channel_identities (id, firm_id, trader_id, channel, channel_user_id, display_name)
                VALUES (:id, :firm_id, :trader_id, :channel, :channel_user_id, :display_name)
                ON CONFLICT (firm_id, channel, channel_user_id) DO UPDATE SET
                    trader_id = :trader_id,
                    display_name = :display_name
            """),
            {
                "id": str(uuid.uuid4()),
                "firm_id": firm_id,
                "trader_id": trader_id,
                "channel": channel,
                "channel_user_id": channel_user_id,
                "display_name": display_name,
            },
        )
        await session.commit()

        logger.info(
            "channel_identity_linked",
            firm_id=firm_id,
            trader_id=trader_id,
            channel=channel,
        )
        return True

    except Exception:
        logger.exception("channel_identity_link_failed")
        return False


async def merge_trader_identities(
    firm_id: str,
    primary_trader_id: str,
    secondary_trader_id: str,
    session: AsyncSession,
) -> bool:
    """
    Merge two trader records — move all channel identities from secondary to primary.

    Used when we discover that two channel identities belong to the same person
    (e.g., same email in Discord and web chat).
    """
    try:
        await session.execute(
            sql_text("""
                UPDATE trader_channel_identities
                SET trader_id = :primary_id
                WHERE trader_id = :secondary_id AND firm_id = :firm_id
            """),
            {
                "primary_id": primary_trader_id,
                "secondary_id": secondary_trader_id,
                "firm_id": firm_id,
            },
        )
        await session.commit()

        logger.info(
            "trader_identities_merged",
            firm_id=firm_id,
            primary=primary_trader_id,
            secondary=secondary_trader_id,
        )
        return True

    except Exception:
        logger.exception("trader_merge_failed")
        return False
