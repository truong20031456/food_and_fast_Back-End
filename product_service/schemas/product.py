from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ProductImageBase(BaseModel):
    """Base product image schema"""

    image_url: str = Field(..., description="Image URL")
    alt_text: Optional[str] = Field(None, description="Alt text for image")
    is_primary: bool = Field(False, description="Is primary image")
    sort_order: int = Field(0, description="Sort order")


class ProductImageCreate(ProductImageBase):
    """Create product image schema"""

    pass


class ProductImageUpdate(BaseModel):
    """Update product image schema"""

    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_primary: Optional[bool] = None
    sort_order: Optional[int] = None


class ProductImageRead(ProductImageBase):
    """Read product image schema"""

    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product schema"""

    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    slug: str = Field(..., min_length=1, max_length=200, description="Product slug")
    description: Optional[str] = Field(None, description="Product description")
    short_description: Optional[str] = Field(
        None, max_length=500, description="Short description"
    )
    price: float = Field(..., gt=0, description="Product price")
    compare_price: Optional[float] = Field(None, gt=0, description="Compare price")
    cost_price: Optional[float] = Field(None, gt=0, description="Cost price")
    category_id: int = Field(..., description="Category ID")
    sku: str = Field(..., min_length=1, max_length=100, description="SKU")
    barcode: Optional[str] = Field(None, max_length=100, description="Barcode")
    weight: Optional[float] = Field(None, gt=0, description="Weight in grams")
    dimensions: Optional[Dict[str, Any]] = Field(None, description="Dimensions")
    is_featured: bool = Field(False, description="Is featured product")
    is_published: bool = Field(True, description="Is published")
    is_virtual: bool = Field(False, description="Is virtual product")
    meta_title: Optional[str] = Field(None, max_length=200, description="Meta title")
    meta_description: Optional[str] = Field(None, description="Meta description")
    meta_keywords: Optional[str] = Field(
        None, max_length=500, description="Meta keywords"
    )
    tags: Optional[List[str]] = Field(None, description="Product tags")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Product attributes")


class ProductCreate(ProductBase):
    """Create product schema"""

    pass


class ProductUpdate(BaseModel):
    """Update product schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    compare_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None
    is_virtual: Optional[bool] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None


class ProductRead(ProductBase):
    """Read product schema"""

    id: int
    is_in_stock: bool
    discount_percentage: float
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageRead] = []

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Product list response schema"""

    total: int
    page: int
    size: int
    pages: int
    products: List[ProductRead]
