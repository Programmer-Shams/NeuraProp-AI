"""Global exception handlers for consistent error responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from neuraprop_core.errors import (
    AuthenticationError,
    AuthorizationError,
    NeuraPropError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    TenantNotFoundError,
    TenantSuspendedError,
    ValidationError,
    IntegrationError,
    IntegrationTimeoutError,
)
from neuraprop_core.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(AuthenticationError)
    async def handle_auth_error(request: Request, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": "authentication_error", "message": exc.message},
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authz_error(request: Request, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": "authorization_error", "message": exc.message},
        )

    @app.exception_handler(TenantNotFoundError)
    async def handle_tenant_not_found(request: Request, exc: TenantNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"error": "tenant_not_found", "message": exc.message},
        )

    @app.exception_handler(TenantSuspendedError)
    async def handle_tenant_suspended(request: Request, exc: TenantSuspendedError) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"error": "tenant_suspended", "message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": exc.message},
        )

    @app.exception_handler(ConflictError)
    async def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": "conflict", "message": exc.message},
        )

    @app.exception_handler(ValidationError)
    async def handle_validation(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "message": exc.message, "details": exc.details},
        )

    @app.exception_handler(RateLimitError)
    async def handle_rate_limit(request: Request, exc: RateLimitError) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"error": "rate_limit_exceeded", "message": exc.message},
            headers={"Retry-After": str(exc.retry_after_seconds)},
        )

    @app.exception_handler(IntegrationTimeoutError)
    async def handle_integration_timeout(request: Request, exc: IntegrationTimeoutError) -> JSONResponse:
        logger.error("integration_timeout", message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=504,
            content={"error": "integration_timeout", "message": "External service timed out"},
        )

    @app.exception_handler(IntegrationError)
    async def handle_integration(request: Request, exc: IntegrationError) -> JSONResponse:
        logger.error("integration_error", message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=502,
            content={"error": "integration_error", "message": "External service error"},
        )

    @app.exception_handler(PydanticValidationError)
    async def handle_pydantic(request: Request, exc: PydanticValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": [
                    {"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]}
                    for e in exc.errors()
                ],
            },
        )

    @app.exception_handler(NeuraPropError)
    async def handle_neuraprop_error(request: Request, exc: NeuraPropError) -> JSONResponse:
        """Catch-all for any NeuraPropError not handled above."""
        logger.error("unhandled_neuraprop_error", message=exc.message, details=exc.details)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": "An unexpected error occurred"},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        """Last-resort handler — never leak internal details."""
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            "unhandled_exception",
            request_id=request_id,
            exc_type=type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            },
        )
