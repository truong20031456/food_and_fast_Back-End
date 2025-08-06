"""
Base Payment Gateway Interface - Abstract class for all payment gateways
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PaymentGateway(ABC):
    """
    Abstract base class for payment gateways.
    All payment gateways must implement these methods.
    """

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: float,
        currency: str,
        order_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a payment intent.

        Args:
            amount: Payment amount
            currency: Payment currency
            order_id: Associated order ID
            metadata: Additional metadata

        Returns:
            Dict containing payment intent details

        Raises:
            PaymentGatewayException: If gateway API call fails
        """
        pass

    @abstractmethod
    async def confirm_payment(
        self, payment_intent_id: str, confirmation_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Confirm a payment intent.

        Args:
            payment_intent_id: Payment intent ID
            confirmation_data: Additional confirmation data

        Returns:
            Dict containing payment confirmation details

        Raises:
            PaymentGatewayException: If gateway API call fails
        """
        pass

    @abstractmethod
    async def get_payment_status(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Get payment status.

        Args:
            payment_intent_id: Payment intent ID

        Returns:
            Dict containing payment status details

        Raises:
            PaymentGatewayException: If gateway API call fails
        """
        pass

    @abstractmethod
    async def refund_payment(
        self, payment_intent_id: str, amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Refund a payment.

        Args:
            payment_intent_id: Payment intent ID
            amount: Refund amount (full refund if None)

        Returns:
            Dict containing refund details

        Raises:
            PaymentGatewayException: If gateway API call fails
        """
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Webhook payload
            signature: Webhook signature

        Returns:
            True if signature is valid, False otherwise
        """
        pass
