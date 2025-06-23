import pytest
from httpx import AsyncClient
from fastapi import status
from main import app
from core.database import Base, engine
import asyncio

import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="module", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Đăng ký
        response = await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword"
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"

        # Đăng nhập
        response = await ac.post("/auth/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer" 