# 🚀 Food & Fast E-Commerce - Refactoring Guide

## Overview

This document outlines the comprehensive refactoring of the Food & Fast E-Commerce platform to implement FastAPI best practices, standardized architecture patterns, and improved maintainability.

## 🎯 Refactoring Goals

- **Standardization**: Consistent structure across all microservices
- **Maintainability**: Easy to understand, modify, and extend
- **Developer Experience**: Simplified onboarding and development
- **Production Ready**: Robust error handling, logging, and monitoring
- **Scalability**: Support for horizontal scaling and service discovery

## 🏗️ New Architecture

### Shared Foundation

All services now build upon a shared foundation located in the `/shared` directory:

```
shared/
├── core/                    # Core application components
│   ├── app.py              # FastAPI application factory
│   ├── config.py           # Standardized configuration management
│   ├── database.py         # Database connection and session management
│   ├── dependencies.py     # Common dependency injection utilities
│   ├── exceptions.py       # Custom exception classes
│   └── repository.py       # Base repository pattern
├── models/                 # Shared data models
│   └── base.py            # Base SQLAlchemy models and Pydantic schemas
├── utils/                  # Utility modules
│   ├── logging.py         # Centralized logging configuration
│   ├── redis.py           # Redis client and caching utilities
│   └── validation.py      # Common validation utilities
└── __init__.py
```

### Service Structure

Each service follows a standardized structure:

```
service_name/
├── controllers/            # HTTP request handlers (FastAPI routers)
├── services/              # Business logic layer
├── models/                # Data models (SQLAlchemy)
├── schemas/               # API schemas (Pydantic)
├── core/                  # Service-specific configuration
├── utils/                 # Service-specific utilities
├── tests/                 # Test suite
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
├── Dockerfile           # Container configuration
└── .env                 # Environment variables
```

## 🔧 Key Components

### 1. Application Factory (`shared/core/app.py`)

The `create_app()` function provides a standardized way to create FastAPI applications with:

- Automatic middleware setup (CORS, request logging, rate limiting)
- Standard exception handlers
- Health check endpoints
- Metrics endpoints (if enabled)
- Database and Redis initialization
- Graceful startup and shutdown

**Usage:**
```python
from core.app import create_app
from core.config import get_service_settings

settings = get_service_settings("auth_service")

app = create_app(
    service_name="Auth Service",
    settings=settings,
    routers=[auth_router, user_router],
    startup_tasks=[create_tables],
    shutdown_tasks=[cleanup_resources]
)
```

### 2. Configuration Management (`shared/core/config.py`)

Centralized configuration with environment-specific settings:

- Type-safe configuration with Pydantic
- Environment validation
- Service-specific defaults
- Shared base configuration

**Usage:**
```python
from core.config import get_service_settings

settings = get_service_settings("auth_service")
print(settings.DATABASE_URL)  # Automatically configured
```

### 3. Database Management (`shared/core/database.py`)

Async database management with:

- Connection pooling
- Session management with proper cleanup
- Health checks
- Automatic reconnection

**Usage:**
```python
from core.database import get_db_session

async def get_user(user_id: str, db: AsyncSession = Depends(get_db_session)):
    # Use database session
    pass
```

### 4. Repository Pattern (`shared/core/repository.py`)

Generic repository with common CRUD operations:

- Type-safe operations
- Pagination support
- Search functionality
- Filtering and sorting

**Usage:**
```python
from core.repository import BaseRepository

class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by_field("email", email)
```

### 5. Dependency Injection (`shared/core/dependencies.py`)

Common dependencies for:

- Authentication and authorization
- Rate limiting
- Pagination parameters
- Request context

**Usage:**
```python
from core.dependencies import require_authentication, get_current_user

@router.get("/profile")
async def get_profile(current_user: CurrentUser = Depends(require_authentication)):
    return current_user
```

### 6. Error Handling (`shared/core/exceptions.py`)

Standardized exception handling:

- Custom exception classes
- Automatic HTTP status code mapping
- Consistent error response format

**Usage:**
```python
from core.exceptions import not_found_exception

if not user:
    raise not_found_exception("User not found", details={"user_id": user_id})
```

### 7. Logging (`shared/utils/logging.py`)

Structured logging with:

- JSON formatting for production
- Request correlation IDs
- Centralized configuration
- Service-specific loggers

**Usage:**
```python
from utils.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing request", extra={"user_id": user_id})
```

### 8. Caching (`shared/utils/redis.py`)

Redis utilities with:

- Async operations
- Automatic serialization/deserialization
- Connection pooling
- Decorator-based caching

