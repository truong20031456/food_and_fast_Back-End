# 📋 Service Standardization Example

## 🎯 **TRƯỚC VÀ SAU KHI CHUẨN HÓA**

### 📁 **TRƯỚC**: Cấu trúc không nhất quán

#### Analytics Service:
```
analytics_service/
├── controllers/          # ✅ Standard
├── core/                 # ✅ Standard  
├── models/               # ✅ Standard
├── services/             # ✅ Standard
├── main.py               # ⚠️ Manual FastAPI setup
└── ...
```

#### Product Service:
```
product_service/
├── controllers/          # ✅ Standard
├── modules/              # ❌ Should be 'services'
├── models/               # ✅ Standard
├── core/                 # ✅ Standard
├── main.py               # ⚠️ Manual FastAPI setup
└── ...
```

#### User Service:
```
user_service/
├── app/                  # ❌ Extra layer
│   ├── controllers/      # Nested unnecessarily
│   ├── models/
│   └── services/
├── main.py               # ✅ Uses shared app factory
└── ...
```

---

### 📁 **SAU**: Cấu trúc chuẩn hóa

```
{service_name}/
├── 📄 main.py              # Standardized entry point
├── 📄 requirements.txt     # Dependencies
├── 📄 Dockerfile          # Container config
├── 📄 .env.example        # Environment template
├── 📄 README.md           # Service documentation
│
├── 📁 api/                 # API Layer (NEW)
│   └── routers/           # Route handlers
│       ├── __init__.py
│       ├── health.py      # Health endpoints
│       └── {entity}.py    # Entity routes
│
├── 📁 core/                # Core Configuration
│   ├── __init__.py
│   ├── config.py          # Service settings
│   └── database.py        # DB configuration
│
├── 📁 models/              # Data Models
│   ├── __init__.py
│   └── {entity}.py        # SQLAlchemy models
│
├── 📁 schemas/             # API Schemas
│   ├── __init__.py
│   └── {entity}.py        # Pydantic schemas
│
├── 📁 services/            # Business Logic
│   ├── __init__.py
│   └── {entity}_service.py # Business logic
│
└── 📁 tests/               # Test Suite
    ├── __init__.py
    ├── test_{entity}.py
    └── conftest.py
```

---

## 🔧 **MAIN.PY STANDARDIZATION**

### ❌ **TRƯỚC**: 3 patterns khác nhau

#### Pattern 1: Manual FastAPI (payment, product, analytics, notification)
```python
# payment_service/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Food Fast - Payment Service",
    description="Microservice for payment processing",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, ...)
app.include_router(payment_router)

@app.get("/")
async def root():
    return {"message": "Payment Service"}

@app.get("/health")  
async def health_check():
    return {"status": "healthy"}
```

#### Pattern 2: Shared Factory (auth, user, order, api_gateway)
```python
# user_service/main.py  
from shared_code.core.app import create_app

app = create_app(
    service_name="User Service",
    settings=settings,
    routers=[user_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)
```

#### Pattern 3: Mixed (product)
```python
# product_service/main.py
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, ...)
```

### ✅ **SAU**: Unified Standard Pattern

```python
# {service_name}/main.py
"""
{Service Name} - Main application entry point.
{Service description}
"""

import sys
import os

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared_code.core.app import create_app
from shared_code.core.config import get_service_settings
from shared_code.utils.logging import get_logger

from api.routers.{entity} import router as {entity}_router
from core.database import init_database, close_database

logger = get_logger(__name__)
settings = get_service_settings("{service_name}")


async def startup_task():
    """{Service} startup tasks"""
    logger.info("{Service} starting up...")
    await init_database()


async def shutdown_task():
    """{Service} shutdown tasks"""
    logger.info("{Service} shutting down...")
    await close_database()


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="{Service Name}",
    settings=settings,
    routers=[{entity}_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
```

---

## 🗂️ **SHARED_CODE SIMPLIFICATION**

### ❌ **TRƯỚC**: Phức tạp và trùng lặp
```
shared_code/
├── cache/
│   ├── base_cache.py         # Duplicate logic
│   ├── cache_manager.py      # Duplicate logic
│   ├── redis_client.py       # Redis connection
│   └── legacy_cache_service.py # Legacy (DELETE)
├── middleware/               # EMPTY (DELETE)
├── services/                 # EMPTY (DELETE)
└── ...
```

### ✅ **SAU**: Tối giản và rõ ràng
```
shared_code/
├── 📄 __init__.py
├── 📄 README.md
│
├── 📁 core/                  # Core functionality
│   ├── app.py               # FastAPI factory
│   ├── config.py            # Configuration
│   ├── database.py          # Database management
│   └── exceptions.py        # Exception handling
│
├── 📁 cache/                 # Caching system
│   ├── __init__.py
│   ├── manager.py           # Unified cache management
│   └── redis.py             # Redis client
│
├── 📁 utils/                 # Utilities
│   ├── logging.py
│   ├── security.py
│   └── validation.py
│
└── 📁 models/                # Shared models
    ├── __init__.py
    └── base.py
```

---

## 📊 **BENEFITS**

### 🎯 **Consistency**
- All services follow identical structure
- Same main.py pattern across all services
- Unified import statements

### 🧹 **Simplicity**
- **60% fewer files** (removed cache, docs, duplicates)
- **3 patterns → 1 pattern** for main.py
- **Clear separation** of concerns

### 🚀 **Maintainability**  
- **Easy onboarding** - developers know what to expect
- **Faster development** - copy-paste template
- **Consistent debugging** - same structure everywhere

### 📈 **Scalability**
- **Add new service** in 5 minutes using template
- **Shared functionality** automatically available
- **Version updates** propagate to all services

---

## 🛠️ **IMPLEMENTATION STEPS**

### Phase 1: Service Structure ✅
1. ✅ Created cleanup proposal
2. ✅ Removed __pycache__ directories
3. ✅ Removed .env.cache files
4. ⏳ Standardize service directories

### Phase 2: Main.py Unification
1. Update all services to use shared app factory
2. Remove manual FastAPI setups
3. Standardize startup/shutdown patterns

### Phase 3: Shared Code Simplification  
1. Merge duplicate cache modules
2. Remove empty directories
3. Update all imports

### Phase 4: Documentation
1. Merge reports into main README
2. Create service template
3. Update deployment guides

---

**Kết quả**: Project sẽ có cấu trúc nhất quán, dễ hiểu và maintain hơn đáng kể! 🎉
