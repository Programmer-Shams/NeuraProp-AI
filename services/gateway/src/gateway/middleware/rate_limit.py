"""Rate limiting middleware using Redis sliding window with tiered limits."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from neuraprop_core.redis import rate_limit_check

# Tiered rate limits by plan
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "starter": {"max_requests": 60, "window_seconds": 60},
    "growth": {"max_requests": 200, "window_seconds": 60},
    "enterprise": {"max_requests": 1000, "window_seconds": 60},
}
DEFAULT_LIMIT = {"max_requests": 100, "window_seconds": 60}

# Per-endpoint stricter limits (method:path_prefix -> requests/window)
ENDPOINT_LIMITS: dict[str, dict[str, int]] = {
    "POST:/api/v1/admin/firms": {"max_requests": 5, "window_seconds": 3600},
    "POST:/api/v1/messages": {"max_requests": 300, "window_seconds": 60},
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Only rate limit authenticated requests
        firm_id = getattr(request.state, "firm_id", None)
        if not firm_id:
            return await call_next(request)

        # Determine plan-based limits
        plan_tier = getattr(request.state, "plan_tier", None)
        limits = PLAN_LIMITS.get(plan_tier, DEFAULT_LIMIT) if plan_tier else DEFAULT_LIMIT

        # Global rate limit per firm
        rate_key = f"rate:{firm_id}:api"
        is_allowed, remaining = await rate_limit_check(
            rate_key,
            max_requests=limits["max_requests"],
            window_seconds=limits["window_seconds"],
        )

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                },
                headers={
                    "Retry-After": str(limits["window_seconds"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Limit": str(limits["max_requests"]),
                },
            )

        # Per-endpoint rate limit check
        endpoint_key = f"{request.method}:{request.url.path}"
        for pattern, ep_limits in ENDPOINT_LIMITS.items():
            if endpoint_key.startswith(pattern) or endpoint_key == pattern:
                ep_rate_key = f"rate:{firm_id}:{pattern}"
                ep_allowed, ep_remaining = await rate_limit_check(
                    ep_rate_key,
                    max_requests=ep_limits["max_requests"],
                    window_seconds=ep_limits["window_seconds"],
                )
                if not ep_allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "endpoint_rate_limit_exceeded",
                            "message": f"Rate limit exceeded for this endpoint.",
                        },
                        headers={
                            "Retry-After": str(ep_limits["window_seconds"]),
                            "X-RateLimit-Remaining": "0",
                        },
                    )
                break

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(limits["max_requests"])
        return response
