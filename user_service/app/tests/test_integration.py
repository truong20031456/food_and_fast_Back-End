"""
Integration tests for User Service
"""

import pytest
import httpx
from fastapi.testclient import TestClient
import asyncio

from app.controllers.user_router import router
from shared_code.core.app import create_app
from shared_code.core.config import get_service_settings


@pytest.fixture
def test_settings():
    """Test settings configuration."""
    settings = get_service_settings("user_service")
    settings.ENVIRONMENT = "testing"
    settings.DATABASE_URL = "sqlite:///./test.db"
    return settings


@pytest.fixture
def test_app(test_settings):
    """Create test FastAPI app."""
    app = create_app(
        service_name="Test User Service", settings=test_settings, routers=[router]
    )
    return app


@pytest.fixture
def client(test_app):
    """Test client fixture."""
    return TestClient(test_app)


class TestUserService:
    """Test suite for User Service."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "User Service"

    def test_create_user(self, client):
        """Test user creation."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "securepassword123",
        }

        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "password" not in data  # Password should not be returned

    def test_get_user_profile(self, client):
        """Test getting user profile."""
        # First create a user
        user_data = {
            "email": "profile@example.com",
            "username": "profileuser",
            "full_name": "Profile User",
            "password": "securepassword123",
        }

        create_response = client.post("/users/", json=user_data)
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # Then get the profile
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]

    def test_update_user_profile(self, client):
        """Test updating user profile."""
        # Create user first
        user_data = {
            "email": "update@example.com",
            "username": "updateuser",
            "full_name": "Update User",
            "password": "securepassword123",
        }

        create_response = client.post("/users/", json=user_data)
        user_id = create_response.json()["id"]

        # Update user
        update_data = {"full_name": "Updated Name"}
        response = client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    def test_user_validation(self, client):
        """Test user data validation."""
        invalid_user_data = {
            "email": "invalid-email",  # Invalid email format
            "username": "",  # Empty username
            "password": "123",  # Too short password
        }

        response = client.post("/users/", json=invalid_user_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, test_app):
        """Test concurrent user creation."""
        async with httpx.AsyncClient(app=test_app, base_url="http://test") as ac:
            tasks = []
            for i in range(5):
                user_data = {
                    "email": f"concurrent{i}@example.com",
                    "username": f"concurrent{i}",
                    "full_name": f"Concurrent User {i}",
                    "password": "securepassword123",
                }
                task = ac.post("/users/", json=user_data)
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

            # All should succeed
            for response in responses:
                assert response.status_code == 201


if __name__ == "__main__":
    pytest.main([__file__])