**Usage:**
```python
from utils.redis import cache, get_redis_manager

@cache("user_profile", expire=300)
async def get_user_profile(user_id: str):
    # Function result will be cached
    return profile
```

### 9. Validation (`shared/utils/validation.py`)

Common validation utilities:

- Email and phone validation
- Password strength checking
- Custom Pydantic validators
- Data sanitization

**Usage:**
```python
from utils.validation import EmailStr, password_validator

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., validators=[password_validator])
```

## 🔄 Migration Process

### Step 1: Set up Shared Foundation

1. The shared foundation has been created in `/shared`
2. Core components are available for all services
3. Base models and utilities are standardized

### Step 2: Update Service Configuration

Each service now uses standardized configuration:

```python
# Old way
from config.settings import settings

# New way
from core.config import get_service_settings
settings = get_service_settings("service_name")
```

### Step 3: Refactor Application Entry Point

Services now use the application factory:

```python
# Old way
app = FastAPI(title="Service Name")
app.include_router(router)

# New way
from core.app import create_app
app = create_app(
    service_name="Service Name",
    settings=settings,
    routers=[router]
)
```

### Step 4: Update Database Models

Models now extend the shared base model:

```python
# Old way
class User(Base):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# New way
from models.base import BaseDBModel

class User(BaseDBModel):
    # id, created_at, updated_at automatically included
    pass
```

### Step 5: Implement Repository Pattern

Replace direct database queries with repositories:

```python
# Old way
async def get_user(db: AsyncSession, user_id: int):
    return await db.execute(select(User).where(User.id == user_id))

# New way
class UserRepository(BaseRepository[User]):
    pass

async def get_user(repo: UserRepository, user_id: str):
    return await repo.get_by_id(user_id)
```

## 📊 Service Status

### ✅ Completed Refactoring

- **Shared Foundation**: Core modules, utilities, and base models
- **API Gateway**: Fully refactored with new architecture
- **Auth Service**: Partially refactored (main.py, config)

### 🚧 In Progress

- **Auth Service**: Controllers, models, and services
- **User Service**: Full refactoring needed
- **Product Service**: Full refactoring needed

### ⏳ Pending

- **Order Service**: Full refactoring needed
- **Payment Service**: Full refactoring needed
- **Notification Service**: Full refactoring needed
- **Analytics Service**: Full refactoring needed

## 🛠️ Development Tools

### Setup Script

Run the development setup script to configure your environment:

```bash
python scripts/dev_setup.py
```

This script will:
- Create symbolic links to shared modules
- Generate environment files
- Install dependencies
- Setup databases (optional)

### Running Services

Each service can be run individually:

```bash
cd auth_service
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker Support

Services maintain Docker support with updated configurations:

```bash
docker-compose up -d
```

## 📈 Benefits of Refactoring

### For Developers

- **Consistent Structure**: Same patterns across all services
- **Reduced Boilerplate**: Shared utilities eliminate repetitive code
- **Better Developer Experience**: Standardized tools and patterns
- **Easier Testing**: Common test utilities and patterns
- **Type Safety**: Full type hints and validation

### For Operations

- **Improved Monitoring**: Standardized metrics and health checks
- **Better Logging**: Structured logging with correlation IDs
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Consistent error responses and logging

### For the Business

- **Faster Development**: Reduced time to implement new features
- **Better Reliability**: Standardized error handling and monitoring
- **Easier Scaling**: Service discovery and health checks
- **Lower Maintenance**: Consistent patterns reduce complexity

## 🔍 Testing the Refactored Services

### Health Checks

Test service health:

```bash
# API Gateway
curl http://localhost:8000/health

# Auth Service  
curl http://localhost:8001/health

# Service Discovery
curl http://localhost:8000/services
```

### API Documentation

Access interactive API documentation:

- API Gateway: http://localhost:8000/docs
- Auth Service: http://localhost:8001/docs

### Logging

Check structured logs in development:

```bash
# View logs with correlation IDs
tail -f auth_service/logs/app.log | jq '.'
```

## 🚀 Next Steps

1. **Complete Service Refactoring**: Finish refactoring remaining services
2. **Add Comprehensive Tests**: Implement test suites for all services
3. **Enhance Monitoring**: Add metrics and alerting
4. **Documentation**: Complete API documentation
5. **Performance Optimization**: Implement caching strategies
6. **Security Hardening**: Add security middleware and validation

## 📚 Additional Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Redis Python Documentation](https://redis.readthedocs.io/en/stable/)

---

**Happy Coding! 🎉**

For questions or support, please refer to the project documentation or create an issue in the repository.