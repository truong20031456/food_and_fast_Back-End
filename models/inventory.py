from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from .base import BaseModel

class Inventory(BaseModel):
    """Inventory model for product stock management"""
    
    __tablename__ = "inventory"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    
    @property
    def available_quantity(self):
        """Get available quantity (total - reserved)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    @property
    def is_low_stock(self):
        """Check if stock is low"""
        return self.available_quantity <= self.low_stock_threshold
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.available_quantity <= 0
    
    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, quantity={self.quantity}, available={self.available_quantity})>" 