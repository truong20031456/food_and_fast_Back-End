"""
Notification Router - Simplified function-based routes for notifications.
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
    NotificationTemplatesResponse,
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

# Initialize services
email_service = EmailService()
sms_service = SMSService()
chat_service = ChatService()


@router.post("/email", response_model=NotificationResponse)
async def send_email_notification(
    background_tasks: BackgroundTasks, request: EmailNotificationRequest
):
    """Send email notification."""
    try:
        # Add to background tasks for async processing
        background_tasks.add_task(
            email_service.send_email,
            recipient=request.recipient,
            subject=request.subject,
            template=request.template,
            data=request.data or {},
        )

        return NotificationResponse(
            message="Email notification queued successfully",
            recipient=request.recipient,
            template=request.template,
        )
    except Exception as e:
        logger.error(f"Failed to queue email notification: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to queue email notification"
        )


@router.post("/sms", response_model=NotificationResponse)
async def send_sms_notification(
    background_tasks: BackgroundTasks, request: SMSNotificationRequest
):
    """Send SMS notification."""
    try:
        # Add to background tasks for async processing
        background_tasks.add_task(
            sms_service.send_sms,
            phone_number=request.phone_number,
            message=request.message,
            template=request.template,
        )

        return NotificationResponse(
            message="SMS notification queued successfully",
            recipient=request.phone_number,
            template=request.template,
        )
    except Exception as e:
        logger.error(f"Failed to queue SMS notification: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to queue SMS notification"
        )


@router.post("/order-confirmation", response_model=NotificationResponse)
async def send_order_confirmation(
    background_tasks: BackgroundTasks, request: OrderConfirmationRequest
):
    """Send order confirmation notification."""
    try:
        # Send email confirmation
        background_tasks.add_task(
            email_service.send_order_confirmation,
            customer_email=request.customer_email,
            order_data=request.order_data,
        )

        # Send SMS if phone provided
        if request.customer_phone:
            background_tasks.add_task(
                sms_service.send_order_confirmation,
                phone_number=request.customer_phone,
                order_data=request.order_data,
            )

        return NotificationResponse(
            message="Order confirmation notification queued successfully",
            recipient=request.customer_email,
            template="order_confirmation",
        )
    except Exception as e:
        logger.error(f"Failed to queue order confirmation: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to queue order confirmation"
        )


@router.post("/password-reset", response_model=NotificationResponse)
async def send_password_reset(
    background_tasks: BackgroundTasks, request: PasswordResetRequest
):
    """Send password reset notification."""
    try:
        background_tasks.add_task(
            email_service.send_password_reset,
            recipient=request.email,
            reset_token=request.reset_token,
            reset_url=request.reset_url,
        )

        return NotificationResponse(
            message="Password reset notification queued successfully",
            recipient=request.email,
            template="password_reset",
        )
    except Exception as e:
        logger.error(f"Failed to queue password reset: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to queue password reset"
        )


@router.post("/welcome", response_model=NotificationResponse)
async def send_welcome_notification(
    background_tasks: BackgroundTasks, request: WelcomeNotificationRequest
):
    """Send welcome notification to new users."""
    try:
        background_tasks.add_task(
            email_service.send_welcome_email,
            recipient=request.email,
            user_data=request.user_data,
        )

        return NotificationResponse(
            message="Welcome notification queued successfully",
            recipient=request.email,
            template="welcome",
        )
    except Exception as e:
        logger.error(f"Failed to queue welcome notification: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to queue welcome notification"
        )


@router.get("/status/{notification_id}", response_model=NotificationStatusResponse)
async def get_notification_status(notification_id: str):
    """Get the status of a notification."""
    try:
        # Implementation would check status from database/queue
        return NotificationStatusResponse(
            notification_id=notification_id,
            status="sent",  # This would be dynamic
            created_at="2024-01-01T00:00:00Z",
            sent_at="2024-01-01T00:01:00Z",
        )
    except Exception as e:
        logger.error(f"Failed to get notification status: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get notification status"
        )


@router.get("/templates", response_model=NotificationTemplatesResponse)
async def get_notification_templates():
    """Get available notification templates."""
    try:
        templates = {
            "email": [
                "welcome",
                "order_confirmation", 
                "password_reset",
                "order_shipped",
                "order_delivered"
            ],
            "sms": [
                "order_confirmation",
                "order_shipped", 
                "order_delivered",
                "otp_verification"
            ]
        }
        
        return NotificationTemplatesResponse(templates=templates)
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get templates"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "notification_service"}
