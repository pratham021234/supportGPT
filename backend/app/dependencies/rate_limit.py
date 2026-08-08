import redis.asyncio as redis
try:
    from fastapi_limiter import FastAPILimiter
except ImportError:
    FastAPILimiter = None
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

redis_client = None

async def init_redis():
    global redis_client
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        if FastAPILimiter:
            await FastAPILimiter.init(redis_client)
        logger.info("Redis Rate Limiter Initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")

async def close_redis():
    if FastAPILimiter and FastAPILimiter.redis:
        await FastAPILimiter.redis.close()
