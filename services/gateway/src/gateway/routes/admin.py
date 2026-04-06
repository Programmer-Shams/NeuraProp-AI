"""Admin endpoints for firm management and configuration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from neuraprop_core.auth import generate_api_key, hash_api_key
from neuraprop_core.logging import get_logger
from neuraprop_core.models.firm import Firm, FirmConfig
from neuraprop_core.database import get_db_session

from gateway.deps import DB, FirmId

logger = get_logger(__name__)
router = APIRouter()


class CreateFirmRequest(BaseModel):
    name: str
    slug: str
    plan_tier: str = "starter"


class GenerateApiKeyRequest(BaseModel):
    name: str
    environment: str = "live"


@router.post("/firms")
async def create_firm(body: CreateFirmRequest) -> dict:
    """Create a new firm (tenant). No auth required for onboarding."""
    async with get_db_session() as db:
        # Check slug uniqueness
        existing = await db.execute(
            select(Firm).where(Firm.slug == body.slug)
        )
        if existing.scalar():
            raise HTTPException(status_code=409, detail="Firm slug already exists")

        firm = Firm(name=body.name, slug=body.slug, plan_tier=body.plan_tier)
        db.add(firm)
        await db.flush()

        # Create default config
        config = FirmConfig(
            firm_id=firm.id,
            branding={
                "logo_url": None,
                "primary_color": "#6366f1",
                "bot_name": f"{body.name} Support",
                "welcome_message": f"Welcome to {body.name} support! How can I help you?",
            },
            supported_channels=["discord", "web_chat", "email"],
        )
        db.add(config)

        # Generate initial API key
        raw_key = generate_api_key(body.slug, "live")
        from sqlalchemy import text
        await db.execute(
            text("""
                INSERT INTO api_keys (firm_id, key_hash, key_prefix, name, environment)
                VALUES (:firm_id, :key_hash, :key_prefix, :name, :environment)
            """),
            {
                "firm_id": str(firm.id),
                "key_hash": hash_api_key(raw_key),
                "key_prefix": raw_key[:30],
                "name": "Default API Key",
                "environment": "live",
            },
        )

        logger.info("firm_created", firm_id=str(firm.id), slug=body.slug)

        return {
            "id": str(firm.id),
            "name": firm.name,
            "slug": firm.slug,
            "status": firm.status,
            "api_key": raw_key,  # Only shown once at creation
            "message": "Firm created successfully. Save the API key — it won't be shown again.",
        }


@router.get("/config")
async def get_firm_config(firm_id: FirmId, db: DB) -> dict:
    """Get the firm's configuration."""
    result = await db.execute(
        select(FirmConfig).where(FirmConfig.firm_id == firm_id)
    )
    config = result.scalar()
    if not config:
        raise HTTPException(status_code=404, detail="Firm config not found")

    return {
        "firm_id": str(config.firm_id),
        "branding": config.branding,
        "agent_configs": config.agent_configs,
        "auto_approve_payout_limit": config.auto_approve_payout_limit,
        "escalation_email": config.escalation_email,
        "supported_channels": config.supported_channels,
        "features": config.features,
    }
