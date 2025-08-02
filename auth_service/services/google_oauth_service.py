import httpx
import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from sqlalchemy.orm import Session

from schemas.auth import GoogleAuthRequest, GoogleUserInfo
from services.user_service import UserService
from services.token_service import TokenService
from services.audit_service import AuditService
from services.cache_service import CacheService
from utils.security import create_access_token, create_refresh_token
from utils.logger import get_logger
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.core.config import get_service_settings

settings = get_service_settings("auth_service")

logger = get_logger(__name__)


class GoogleOAuthService:
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

    async def verify_google_token(self, id_token_str: str) -> GoogleUserInfo:
        """Verify Google ID token and return user information"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), settings.GOOGLE_CLIENT_ID
            )

            # Check if the token is expired
            if idinfo["exp"] < jwt.utils.timegm(
                jwt.utils.datetime_to_timestamp(jwt.utils.datetime.utcnow())
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
                )

            # Check if the token was issued for our app
            if idinfo["aud"] != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong audience"
                )

            # Check if the token was issued by Google
            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong issuer"
                )

            # Return user info
            return GoogleUserInfo(
                sub=idinfo["sub"],
                email=idinfo["email"],
                email_verified=idinfo.get("email_verified", False),
                name=idinfo.get("name"),
                given_name=idinfo.get("given_name"),
                family_name=idinfo.get("family_name"),
                picture=idinfo.get("picture"),
                locale=idinfo.get("locale"),
            )

        except GoogleAuthError as e:
            logger.error(f"Google token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token"
            )
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed",
            )

    async def get_google_user_info(self, access_token: str) -> GoogleUserInfo:
        """Get user information from Google using access token"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                response = await client.get(
                    settings.GOOGLE_USERINFO_URL, headers=headers
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to get user info from Google",
                    )

                user_data = response.json()
                return GoogleUserInfo(
                    sub=user_data["id"],
                    email=user_data["email"],
                    email_verified=user_data.get("verified_email", False),
                    name=user_data.get("name"),
                    given_name=user_data.get("given_name"),
                    family_name=user_data.get("family_name"),
                    picture=user_data.get("picture"),
                    locale=user_data.get("locale"),
                )

        except Exception as e:
            logger.error(f"Failed to get Google user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user information",
            )

    async def authenticate_google_user(
        self, google_request: GoogleAuthRequest, client_ip: str
    ) -> Dict[str, Any]:
        """Authenticate or register user with Google OAuth"""
        try:
            # Verify Google token
            if google_request.id_token:
                google_user_info = await self.verify_google_token(
                    google_request.id_token
                )
            elif google_request.access_token:
                google_user_info = await self.get_google_user_info(
                    google_request.access_token
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either id_token or access_token must be provided",
                )

            # Check if user exists
            existing_user = await self.user_service.get_by_email(google_user_info.email)

            if existing_user:
                # User exists, check if they have Google OAuth linked
                if not existing_user.google_id:
                    # Link Google account to existing user
                    await self.user_service.link_google_account(
                        existing_user.id, google_user_info.sub
                    )

                # Update last login
                await self.user_service.update_last_login(existing_user.id)
                user = existing_user
                action = "LOGIN_SUCCESS"
            else:
                # Create new user with Google OAuth
                user = await self.user_service.create_google_user(google_user_info)
                action = "USER_REGISTERED"

            # Generate tokens
            access_token = create_access_token(user=user.to_dict())
            refresh_token = create_refresh_token(user=user.to_dict())

            # Save refresh token
            await self.token_service.create_refresh_token(user.id, refresh_token)

            # Log the action
            await self.audit_service.log_user_action(
                user_id=user.id,
                action=action,
                ip_address=client_ip,
                details={"provider": "google", "google_id": google_user_info.sub},
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
                    "google_id": user.google_id,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Google authentication failed: {e}", exc_info=True)
            await self.audit_service.log_user_action(
                user_id=None,
                action="GOOGLE_AUTH_FAILED",
                ip_address=client_ip,
                details={"error": str(e)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google authentication failed",
            )

    async def get_google_auth_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }

        if state:
            params["state"] = state

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{settings.GOOGLE_AUTH_URL}?{query_string}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                }

                response = await client.post(settings.GOOGLE_TOKEN_URL, data=data)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange code for tokens",
                    )

                return response.json()

        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to exchange authorization code",
            )
