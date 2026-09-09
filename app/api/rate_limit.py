import time

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status

from app.api.security import get_current_principal
from app.core.config import settings
from app.core.redis import get_redis_client
from app.domain.auth import Principal


class RateLimitDependency:
    """
    Fixed window rate limiter using Redis.
    """

    def __init__(self, requests_per_min: int = settings.RATE_LIMIT_REQUESTS_PER_MIN):
        self.requests_per_min = requests_per_min

    async def __call__(
        self,
        request: Request,
        principal: Principal = Depends(get_current_principal),
        redis_client: redis.Redis = Depends(get_redis_client),
    ):
        if not settings.RATE_LIMIT_ENABLED:
            return

        # Use the current minute as the window
        current_minute = int(time.time() / 60)
        key = f"rate_limit:{principal.principal_id}:{current_minute}"

        # Increment request count
        count = await redis_client.incr(key)

        # Set expiration for the key (e.g. 60 seconds) only on first increment
        if count == 1:
            await redis_client.expire(key, 60)

        if count > self.requests_per_min:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(60 - int(time.time()) % 60)},
            )
