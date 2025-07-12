from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum
from schemas.common import FilterParams


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username") # Made optional
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="Phone number") # Renamed from phone
    bio: Optional[str] = Field(None, max_length=500, description="User bio")

    @validator("username")
    def validate_username(cls, v):
        if v is None: # Allow None for optional username
            return v
        # Allow alphanumeric characters, underscores, and hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Username must contain only alphanumeric characters, underscores, or hyphens"
            )
        return v


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(..., min_length=8, description="Password")
    confirm_password: str = Field(..., description="Password confirmation")

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

    # Removed redundant password strength validation, relying on utils.validators.validate_password


class UserUpdate(BaseModel):
    """User update schema"""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20) # Renamed from phone
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    status: Optional[UserStatus] = Field(None, description="User status") # Added status update
    is_email_verified: Optional[bool] = Field(None, description="Is email verified") # Added
    is_phone_verified: Optional[bool] = Field(None, description="Is phone verified") # Added


class UserResponse(UserBase):
    """User response schema"""

    id: int
    user_uuid: str # Renamed from uuid
    status: UserStatus
    is_email_verified: bool # Renamed from is_verified
    is_phone_verified: bool # Added
    is_active: bool # Derived from status in model
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None # Renamed from last_login
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile schema"""

    full_name: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    preferences: Optional[dict] = None # Added for user preferences


class UserProfileUpdate(BaseModel):
    """User profile update schema"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20) # Renamed from phone
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferences: Optional[dict] = None # Added for user preferences


class UserList(BaseModel):
    """User list item schema"""

    id: int
    user_uuid: str # Renamed from uuid
    email: EmailStr
    username: Optional[str] = None # Made optional
    full_name: Optional[str] = None
    status: UserStatus
    is_email_verified: bool # Renamed from is_verified
    is_phone_verified: bool # Added
    is_active: bool # Derived from status in model
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None # Renamed from last_login
    created_at: datetime

    class Config:
        from_attributes = True


class UserFilter(FilterParams):
    """User filter parameters"""

    status: Optional[UserStatus] = None
    is_email_verified: Optional[bool] = None # Renamed from is_verified
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailStr = Field(..., description="User email") # Changed from username
    password: str = Field(..., min_length=8, description="Password")


UserRead = UserResponse