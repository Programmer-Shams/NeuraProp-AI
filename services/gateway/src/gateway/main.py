"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neuraprop_core.config import get_settings
from neuraprop_core.database import close_db
from neuraprop_core.logging import setup_logging, get_logger
from neuraprop_core.redis import close_redis

from gateway.middleware.request_id import RequestIdMiddleware
from gateway.middleware.security_headers import SecurityHeadersMiddleware
from gateway.middleware.audit import AuditMiddleware
from gateway.middleware.tenant import TenantMiddleware
from gateway.middleware.rate_limit import RateLimitMiddleware
from gateway.middleware.ip_filter import IpFilterMiddleware
from gateway.exception_handlers import register_exception_handlers
from gateway.routes import messages, conversations, traders, knowledge, admin, health, webhooks
from channels.webchat.routes import router as webchat_router

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

    # --- Exception Handlers ---
    register_exception_handlers(app)

    # --- CORS (tightened for production) ---
    if settings.is_production:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[settings.dashboard_url],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "X-API-Key",
                "X-Request-ID",
            ],
            expose_headers=[
                "X-Request-ID",
                "X-RateLimit-Remaining",
                "X-RateLimit-Limit",
            ],
            max_age=3600,
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # --- Middleware stack ---
    # Order matters: last added = first executed.
    # Execution order: RequestId → SecurityHeaders → Tenant → IpFilter → RateLimit → Audit → Handler
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(IpFilterMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # --- Routes ---
    app.include_router(health.router, tags=["Health"])
    app.include_router(messages.router, prefix="/api/v1", tags=["Messages"])
    app.include_router(conversations.router, prefix="/api/v1", tags=["Conversations"])
    app.include_router(traders.router, prefix="/api/v1", tags=["Traders"])
    app.include_router(knowledge.router, prefix="/api/v1", tags=["Knowledge Base"])
    app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
    app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])
    app.include_router(webchat_router, tags=["WebChat"])

    return app


app = create_app()

# Lambda handler via Mangum (for AWS Lambda deployment)
# handler = Mangum(app)
