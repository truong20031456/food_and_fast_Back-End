"""
Payment Schemas - Pydantic models for data validation.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class PaymentIntentRequest(BaseModel):
    """Payment intent request schema."""
    amount: float = Field(..., description="Payment amount", gt=0)
    currency: str = Field(default="USD", description="Payment currency")
    payment_method: str = Field(..., description="Payment method (stripe, momo, vnpay)")
    order_id: Optional[str] = Field(default=None, description="Order ID")
    promotion_code: Optional[str] = Field(default=None, description="Promotion code")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class PaymentIntentResponse(BaseModel):
    """Payment intent response schema."""
    payment_intent_id: str = Field(..., description="Payment intent ID")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency")
    payment_method: str = Field(..., description="Payment method used")
    status: str = Field(..., description="Payment status")


class PaymentConfirmationRequest(BaseModel):
    """Payment confirmation request schema."""
    payment_intent_id: str = Field(..., description="Payment intent ID")
    payment_method: str = Field(..., description="Payment method used")
    confirmation_data: Optional[Dict[str, Any]] = Field(default=None, description="Confirmation data")


class PaymentStatusResponse(BaseModel):
    """Payment status response schema."""
    payment_intent_id: str = Field(..., description="Payment intent ID")
    status: str = Field(..., description="Payment status")
    amount: Optional[float] = Field(default=None, description="Payment amount")
    currency: Optional[str] = Field(default=None, description="Payment currency")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp")


class PaymentMethodInfo(BaseModel):
    """Payment method information schema."""
    id: str = Field(..., description="Payment method ID")
    name: str = Field(..., description="Payment method name")
    description: str = Field(..., description="Payment method description")
    supported_currencies: List[str] = Field(..., description="Supported currencies")


class PaymentMethodResponse(BaseModel):
    """Payment methods response schema."""
    payment_methods: List[PaymentMethodInfo] = Field(..., description="Available payment methods")


class RefundRequest(BaseModel):
    """Refund request schema."""
    amount: Optional[float] = Field(default=None, description="Refund amount (full refund if not specified)")
    reason: Optional[str] = Field(default=None, description="Refund reason")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class RefundResponse(BaseModel):
    """Refund response schema."""
    refund_id: str = Field(..., description="Refund ID")
    payment_intent_id: str = Field(..., description="Payment intent ID")
    amount: float = Field(..., description="Refund amount")
    status: str = Field(..., description="Refund status")
    created_at: str = Field(..., description="Refund creation timestamp")


class PromotionRequest(BaseModel):
    """Promotion request schema."""
    promotion_code: str = Field(..., description="Promotion code")
    amount: float = Field(..., description="Original amount")


class PromotionResponse(BaseModel):
    """Promotion response schema."""
    promotion_code: str = Field(..., description="Promotion code")
    original_amount: float = Field(..., description="Original amount")
    discount_amount: float = Field(..., description="Discount amount")
    final_amount: float = Field(..., description="Final amount after discount")
    discount_percentage: Optional[float] = Field(default=None, description="Discount percentage")


class PaymentWebhookRequest(BaseModel):
    """Payment webhook request schema."""
    event_type: str = Field(..., description="Webhook event type")
    payment_intent_id: str = Field(..., description="Payment intent ID")
    data: Dict[str, Any] = Field(..., description="Webhook data")
    signature: Optional[str] = Field(default=None, description="Webhook signature for verification")