from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime


class RegisterRequest(BaseModel):
    """User registration request schema"""

    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Password confirmation")
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number")
    terms_accepted: bool = Field(..., description="Terms and conditions acceptance")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    """User login request schema"""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password")


class GoogleAuthRequest(BaseModel):
    """Google OAuth request schema"""

    id_token: str = Field(..., description="Google ID token")
    access_token: Optional[str] = Field(None, description="Google access token")


class GoogleUserInfo(BaseModel):
    """Google user information schema"""

    sub: str = Field(..., description="Google user ID")
    email: EmailStr = Field(..., description="User email")
    email_verified: bool = Field(..., description="Email verification status")
    name: Optional[str] = Field(None, description="Full name")
    given_name: Optional[str] = Field(None, description="First name")
    family_name: Optional[str] = Field(None, description="Last name")
    picture: Optional[str] = Field(None, description="Profile picture URL")
    locale: Optional[str] = Field(None, description="User locale")


class LoginResponse(BaseModel):
    """User login response schema"""

    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    user: Dict[str, Any] = Field(..., description="User information")


class MessageResponse(BaseModel):
    """Generic message response schema"""

    message: str = Field(..., description="Response message")


class CommonResponse(BaseModel):
    """Common response schema"""

    success: bool = Field(..., description="Success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
