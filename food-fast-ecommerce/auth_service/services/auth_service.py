from datetime import timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from schemas.auth import LoginRequest, RegisterRequest, LoginResponse
from core.security import create_access_token, create_refresh_token
from core.config import settings
from services.user_service import UserService
from services.token_service import TokenService
from services.audit_service import AuditService
from services.cache_service import CacheService
from utils.logger import get_logger # Import logger

logger = get_logger(__name__) # Initialize logger


class AuthService:
    def __init__(
        self,
        db: Session,
        user_service: UserService,
        token_service: TokenService,
        audit_service: AuditService,
        cache_service: CacheService,
    ):
        self.db = db
        self.user_service = user_service
        self.token_service = token_service
        self.audit_service = audit_service
        self.cache_service = cache_service
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register(
        self, request: RegisterRequest, client_ip: str
    ) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.user_service.get_by_email(request.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            # Create new user
            user = await self.user_service.create_user(request)

            # Generate tokens
            # Ensure user object has 'id', 'username', 'email' attributes for create_access_token
            access_token = create_access_token(user=user.to_dict())
            refresh_token = create_refresh_token(user=user.to_dict()) # Assuming create_refresh_token also takes user dict

            # Save refresh token
            await self.token_service.create_refresh_token(user.id, refresh_token)

            # Log registration
            await self.audit_service.log_user_action(
                user_id=user.id, action="USER_REGISTERED", ip_address=client_ip
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration failed for email {request.email}. Error: {e}", exc_info=True)
            await self.audit_service.log_user_action(
                user_id=None,
                action="REGISTRATION_FAILED",
                ip_address=client_ip,
                details={
                    "email": request.email,
                    "error": str(e)
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed",
            )

    async def login(self, request: LoginRequest, client_ip: str) -> LoginResponse:
        """Authenticate user and return tokens"""
        try:
            # Check for account lockout
            lockout_key = f"lockout:{request.email}"
            if await self.cache_service.get(lockout_key):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Account temporarily locked due to too many failed attempts",
                )

            # Get user
            user = await self.user_service.get_by_email(request.email)
            if not user:
                await self._handle_failed_login(request.email, client_ip)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            # Check password
            if not self.pwd_context.verify(request.password, user.password_hash):
                await self._handle_failed_login(request.email, client_ip)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled",
                )

            # Generate tokens
            access_token = create_access_token(user=user.to_dict())
            refresh_token = create_refresh_token(user=user.to_dict())

            # Save refresh token
            await self.token_service.create_refresh_token(user.id, refresh_token)

            # Update user last login
            await self.user_service.update_last_login(user.id)

            # Clear failed attempts
            await self.cache_service.delete(f"failed_attempts:{request.email}")

            # Log successful login
            await self.audit_service.log_user_action(
                user_id=user.id, action="LOGIN_SUCCESS", ip_address=client_ip
            )

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user={
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed for email {request.email}. Error: {e}", exc_info=True)
            await self.audit_service.log_user_action(
                user_id=None,
                action="LOGIN_ERROR",
                ip_address=client_ip,
                details={
                    "email": request.email,
                    "error": str(e)
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
            )

    async def logout(
        self, refresh_token: str, user_id: int, client_ip: str
    ) -> Dict[str, str]:
        """Logout user and invalidate tokens"""
        try:
            # Invalidate refresh token
            await self.token_service.invalidate_refresh_token(refresh_token)

            # Log logout
            await self.audit_service.log_user_action(
                user_id=user_id, action="LOGOUT", ip_address=client_ip
            )

            return {"message": "Successfully logged out"}

        except Exception as e:
            logger.error(f"Logout failed for user {user_id}. Error: {e}", exc_info=True)
            await self.audit_service.log_user_action(
                user_id=user_id,
                action="LOGOUT_ERROR",
                ip_address=client_ip,
                details={
                    "error": str(e)
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed",
            )

    async def _handle_failed_login(self, email: str, client_ip: str):
        """Handle failed login attempts"""
        attempts_key = f"failed_attempts:{email}"
        attempts = await self.cache_service.get(attempts_key) or 0
        attempts += 1

        # Store failed attempts with expiration
        await self.cache_service.set(
            attempts_key,
            attempts,
            expire=timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES),
        )

        # Lock account if too many attempts
        if attempts >= settings.MAX_LOGIN_ATTEMPTS:
            lockout_key = f"lockout:{email}"
            await self.cache_service.set(
                lockout_key,
                True,
                expire=timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES),
            )

        # Log failed attempt
        await self.audit_service.log_user_action(
            user_id=None,
            action="LOGIN_FAILED",
            ip_address=client_ip,
            details={
                "email": email,
                "attempts": attempts
            },
        )