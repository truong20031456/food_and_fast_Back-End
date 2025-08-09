# Shared Code for Food Fast E-commerce

This directory contains shared components, utilities, and base classes for all microservices in the Food & Fast E-Commerce Platform.

## 📁 Directory Structure

```
shared_code/
├── cache/               # 🔥 Redis caching system
│   ├── __init__.py     # Cache module exports
│   ├── base_cache.py   # Base cache service implementation
│   ├── cache_manager.py # Cache management utilities
│   ├── redis_client.py # Redis connection management
│   └── legacy_cache_service.py # Legacy cache service
├── core/                # Core configuration and base classes
│   ├── app.py          # FastAPI application factory
│   ├── config.py       # Base settings configuration
│   ├── database.py     # Database connection management
│   ├── dependencies.py # Common dependency injection
│   ├── exceptions.py   # Custom exception classes
│   └── repository.py   # Base repository pattern
├── middleware/          # 🛡️ Common middleware components
│   └── __init__.py     # Middleware module
├── models/              # Shared data models
│   └── base.py         # Base model classes
├── monitoring/          # 📊 Monitoring and observability
│   ├── __init__.py     # Monitoring module
│   └── performance_monitor.py # Performance monitoring
├── services/            # Shared services
│   └── __init__.py     # Services module
├── utils/               # 🔧 Utility functions
│   ├── cache_manager.py # Cache management
│   ├── logging.py       # Logging configuration
│   ├── redis.py         # Redis client utilities
│   └── validation.py    # Validation utilities
├── env.example          # Environment configuration example
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Environment Configuration

Copy the example environment file and configure it for your service:

```bash
cp shared_code/env.example .env
```

### 2. Basic Service Setup

```python
from shared_code.core.config import get_service_settings
from shared_code.core.app import create_app

# Get service-specific settings
settings = get_service_settings("your_service_name")

# Create FastAPI app
app = create_app(
    service_name="Your Service",
    settings=settings,
    routers=[your_routers]
)
```

### 3. Using Shared Models

```python
from shared_code.models.base import BaseDBModel, BaseSchema

class YourModel(BaseDBModel):
    __tablename__ = "your_table"
    # Your model fields

class YourSchema(BaseSchema):
    # Your schema fields
```

## ⚙️ Configuration

### Base Settings

The `BaseServiceSettings` class provides comprehensive configuration for all services:

```python
from shared_code.core.config import BaseServiceSettings

settings = BaseServiceSettings()
```

#### Key Configuration Areas:

- **Environment**: Development, staging, production, testing
- **Database**: Connection pooling, URLs, echo mode
- **Redis**: Connection pooling, URLs
- **Security**: JWT, secrets, OAuth
- **CORS**: Origins, methods, headers
- **Rate Limiting**: Requests per minute
- **Logging**: Levels, formats, files
- **API**: Documentation, health checks, metrics

### Environment Variables

All configuration can be set via environment variables. See `env.example` for a complete list.

### Service-Specific Configuration

Use the factory function to get service-specific defaults:

```python
from shared_code.core.config import get_service_settings

# Gets pre-configured settings for auth_service
auth_settings = get_service_settings("auth_service")

# Override specific values
auth_settings = get_service_settings("auth_service", SERVICE_PORT=8001)
```

## 🗄️ Database Management

### Connection Management

```python
from shared_code.core.database import get_database_manager

# Get database manager with settings
db_manager = get_database_manager(settings=settings)

# Use in dependency injection
async def get_db():
    async with db_manager.get_db() as session:
        yield session
```

### Repository Pattern

```python
from shared_code.core.repository import BaseRepository

class YourRepository(BaseRepository[YourModel]):
    def __init__(self, db_session):
        super().__init__(YourModel, db_session)
    
    # Custom methods
    async def get_by_custom_field(self, field_value):
        return await self.get_by_field("custom_field", field_value)
```

## 🔄 Redis Management

### Connection Management

```python
from shared_code.utils.redis import get_redis_manager

# Get Redis manager
redis_manager = get_redis_manager()

# Use Redis operations
await redis_manager.set("key", "value", expire=300)
value = await redis_manager.get("key")
```

### Caching Decorator

```python
from shared_code.utils.redis import cache

