from typing import Optional, List
from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    """Base filter parameters"""

    limit: int = Field(
        default=20, ge=1, le=100, description="Number of items to return"
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


class MessageResponse(BaseModel):
    """Message response schema"""

    message: str = Field(..., description="Response message")


class SearchQuery(BaseModel):
    """Search query schema"""

    q: str = Field(..., description="Search query")
    category_id: Optional[int] = Field(None, description="Filter by category")
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")
    in_stock: Optional[bool] = Field(None, description="Filter by stock availability")
    featured: Optional[bool] = Field(None, description="Filter featured products")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    attributes: Optional[dict] = Field(None, description="Filter by attributes")
