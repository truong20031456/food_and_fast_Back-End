import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import (
    create_user,
    get_user,
    update_user,
    soft_delete_user,
    list_users,
)
from app.utils.redis_client import redis_client
import asyncio


@pytest.mark.asyncio
async def test_create_and_get_user(async_session: AsyncSession):
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        profile=None,
    )
    user = await create_user(async_session, user_in)
    assert user.id is not None
    fetched = await get_user(async_session, user.id)
    assert fetched.email == user_in.email


@pytest.mark.asyncio
async def test_update_user(async_session: AsyncSession):
    user_in = UserCreate(
        username="updateuser",
        email="update@example.com",
        password="password123",
        profile=None,
    )
    user = await create_user(async_session, user_in)
    update_in = UserUpdate(username="updated", email=None, password=None, profile=None)
    updated = await update_user(async_session, user.id, update_in)
    assert updated.username == "updated"


@pytest.mark.asyncio
async def test_soft_delete_user(async_session: AsyncSession):
    user_in = UserCreate(
        username="deleteuser",
        email="delete@example.com",
        password="password123",
        profile=None,
    )
    user = await create_user(async_session, user_in)
    deleted = await soft_delete_user(async_session, user.id)
    assert deleted is True
    fetched = await get_user(async_session, user.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_list_users(async_session: AsyncSession):
    # Tạo nhiều user
    for i in range(5):
        await create_user(
            async_session,
            UserCreate(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123",
                profile=None,
            ),
        )
    total, users = await list_users(async_session, limit=3, offset=0)
    assert total >= 5
    assert len(users) == 3


@pytest.mark.asyncio
async def test_soft_deleted_user_not_in_list(async_session: AsyncSession):
    # Tạo user và xóa mềm
    user_in = UserCreate(
        username="softdeluser",
        email="softdel@example.com",
        password="password123",
        profile=None,
    )
    user = await create_user(async_session, user_in)
    await soft_delete_user(async_session, user.id)
    total, users = await list_users(async_session, limit=100, offset=0)
    ids = [u.id for u in users]
    assert user.id not in ids


@pytest.mark.asyncio
async def test_get_user_cache(async_session: AsyncSession):
    user_in = UserCreate(
        username="cacheuser",
        email="cacheuser@example.com",
        password="password123",
        profile=None,
    )
    user = await create_user(async_session, user_in)
    # Xóa cache nếu có
    await redis_client.delete(f"user:{user.id}")
    # Lần 1: lấy từ DB và cache
    fetched1 = await get_user(async_session, user.id)
    # Lần 2: lấy từ cache
    fetched2 = await get_user(async_session, user.id)
    assert fetched1.id == fetched2.id
    # Dọn dẹp
    await redis_client.delete(f"user:{user.id}")
