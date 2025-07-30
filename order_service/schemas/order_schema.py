from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    product_description: Optional[str] = None
    price: float
    quantity: int
    special_instructions: Optional[str] = None
    subtotal: float

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    delivery_address: str
    delivery_phone: str
    delivery_notes: Optional[str] = None
    discount_amount: Optional[float] = 0.0
    
    @field_validator('delivery_phone')
    @classmethod
    def validate_phone(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Valid phone number is required')
        return v
    
    @field_validator('delivery_address')
    @classmethod
    def validate_address(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Valid delivery address is required')
        return v

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    delivery_notes: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    total_amount: float
    tax_amount: float
    delivery_fee: float
    discount_amount: float
    final_amount: float
    status: str
    payment_status: str
    delivery_address: str
    delivery_phone: str
    delivery_notes: Optional[str]
    estimated_delivery_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    delivered_at: Optional[datetime]
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class OrderSummary(BaseModel):
    id: int
    order_number: str
    final_amount: float
    status: str
    payment_status: str
    created_at: datetime
    estimated_delivery_time: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    status: str
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid_statuses = ['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class PaymentStatusUpdate(BaseModel):
    payment_status: str
    
    @field_validator('payment_status')
    @classmethod
    def validate_payment_status(cls, v):
        valid_statuses = ['pending', 'paid', 'failed', 'refunded']
        if v not in valid_statuses:
            raise ValueError(f'Payment status must be one of: {", ".join(valid_statuses)}')
        return v