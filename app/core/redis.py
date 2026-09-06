from collections.abc import AsyncGenerator

import redis.asyncio as redis

from app.core.config import settings

# Global redis pool
redis_pool: redis.ConnectionPool | None = None


async def init_redis_pool() -> None:
    global redis_pool
    redis_pool = redis.ConnectionPool.from_url(
        settings.REDIS_URL, decode_responses=True
    )


async def close_redis_pool() -> None:
    if redis_pool:
        await redis_pool.disconnect()


async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    if not redis_pool:
        raise RuntimeError("Redis pool not initialized")

    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()