@cache("user_profile", expire=300)
async def get_user_profile(user_id: str):
    # Expensive operation
    return user_data
```

## 📝 Logging

### Setup Logging

```python
from shared_code.utils.logging import setup_logging

# Setup service logging
logger = setup_logging("your_service", settings)
```

### Request Logging

```python
from shared_code.utils.logging import log_request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    with log_request(logger, request_id, method, path):
        response = await call_next(request)
    return response
```

## 🔒 Security

### Authentication Dependencies

```python
from shared_code.core.dependencies import get_current_user, require_authentication

@app.get("/protected")
async def protected_route(current_user = Depends(require_authentication)):
    return {"user": current_user.user_id}

@app.get("/optional-auth")
async def optional_auth_route(current_user = Depends(get_current_user)):
    if current_user:
        return {"authenticated": True, "user": current_user.user_id}
    return {"authenticated": False}
```

### Role-Based Access

```python
from shared_code.core.dependencies import require_roles

@app.get("/admin-only")
async def admin_route(current_user = Depends(require_roles("admin"))):
    return {"message": "Admin access granted"}
```

## ✅ Validation

### Input Validation

```python
from shared_code.utils.validation import ValidationUtils

# Validate email
is_valid, email = ValidationUtils.validate_email_address("user@example.com")

# Validate phone number
is_valid, phone = ValidationUtils.validate_phone_number("+1234567890", "US")

# Validate password strength
is_valid, errors = ValidationUtils.validate_password_strength("MyPass123!")
```

### Pydantic Validators

```python
from shared_code.utils.validation import email_validator, password_validator

class UserSchema(BaseSchema):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
    
    @validator("email")
    def validate_email(cls, v):
        return email_validator(v)
    
    @validator("password")
    def validate_password(cls, v):
        return password_validator(v)
```

## 🏥 Health Checks

All services automatically include health check endpoints:

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics` (if enabled)

## 🔧 Customization

### Custom Startup/Shutdown Tasks

```python
async def custom_startup():
    # Your startup logic
    pass

async def custom_shutdown():
    # Your shutdown logic
    pass

app = create_app(
    service_name="Your Service",
    settings=settings,
    startup_tasks=[custom_startup],
    shutdown_tasks=[custom_shutdown]
)
```

### Custom Exception Handling

```python
from shared_code.core.exceptions import BaseServiceException

class CustomException(BaseServiceException):
    def __init__(self, message: str):
        super().__init__(message, "CUSTOM_ERROR")
```

## 🧪 Testing

### Test Configuration

```python
import pytest
from shared_code.core.config import get_service_settings

@pytest.fixture
def test_settings():
    return get_service_settings("test_service", ENVIRONMENT="testing")
```

### Database Testing

```python
from shared_code.core.database import get_database_manager

@pytest.fixture
async def db_session():
    db_manager = get_database_manager(settings=test_settings)
    async with db_manager.get_db() as session:
        yield session
```

## 📊 Monitoring

### Metrics

Enable metrics in your settings:

```python
settings = get_service_settings("your_service", ENABLE_METRICS=True)
```

### Logging

Configure structured logging for production:

```python
settings = get_service_settings(
    "your_service",
    LOG_LEVEL="INFO",
    LOG_FILE="logs/app.log"
)
```

## 🔐 Security Best Practices

1. **Environment Variables**: Never hardcode secrets
2. **Production Settings**: Always use production-specific configurations
3. **CORS**: Restrict allowed origins in production
4. **Rate Limiting**: Configure appropriate limits
5. **Logging**: Use structured logging and avoid logging sensitive data
6. **Validation**: Always validate input data
7. **Authentication**: Use proper JWT validation
8. **Database**: Use connection pooling and secure credentials

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` format
   - Verify database is running
   - Check network connectivity

2. **Redis Connection Failed**
   - Check `REDIS_URL` format
   - Verify Redis is running
   - Check network connectivity

3. **Configuration Validation Errors**
   - Check environment variable formats
   - Verify required fields are set
   - Check production security requirements

4. **Import Errors**
   - Ensure `shared_code` is in Python path
   - Check relative imports in your service

### Debug Mode

Enable debug mode for detailed error messages:

```python
settings = get_service_settings("your_service", DEBUG=True)
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Redis Python Documentation](https://redis-py.readthedocs.io/) 