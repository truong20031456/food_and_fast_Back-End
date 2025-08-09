# 🏗️ Food Fast E-commerce - Service Architecture Standard

## Overview
Standardized architecture for all microservices in the Food Fast e-commerce platform.

## 📋 Current Service Analysis

### Inconsistencies Found:
1. **Structure Variations**:
   - Analytics: `controllers/`, `core/`, `models/`, `services/`
   - Product: `controllers/`, `modules/`, `models/`, `core/`
   - User: `app/controllers/`, `app/models/`, `app/services/`
   - Auth: `controllers/`, `core/`, `models/`, `services/`
   - Order: `controllers/`, `services/`, `models/`, `core/`

2. **Import Inconsistencies**:
   - Some use relative imports
   - Different shared_code integration patterns
   - Mixed dependency injection styles

3. **Configuration Variations**:
   - Different environment file patterns
   - Inconsistent shared_code usage
   - Various startup/shutdown patterns

## 🎯 Standardized Architecture

### 📁 Standard Directory Structure:
```
{service_name}/
├── 📄 __init__.py              # Service module
├── 📄 main.py                  # FastAPI application entry point
├── 📄 README.md                # Service documentation
├── 📄 requirements.txt         # Python dependencies
├── 📄 Dockerfile              # Production container
├── 📄 .env.example            # Environment template
├── 📄 .dockerignore           # Docker ignore rules
│
├── 📁 api/                     # 🌐 API Layer
│   ├── __init__.py            # API exports
│   ├── dependencies.py        # FastAPI dependencies
│   └── routers/               # API route handlers
│       ├── __init__.py        # Router exports
│       ├── health.py          # Health check endpoints
│       └── {entity}_router.py # Entity-specific routes
│
├── 📁 core/                    # ⚙️ Core Configuration
│   ├── __init__.py            # Core exports
│   ├── config.py              # Service-specific settings
│   ├── database.py            # Database configuration
│   └── events.py              # Application events
│
├── 📁 domain/                  # 🏢 Business Domain
│   ├── __init__.py            # Domain exports
│   ├── entities/              # Domain entities (models)
│   │   ├── __init__.py        # Entity exports
│   │   └── {entity}.py        # Entity definitions
│   ├── services/              # Business logic services
│   │   ├── __init__.py        # Service exports
│   │   └── {entity}_service.py # Entity business logic
│   └── repositories/          # Data access layer
│       ├── __init__.py        # Repository exports
│       └── {entity}_repository.py # Entity data access
│
├── 📁 infrastructure/          # 🛠️ Infrastructure Layer
│   ├── __init__.py            # Infrastructure exports
│   ├── cache/                 # Cache implementations
│   ├── external/              # External service clients
│   ├── messaging/             # Message queue handlers
│   └── storage/               # Storage implementations
│
├── 📁 schemas/                 # 📋 API Schemas
│   ├── __init__.py            # Schema exports
│   ├── requests/              # Request DTOs
│   ├── responses/             # Response DTOs
│   └── {entity}.py            # Entity schemas
│
└── 📁 tests/                   # 🧪 Test Suite
    ├── __init__.py            # Test exports
    ├── conftest.py            # Test configuration
    ├── unit/                  # Unit tests
    ├── integration/           # Integration tests
    └── fixtures/              # Test fixtures
```

## 🚀 Implementation Plan

### Phase 1: Create Standard Templates
1. **Service Template Generator**
2. **Standard main.py Template**
3. **Configuration Templates**
4. **Docker Templates**

### Phase 2: Migrate Existing Services
1. **Analytics Service** ✅ (Already well-structured)
2. **User Service** (Needs restructuring)
3. **Product Service** (Needs consolidation)
4. **Auth Service** (Needs completion)
5. **Order Service** (Needs restructuring)
6. **Payment Service** (Needs restructuring)
7. **Notification Service** (Needs restructuring)

### Phase 3: Implement Advanced Features
1. **Service Discovery**
2. **Distributed Tracing**
3. **Event Sourcing**
4. **Circuit Breakers**

## 📝 Standards and Conventions

### 1. **Naming Conventions**:
- Services: `{service_name}_service`
- Routers: `{entity}_router.py`
- Models: `{entity}.py`
- Services: `{entity}_service.py`
- Repositories: `{entity}_repository.py`

### 2. **Import Standards**:
```python
# External imports first
from fastapi import FastAPI
from sqlalchemy.orm import Session

# Shared code imports
from shared_code.core import BaseSettings
from shared_code.cache import get_cache_service

# Local imports last
from .api.routers import user_router
from .domain.services import UserService
```

### 3. **Configuration Standards**:
```python
# Service-specific settings extending BaseServiceSettings
class ServiceSettings(BaseServiceSettings):
    service_name: str = "Service Name"
    service_port: int = 8001
```

### 4. **Main.py Standards**:
```python
# Standard application factory pattern
app = create_app(
    service_name="Service Name",
    settings=settings,
    routers=[router1, router2],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)
```

## 🎯 Benefits

### 1. **Consistency**:
- Uniform structure across all services
- Predictable file locations
- Standard naming conventions

### 2. **Maintainability**:
- Clear separation of concerns
- Easy to navigate and understand
- Consistent dependency injection

### 3. **Scalability**:
- Modular architecture
- Easy to add new features
- Service template reusability

### 4. **Developer Experience**:
- Quick onboarding for new developers
- Consistent development patterns
- Shared tooling and utilities

## 🔄 Migration Strategy

### For Each Service:
1. **Analyze current structure**
2. **Create migration plan**
3. **Implement new structure**
4. **Update imports and dependencies**
5. **Test functionality**
6. **Update documentation**

### Migration Order (Priority):
1. **User Service** (Most inconsistent)
2. **Product Service** (Complex structure)
3. **Auth Service** (Core dependency)
4. **Order Service** (Business critical)
5. **Payment Service** (Security sensitive)
6. **Notification Service** (Supporting service)
7. **API Gateway** (Entry point)

---

**Next: Implement service restructuring starting with User Service**
