"""
Notification Service Test Configuration
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add the service root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the notification service."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for the notification service."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_notification_data():
    """Sample notification data for testing."""
    return {
        "user_id": "user_123",
        "type": "email",
        "template": "order_confirmation",
        "data": {
            "order_id": "order_456",
            "customer_name": "John Doe",
            "total_amount": 99.99,
            "items": [
                {"name": "Pizza", "quantity": 2, "price": 25.99},
                {"name": "Burger", "quantity": 1, "price": 15.99}
            ]
        },
        "recipient": "john.doe@example.com"
    }


@pytest.fixture
def sample_bulk_notification_data():
    """Sample bulk notification data for testing."""
    return {
        "notifications": [
            {
                "user_id": "user_123",
                "type": "email",
                "template": "promotion",
                "data": {"discount": "20%", "code": "SAVE20"},
                "recipient": "user1@example.com"
            },
            {
                "user_id": "user_456",
                "type": "sms",
                "template": "order_update",
                "data": {"order_id": "order_789", "status": "shipped"},
                "recipient": "+1234567890"
            }
        ]
    }
