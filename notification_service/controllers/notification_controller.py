"""
Notification Controller - Handles HTTP requests for notification endpoints.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from channels.email import EmailService
from channels.sms import SMSService
from support.chat_service import ChatService
from schemas.notification import (
    EmailNotificationRequest,
    SMSNotificationRequest,
    OrderConfirmationRequest,
    PasswordResetRequest,
    WelcomeNotificationRequest,
    NotificationResponse,
    NotificationStatusResponse,
    NotificationTemplatesResponse
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationController:
    """Controller for notification endpoints."""
    
    def __init__(self, email_service: EmailService, sms_service: SMSService, chat_service: ChatService):
        self.email_service = email_service
        self.sms_service = sms_service
        self.chat_service = chat_service
    
    @router.post("/email", response_model=NotificationResponse)
    async def send_email_notification(
        self,
        background_tasks: BackgroundTasks,
        request: EmailNotificationRequest
    ):
        """Send email notification."""
        try:
            # Add to background tasks for async processing
            background_tasks.add_task(
                self.email_service.send_email,
                recipient=request.recipient,
                subject=request.subject,
                template=request.template,
                data=request.data or {}
            )
            
            return NotificationResponse(
                message="Email notification queued successfully",
                recipient=request.recipient,
                template=request.template
            )
        except Exception as e:
            logger.error(f"Failed to queue email notification: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue email notification")
    
    @router.post("/sms", response_model=NotificationResponse)
    async def send_sms_notification(
        self,
        background_tasks: BackgroundTasks,
        request: SMSNotificationRequest
    ):
        """Send SMS notification."""
        try:
            # Add to background tasks for async processing
            background_tasks.add_task(
                self.sms_service.send_sms,
                phone_number=request.phone_number,
                message=request.message,
                template=request.template
            )
            
            return NotificationResponse(
                message="SMS notification queued successfully",
                recipient=request.phone_number,
                template=request.template
            )
        except Exception as e:
            logger.error(f"Failed to queue SMS notification: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue SMS notification")
    
    @router.post("/order-confirmation", response_model=NotificationResponse)
    async def send_order_confirmation(
        self,
        background_tasks: BackgroundTasks,
        request: OrderConfirmationRequest
    ):
        """Send order confirmation notification."""
        try:
            # Add to background tasks for async processing
            background_tasks.add_task(
                self.email_service.send_order_confirmation,
                user_id=request.user_id,
                order_id=request.order_id,
                order_data=request.order_data
            )
            
            return NotificationResponse(
                message="Order confirmation notification queued successfully",
                recipient=f"user_{request.user_id}",
                template="order_confirmation"
            )
        except Exception as e:
            logger.error(f"Failed to queue order confirmation: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue order confirmation")
    
    @router.post("/password-reset", response_model=NotificationResponse)
    async def send_password_reset(
        self,
        background_tasks: BackgroundTasks,
        request: PasswordResetRequest
    ):
        """Send password reset notification."""
        try:
            # Add to background tasks for async processing
            background_tasks.add_task(
                self.email_service.send_password_reset,
                user_id=request.user_id,
                reset_token=request.reset_token,
                email=request.email
            )
            
            return NotificationResponse(
                message="Password reset notification queued successfully",
                recipient=request.email,
                template="password_reset"
            )
        except Exception as e:
            logger.error(f"Failed to queue password reset notification: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue password reset notification")
    
    @router.post("/welcome", response_model=NotificationResponse)
    async def send_welcome_notification(
        self,
        background_tasks: BackgroundTasks,
        request: WelcomeNotificationRequest
    ):
        """Send welcome notification to new users."""
        try:
            # Add to background tasks for async processing
            background_tasks.add_task(
                self.email_service.send_welcome_email,
                user_id=request.user_id,
                email=request.email,
                username=request.username
            )
            
            return NotificationResponse(
                message="Welcome notification queued successfully",
                recipient=request.email,
                template="welcome"
            )
        except Exception as e:
            logger.error(f"Failed to queue welcome notification: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue welcome notification")
    
    @router.get("/status/{notification_id}", response_model=NotificationStatusResponse)
    async def get_notification_status(self, notification_id: str):
        """Get notification delivery status."""
        try:
            # This would typically check the status from a database or cache
            # For now, return a mock status
            return NotificationStatusResponse(
                notification_id=notification_id,
                status="delivered",
                delivered_at="2024-01-01T12:00:00Z",
                channel="email"
            )
        except Exception as e:
            logger.error(f"Failed to get notification status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get notification status")
    
    @router.get("/templates", response_model=NotificationTemplatesResponse)
    async def get_notification_templates(self):
        """Get available notification templates."""
        try:
            return NotificationTemplatesResponse(
                email_templates=[
                    "order_confirmation",
                    "password_reset",
                    "welcome",
                    "order_status_update",
                    "promotional"
                ],
                sms_templates=[
                    "order_confirmation",
                    "delivery_update",
                    "promotional"
                ]
            )
        except Exception as e:
            logger.error(f"Failed to get notification templates: {e}")
            raise HTTPException(status_code=500, detail="Failed to get notification templates")