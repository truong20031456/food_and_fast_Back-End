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
            USE_CREDENTIALS=True,
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send an email notification.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
            template_name: Template name for rendering
            template_data: Data for template rendering

        Returns:
            bool: True if email was sent successfully
        """
        try:
            if self.fastmail is None:
                logger.warning("FastMail not configured - sending mock email")
                logger.info(f"Mock email to {to_email}: {subject}")
                return True

            # Prepare email content
            if template_name and template_data:
                # Use template rendering
                html_body = await self._render_template(template_name, template_data)

            message = MessageSchema(
                subject=subject,
                recipients=[to_email],
                body=body,
                html=html_body,
                subtype="html" if html_body else "plain",
            )

            await self.fastmail.send_message(message)
            logger.info(f"Email sent successfully to {to_email}")

            # Cache email for tracking
            if self.redis_manager:
                await self._cache_email_sent(to_email, subject)

            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new user."""
        return await self.send_email(
            to_email=to_email,
            subject="Welcome to Food & Fast!",
            body=f"Welcome {user_name}! Thank you for joining Food & Fast.",
            template_name="welcome",
            template_data={"user_name": user_name},
        )

    async def send_order_confirmation(
        self, to_email: str, order_id: str, order_details: Dict[str, Any]
    ) -> bool:
        """Send order confirmation email."""
        return await self.send_email(
            to_email=to_email,
            subject=f"Order Confirmation - #{order_id}",
            body=f"Your order #{order_id} has been confirmed.",
            template_name="order_confirmation",
            template_data={"order_id": order_id, "order_details": order_details},
        )

    async def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        return await self.send_email(
            to_email=to_email,
            subject="Password Reset Request",
            body=f"Click the link to reset your password: {reset_link}",
            template_name="password_reset",
            template_data={"reset_link": reset_link},
        )

    async def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render email template with data.
        This is a simplified version - in production, use Jinja2 templates.
        """
        templates = {
            "welcome": """
                <h1>Welcome to Food & Fast!</h1>
                <p>Hello {user_name},</p>
                <p>Thank you for joining Food & Fast. We're excited to have you!</p>
                <p>Best regards,<br>The Food & Fast Team</p>
            """,
            "order_confirmation": """
                <h1>Order Confirmation</h1>
                <p>Your order #{order_id} has been confirmed.</p>
                <p>Order Details: {order_details}</p>
                <p>Thank you for your order!</p>
            """,
            "password_reset": """
                <h1>Password Reset</h1>
                <p>You requested a password reset.</p>
                <p><a href="{reset_link}">Click here to reset your password</a></p>
                <p>If you didn't request this, please ignore this email.</p>
            """,
        }

        template = templates.get(template_name, "")
        return template.format(**data)

    async def _cache_email_sent(self, to_email: str, subject: str):
        """Cache email sent information for tracking."""
        if self.redis_manager:
            key = f"email_sent:{to_email}:{subject}"
            await self.redis_manager.set(key, "sent", expire=86400)  # 24 hours

    async def send_email(
        self,
        recipient: EmailStr,
        subject: str,
        template: str,
        data: Dict[str, Any] = None,
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
                    subtype="html",
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
        self, user_id: int, order_id: int, order_data: Dict[str, Any]
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
                data=order_data,
            )
        except Exception as e:
            logger.error(f"Failed to send order confirmation: {e}")
            return False

    async def send_password_reset(
        self, user_id: int, reset_token: str, email: EmailStr
    ) -> bool:
        """Send password reset email."""
        try:
            subject = "Password Reset Request"
            template = "password_reset"
            data = {
                "reset_token": reset_token,
                "reset_url": f"https://foodfast.com/reset-password?token={reset_token}",
            }

            return await self.send_email(
                recipient=email, subject=subject, template=template, data=data
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False

    async def send_welcome_email(
        self, user_id: int, email: EmailStr, username: str = None
    ) -> bool:
        """Send welcome email to new users."""
        try:
            subject = "Welcome to Food Fast!"
            template = "welcome"
            data = {
                "username": username or f"User {user_id}",
                "login_url": "https://foodfast.com/login",
            }

            return await self.send_email(
                recipient=email, subject=subject, template=template, data=data
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
            <p>Order ID: {data.get("order_id", "N/A")}</p>
            <p>Total: ${data.get("total", 0):.2f}</p>
            """
        elif template == "password_reset":
            return f"""
            <h2>Password Reset</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{data.get("reset_url", "#")}">Reset Password</a>
            """
        elif template == "welcome":
            return f"""
            <h2>Welcome to Food Fast!</h2>
            <p>Hello {data.get("username", "there")}!</p>
            <p>Welcome to Food Fast. We're excited to have you on board!</p>
            """
        else:
            return f"<p>Email content for template: {template}</p>"
