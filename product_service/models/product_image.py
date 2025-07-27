from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

class ProductImage(BaseModel):
    """Product image model"""
    
    __tablename__ = "product_images"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="images")
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, is_primary={self.is_primary})>" 