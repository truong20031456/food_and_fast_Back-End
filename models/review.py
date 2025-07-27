from sqlalchemy import Column, Integer, ForeignKey, String, Text, Float, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class Review(BaseModel):
    """Review model for product reviews"""
    
    __tablename__ = "reviews"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to user service
    rating = Column(Float, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    is_verified_purchase = Column(Boolean, default=False, nullable=False)
    is_helpful = Column(Integer, default=0, nullable=False)  # Number of helpful votes
    is_approved = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>" 