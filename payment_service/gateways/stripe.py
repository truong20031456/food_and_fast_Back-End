"""
Stripe Payment Gateway - Handles Stripe payment processing.
"""

import logging
from typing import Dict, Any, Optional
import os
import httpx

from .base import PaymentGateway
from utils.logger import get_logger

logger = get_logger(__name__)


class StripeException(Exception):
    """Exception for Stripe-specific errors"""

    pass


class StripeGateway(PaymentGateway):
    """
    Stripe payment gateway implementation.
    Implements the PaymentGateway interface for Stripe API.
    """

    def __init__(self):
        self.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.base_url = "https://api.stripe.com/v1"

        if not self.api_key:
            logger.warning("Stripe API key not configured, using mock mode")
            self.mock_mode = True
        else:
            self.mock_mode = False

    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
        order_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Stripe payment intent.

        Args:
            amount: Payment amount (in smallest currency unit, e.g., cents)
            currency: Three-letter ISO currency code
            order_id: Optional order identifier
            metadata: Optional metadata to attach to the payment

        Returns:
            Dict containing payment intent details
        """
        if self.mock_mode:
            logger.info("Mock mode: Creating mock payment intent")
            return {
                "id": f"pi_mock_{order_id or 'test'}",
                "client_secret": "pi_mock_client_secret",
                "status": "requires_payment_method",
                "amount": int(amount * 100),  # Convert to cents
                "currency": currency,
                "metadata": metadata or {},
            }

        try:
            # Convert amount to cents (Stripe expects smallest currency unit)
            amount_cents = int(amount * 100)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {
                "amount": amount_cents,
                "currency": currency,
                "automatic_payment_methods[enabled]": "true",
            }

            if order_id:
                data["metadata[order_id]"] = order_id

            if metadata:
                for key, value in metadata.items():
                    data[f"metadata[{key}]"] = str(value)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payment_intents",
                    headers=headers,
                    data=data,
                    timeout=30.0,
                )

                if response.status_code != 200:
                    error_data = response.json()
                    raise StripeException(
                        f"Stripe API error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                    )

                result = response.json()
                logger.info(f"Payment intent created successfully: {result['id']}")
                return result

        except httpx.TimeoutException:
            logger.error("Stripe API timeout")
            raise StripeException("Payment gateway timeout")
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise StripeException(f"Failed to create payment intent: {str(e)}")

    async def confirm_payment(
        self, payment_intent_id: str, confirmation_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Confirm a Stripe payment.

        Args:
            payment_intent_id: Payment intent ID
            confirmation_data: Additional confirmation data

        Returns:
            Dict containing payment confirmation details

        Raises:
            StripeException: If Stripe API call fails
        """
        try:
            if self.mock_mode:
                # Mock response
                return {
                    "id": payment_intent_id,
                    "status": "succeeded",
                    "amount": 1000,  # Mock amount
                    "currency": "usd",
                }

            # Real Stripe API implementation
            try:
                import stripe

                stripe.api_key = self.api_key

                confirm_data = {}
                if confirmation_data:
                    confirm_data.update(confirmation_data)

                intent = stripe.PaymentIntent.confirm(payment_intent_id, **confirm_data)

                return {
                    "id": intent.id,
                    "status": intent.status,
                    "amount": intent.amount / 100,  # Convert from cents
                    "currency": intent.currency,
                }

            except ImportError:
                logger.error("Stripe library not installed, using mock response")
                return await self.confirm_payment(payment_intent_id, confirmation_data)

        except Exception as e:
            logger.error(f"Failed to confirm Stripe payment: {e}")
            raise StripeException(f"Failed to confirm payment: {str(e)}")

    async def get_payment_status(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Get payment status from Stripe.

        Args:
            payment_intent_id: Payment intent ID

        Returns:
            Dict containing payment status details

        Raises:
            StripeException: If Stripe API call fails
        """
        try:
            if self.mock_mode:
                # Mock response
                return {
                    "id": payment_intent_id,
                    "status": "succeeded",
                    "amount": 1000,
                    "currency": "usd",
                    "created": 1234567890,
                }

            # Real Stripe API implementation
            try:
                import stripe

                stripe.api_key = self.api_key

                intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                return {
                    "id": intent.id,
                    "status": intent.status,
                    "amount": intent.amount / 100,  # Convert from cents
                    "currency": intent.currency,
                    "created": intent.created,
                }

            except ImportError:
                logger.error("Stripe library not installed, using mock response")
                return await self.get_payment_status(payment_intent_id)

        except Exception as e:
            logger.error(f"Failed to get Stripe payment status: {e}")
            raise StripeException(f"Failed to get payment status: {str(e)}")

    async def refund_payment(
        self, payment_intent_id: str, amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Refund a Stripe payment.

        Args:
            payment_intent_id: Payment intent ID
            amount: Refund amount (full refund if None)

        Returns:
            Dict containing refund details

        Raises:
            StripeException: If Stripe API call fails
        """
        try:
            if self.mock_mode:
                # Mock response
                refund_id = f"re_stripe_{payment_intent_id}"
                return {
                    "id": refund_id,
                    "payment_intent": payment_intent_id,
                    "amount": amount or 1000,
                    "status": "succeeded",
                }

            # Real Stripe API implementation
            try:
                import stripe

                stripe.api_key = self.api_key

                refund_data = {"payment_intent": payment_intent_id}
                if amount is not None:
                    refund_data["amount"] = int(amount * 100)  # Convert to cents

                refund = stripe.Refund.create(**refund_data)

                return {
                    "id": refund.id,
                    "payment_intent": payment_intent_id,
                    "amount": refund.amount / 100,  # Convert from cents
                    "status": refund.status,
                }

            except ImportError:
                logger.error("Stripe library not installed, using mock response")
                return await self.refund_payment(payment_intent_id, amount)

        except Exception as e:
            logger.error(f"Failed to refund Stripe payment: {e}")
            raise StripeException(f"Failed to refund payment: {str(e)}")

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Stripe webhook signature.

        Args:
            payload: Webhook payload
            signature: Webhook signature

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if self.mock_mode:
                # Mock verification - always return True in development
                return True

            # Real Stripe webhook verification
            try:
                import stripe

                stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
                return True

            except ImportError:
                logger.error(
                    "Stripe library not installed, webhook verification skipped"
                )
                return True
            except stripe.error.SignatureVerificationError:
                logger.error("Invalid webhook signature")
                return False

        except Exception as e:
            logger.error(f"Failed to verify Stripe webhook signature: {e}")
            return False
