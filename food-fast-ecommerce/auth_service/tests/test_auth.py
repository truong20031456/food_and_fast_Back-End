import pytest
from httpx import AsyncClient
from fastapi import status
from main import app
from core.database import Base, engine
import asyncio
from jose import jwt
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

@pytest.fixture(scope="module", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_register_and_login_all_cases():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Đăng ký thành công
        response = await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"

        # Đăng nhập đúng
        response = await ac.post("/auth/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Giải mã token kiểm tra payload
        payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["username"] == "testuser"
        assert payload["email"] == "testuser@example.com"
        assert "id" in payload

        # Đăng ký trùng username
        response = await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "testuser2@example.com",
            "password": "testpassword"
        })
        assert response.status_code == 400
        assert response.json()["detail"] == "Username already registered"

        # Đăng nhập sai mật khẩu
        response = await ac.post("/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

        # Đăng nhập user không tồn tại
        response = await ac.post("/auth/login", json={
            "username": "notfound",
            "password": "any"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

        # Đăng ký thiếu trường
        response = await ac.post("/auth/register", json={
            "username": "user2"
        })
        assert response.status_code == 422

        # Đăng nhập thiếu trường
        response = await ac.post("/auth/login", json={
            "username": "testuser"
        })
        assert response.status_code == 422 