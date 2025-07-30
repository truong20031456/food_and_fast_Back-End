from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from pydantic import BaseModel as PydanticBaseModel, ConfigDict
from uuid import uuid4


Base = declarative_base()


class TimestampMixin:
    """Mixin that adds timestamp fields to models"""

    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


class UUIDMixin:
    """Mixin that adds UUID primary key"""

    @declared_attr
    def id(cls):
        return Column(String(36), primary_key=True, default=lambda: str(uuid4()))


class BaseDBModel(Base, TimestampMixin, UUIDMixin):
    """Base model class with common fields"""

    __abstract__ = True


class BaseSchema(PydanticBaseModel):
    """Base Pydantic schema with common configuration"""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""

    created_at: datetime
    updated_at: datetime


class BaseResponseSchema(TimestampSchema):
    """Base response schema with ID and timestamps"""

    id: str


class PaginationParams(BaseSchema):
    """Standard pagination parameters"""

    page: int = 1
    size: int = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseSchema):
    """Standard paginated response"""

    items: list
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: list, total: int, page: int, size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )


class HealthResponse(BaseSchema):
    """Standard health check response"""

    status: str = "healthy"
    timestamp: datetime
    service: str
    version: Optional[str] = None
    dependencies: Optional[dict] = None
