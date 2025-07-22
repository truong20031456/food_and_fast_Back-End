# User business logic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext
from typing import Optional, List, Tuple
from app.utils.redis_client import redis_client
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    # Check duplicate email/username
    result = await db.execute(
        select(User).where(
            (User.email == user_in.email) | (User.username == user_in.username)
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise ValueError("Email or username already exists")
    hashed_pw = hash_password(user_in.password)
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hashed_pw,
        profile=UserProfile(**user_in.profile.dict()) if user_in.profile else None,
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Failed to create user due to integrity error")
    return db_user


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    cache_key = f"user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        from app.schemas.user import UserRead

        return UserRead.model_validate(json.loads(cached))
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if user:
        from app.schemas.user import UserRead

        user_data = UserRead.model_validate(user).model_dump()
        await redis_client.set(cache_key, json.dumps(user_data), ex=300)
    return user


async def update_user(
    db: AsyncSession, user_id: int, user_data: UserUpdate
) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return None
    if user_data.username:
        db_user.username = user_data.username
    if user_data.email:
        db_user.email = user_data.email
    if user_data.password:
        db_user.password = hash_password(user_data.password)
    if user_data.profile:
        if db_user.profile:
            for field, value in user_data.profile.dict(exclude_unset=True).items():
                setattr(db_user.profile, field, value)
        else:
            db_user.profile = UserProfile(**user_data.profile.dict())
    await db.commit()
    await db.refresh(db_user)
    # Xóa cache user
    await redis_client.delete(f"user:{user_id}")
    await redis_client.delete("user_list:*")
    return db_user


async def soft_delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False
    db_user.is_deleted = True
    await db.commit()
    # Xóa cache user
    await redis_client.delete(f"user:{user_id}")
    await redis_client.delete("user_list:*")
    return True


async def list_users(
    db: AsyncSession, limit: int = 10, offset: int = 0
) -> Tuple[int, List[User]]:
    cache_key = f"user_list:{limit}:{offset}"
    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        from app.schemas.user import UserRead

        users = [UserRead.model_validate(u) for u in data["users"]]
        return data["total"], users
    total_result = await db.execute(select(User).where(User.is_deleted == False))
    total = len(total_result.scalars().all())
    result = await db.execute(
        select(User).where(User.is_deleted == False).offset(offset).limit(limit)
    )
    users = result.scalars().all()
    from app.schemas.user import UserRead

    users_data = [UserRead.model_validate(u).model_dump() for u in users]
    await redis_client.set(
        cache_key, json.dumps({"total": total, "users": users_data}), ex=300
    )
    return total, users
