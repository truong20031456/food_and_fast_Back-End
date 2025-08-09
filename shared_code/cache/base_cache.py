"""
Shared Cache Service - Base Redis cache implementation for all microservices
"""
import json
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import logging
import os

try:
    import redis.asyncio as redis
except ImportError:
    redis = None
    logging.warning("Redis package not installed. Cache functionality will be disabled.")

logger = logging.getLogger(__name__)

class BaseCacheService:
    """Base Redis cache service for all microservices."""
    
    def __init__(self, service_name: str, db_number: int = 0):
        self.service_name = service_name
        self.db_number = db_number
        self.redis_client = None
        self.prefix = f"{service_name}_cache"
        
        # Default TTL values (can be overridden)
        self.default_ttl = 3600  # 1 hour
        self.short_ttl = 300     # 5 minutes
        self.long_ttl = 7200     # 2 hours
    
    async def connect(self):
        """Connect to Redis."""
        if redis is None:
            logger.warning("Redis not available. Cache operations will be disabled.")
            return
            
        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            redis_url = f"redis://{redis_host}:{redis_port}/{self.db_number}"
            if redis_password:
                redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{self.db_number}"
            
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info(f"[{self.service_name}] Successfully connected to Redis DB {self.db_number}")
        except Exception as e:
            logger.error(f"[{self.service_name}] Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info(f"[{self.service_name}] Disconnected from Redis cache")
    
    def _get_key(self, key: str) -> str:
        """Get prefixed cache key."""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._get_key(key)
            data = await self.redis_client.get(cache_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"[{self.service_name}] Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(key)
            serialized_value = json.dumps(value, default=str)
            
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(cache_key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"[{self.service_name}] Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(key)
            await self.redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"[{self.service_name}] Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            cache_pattern = self._get_key(pattern)
            keys = await self.redis_client.keys(cache_pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"[{self.service_name}] Cache delete pattern error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._get_key(key)
            return await self.redis_client.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"[{self.service_name}] Cache exists error: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get TTL of key."""
        if not self.redis_client:
            return -1
        
        try:
            cache_key = self._get_key(key)
            return await self.redis_client.ttl(cache_key)
        except Exception as e:
            logger.error(f"[{self.service_name}] Cache TTL error: {e}")
            return -1
    
    async def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        if not self.redis_client:
            return {"status": "disconnected", "service": self.service_name}
        
        try:
            info = await self.redis_client.info()
            keys_count = await self.redis_client.dbsize()
            
            return {
                "service": self.service_name,
                "status": "connected",
                "db_number": self.db_number,
                "keys_count": keys_count,
                "memory_used": info.get("used_memory_human", "N/A"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)) * 100, 2
                )
            }
        except Exception as e:
            logger.error(f"[{self.service_name}] Error getting cache stats: {e}")
            return {"service": self.service_name, "status": "error", "error": str(e)}


# Service-specific cache implementations
class ProductCacheService(BaseCacheService):
    """Product service cache implementation."""
    
    def __init__(self):
        super().__init__("product", db_number=1)
    
    async def get_product(self, product_id: int) -> Optional[Dict]:
        """Get cached product."""
        return await self.get(f"product:{product_id}")
    
    async def set_product(self, product_id: int, product_data: Dict, ttl: int = 3600) -> bool:
        """Cache product data."""
        return await self.set(f"product:{product_id}", product_data, ttl)
    
    async def get_category(self, category_id: int) -> Optional[Dict]:
        """Get cached category."""
        return await self.get(f"category:{category_id}")
    
    async def set_category(self, category_id: int, category_data: Dict, ttl: int = 7200) -> bool:
        """Cache category data."""
        return await self.set(f"category:{category_id}", category_data, ttl)
    
    async def get_search_results(self, query_hash: str) -> Optional[List]:
        """Get cached search results."""
        return await self.get(f"search:{query_hash}")
    
    async def set_search_results(self, query_hash: str, results: List, ttl: int = 1800) -> bool:
        """Cache search results."""
        return await self.set(f"search:{query_hash}", results, ttl)


class AuthCacheService(BaseCacheService):
    """Auth service cache implementation."""
    
    def __init__(self):
        super().__init__("auth", db_number=2)
    
    async def get_user_session(self, token_hash: str) -> Optional[Dict]:
        """Get cached user session."""
        return await self.get(f"session:{token_hash}")
    
    async def set_user_session(self, token_hash: str, session_data: Dict, ttl: int = 1800) -> bool:
        """Cache user session."""
        return await self.set(f"session:{token_hash}", session_data, ttl)
    
    async def get_user_permissions(self, user_id: int) -> Optional[List]:
        """Get cached user permissions."""
        return await self.get(f"permissions:{user_id}")
    
    async def set_user_permissions(self, user_id: int, permissions: List, ttl: int = 3600) -> bool:
        """Cache user permissions."""
        return await self.set(f"permissions:{user_id}", permissions, ttl)
    
    async def check_rate_limit(self, key: str) -> int:
        """Check rate limit counter."""
        if not self.redis_client:
            return 0
        try:
            cache_key = self._get_key(f"rate_limit:{key}")
            count = await self.redis_client.get(cache_key)
            return int(count) if count else 0
        except Exception:
            return 0
    
    async def increment_rate_limit(self, key: str, ttl: int = 60) -> int:
        """Increment rate limit counter."""
        if not self.redis_client:
            return 0
        try:
            cache_key = self._get_key(f"rate_limit:{key}")
            pipe = self.redis_client.pipeline()
            pipe.incr(cache_key)
            pipe.expire(cache_key, ttl)
            results = await pipe.execute()
            return results[0]
        except Exception:
            return 0


class UserCacheService(BaseCacheService):
    """User service cache implementation."""
    
    def __init__(self):
        super().__init__("user", db_number=3)
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get cached user profile."""
        return await self.get(f"profile:{user_id}")
    
    async def set_user_profile(self, user_id: int, profile_data: Dict, ttl: int = 3600) -> bool:
        """Cache user profile."""
        return await self.set(f"profile:{user_id}", profile_data, ttl)
    
    async def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """Get cached user preferences."""
        return await self.get(f"preferences:{user_id}")
    
    async def set_user_preferences(self, user_id: int, preferences: Dict, ttl: int = 7200) -> bool:
        """Cache user preferences."""
        return await self.set(f"preferences:{user_id}", preferences, ttl)


class OrderCacheService(BaseCacheService):
    """Order service cache implementation."""
    
    def __init__(self):
        super().__init__("order", db_number=4)
    
    async def get_user_cart(self, user_id: int) -> Optional[Dict]:
        """Get cached user cart."""
        return await self.get(f"cart:{user_id}")
    
    async def set_user_cart(self, user_id: int, cart_data: Dict, ttl: int = 1800) -> bool:
        """Cache user cart."""
        return await self.set(f"cart:{user_id}", cart_data, ttl)
    
    async def get_order_status(self, order_id: int) -> Optional[Dict]:
        """Get cached order status."""
        return await self.get(f"order_status:{order_id}")
    
    async def set_order_status(self, order_id: int, status_data: Dict, ttl: int = 3600) -> bool:
        """Cache order status."""
        return await self.set(f"order_status:{order_id}", status_data, ttl)


# Cache service instances
_cache_services = {}

def get_cache_service(service_name: str) -> BaseCacheService:
    """Get cache service instance for specific service."""
    if service_name not in _cache_services:
        if service_name == "product":
            _cache_services[service_name] = ProductCacheService()
        elif service_name == "auth":
            _cache_services[service_name] = AuthCacheService()
        elif service_name == "user":
            _cache_services[service_name] = UserCacheService()
        elif service_name == "order":
            _cache_services[service_name] = OrderCacheService()
        else:
            # Default cache service for other services
            db_mapping = {
                "api_gateway": 0,
                "analytics": 5,
                "payment": 6,
                "notification": 7
            }
            db_number = db_mapping.get(service_name, 0)
            _cache_services[service_name] = BaseCacheService(service_name, db_number)
    
    return _cache_services[service_name]
