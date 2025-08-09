"""
Reviews Router - Handles product reviews and ratings.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewRead,
    ReviewListResponse,
)
from schemas.common import MessageResponse
from services.review_service import ReviewService

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


async def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    """Get ReviewService instance"""
    return ReviewService(db)


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
):
    """Create a new product review"""
    try:
        review = await review_service.create_review(review_data)
        return review
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create review")


@router.get("/product/{product_id}", response_model=ReviewListResponse)
async def get_product_reviews(
    product_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Page size"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    review_service: ReviewService = Depends(get_review_service),
):
    """Get reviews for a specific product"""
    try:
        reviews = await review_service.get_product_reviews(
            product_id=product_id, page=page, size=size, rating=rating
        )
        return reviews
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve reviews")


@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """Get a specific review by ID"""
    try:
        review = await review_service.get_review_by_id(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve review")


@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service),
):
    """Update a review"""
    try:
        review = await review_service.update_review(review_id, review_data)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        return review
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update review")


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """Delete a review"""
    try:
        success = await review_service.delete_review(review_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
        return MessageResponse(message="Review deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete review")


@router.get("/product/{product_id}/stats")
async def get_product_review_stats(
    product_id: int,
    review_service: ReviewService = Depends(get_review_service),
):
    """Get review statistics for a product"""
    try:
        stats = await review_service.get_product_review_stats(product_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve review stats")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "product_service", "component": "reviews"}
