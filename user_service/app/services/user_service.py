# User business logic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserProfile
from app.schemas.user import UserCreate, UserUpdate
from app.exceptions import (
    UserNotFoundError,
    DuplicateUserError,
    DatabaseError,
    CacheError,
)
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
        raise DuplicateUserError("Email or username already exists")
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
        raise DatabaseError("Failed to create user due to integrity error")
    return db_user


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    cache_key = f"user:{user_id}"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            # Return cached data but still return User model for consistency
            from app.schemas.user import UserRead

            cached_user = UserRead.model_validate(json.loads(cached))
            # Convert back to User model for consistency
            result = await db.execute(
                select(User).where(User.id == user_id, User.is_deleted == False)
            )
            return result.scalar_one_or_none()
    except Exception as e:
        # Log Redis error but continue without cache
        print(f"Redis error in get_user: {e}")

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if user:
        from app.schemas.user import UserRead

        user_data = UserRead.model_validate(user).model_dump()
        try:
            await redis_client.set(cache_key, json.dumps(user_data), ex=300)
        except Exception as e:
            # Log Redis error but continue
            print(f"Redis error setting cache: {e}")
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

    # Check for duplicate email/username if updating
    if user_data.username or user_data.email:
        duplicate_query = select(User).where(
            (User.id != user_id) & (User.is_deleted == False)
        )
        if user_data.username:
            duplicate_query = duplicate_query.where(User.username == user_data.username)
        if user_data.email:
            duplicate_query = duplicate_query.where(User.email == user_data.email)

        existing_user = await db.execute(duplicate_query)
        if existing_user.scalar_one_or_none():
            raise DuplicateUserError("Email or username already exists")

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

    try:
        await db.commit()
        await db.refresh(db_user)
        # Clear user cache
        await redis_client.delete(f"user:{user_id}")
        # Clear all list caches (more efficient than wildcard)
        await redis_client.delete("user_list:*")
        return db_user
    except IntegrityError:
        await db.rollback()
        raise DatabaseError("Failed to update user due to integrity error")


async def soft_delete_user(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        return False
    db_user.is_deleted = True
    await db.commit()
    # Clear user cache
    await redis_client.delete(f"user:{user_id}")
    # Clear all list caches (more efficient than wildcard)
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
    from sqlalchemy import func

    total_result = await db.execute(
        select(func.count(User.id)).where(User.is_deleted == False)
    )
    total = total_result.scalar()
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


async def authenticate_user(
    db: AsyncSession, username_or_email: str, password: str
) -> Optional[User]:
    """Authenticate user with username/email and password"""
    # Check if input is email or username
    if "@" in username_or_email:
        result = await db.execute(
            select(User).where(
                User.email == username_or_email, User.is_deleted == False
            )
        )
    else:
        result = await db.execute(
            select(User).where(
                User.username == username_or_email, User.is_deleted == False
            )
        )

    user = result.scalar_one_or_none()
    if not user:
        return None

    # Verify password
    if not pwd_context.verify(password, user.password):
        return None

    return user
