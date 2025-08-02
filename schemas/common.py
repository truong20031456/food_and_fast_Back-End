from typing import Optional, List
from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    """Base filter parameters"""

    limit: int = Field(
        default=10, ge=1, le=100, description="Number of items to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    search: Optional[str] = Field(None, description="Search term")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: Optional[str] = Field(
        default="asc", pattern="^(asc|desc)$", description="Sort order"
    )


class PaginatedResponse(BaseModel):
    """Paginated response base class"""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class ErrorResponse(BaseModel):
    """Error response schema"""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")
