"""
Payment Service Test Configuration
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
    """Create a test client for the payment service."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for the payment service."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing."""
    return {
        "order_id": "order_123",
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card",
        "customer_id": "customer_456",
        "card_details": {
            "number": "4111111111111111",
            "exp_month": 12,
            "exp_year": 2025,
            "cvc": "123",
            "name": "John Doe"
        }
    }


@pytest.fixture 
def sample_refund_data():
    """Sample refund data for testing."""
    return {
        "payment_id": "pay_123",
        "amount": 50.00,
        "reason": "Customer request",
        "refund_type": "partial"
    }


@pytest.fixture
def webhook_payment_data():
    """Sample webhook payment data for testing."""
    return {
        "id": "evt_test_webhook",
        "object": "event",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_payment",
                "amount": 9999,
                "currency": "usd",
                "status": "succeeded"
            }
        }
    }
