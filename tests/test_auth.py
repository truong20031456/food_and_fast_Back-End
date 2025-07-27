import pytest
from httpx import AsyncClient
from fastapi import status
from jose import jwt

# Assuming SECRET_KEY and ALGORITHM are loaded from conftest.py's environment setup
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")


@pytest.mark.asyncio
async def test_register_and_login_all_cases(client: AsyncClient):
    # Successful Registration
    register_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "Testpassword1!",
        "confirm_password": "Testpassword1!",
        "terms_accepted": True,
    }
    response = await client.post("/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["username"] == "testuser"

    # Successful Login
    login_data = {"email": "testuser@example.com", "password": "Testpassword1!"}
    response = await client.post("/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Decode token to check payload
    payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["email"] == "testuser@example.com"
    assert payload["id"] is not None

    # Register with existing email
    register_data_duplicate_email = {
        "email": "testuser@example.com",
        "username": "anotheruser",
        "password": "Anotherpassword1!",
        "confirm_password": "Anotherpassword1!",
        "terms_accepted": True,
    }
    response = await client.post("/register", json=register_data_duplicate_email)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

    # Login with incorrect password
    response = await client.post(
        "/login", json={"email": "testuser@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"

    # Login with non-existent user
    response = await client.post(
        "/login", json={"email": "nonexistent@example.com", "password": "any"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid credentials"

    # Register with missing fields
    response = await client.post("/register", json={"email": "missing@example.com"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Login with missing fields
    response = await client.post("/login", json={"email": "testuser@example.com"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test password strength validation during registration
    weak_password_data = {
        "email": "weakpass@example.com",
        "username": "weakpass",
        "password": "short",
        "confirm_password": "short",
        "terms_accepted": True,
    }
    response = await client.post("/register", json=weak_password_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        "Password must be at least 8 characters long"
        in response.json()["detail"]["password"]
    )

    # Test password mismatch during registration
    mismatch_password_data = {
        "email": "mismatch@example.com",
        "username": "mismatch",
        "password": "StrongPass1!",
        "confirm_password": "MismatchPass2@",
        "terms_accepted": True,
    }
    response = await client.post("/register", json=mismatch_password_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Passwords do not match" in response.json()["detail"]["confirm_password"]
