# Cache Module Documentation

## Overview
The cache module provides Redis-based caching solutions for all microservices in the Food Fast e-commerce platform.

## Components

### 1. BaseCacheService (`base_cache.py`)
Core cache service that provides base functionality for all services.

**Features:**
- Multi-database Redis support
- Automatic TTL management
- Connection pooling
- Error handling and logging
- Hit/miss ratio tracking

**Usage:**
```python
from shared_code.cache import get_cache_service

# Get cache service for specific microservice
cache = get_cache_service('product')
await cache.connect()

# Basic operations
await cache.set('product:123', product_data, ttl=3600)
product = await cache.get('product:123')
await cache.delete('product:123')

# Pattern operations
await cache.delete_pattern('product:*')
```

### 2. Service-Specific Cache Classes

#### ProductCacheService
- **Database**: Redis DB 1
- **Purpose**: Product catalog, search results, categories
- **TTL**: 1-2 hours for products, 30 minutes for search

```python
from shared_code.cache import ProductCacheService

cache = ProductCacheService()
await cache.connect()

# Cache product
await cache.set_product(123, product_data)
product = await cache.get_product(123)

# Cache search results
await cache.set_search_results(query_hash, results)
results = await cache.get_search_results(query_hash)
```

#### AuthCacheService  
- **Database**: Redis DB 2
- **Purpose**: Sessions, permissions, rate limiting
- **TTL**: 30 minutes for sessions, 1 hour for permissions

```python
from shared_code.cache import AuthCacheService

cache = AuthCacheService()
await cache.connect()

# Session management
await cache.set_user_session(token_hash, session_data)
session = await cache.get_user_session(token_hash)

# Rate limiting
count = await cache.increment_rate_limit(f"api:{user_ip}")
if count > 100:  # Rate limit exceeded
    raise HTTPException(429, "Rate limit exceeded")
```

#### UserCacheService
- **Database**: Redis DB 3  
- **Purpose**: User profiles, preferences, addresses
- **TTL**: 1 hour for profiles, 2 hours for preferences

#### OrderCacheService
- **Database**: Redis DB 4
- **Purpose**: Shopping carts, order status, order history
- **TTL**: 30 minutes for carts, 1 hour for orders

### 3. Cache Manager (`cache_manager.py`)
Administrative tool for cache operations.

**Operations:**
- Clear service cache
- Backup/restore cache data
- List cache keys
- Warm up cache

**Usage:**
```bash
# Clear specific service cache
python scripts/cache_manager.py clear product

# Backup cache
python scripts/cache_manager.py backup analytics

# Restore cache
python scripts/cache_manager.py restore analytics backup.json
```

### 4. Redis Client (`redis_client.py`)
Low-level Redis connection management.

## Database Allocation

| Database | Service | Purpose |
|----------|---------|---------|
| DB 0 | API Gateway | Sessions, routing cache |
| DB 1 | Product Service | Catalog, search, categories |
| DB 2 | Auth Service | Tokens, permissions, rate limits |
| DB 3 | User Service | Profiles, preferences |  
| DB 4 | Order Service | Carts, orders, status |
| DB 5 | Analytics Service | Dashboard, reports |
| DB 6 | Payment Service | Methods, transactions |
| DB 7 | Notification Service | Templates, preferences |
| DB 8-15 | Reserved | Future services |

## Configuration

### Environment Variables
```bash
# Redis connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=1

# Cache settings
CACHE_TTL_DEFAULT=3600
CACHE_TTL_SHORT=300
CACHE_TTL_LONG=7200
CACHE_PREFIX=service_cache
```

### Service-Specific Config
Each service should have cache configuration in `.env.cache`:
```bash
# Product Service Cache
REDIS_DB=1
CACHE_TTL_PRODUCTS=3600
CACHE_TTL_CATEGORIES=7200
CACHE_TTL_SEARCH=1800
```

## Best Practices

### 1. TTL Strategy
- **Frequently changing data**: 5-30 minutes
- **Stable data**: 1-2 hours  
- **Reference data**: 2+ hours
- **User sessions**: 30 minutes

### 2. Key Naming
```python
# Good patterns
"product:123"
"user_profile:456"  
"search:query_hash"
"cart:user_789"

# Avoid
"prod123"
"u456"
"search_results"
```

### 3. Error Handling
```python
try:
    data = await cache.get('key')
    if data is None:
        # Cache miss - fetch from database
        data = await database.get_data()
        await cache.set('key', data)
except Exception as e:
    logger.error(f"Cache error: {e}")
    # Fallback to database
    data = await database.get_data()
```

### 4. Cache Invalidation
```python
# Invalidate on updates
await cache.delete(f"product:{product_id}")
await cache.delete_pattern(f"search:*")

# Invalidate related data
await cache.delete(f"category:{category_id}")
await cache.delete_pattern(f"user:{user_id}:*")
```

## Monitoring

### Performance Metrics
- Hit rate (target: >70%)
- Response time
- Memory usage
- Key count per service

### Alerts
- Hit rate < 70%
- Memory usage > 80%
- Connection failures
- Slow queries

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check Redis service status
   - Verify network connectivity
   - Check authentication credentials

2. **Low Hit Rate**
   - Review TTL settings
   - Check key naming patterns
   - Analyze cache invalidation strategy

3. **Memory Issues**
   - Review eviction policy (LRU recommended)
   - Check for memory leaks
   - Optimize data serialization

4. **Performance Problems**
   - Use connection pooling
   - Implement batching for bulk operations
   - Consider Redis clustering for scale
