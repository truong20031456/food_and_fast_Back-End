import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def test_headers():
    """Test headers fixture"""
    return {"Content-Type": "application/json", "User-Agent": "test-client"}
