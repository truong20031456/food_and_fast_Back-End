"""
SMS Service - Handles SMS notifications.
"""

import logging
from typing import Dict, Any, Optional
import os

from utils.logger import get_logger

logger = get_logger(__name__)


class SMSService:
    """Service for sending SMS notifications."""

    def __init__(self, redis_manager=None):
        self.redis_manager = redis_manager
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER", "")

    async def send_sms(
        self, phone_number: str, message: str, template: str = None
    ) -> bool:
        """Send SMS notification."""
        try:
            # For now, just log the SMS - in production, integrate with Twilio
            logger.info(f"SMS would be sent to {phone_number}: {message}")

            # Placeholder for actual SMS sending
            # In production, use Twilio or other SMS provider
            # from twilio.rest import Client
            # client = Client(self.twilio_account_sid, self.twilio_auth_token)
            # message = client.messages.create(
            #     body=message,
            #     from_=self.twilio_from_number,
            #     to=phone_number
            # )

            return True

        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {e}")
            return False

    async def send_bulk_sms(self, phone_numbers: list, message: str) -> Dict[str, bool]:
        """Send bulk SMS notifications."""
        results = {}

        for phone_number in phone_numbers:
            success = await self.send_sms(phone_number, message)
            results[phone_number] = success

        return results

    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render SMS template with data."""
        # Simple template rendering
        if template == "order_confirmation":
            return f"Order #{data.get('order_id', 'N/A')} confirmed. Total: ${data.get('total', 0):.2f}"
        elif template == "delivery_update":
            return f"Your order #{data.get('order_id', 'N/A')} is {data.get('status', 'being processed')}"
        elif template == "promotional":
            return (
                f"Special offer: {data.get('message', 'Check out our latest deals!')}"
            )
        else:
            return data.get("message", "SMS notification")
