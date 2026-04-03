import redis.asyncio as aioredis
from typing import AsyncGenerator
from src.config import settings

# Global redis pool
redis_pool: aioredis.ConnectionPool | None = None

async def init_redis_pool() -> None:
    global redis_pool
    redis_pool = aioredis.ConnectionPool.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )

async def close_redis_pool() -> None:
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()

async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    if not redis_pool:
        await init_redis_pool()
    client = aioredis.Redis(connection_pool=redis_pool) # type: ignore
    try:
        yield client
    finally:
        await client.aclose() # type: ignore
