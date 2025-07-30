from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: str = Field(..., min_length=1, max_length=100, description="Category slug")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    image_url: Optional[str] = Field(
        None, max_length=255, description="Category image URL"
    )
    sort_order: int = Field(0, description="Sort order")


class CategoryCreate(CategoryBase):
    """Create category schema"""

    pass


class CategoryUpdate(BaseModel):
    """Update category schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=255)
    sort_order: Optional[int] = None


class CategoryRead(CategoryBase):
    """Read category schema"""

    id: int
    created_at: datetime
    updated_at: datetime
    children: List["CategoryRead"] = []
    product_count: int = 0

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Category list response schema"""

    total: int
    categories: List[CategoryRead]


# Update forward reference
CategoryRead.model_rebuild()
