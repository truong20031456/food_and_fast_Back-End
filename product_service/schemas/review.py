from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review schema"""

    product_id: int = Field(..., description="Product ID")
    user_id: int = Field(..., description="User ID")
    rating: float = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    comment: Optional[str] = Field(None, description="Review comment")
    is_verified_purchase: bool = Field(False, description="Is verified purchase")
    is_approved: bool = Field(True, description="Is approved")


class ReviewCreate(ReviewBase):
    """Create review schema"""

    pass


class ReviewUpdate(BaseModel):
    """Update review schema"""

    rating: Optional[float] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = None
    is_verified_purchase: Optional[bool] = None
    is_approved: Optional[bool] = None


class ReviewRead(ReviewBase):
    """Read review schema"""

    id: int
    is_helpful: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Review list response schema"""

    total: int
    average_rating: float
    reviews: list[ReviewRead]


class ReviewStats(BaseModel):
    """Review statistics schema"""

    total_reviews: int
    average_rating: float
    rating_distribution: dict[str, int]  # {"1": 10, "2": 20, "3": 30, "4": 40, "5": 50}
    verified_purchases: int
