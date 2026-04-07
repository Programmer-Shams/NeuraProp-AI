"""IP allowlisting middleware — restrict API access by IP when configured.

IP allowlists are stored per-firm in Redis (set by admin endpoints).
When no allowlist exists for a firm, all IPs are permitted.
"""

import ipaddress

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from neuraprop_core.logging import get_logger
from neuraprop_core.redis import get_redis

logger = get_logger(__name__)


class IpFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        firm_id = getattr(request.state, "firm_id", None)
        if not firm_id:
            return await call_next(request)

        # Check if this firm has an IP allowlist
        client_ip = self._get_client_ip(request)
        allowed = await self._check_ip_allowed(firm_id, client_ip)

        if not allowed:
            logger.warning(
                "ip_blocked",
                firm_id=firm_id,
                client_ip=client_ip,
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "ip_not_allowed",
                    "message": "Your IP address is not in the firm's allowlist.",
                },
            )

        return await call_next(request)

    @staticmethod
    async def _check_ip_allowed(firm_id: str, client_ip: str) -> bool:
        """
        Check if the client IP is in the firm's allowlist.

        If no allowlist exists (empty set), all IPs are allowed.
        Supports both individual IPs and CIDR ranges.
        """
        client = get_redis()
        allowlist_key = f"ip_allowlist:{firm_id}"

        # Get the allowlist
        members = await client.smembers(allowlist_key)

        # No allowlist = all IPs allowed
        if not members:
            return True

        try:
            client_addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return False

        for entry in members:
            try:
                # Check if entry is a CIDR range
                if "/" in entry:
                    if client_addr in ipaddress.ip_network(entry, strict=False):
                        return True
                else:
                    if client_addr == ipaddress.ip_address(entry):
                        return True
            except ValueError:
                continue

        return False

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Extract client IP, respecting proxy headers."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        if request.client:
            return request.client.host
        return "unknown"
