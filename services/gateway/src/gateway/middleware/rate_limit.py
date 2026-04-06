"""Rate limiting middleware using Redis sliding window."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from neuraprop_core.redis import rate_limit_check

# Default rate limits per firm
DEFAULT_MAX_REQUESTS = 100  # requests per window
DEFAULT_WINDOW_SECONDS = 60  # 1 minute window


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Only rate limit authenticated requests
        firm_id = getattr(request.state, "firm_id", None)
        if not firm_id:
            return await call_next(request)

        rate_key = f"rate:{firm_id}:api"
        is_allowed, remaining = await rate_limit_check(
            rate_key,
            max_requests=DEFAULT_MAX_REQUESTS,
            window_seconds=DEFAULT_WINDOW_SECONDS,
        )

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                },
                headers={
                    "Retry-After": str(DEFAULT_WINDOW_SECONDS),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(DEFAULT_MAX_REQUESTS)
        return response
