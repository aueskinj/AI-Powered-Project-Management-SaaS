from typing import Optional

import redis.asyncio as redis

from app.core.config import get_settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def connect_to_redis() -> None:
    client = get_redis_client()
    await client.ping()


async def close_redis_connection() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
    _redis_client = None
