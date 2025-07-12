from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TokenPayload(BaseModel):
    """JWT token payload schema"""

    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    username: Optional[str] = Field(None, description="Username") # Made optional
    roles: List[str] = Field(default=[], description="User roles")
    permissions: List[str] = Field(default=[], description="User permissions")
    is_superuser: bool = Field(False, description="Is superuser")
    exp: int = Field(..., description="Expiration time")
    iat: int = Field(..., description="Issued at")
    jti: Optional[str] = Field(None, description="JWT ID") # Made optional
    token_type: str = Field("access", description="Token type")


class RefreshTokenData(BaseModel):
    """Refresh token data schema"""

    token: str = Field(..., description="Refresh token")
    user_id: int = Field(..., description="User ID")
    expires_at: datetime = Field(..., description="Expiration time")
    device_id: Optional[str] = Field(None, description="Device ID")
    user_agent: Optional[str] = Field(None, description="User agent")
    ip_address: Optional[str] = Field(None, description="IP address")
    is_active: bool = Field(True, description="Is active") # Changed from is_revoked

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""

    access_token: str = Field(..., description="Access token (JWT)")
    refresh_token: Optional[str] = Field(None, description="Refresh token (JWT)")
    token_type: str = Field("bearer", description="Token type")