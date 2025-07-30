from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewRead,
    ReviewListResponse,
    ReviewStats,
)
from schemas.common import MessageResponse
from modules.reviews.review_service import ReviewService

router = APIRouter()


async def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    """Get ReviewService instance"""
    return ReviewService(db)


@router.post("/", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    review_service: ReviewService = Depends(get_review_service),
):
    """Create a new review"""
    try:
        review = await review_service.create_review(review_data)
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(
    review_id: int, review_service: ReviewService = Depends(get_review_service)
):
    """Get review by ID"""
    review = await review_service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    review_service: ReviewService = Depends(get_review_service),
):
    """Update review"""
    review = await review_service.update_review(review_id, review_data)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: int, review_service: ReviewService = Depends(get_review_service)
):
    """Delete review"""
    success = await review_service.delete_review(review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}


@router.get("/product/{product_id}", response_model=ReviewListResponse)
async def list_product_reviews(
    product_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    rating: Optional[float] = Query(None, ge=1, le=5),
    is_verified: Optional[bool] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    review_service: ReviewService = Depends(get_review_service),
):
    """List reviews for a product"""
    return await review_service.list_product_reviews(
        product_id=product_id,
        limit=limit,
        offset=offset,
        rating=rating,
        is_verified=is_verified,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/product/{product_id}/stats", response_model=ReviewStats)
async def get_product_review_stats(
    product_id: int, review_service: ReviewService = Depends(get_review_service)
):
    """Get review statistics for a product"""
    return await review_service.get_product_review_stats(product_id)


@router.post("/{review_id}/helpful", response_model=MessageResponse)
async def mark_review_helpful(
    review_id: int, review_service: ReviewService = Depends(get_review_service)
):
    """Mark review as helpful"""
    success = await review_service.mark_review_helpful(review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review marked as helpful"}


@router.post("/{review_id}/approve", response_model=MessageResponse)
async def approve_review(
    review_id: int, review_service: ReviewService = Depends(get_review_service)
):
    """Approve a review"""
    success = await review_service.approve_review(review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review approved successfully"}
