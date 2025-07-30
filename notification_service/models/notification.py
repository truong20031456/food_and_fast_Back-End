"""
Notification Models - Data models for notification service.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class NotificationType(str, Enum):
    """Notification types."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Notification status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationTemplate(BaseModel):
    """Model for notification templates."""
    template_id: str
    name: str
    type: NotificationType
    subject: Optional[str] = None
    content: str
    variables: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class NotificationRequest(BaseModel):
    """Model for notification request."""
    notification_id: str
    user_id: str
    type: NotificationType
    template_id: Optional[str] = None
    subject: Optional[str] = None
    content: str
    recipient: str  # email or phone number
    variables: Dict[str, Any] = Field(default_factory=dict)
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationDelivery(BaseModel):
    """Model for notification delivery tracking."""
    delivery_id: str
    notification_id: str
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class NotificationHistory(BaseModel):
    """Model for notification history."""
    history_id: str
    notification_id: str
    user_id: str
    type: NotificationType
    status: NotificationStatus
    recipient: str
    subject: Optional[str] = None
    content: str
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """Model for chat messages."""
    message_id: str
    conversation_id: str
    user_id: str
    content: str
    message_type: str = "text"  # text, image, file
    timestamp: datetime
    is_read: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    """Model for chat conversations."""
    conversation_id: str
    user_id: str
    agent_id: Optional[str] = None
    status: str = "active"  # active, closed, archived
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationConfig(BaseModel):
    """Model for notification configuration."""
    service_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    max_retries: int = 3
    retry_delay: int = 300  # seconds
    rate_limit: int = 100  # notifications per minute
    template_cache_ttl: int = 3600  # seconds