from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from typing import Optional, List
from datetime import datetime, timezone

from models.review import Review
from models.product import Product
from schemas.review import ReviewCreate, ReviewUpdate, ReviewRead, ReviewListResponse, ReviewStats
from utils.logger import get_logger

logger = get_logger(__name__)


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(self, review_data: ReviewCreate) -> Review:
        """Create a new review"""
        try:
            # Check if user already reviewed this product
            existing_review = await self.get_user_product_review(
                review_data.user_id, review_data.product_id
            )
            if existing_review:
                raise ValueError(f"User {review_data.user_id} already reviewed product {review_data.product_id}")

            # Verify product exists
            product = await self.get_product(review_data.product_id)
            if not product:
                raise ValueError(f"Product {review_data.product_id} not found")

            review = Review(**review_data.dict())
            self.db.add(review)
            await self.db.commit()
            await self.db.refresh(review)
            
            logger.info(f"Review created for product {review_data.product_id} by user {review_data.user_id}")
            return review

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create review: {e}")
            raise

    async def get_review(self, review_id: int) -> Optional[Review]:
        """Get review by ID"""
        try:
            result = await self.db.execute(
                select(Review).where(Review.id == review_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get review: {e}")
            return None

    async def get_user_product_review(self, user_id: int, product_id: int) -> Optional[Review]:
        """Get review by user and product"""
        try:
            result = await self.db.execute(
                select(Review).where(
                    and_(Review.user_id == user_id, Review.product_id == product_id)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user product review: {e}")
            return None

    async def update_review(self, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
        """Update review"""
        try:
            review = await self.get_review(review_id)
            if not review:
                return None

            # Update fields
            update_data = review_data.dict(exclude_unset=True)
            if update_data:
                await self.db.execute(
                    update(Review)
                    .where(Review.id == review_id)
                    .values(**update_data, updated_at=datetime.now(timezone.utc))
                )
                await self.db.commit()
                await self.db.refresh(review)

            return review

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update review: {e}")
            return None

    async def delete_review(self, review_id: int) -> bool:
        """Delete review"""
        try:
            result = await self.db.execute(
                update(Review)
                .where(Review.id == review_id)
                .values(is_deleted=True, updated_at=datetime.now(timezone.utc))
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete review: {e}")
            return False

    async def list_product_reviews(
        self,
        product_id: int,
        limit: int = 20,
        offset: int = 0,
        rating: Optional[float] = None,
        is_verified: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> ReviewListResponse:
        """List reviews for a product"""
        try:
            # Build query
            query = select(Review).where(
                and_(Review.product_id == product_id, Review.is_deleted == False)
            )
            
            # Add filters
            if rating is not None:
                query = query.where(Review.rating == rating)
            
            if is_verified is not None:
                query = query.where(Review.is_verified_purchase == is_verified)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Add sorting and pagination
            if hasattr(Review, sort_by):
                sort_column = getattr(Review, sort_by)
                if sort_order == "desc":
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)
            
            query = query.offset(offset).limit(limit)

            # Execute query
            result = await self.db.execute(query)
            reviews = result.scalars().all()

            # Calculate average rating
            avg_rating = await self.get_product_average_rating(product_id)

            return ReviewListResponse(
                total=total,
                average_rating=avg_rating,
                reviews=reviews
            )

        except Exception as e:
            logger.error(f"Failed to list product reviews: {e}")
            return ReviewListResponse(total=0, average_rating=0.0, reviews=[])

    async def get_product_review_stats(self, product_id: int) -> ReviewStats:
        """Get review statistics for a product"""
        try:
            # Get total reviews
            total_query = select(func.count()).where(
                and_(Review.product_id == product_id, Review.is_deleted == False)
            )
            total_result = await self.db.execute(total_query)
            total_reviews = total_result.scalar()

            # Get average rating
            avg_rating = await self.get_product_average_rating(product_id)

            # Get rating distribution
            rating_distribution = {}
            for rating in range(1, 6):
                count_query = select(func.count()).where(
                    and_(
                        Review.product_id == product_id,
                        Review.rating == rating,
                        Review.is_deleted == False
                    )
                )
                count_result = await self.db.execute(count_query)
                rating_distribution[str(rating)] = count_result.scalar()

            # Get verified purchases count
            verified_query = select(func.count()).where(
                and_(
                    Review.product_id == product_id,
                    Review.is_verified_purchase == True,
                    Review.is_deleted == False
                )
            )
            verified_result = await self.db.execute(verified_query)
            verified_purchases = verified_result.scalar()

            return ReviewStats(
                total_reviews=total_reviews,
                average_rating=avg_rating,
                rating_distribution=rating_distribution,
                verified_purchases=verified_purchases
            )

        except Exception as e:
            logger.error(f"Failed to get product review stats: {e}")
            return ReviewStats(
                total_reviews=0,
                average_rating=0.0,
                rating_distribution={},
                verified_purchases=0
            )

    async def get_product_average_rating(self, product_id: int) -> float:
        """Get average rating for a product"""
        try:
            result = await self.db.execute(
                select(func.avg(Review.rating)).where(
                    and_(Review.product_id == product_id, Review.is_deleted == False)
                )
            )
            avg_rating = result.scalar()
            return float(avg_rating) if avg_rating else 0.0
        except Exception as e:
            logger.error(f"Failed to get product average rating: {e}")
            return 0.0

    async def mark_review_helpful(self, review_id: int) -> bool:
        """Mark review as helpful"""
        try:
            result = await self.db.execute(
                update(Review)
                .where(Review.id == review_id)
                .values(
                    is_helpful=Review.is_helpful + 1,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to mark review helpful: {e}")
            return False

    async def approve_review(self, review_id: int) -> bool:
        """Approve a review"""
        try:
            result = await self.db.execute(
                update(Review)
                .where(Review.id == review_id)
                .values(
                    is_approved=True,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to approve review: {e}")
            return False

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        try:
            result = await self.db.execute(
                select(Product).where(Product.id == product_id, Product.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get product: {e}")
            return None
