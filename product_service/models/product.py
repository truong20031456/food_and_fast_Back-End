from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Product(BaseModel):
    """Product model for e-commerce products"""

    __tablename__ = "products"

    # Basic info
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)

    # Pricing
    price = Column(Float, nullable=False, index=True)
    compare_price = Column(Float, nullable=True)  # Original price for discounts
    cost_price = Column(Float, nullable=True)  # Cost to business

    # Category
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, index=True
    )

    # Product details
    sku = Column(String(100), unique=True, nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    weight = Column(Float, nullable=True)  # in grams
    dimensions = Column(JSON, nullable=True)  # {"length": 10, "width": 5, "height": 2}

    # Status
    is_featured = Column(Boolean, default=False, nullable=False)
    is_published = Column(Boolean, default=True, nullable=False)
    is_virtual = Column(Boolean, default=False, nullable=False)  # Digital products

    # SEO
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String(500), nullable=True)

    # Additional info
    tags = Column(JSON, nullable=True)  # ["organic", "gluten-free"]
    attributes = Column(JSON, nullable=True)  # {"brand": "Nike", "color": "Red"}

    # Relationships
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    reviews = relationship("Review", back_populates="product")
    images = relationship("ProductImage", back_populates="product")

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if self.inventory:
            return self.inventory.quantity > 0
        return False

    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.compare_price and self.price < self.compare_price:
            return round(
                ((self.compare_price - self.price) / self.compare_price) * 100, 2
            )
        return 0

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
