"""Redis client for caching, sessions, and rate limiting."""

import json
from typing import Any

import redis.asyncio as redis

from neuraprop_core.config import get_settings

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Get or create the Redis client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    """Close the Redis connection."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


# --- Convenience methods ---


async def cache_get(key: str) -> dict | None:
    """Get a JSON value from cache."""
    client = get_redis()
    value = await client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Set a JSON value in cache with TTL."""
    client = get_redis()
    await client.setex(key, ttl_seconds, json.dumps(value, default=str))


async def cache_delete(key: str) -> None:
    """Delete a cache key."""
    client = get_redis()
    await client.delete(key)


async def rate_limit_check(
    key: str,
    max_requests: int,
    window_seconds: int,
) -> tuple[bool, int]:
    """
    Sliding window rate limit check.

    Returns (is_allowed, remaining_requests).
    """
    import time

    client = get_redis()
    now = time.time()
    window_start = now - window_seconds

    pipe = client.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()

    current_count = results[2]
    is_allowed = current_count <= max_requests
    remaining = max(0, max_requests - current_count)

    return is_allowed, remaining
