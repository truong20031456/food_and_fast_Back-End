import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from core.database import get_db, Base
from core.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


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
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """Get test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "slug": "test-product",
        "description": "A test product for testing",
        "short_description": "Test product",
        "price": 29.99,
        "category_id": 1,
        "sku": "TEST-001",
        "is_featured": False,
        "is_published": True,
        "is_virtual": False,
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "name": "Test Category",
        "slug": "test-category",
        "description": "A test category for testing",
        "sort_order": 1,
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return {
        "product_id": 1,
        "quantity": 100,
        "reserved_quantity": 0,
        "low_stock_threshold": 10,
        "location": "Warehouse A",
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "product_id": 1,
        "user_id": 1,
        "rating": 4.5,
        "title": "Great product!",
        "comment": "This is a great test product.",
        "is_verified_purchase": True,
    }
