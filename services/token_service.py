from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional
from datetime import datetime, timezone, timedelta
import redis.asyncio as redis

from core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TokenService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_client = redis.from_url(settings.REDIS_URL)

    async def create_refresh_token(self, user_id: int, refresh_token: str) -> bool:
        """Store refresh token in Redis"""
        try:
            # Set refresh token with expiration
            key = f"refresh_token:{refresh_token}"
            await self.redis_client.setex(
                key,
                settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert days to seconds
                str(user_id)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            return False

    async def validate_refresh_token(self, refresh_token: str) -> Optional[int]:
        """Validate refresh token and return user ID"""
        try:
            key = f"refresh_token:{refresh_token}"
            user_id = await self.redis_client.get(key)
            return int(user_id) if user_id else None
        except Exception as e:
            logger.error(f"Failed to validate refresh token: {e}")
            return None

    async def invalidate_refresh_token(self, refresh_token: str) -> bool:
        """Invalidate refresh token"""
        try:
            key = f"refresh_token:{refresh_token}"
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate refresh token: {e}")
            return False

    async def invalidate_all_user_tokens(self, user_id: int) -> bool:
        """Invalidate all tokens for a user"""
        try:
            # This is a simplified implementation
            # In production, you might want to store user_id -> token mappings
            pattern = f"refresh_token:*"
            keys = await self.redis_client.keys(pattern)
            
            for key in keys:
                token_user_id = await self.redis_client.get(key)
                if token_user_id and int(token_user_id) == user_id:
                    await self.redis_client.delete(key)
            
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate all user tokens: {e}")
            return False

    async def get_token_info(self, refresh_token: str) -> Optional[dict]:
        """Get token information"""
        try:
            key = f"refresh_token:{refresh_token}"
            user_id = await self.redis_client.get(key)
            if user_id:
                ttl = await self.redis_client.ttl(key)
                return {
                    "user_id": int(user_id),
                    "expires_in": ttl
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            return None 