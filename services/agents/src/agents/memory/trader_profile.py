"""Trader profile memory — load structured trader data for agent context."""

from typing import Any

from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from neuraprop_core.logging import get_logger

logger = get_logger(__name__)


async def load_trader_profile(
    trader_id: str,
    firm_id: str,
    session: AsyncSession,
) -> dict[str, Any] | None:
    """
    Load the full trader profile including linked accounts.

    Returns a structured dict suitable for injecting into agent context.
    """
    # Load trader base info
    result = await session.execute(
        sql_text("""
            SELECT id, email, display_name, kyc_status, risk_tier, profile_data, created_at
            FROM traders
            WHERE id = :trader_id AND firm_id = :firm_id
        """),
        {"trader_id": trader_id, "firm_id": firm_id},
    )
    row = result.mappings().first()

    if not row:
        logger.warning("trader_not_found", trader_id=trader_id, firm_id=firm_id)
        return None

    # Load linked trading accounts
    accounts_result = await session.execute(
        sql_text("""
            SELECT account_id, platform, account_type, status, metadata
            FROM trader_accounts
            WHERE trader_id = :trader_id
        """),
        {"trader_id": trader_id},
    )
    accounts = [dict(r) for r in accounts_result.mappings().all()]

    profile = {
        "id": str(row["id"]),
        "email": row["email"],
        "display_name": row["display_name"],
        "kyc_status": row["kyc_status"],
        "risk_tier": row["risk_tier"],
        "profile_data": row["profile_data"] or {},
        "accounts": accounts,
        "member_since": str(row["created_at"]),
    }

    logger.info("trader_profile_loaded", trader_id=trader_id, accounts=len(accounts))
    return profile


async def resolve_trader_from_channel(
    firm_id: str,
    channel: str,
    channel_user_id: str,
    session: AsyncSession,
) -> str | None:
    """
    Resolve a trader ID from their channel identity.

    Maps discord_id / email / widget_session to a trader record.
    """
    result = await session.execute(
        sql_text("""
            SELECT trader_id FROM trader_channel_identities
            WHERE firm_id = :firm_id AND channel = :channel AND channel_user_id = :channel_user_id
        """),
        {"firm_id": firm_id, "channel": channel, "channel_user_id": channel_user_id},
    )
    row = result.first()

    if row:
        return str(row[0])

    logger.info(
        "trader_identity_not_found",
        firm_id=firm_id,
        channel=channel,
        channel_user_id=channel_user_id[:20],
    )
    return None
