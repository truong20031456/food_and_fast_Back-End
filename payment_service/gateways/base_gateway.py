"""
Base Payment Gateway Interface - Abstract class for all payment gateways
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class PaymentGateway(ABC):
    """
    Abstract base class for payment gateways.
    All payment gateway implementations must inherit from this class.
    """

    @abstractmethod
    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "usd",
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
        """
        pass

    @abstractmethod
    async def confirm_payment(
        self, payment_intent_id: str, payment_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Confirm a payment.

        Args:
            payment_intent_id: Payment intent ID
            payment_method: Payment method ID

        Returns:
            Dict containing payment confirmation details
        """
        pass

    @abstractmethod
    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: str = "requested_by_customer",
    ) -> Dict[str, Any]:
        """
        Refund a payment.

        Args:
            payment_intent_id: Payment intent ID
            amount: Refund amount (None for full refund)
            reason: Refund reason

        Returns:
            Dict containing refund details
        """
        pass

    @abstractmethod
    async def get_payment_status(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Get payment status.

        Args:
            payment_intent_id: Payment intent ID

        Returns:
            Dict containing payment status
        """
        pass

    @abstractmethod
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle webhook events.

        Args:
            payload: Webhook payload
            signature: Webhook signature

        Returns:
            Dict containing processed webhook data
        """
        pass


class PaymentResult:
    """
    Standardized payment result class.
    """

    def __init__(
        self,
        success: bool,
        transaction_id: str,
        amount: float,
        currency: str,
        status: str,
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.transaction_id = transaction_id
        self.amount = amount
        self.currency = currency
        self.status = status
        self.message = message
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "message": self.message,
            "metadata": self.metadata,
        }
