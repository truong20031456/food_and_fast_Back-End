from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session  # Use Session for SQLAlchemy ORM
from typing import Annotated

from core.database import get_db  # Import get_db from core.database
from schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
)  # Use RegisterRequest, LoginRequest
from schemas.user import UserRead  # For response model
from schemas.auth import MessageResponse

from services.auth_service import AuthService
from services.user_service import UserService
from services.token_service import TokenService
from services.audit_service import AuditService
from services.cache_service import CacheService
from core.dependencies import (
    get_user_service,
    get_token_service,
    get_audit_service,
    get_cache_service,
)

from core.dependencies import (
    get_current_user,
)  # Use get_current_user from core.dependencies

router = APIRouter()


# Dependency to get AuthService instance
async def get_auth_service(
    db: Session = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
    audit_service: AuditService = Depends(get_audit_service),
    cache_service: CacheService = Depends(get_cache_service),
) -> AuthService:
    return AuthService(db, user_service, token_service, audit_service, cache_service)


@router.post(
    "/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED
)  # Changed response_model to LoginResponse
async def register(
    user_data: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    request: Request,  # To get client IP
):
    """Register a new user"""
    client_ip = request.client.host  # Get client IP
    return await auth_service.register(user_data, client_ip)


@router.post(
    "/login", response_model=LoginResponse
)  # Changed response_model to LoginResponse
async def login(
    user_login: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    request: Request,  # To get client IP
):
    """Login user and return access/refresh tokens"""
    client_ip = request.client.host  # Get client IP
    return await auth_service.login(user_login, client_ip)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: Annotated[
        UserRead, Depends(get_current_user)
    ],  # Use get_current_user from core.dependencies
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    request: Request,  # To get client IP
):
    """Logout user and invalidate tokens"""
    client_ip = request.client.host  # Get client IP
    # Assuming refresh token is passed in a cookie or header. For now, let's assume it's in a header for simplicity.
    # You might need to adjust this based on how your frontend sends the refresh token.
    refresh_token = request.headers.get(
        "X-Refresh-Token"
    )  # Example: get from custom header

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token not provided"
        )

    await auth_service.logout(refresh_token, current_user.id, client_ip)

    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: Annotated[
        UserRead, Depends(get_current_user)
    ],  # Use get_current_user from core.dependencies
):
    """Get current user information"""
    return current_user
