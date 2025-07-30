from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InventoryBase(BaseModel):
    """Base inventory schema"""

    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(0, ge=0, description="Available quantity")
    reserved_quantity: int = Field(0, ge=0, description="Reserved quantity")
    low_stock_threshold: int = Field(10, ge=0, description="Low stock threshold")
    location: Optional[str] = Field(
        None, max_length=100, description="Storage location"
    )
    notes: Optional[str] = Field(None, description="Inventory notes")


class InventoryCreate(InventoryBase):
    """Create inventory schema"""

    pass


class InventoryUpdate(BaseModel):
    """Update inventory schema"""

    quantity: Optional[int] = Field(None, ge=0)
    reserved_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class InventoryRead(InventoryBase):
    """Read inventory schema"""

    id: int
    available_quantity: int
    is_low_stock: bool
    is_out_of_stock: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryAdjustment(BaseModel):
    """Inventory adjustment schema"""

    quantity_change: int = Field(
        ...,
        description="Quantity change (positive for addition, negative for reduction)",
    )
    reason: str = Field(..., description="Reason for adjustment")
    notes: Optional[str] = Field(None, description="Additional notes")
