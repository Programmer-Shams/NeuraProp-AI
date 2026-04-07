"""Audit logging middleware — logs all API operations for compliance and debugging."""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from neuraprop_core.logging import get_logger

logger = get_logger("audit")

# Paths to skip audit logging
SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}

# Sensitive paths that get extra scrutiny
SENSITIVE_PATHS = {
    "/api/v1/admin/firms",
    "/api/v1/admin/config",
    "/api/v1/messages",
}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        if path in SKIP_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        client_ip = self._get_client_ip(request)
        firm_id = getattr(request.state, "firm_id", None)
        request_id = getattr(request.state, "request_id", None)

        # Execute request
        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Build audit entry
        audit_entry = {
            "request_id": request_id,
            "firm_id": firm_id,
            "method": request.method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
            "user_agent": request.headers.get("User-Agent", "")[:200],
        }

        # Log level based on status code
        if response.status_code >= 500:
            logger.error("api_request", **audit_entry)
        elif response.status_code >= 400:
            logger.warning("api_request", **audit_entry)
        elif path in SENSITIVE_PATHS:
            # Always log sensitive operations at info level
            logger.info("api_request_sensitive", **audit_entry)
        else:
            logger.info("api_request", **audit_entry)

        return response

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP, respecting proxy headers."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP (original client)
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        if request.client:
            return request.client.host
        return "unknown"
