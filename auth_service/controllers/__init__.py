from .auth_controller import router as auth_router

# Placeholder routers - these need to be implemented
from fastapi import APIRouter

# Temporary placeholder routers
user_router = APIRouter(prefix="/users", tags=["User Management"])
token_router = APIRouter(prefix="/tokens", tags=["Token Management"])
password_router = APIRouter(prefix="/passwords", tags=["Password Management"])
profile_router = APIRouter(prefix="/profile", tags=["Profile Management"])

__all__ = [
    "auth_router",
    "user_router", 
    "token_router",
    "password_router",
    "profile_router"
] 