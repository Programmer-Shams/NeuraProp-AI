"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neuraprop_core.config import get_settings
from neuraprop_core.database import close_db
from neuraprop_core.logging import setup_logging, get_logger
from neuraprop_core.redis import close_redis

from gateway.middleware.tenant import TenantMiddleware
from gateway.middleware.rate_limit import RateLimitMiddleware
from gateway.routes import messages, conversations, traders, knowledge, admin, health

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan: startup and shutdown events."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level, json_output=settings.is_production)
    logger.info("neuraprop_gateway_starting", env=settings.app_env)
    yield
    await close_db()
    await close_redis()
    logger.info("neuraprop_gateway_stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="NeuraProp AI Gateway",
        description="AI-powered customer support platform for prop trading firms",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.dashboard_url] if settings.is_production else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware (order matters: last added = first executed)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantMiddleware)

    # Routes
    app.include_router(health.router, tags=["Health"])
    app.include_router(messages.router, prefix="/api/v1", tags=["Messages"])
    app.include_router(conversations.router, prefix="/api/v1", tags=["Conversations"])
    app.include_router(traders.router, prefix="/api/v1", tags=["Traders"])
    app.include_router(knowledge.router, prefix="/api/v1", tags=["Knowledge Base"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

    return app


app = create_app()

# Lambda handler via Mangum (for AWS Lambda deployment)
# handler = Mangum(app)
