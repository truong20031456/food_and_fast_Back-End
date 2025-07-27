from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from typing import Optional

from core.config import settings  # Import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def create_access_token(user: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token for a user"""
    to_encode = {
        "sub": str(user["id"]),  # Use user ID as sub for consistency
        "id": user["id"],
        "username": user.get("username"),  # Use .get() for optional fields
        "email": user.get("email"),
    }
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})

    # SECRET_KEY is guaranteed to be set by Pydantic Settings
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a refresh token for a user"""
    to_encode = {
        "sub": str(user["id"]),
        "id": user["id"],
        "username": user.get("username"),
        "email": user.get("email"),
        "token_type": "refresh"
    }
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode an access token and return its payload"""
    try:
        # SECRET_KEY is guaranteed to be set by Pydantic Settings
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Ensure 'id' is present in the payload
        if "id" not in payload:
            return None

        return {
            "id": payload.get("id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
        }
    except JWTError:
        return None
