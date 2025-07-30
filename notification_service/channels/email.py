"""
Email Service - Handles email notifications.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import EmailStr
import os

from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import fastapi_mail, but handle gracefully if not available
try:
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
    FASTAPI_MAIL_AVAILABLE = True
except ImportError:
    FASTAPI_MAIL_AVAILABLE = False
    logger.warning("fastapi_mail not available - email functionality will be limited")


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self, redis_manager=None):
        self.redis_manager = redis_manager
        if FASTAPI_MAIL_AVAILABLE:
            self.fastmail = self._setup_fastmail()
        else:
            self.fastmail = None
    
    def _setup_fastmail(self):
        """Setup FastMail configuration."""
        if not FASTAPI_MAIL_AVAILABLE:
            return None
            
        conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("SMTP_USERNAME", ""),
            MAIL_PASSWORD=os.getenv("SMTP_PASSWORD", ""),
            MAIL_FROM=os.getenv("FROM_EMAIL", "noreply@foodfast.com"),
            MAIL_PORT=int(os.getenv("SMTP_PORT", "587")),
            MAIL_SERVER=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            MAIL_TLS=True,
            MAIL_SSL=False,
            USE_CREDENTIALS=True
        )
        return FastMail(conf)
    
    async def send_email(
        self, 
        recipient: EmailStr, 
        subject: str, 
        template: str, 
        data: Dict[str, Any] = None
    ) -> bool:
        """Send email notification."""
        try:
            # For now, use a simple template
            content = self._render_template(template, data or {})
            
            if self.fastmail:
                message = MessageSchema(
                    subject=subject,
                    recipients=[recipient],
                    body=content,
                    subtype="html"
                )
                
                await self.fastmail.send_message(message)
            else:
                # Log the email instead of sending
                logger.info(f"Email would be sent to {recipient}: {subject}")
                logger.info(f"Content: {content}")
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False
    
    async def send_order_confirmation(
        self, 
        user_id: int, 
        order_id: int, 
        order_data: Dict[str, Any]
    ) -> bool:
        """Send order confirmation email."""
        try:
            # This would typically get user email from user service
            user_email = f"user_{user_id}@example.com"  # Placeholder
            
            subject = f"Order Confirmation - Order #{order_id}"
            template = "order_confirmation"
            
            return await self.send_email(
                recipient=user_email,
                subject=subject,
                template=template,
                data=order_data
            )
        except Exception as e:
            logger.error(f"Failed to send order confirmation: {e}")
            return False
    
    async def send_password_reset(
        self, 
        user_id: int, 
        reset_token: str, 
        email: EmailStr
    ) -> bool:
        """Send password reset email."""
        try:
            subject = "Password Reset Request"
            template = "password_reset"
            data = {
                "reset_token": reset_token,
                "reset_url": f"https://foodfast.com/reset-password?token={reset_token}"
            }
            
            return await self.send_email(
                recipient=email,
                subject=subject,
                template=template,
                data=data
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    async def send_welcome_email(
        self, 
        user_id: int, 
        email: EmailStr, 
        username: str = None
    ) -> bool:
        """Send welcome email to new users."""
        try:
            subject = "Welcome to Food Fast!"
            template = "welcome"
            data = {
                "username": username or f"User {user_id}",
                "login_url": "https://foodfast.com/login"
            }
            
            return await self.send_email(
                recipient=email,
                subject=subject,
                template=template,
                data=data
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render email template with data."""
        # Simple template rendering - in production, use Jinja2
        if template == "order_confirmation":
            return f"""
            <h2>Order Confirmation</h2>
            <p>Thank you for your order!</p>
            <p>Order ID: {data.get('order_id', 'N/A')}</p>
            <p>Total: ${data.get('total', 0):.2f}</p>
            """
        elif template == "password_reset":
            return f"""
            <h2>Password Reset</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{data.get('reset_url', '#')}">Reset Password</a>
            """
        elif template == "welcome":
            return f"""
            <h2>Welcome to Food Fast!</h2>
            <p>Hello {data.get('username', 'there')}!</p>
            <p>Welcome to Food Fast. We're excited to have you on board!</p>
            """
        else:
            return f"<p>Email content for template: {template}</p>"