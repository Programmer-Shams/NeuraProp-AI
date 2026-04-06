"""Trader management endpoints."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select

from neuraprop_core.logging import get_logger
from neuraprop_core.models.trader import Trader

from gateway.deps import DB, FirmId

logger = get_logger(__name__)
router = APIRouter()


class CreateTraderRequest(BaseModel):
    external_id: str | None = None
    email: str | None = None
    display_name: str | None = None
    profile_data: dict | None = None


@router.get("/traders")
async def list_traders(
    firm_id: FirmId,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """List traders for the firm."""
    query = select(Trader).where(Trader.firm_id == firm_id)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Trader.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    traders = result.scalars().all()

    return {
        "items": [
            {
                "id": str(t.id),
                "external_id": t.external_id,
                "email": t.email,
                "display_name": t.display_name,
                "kyc_status": t.kyc_status,
                "risk_tier": t.risk_tier,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in traders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/traders/{trader_id}")
async def get_trader(trader_id: str, firm_id: FirmId, db: DB) -> dict:
    """Get a trader by ID."""
    trader = await db.get(Trader, trader_id)
    if not trader:
        raise HTTPException(status_code=404, detail="Trader not found")

    return {
        "id": str(trader.id),
        "firm_id": str(trader.firm_id),
        "external_id": trader.external_id,
        "email": trader.email,
        "display_name": trader.display_name,
        "kyc_status": trader.kyc_status,
        "risk_tier": trader.risk_tier,
        "profile_data": trader.profile_data,
        "created_at": trader.created_at.isoformat() if trader.created_at else None,
        "updated_at": trader.updated_at.isoformat() if trader.updated_at else None,
    }
