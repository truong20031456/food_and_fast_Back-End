from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=200)
    profile: Optional[UserProfileCreate] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=200)
    profile: Optional[UserProfileCreate] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    profile: Optional[UserProfileRead] = None

    class Config:
        orm_mode = True


class UserListResponse(BaseModel):
    total: int
    users: List[UserRead]
