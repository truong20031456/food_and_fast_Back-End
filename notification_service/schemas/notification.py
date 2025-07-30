"""
Notification Schemas - Pydantic models for data validation.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, EmailStr


class EmailNotificationRequest(BaseModel):
    """Email notification request schema."""
    recipient: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject", min_length=1, max_length=200)
    template: str = Field(..., description="Email template name")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Template data")


class SMSNotificationRequest(BaseModel):
    """SMS notification request schema."""
    phone_number: str = Field(..., description="Recipient phone number", min_length=10, max_length=15)
    message: str = Field(..., description="SMS message content", min_length=1, max_length=160)
    template: Optional[str] = Field(default=None, description="SMS template name")


class OrderConfirmationRequest(BaseModel):
    """Order confirmation notification request schema."""
    user_id: int = Field(..., description="User ID", gt=0)
    order_id: int = Field(..., description="Order ID", gt=0)
    order_data: Dict[str, Any] = Field(..., description="Order data for template")


class PasswordResetRequest(BaseModel):
    """Password reset notification request schema."""
    user_id: int = Field(..., description="User ID", gt=0)
    reset_token: str = Field(..., description="Password reset token", min_length=1)
    email: EmailStr = Field(..., description="User email address")


class WelcomeNotificationRequest(BaseModel):
    """Welcome notification request schema."""
    user_id: int = Field(..., description="User ID", gt=0)
    email: EmailStr = Field(..., description="User email address")
    username: Optional[str] = Field(default=None, description="Username")


class NotificationResponse(BaseModel):
    """Notification response schema."""
    message: str = Field(..., description="Response message")
    recipient: str = Field(..., description="Notification recipient")
    template: Optional[str] = Field(default=None, description="Template used")


class NotificationStatusResponse(BaseModel):
    """Notification status response schema."""
    notification_id: str = Field(..., description="Notification ID")
    status: str = Field(..., description="Delivery status")
    delivered_at: Optional[str] = Field(default=None, description="Delivery timestamp")
    channel: str = Field(..., description="Notification channel")


class NotificationTemplatesResponse(BaseModel):
    """Notification templates response schema."""
    email_templates: List[str] = Field(..., description="Available email templates")
    sms_templates: List[str] = Field(..., description="Available SMS templates")


class ChatMessageRequest(BaseModel):
    """Chat message request schema."""
    user_id: int = Field(..., description="User ID", gt=0)
    message: str = Field(..., description="Chat message", min_length=1, max_length=1000)
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")


class ChatMessageResponse(BaseModel):
    """Chat message response schema."""
    message_id: str = Field(..., description="Message ID")
    user_id: int = Field(..., description="User ID")
    message: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp")
    conversation_id: str = Field(..., description="Conversation ID")


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    conversation_id: str = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    status: str = Field(..., description="Conversation status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    messages: List[ChatMessageResponse] = Field(..., description="Conversation messages")