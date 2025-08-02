from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
import sys
import os

# Local database import
from .database import get_db_session
from services.user_service import UserService
from services.token_service import TokenService
from services.audit_service import AuditService
from services.cache_service import CacheService
from utils.security import decode_access_token
from schemas.user import UserRead


async def get_db():
    """Get database session dependency"""
    async for session in get_db_session():
        yield session


async def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get UserService instance"""
    return UserService(db)


async def get_token_service(db: Session = Depends(get_db)) -> TokenService:
    """Get TokenService instance"""
    return TokenService(db)


async def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Get AuditService instance"""
    return AuditService(db)


async def get_cache_service(db: Session = Depends(get_db)) -> CacheService:
    """Get CacheService instance"""
    return CacheService(db)


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserRead:
    """Get current authenticated user"""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        user = await user_service.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return UserRead.from_orm(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
