from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
)  # Import Text and JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum
from .base import BaseModel
from datetime import datetime, timezone  # Import timezone


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending verification"


class User(BaseModel):
    """User model for the application."""

    __tablename__ = "users"

    user_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False
    )
    username = Column(
        String(50), unique=True, nullable=True
    )  # Made nullable=True as email can be primary identifier
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Renamed from hashed_password

    # profile infor
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(String(500), nullable=True)
    preferences = Column(JSON, nullable=True)  # Added for user preferences

    # status
    status = Column(
        String(20), default=UserStatus.PENDING_VERIFICATION.value, nullable=False
    )  # Use .value for enum
    is_email_verified = Column(
        Boolean, default=False, nullable=False
    )  # Renamed from is_verified
    is_phone_verified = Column(
        Boolean, default=False, nullable=False
    )  # Added for phone verification
    # Removed is_active and is_suspended, relying on status enum

    # Login tracking
    last_login_at = Column(
        DateTime(timezone=True), nullable=True
    )  # Renamed from last_login
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan"
    )
    # Removed email_verification_token and email_verification_expires

    @property
    def full_name(self):
        """Get the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username if self.username else self.email

    @property
    def is_locked(self):
        if self.locked_until:
            return (
                datetime.now(timezone.utc) < self.locked_until
            )  # Use timezone-aware datetime
        return False

    @property
    def is_active(self):
        """Determine if the user is active based on their status."""
        return self.status == UserStatus.ACTIVE.value

    @property
    def is_superuser(self):
        """Determine if the user has superuser role."""
        # Assuming 'admin' or 'superuser' is a role name indicating superuser
        return any(
            role.name == "admin" or role.name == "superuser" for role in self.roles
        )

    def to_dict(self):
        """Converts the User object to a dictionary for serialization."""
        return {
            "id": self.id,
            "user_uuid": str(self.user_uuid),
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "preferences": self.preferences,
            "status": self.status,
            "is_email_verified": self.is_email_verified,
            "is_phone_verified": self.is_phone_verified,
            "is_active": self.is_active,
            "is_locked": self.is_locked,
            "last_login_at": self.last_login_at.isoformat()
            if self.last_login_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "roles": [role.name for role in self.roles],  # Include role names
            "permissions": [
                perm.name for role in self.roles for perm in role.permissions
            ],  # Include permissions
        }

    def __repr__(self):
        return f"<User(user_uuid={self.user_uuid}, username={self.username}, email={self.email})>"
