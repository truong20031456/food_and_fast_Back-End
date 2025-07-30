"""
Redis client and utilities
"""
import json
import pickle
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging

from ..core.config import BaseServiceSettings

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis connection and operations manager"""
    
    def __init__(self, settings: BaseServiceSettings):
        self.settings = settings
        self.redis_client = None
        self.connection_pool = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup Redis client with connection pool"""
        try:
            # Create connection pool
            self.connection_pool = redis.ConnectionPool.from_url(
                self.settings.REDIS_URL,
                max_connections=self.settings.REDIS_POOL_SIZE,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Create Redis client
            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=False
            )
            
            logger.info(f"Redis client initialized for {self.settings.SERVICE_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            raise
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[Union[int, timedelta]] = None,
        json_encode: bool = True
    ) -> bool:
        """Set a key-value pair in Redis"""
        try:
            # Serialize value
            if json_encode:
                try:
                    serialized_value = json.dumps(value, default=str)
                except (TypeError, ValueError):
                    # Fallback to pickle for complex objects
                    serialized_value = pickle.dumps(value)
                    json_encode = False
            else:
                serialized_value = pickle.dumps(value)
            
            # Set with expiration
            if expire:
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                await self.redis_client.setex(key, expire, serialized_value)
            else:
                await self.redis_client.set(key, serialized_value)
            
            # Store metadata about encoding
            await self.redis_client.hset(
                f"{key}:meta",
                mapping={
                    "json_encoded": str(json_encode),
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            if expire:
                await self.redis_client.expire(f"{key}:meta", expire)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis SET failed for key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            # Get value and metadata
            value_bytes = await self.redis_client.get(key)
            if value_bytes is None:
                return None
            
            # Get encoding metadata
            meta = await self.redis_client.hgetall(f"{key}:meta")
            json_encoded = meta.get(b"json_encoded", b"true") == b"true"
            
            # Deserialize value
            if json_encoded:
                try:
                    return json.loads(value_bytes.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fallback to pickle
                    return pickle.loads(value_bytes)
            else:
                return pickle.loads(value_bytes)
                
        except Exception as e:
            logger.error(f"Redis GET failed for key {key}: {e}")
            return None
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis"""
        try:
            # Delete keys and their metadata
            all_keys = list(keys) + [f"{key}:meta" for key in keys]
            return await self.redis_client.delete(*all_keys)
        except Exception as e:
            logger.error(f"Redis DELETE failed for keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        \"\"\"Check if key exists in Redis\"\"\"
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS failed for key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: Union[int, timedelta]) -> bool:
        \"\"\"Set expiration for a key\"\"\"
        try:
            if isinstance(seconds, timedelta):
                seconds = int(seconds.total_seconds())
            return bool(await self.redis_client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis EXPIRE failed for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        \"\"\"Get time to live for a key\"\"\"
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL failed for key {key}: {e}")
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        \"\"\"Increment a key's value\"\"\"
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR failed for key {key}: {e}")
            return None
    
    async def set_hash(self, key: str, mapping: dict, expire: Optional[int] = None) -> bool:
        \"\"\"Set hash fields\"\"\"
        try:
            # Serialize hash values
            serialized_mapping = {}
            for field, value in mapping.items():
                try:
                    serialized_mapping[field] = json.dumps(value, default=str)
                except (TypeError, ValueError):
                    serialized_mapping[field] = pickle.dumps(value)
            
            await self.redis_client.hset(key, mapping=serialized_mapping)
            
            if expire:
                await self.redis_client.expire(key, expire)
            
            return True
        except Exception as e:
            logger.error(f"Redis HSET failed for key {key}: {e}")
            return False
    
    async def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Union[Any, dict]]:
        \"\"\"Get hash field(s)\"\"\"
        try:
            if field:
                value_bytes = await self.redis_client.hget(key, field)
                if value_bytes is None:
                    return None
                
                try:
                    return json.loads(value_bytes.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return pickle.loads(value_bytes)
            else:
                hash_data = await self.redis_client.hgetall(key)
                if not hash_data:
                    return None
                
                result = {}
                for field_bytes, value_bytes in hash_data.items():
                    field_str = field_bytes.decode('utf-8')
                    try:
                        result[field_str] = json.loads(value_bytes.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        result[field_str] = pickle.loads(value_bytes)
                
                return result
                
        except Exception as e:
            logger.error(f"Redis HGET failed for key {key}: {e}")
            return None
    
    async def close(self):
        \"\"\"Close Redis connections\"\"\"
        try:
            if self.redis_client:
                await self.redis_client.close()
            if self.connection_pool:
                await self.connection_pool.disconnect()
            logger.info("Redis connections closed")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")


# Global Redis manager instance
_redis_manager: RedisManager = None


def init_redis(settings: BaseServiceSettings) -> RedisManager:
    \"\"\"Initialize Redis manager\"\"\"
    global _redis_manager
    _redis_manager = RedisManager(settings)
    return _redis_manager


def get_redis_manager() -> RedisManager:
    \"\"\"Get current Redis manager\"\"\"
    if _redis_manager is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_manager


async def get_redis_client() -> RedisManager:
    \"\"\"Dependency to get Redis client\"\"\"
    return get_redis_manager()


# Cache decorator
def cache(
    key_prefix: str,
    expire: Optional[Union[int, timedelta]] = None,
    json_encode: bool = True
):
    \"\"\"Decorator to cache function results\"\"\"
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            redis_client = get_redis_manager()
            
            # Try to get from cache
            cached_result = await redis_client.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_client.set(cache_key, result, expire, json_encode)
            
            return result
        return wrapper
    return decorator