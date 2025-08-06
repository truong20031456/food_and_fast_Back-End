from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis
import json

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from shared_code.core.config import get_service_settings

settings = get_service_settings("auth_service")
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client = redis.from_url(settings.REDIS_URL)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get from cache: {e}")
            return None

    async def set(
        self, key: str, value: Any, expire: Optional[timedelta] = None
    ) -> bool:
        """Set value in cache"""
        try:
            serialized_value = json.dumps(value)
            if expire:
                await self.redis_client.setex(
                    key, int(expire.total_seconds()), serialized_value
                )
            else:
                await self.redis_client.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete from cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check cache existence: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in cache"""
        try:
            return await self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment cache: {e}")
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key"""
        try:
            return await self.redis_client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Failed to set cache expiration: {e}")
            return False
