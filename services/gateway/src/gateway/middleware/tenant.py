"""Tenant resolution middleware — resolves firm from API key."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from neuraprop_core.auth import extract_firm_slug, hash_api_key
from neuraprop_core.database import get_db_session
from neuraprop_core.logging import get_logger
from neuraprop_core.redis import cache_get, cache_set

from sqlalchemy import select, text

logger = get_logger(__name__)

# Paths that don't require authentication
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Skip auth for public paths
        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "authentication_required", "message": "X-API-Key header is required"},
            )

        # Try cache first
        key_hash = hash_api_key(api_key)
        cache_key = f"apikey:{key_hash}"
        cached = await cache_get(cache_key)

        if cached:
            request.state.firm_id = cached["firm_id"]
            request.state.firm_slug = cached["firm_slug"]
            request.state.api_key_id = cached["api_key_id"]
            return await call_next(request)

        # Look up in database (no RLS for this query — we need to find the firm)
        async with get_db_session() as session:
            # Disable RLS for API key lookup
            await session.execute(text("SET app.current_firm_id = ''"))
            result = await session.execute(
                text("""
                    SELECT ak.id, ak.firm_id, f.slug, f.status
                    FROM api_keys ak
                    JOIN firms f ON f.id = ak.firm_id
                    WHERE ak.key_hash = :key_hash AND ak.is_active = true
                """),
                {"key_hash": key_hash},
            )
            row = result.first()

        if not row:
            return JSONResponse(
                status_code=401,
                content={"error": "invalid_api_key", "message": "Invalid or inactive API key"},
            )

        if row.status == "suspended":
            return JSONResponse(
                status_code=403,
                content={"error": "firm_suspended", "message": "This firm account is suspended"},
            )

        # Cache the resolved tenant
        tenant_data = {
            "firm_id": str(row.firm_id),
            "firm_slug": row.slug,
            "api_key_id": str(row.id),
        }
        await cache_set(cache_key, tenant_data, ttl_seconds=300)

        # Update last_used_at (fire and forget)
        async with get_db_session() as session:
            await session.execute(text("SET app.current_firm_id = ''"))
            await session.execute(
                text("UPDATE api_keys SET last_used_at = NOW() WHERE id = :id"),
                {"id": str(row.id)},
            )

        request.state.firm_id = str(row.firm_id)
        request.state.firm_slug = row.slug
        request.state.api_key_id = str(row.id)

        logger.info("tenant_resolved", firm_id=str(row.firm_id), firm_slug=row.slug)
        return await call_next(request)
