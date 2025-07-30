from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from datetime import datetime, timezone
from passlib.context import CryptContext

from models.user import User
from schemas.user import UserCreate, UserUpdate
from utils.security import get_password_hash
from utils.logger import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await self.get_by_email(user_data.email)
            if existing_user:
                raise ValueError("Email already registered")

            # Create user object
            user = User(
                email=user_data.email,
                username=user_data.username,
                password_hash=get_password_hash(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone_number=user_data.phone_number,
                bio=user_data.bio,
                status="pending_verification",
            )

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            logger.info(f"User created successfully: {user.email}")
            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            user = await self.get_by_id(user_id)
            if not user:
                return None

            # Update fields
            update_data = user_data.dict(exclude_unset=True)
            if update_data:
                await self.db.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(**update_data, updated_at=datetime.now(timezone.utc))
                )
                await self.db.commit()
                await self.db.refresh(user)

            return user

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user: {e}")
            return None

    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    last_login_at=datetime.now(timezone.utc), failed_login_attempts=0
                )
            )
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update last login: {e}")
            return False

    async def increment_failed_attempts(self, user_id: int) -> bool:
        """Increment failed login attempts"""
        try:
            user = await self.get_by_id(user_id)
            if user:
                user.failed_login_attempts += 1
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to increment failed attempts: {e}")
            return False
