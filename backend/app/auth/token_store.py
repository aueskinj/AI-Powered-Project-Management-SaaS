from datetime import datetime, timezone

import redis.asyncio as redis


def _refresh_key(jti: str) -> str:
    return f"auth:refresh:{jti}"


async def store_refresh_token(
    redis_client: redis.Redis, jti: str, user_id: str, expires_at_ts: int
) -> None:
    ttl = max(expires_at_ts - int(datetime.now(timezone.utc).timestamp()), 1)
    await redis_client.set(_refresh_key(jti), user_id, ex=ttl)


async def is_refresh_token_active(
    redis_client: redis.Redis, jti: str, user_id: str
) -> bool:
    stored_user_id = await redis_client.get(_refresh_key(jti))
    return stored_user_id == user_id


async def revoke_refresh_token(redis_client: redis.Redis, jti: str) -> None:
    await redis_client.delete(_refresh_key(jti))
