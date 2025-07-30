"""
Pytest Configuration - Analytics Service Tests.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import Base, get_db_session
from core.config import settings


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_analytics_db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Override database session for testing."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_db_setup):
    """Get database session for testing."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(db_session):
    """Get test client."""
    app.dependency_overrides[get_db_session] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_sales_data():
    """Sample sales data for testing."""
    return {
        "date": "2024-01-01",
        "amount": 1000.0,
        "order_count": 10,
        "customer_count": 8
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_id": "prod_001",
        "product_name": "Test Product",
        "quantity_sold": 50,
        "revenue": 500.0,
        "category": "Electronics"
    }


@pytest.fixture
def sample_user_activity_data():
    """Sample user activity data for testing."""
    return {
        "user_id": "user_001",
        "login_count": 5,
        "last_login": "2024-01-01T10:00:00",
        "total_orders": 3,
        "total_spent": 150.0
    }