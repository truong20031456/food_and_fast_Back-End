from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List
from datetime import date, datetime


class UserProfileBase(BaseModel):
    """Base schema for user profile."""

    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None


class UserProfileRead(UserProfileBase):
    """Schema for reading user profile."""

    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base schema for user."""

    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=200)
    profile: Optional[UserProfileBase] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=200)
    profile: Optional[UserProfileBase] = None


class UserRead(UserBase):
    """Schema for reading a user."""

    id: int
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    profile: Optional[UserProfileRead] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response schema for a list of users."""

    total: int
    users: List[UserRead]


class UserGoogleRequest(BaseModel):
    """Schema for Google OAuth user data."""

    email: EmailStr
    name: Optional[str] = None
    avatar: Optional[HttpUrl] = None
