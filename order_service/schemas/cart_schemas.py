from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    product_name: str
    product_description: Optional[str] = None
    price: float
    quantity: int = 1
    special_instructions: Optional[str] = None
    
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    special_instructions: Optional[str] = None
    
    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class CartItemResponse(CartItemBase):
    id: int
    cart_id: int
    subtotal: float
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CartBase(BaseModel):
    user_id: int
    session_id: Optional[str] = None

class CartCreate(CartBase):
    pass

class CartResponse(BaseModel):
    id: int
    user_id: int
    session_id: Optional[str]
    status: str
    total_amount: float
    total_items: int
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CartSummary(BaseModel):
    id: int
    user_id: int
    total_amount: float
    total_items: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)