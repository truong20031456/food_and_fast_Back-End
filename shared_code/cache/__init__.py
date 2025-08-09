"""
Shared Cache Module for Food Fast E-commerce

This module provides Redis-based caching solutions for all microservices.

Components:
- base_cache: Base cache service implementation
- cache_manager: Cache management utilities
- redis_client: Redis connection and client management
- service_caches: Service-specific cache implementations

Usage:
    from shared_code.cache import get_cache_service
    
    # Get cache service for specific microservice
    cache = get_cache_service('product')
    await cache.connect()
    
    # Use cache
    await cache.set('key', 'value', ttl=3600)
    value = await cache.get('key')
"""

from .base_cache import (
    BaseCacheService,
    ProductCacheService,
    AuthCacheService,
    UserCacheService,
    OrderCacheService,
    get_cache_service
)

__all__ = [
    'BaseCacheService',
    'ProductCacheService', 
    'AuthCacheService',
    'UserCacheService',
    'OrderCacheService',
    'get_cache_service'
]
