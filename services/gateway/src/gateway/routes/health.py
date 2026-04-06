"""Health check endpoints."""

from fastapi import APIRouter

from neuraprop_core.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Basic health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "neuraprop-gateway",
        "version": "0.1.0",
        "environment": settings.app_env,
    }
