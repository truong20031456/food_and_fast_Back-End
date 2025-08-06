"""
Payment Service - Business logic layer for payment processing
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from schemas.payment import (
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentConfirmationRequest,
    PaymentStatusResponse,
    RefundRequest,
    RefundResponse,
)
from gateways.base import PaymentGateway
from gateways.stripe import StripeGateway
from gateways.momo import MoMoGateway
from gateways.vnpay import VNPayGateway
from promotions.promotion_service import PromotionService
from models.payment import Payment, PaymentTransaction
from utils.logger import get_logger

logger = get_logger(__name__)


class PaymentException(Exception):
    """Base exception for payment errors"""

    pass


class InsufficientFundsException(PaymentException):
    """Exception raised when payment fails due to insufficient funds"""

    pass


class InvalidPaymentMethodException(PaymentException):
    """Exception raised when payment method is invalid or not supported"""

    pass


class PaymentGatewayException(PaymentException):
    """Exception raised when payment gateway returns an error"""

    pass


class PaymentService:
    """
    Business logic layer for payment processing.
    Handles complete payment lifecycle including validation, gateway calls, and status tracking.
    """

    def __init__(
        self,
        db: Session,
        stripe_gateway: StripeGateway,
        momo_gateway: MoMoGateway,
        vnpay_gateway: VNPayGateway,
        promotion_service: PromotionService,
    ):
        self.db = db
        self.gateways = {
            "stripe": stripe_gateway,
            "momo": momo_gateway,
            "vnpay": vnpay_gateway,
        }
        self.promotion_service = promotion_service

    def _get_gateway(self, payment_method: str) -> PaymentGateway:
        """
        Get payment gateway instance for specified method.

        Args:
            payment_method: Payment method identifier

        Returns:
            PaymentGateway: Gateway instance

        Raises:
            InvalidPaymentMethodException: If payment method not supported
        """
        gateway = self.gateways.get(payment_method)
        if not gateway:
            raise InvalidPaymentMethodException(
                f"Unsupported payment method: {payment_method}"
            )
        return gateway

    async def create_payment_intent(
        self, request: PaymentIntentRequest
    ) -> PaymentIntentResponse:
        """
        Create payment intent with full business logic.

        Args:
            request: Payment intent request data

        Returns:
            PaymentIntentResponse: Created payment intent details

        Raises:
            PaymentException: If payment creation fails
        """
        try:
            # Validate payment method
            gateway = self._get_gateway(request.payment_method)

            # Apply promotions if provided
            original_amount = request.amount
            final_amount = original_amount
            discount_amount = 0

            if request.promotion_code:
                promotion_result = await self.promotion_service.apply_promotions(
                    original_amount, request.promotion_code
                )
                final_amount = promotion_result.get("final_amount", original_amount)
                discount_amount = original_amount - final_amount

            # Create payment record in database
            payment = Payment(
                order_id=request.order_id,
                original_amount=Decimal(str(original_amount)),
                discount_amount=Decimal(str(discount_amount)),
                final_amount=Decimal(str(final_amount)),
                currency=request.currency,
                payment_method=request.payment_method,
                status="pending",
                promotion_code=request.promotion_code,
                metadata=request.metadata or {},
                created_at=datetime.now(),
            )

            self.db.add(payment)
            self.db.flush()  # Get payment ID

            # Create payment intent via gateway
            gateway_response = await gateway.create_payment_intent(
                amount=float(final_amount),
                currency=request.currency,
                order_id=request.order_id,
                metadata={
                    "payment_id": payment.id,
                    "order_id": request.order_id,
                    **(request.metadata or {}),
                },
            )

            # Update payment with gateway information
            payment.gateway_payment_id = gateway_response["id"]
            payment.gateway_status = gateway_response["status"]
            payment.client_secret = gateway_response.get("client_secret")
            payment.updated_at = datetime.now()

            # Create transaction record
            transaction = PaymentTransaction(
                payment_id=payment.id,
                transaction_type="create_intent",
                gateway_response=gateway_response,
                status="success",
                created_at=datetime.now(),
            )
            self.db.add(transaction)

            self.db.commit()

            logger.info(f"Payment intent created successfully: {payment.id}")

            return PaymentIntentResponse(
                payment_intent_id=payment.gateway_payment_id,
                amount=float(final_amount),
                currency=request.currency,
                payment_method=request.payment_method,
                status=gateway_response["status"],
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating payment intent: {e}")
            raise PaymentException("Database error occurred")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create payment intent: {e}")
            raise PaymentException(f"Failed to create payment intent: {str(e)}")

    async def confirm_payment(
        self, request: PaymentConfirmationRequest
    ) -> PaymentStatusResponse:
        """
        Confirm payment and update status.

        Args:
            request: Payment confirmation request

        Returns:
            PaymentStatusResponse: Updated payment status

        Raises:
            PaymentException: If confirmation fails
        """
        try:
            # Find payment record
            payment = (
                self.db.query(Payment)
                .filter(Payment.gateway_payment_id == request.payment_intent_id)
                .first()
            )

            if not payment:
                raise PaymentException(
                    f"Payment not found: {request.payment_intent_id}"
                )

            # Get gateway and confirm payment
            gateway = self._get_gateway(request.payment_method)
            gateway_response = await gateway.confirm_payment(
                request.payment_intent_id, request.confirmation_data
            )

            # Update payment status
            payment.status = self._map_gateway_status(gateway_response["status"])
            payment.gateway_status = gateway_response["status"]
            payment.confirmed_at = datetime.now()
            payment.updated_at = datetime.now()

            # Create transaction record
            transaction = PaymentTransaction(
                payment_id=payment.id,
                transaction_type="confirm_payment",
                gateway_response=gateway_response,
                status="success",
                created_at=datetime.now(),
            )
            self.db.add(transaction)

            self.db.commit()

            logger.info(f"Payment confirmed successfully: {payment.id}")

            return PaymentStatusResponse(
                payment_intent_id=request.payment_intent_id,
                status=payment.status,
                amount=float(payment.final_amount),
                currency=payment.currency,
                created_at=payment.created_at.isoformat(),
                updated_at=payment.updated_at.isoformat(),
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error confirming payment: {e}")
            raise PaymentException("Database error occurred")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to confirm payment: {e}")
            raise PaymentException(f"Failed to confirm payment: {str(e)}")

    async def get_payment_status(
        self, payment_intent_id: str, payment_method: str
    ) -> PaymentStatusResponse:
        """
        Get current payment status.

        Args:
            payment_intent_id: Payment intent ID
            payment_method: Payment method used

        Returns:
            PaymentStatusResponse: Current payment status
        """
        try:
            # Find payment record
            payment = (
                self.db.query(Payment)
                .filter(Payment.gateway_payment_id == payment_intent_id)
                .first()
            )

            if not payment:
                raise PaymentException(f"Payment not found: {payment_intent_id}")

            # Get latest status from gateway
            gateway = self._get_gateway(payment_method)
            gateway_response = await gateway.get_payment_status(payment_intent_id)

            # Update status if changed
            new_status = self._map_gateway_status(gateway_response["status"])
            if new_status != payment.status:
                payment.status = new_status
                payment.gateway_status = gateway_response["status"]
                payment.updated_at = datetime.now()
                self.db.commit()

            return PaymentStatusResponse(
                payment_intent_id=payment_intent_id,
                status=payment.status,
                amount=float(payment.final_amount),
                currency=payment.currency,
                created_at=payment.created_at.isoformat(),
                updated_at=payment.updated_at.isoformat(),
            )

        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            raise PaymentException(f"Failed to get payment status: {str(e)}")

    async def refund_payment(
        self, payment_intent_id: str, payment_method: str, refund_request: RefundRequest
    ) -> RefundResponse:
        """
        Process payment refund.

        Args:
            payment_intent_id: Payment intent ID
            payment_method: Payment method used
            refund_request: Refund request details

        Returns:
            RefundResponse: Refund details
        """
        try:
            # Find payment record
            payment = (
                self.db.query(Payment)
                .filter(Payment.gateway_payment_id == payment_intent_id)
                .first()
            )

            if not payment:
                raise PaymentException(f"Payment not found: {payment_intent_id}")

            if payment.status != "completed":
                raise PaymentException("Can only refund completed payments")

            # Process refund via gateway
            gateway = self._get_gateway(payment_method)
            refund_amount = refund_request.amount or float(payment.final_amount)

            gateway_response = await gateway.refund_payment(
                payment_intent_id, refund_amount
            )

            # Update payment status
            payment.status = (
                "refunded"
                if refund_amount >= float(payment.final_amount)
                else "partially_refunded"
            )
            payment.refunded_amount = Decimal(str(refund_amount))
            payment.updated_at = datetime.now()

            # Create transaction record
            transaction = PaymentTransaction(
                payment_id=payment.id,
                transaction_type="refund",
                amount=Decimal(str(refund_amount)),
                gateway_response=gateway_response,
                status="success",
                created_at=datetime.now(),
            )
            self.db.add(transaction)

            self.db.commit()

            logger.info(
                f"Payment refunded successfully: {payment.id}, amount: {refund_amount}"
            )

            return RefundResponse(
                refund_id=gateway_response["id"],
                payment_intent_id=payment_intent_id,
                amount=refund_amount,
                status=gateway_response["status"],
                created_at=datetime.now().isoformat(),
            )

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error processing refund: {e}")
            raise PaymentException("Database error occurred")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process refund: {e}")
            raise PaymentException(f"Failed to process refund: {str(e)}")

    def _map_gateway_status(self, gateway_status: str) -> str:
        """
        Map gateway-specific status to standardized payment status.

        Args:
            gateway_status: Status from payment gateway

        Returns:
            str: Standardized payment status
        """
        status_mapping = {
            # Stripe statuses
            "requires_payment_method": "pending",
            "requires_confirmation": "pending",
            "requires_action": "pending",
            "processing": "processing",
            "succeeded": "completed",
            "canceled": "cancelled",
            # MoMo statuses
            "pending": "pending",
            "success": "completed",
            "failed": "failed",
            # VNPay statuses
            "00": "completed",  # Success
            "01": "pending",  # Pending
            "02": "failed",  # Failed
        }

        return status_mapping.get(gateway_status, "unknown")

    async def get_payment_history(
        self,
        order_id: Optional[str] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[PaymentStatusResponse]:
        """
        Get payment history with optional filters.

        Args:
            order_id: Filter by order ID
            user_id: Filter by user ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List[PaymentStatusResponse]: Payment history
        """
        try:
            query = self.db.query(Payment)

            if order_id:
                query = query.filter(Payment.order_id == order_id)
            if user_id:
                query = query.filter(Payment.user_id == user_id)

            payments = (
                query.order_by(Payment.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            return [
                PaymentStatusResponse(
                    payment_intent_id=payment.gateway_payment_id,
                    status=payment.status,
                    amount=float(payment.final_amount),
                    currency=payment.currency,
                    created_at=payment.created_at.isoformat(),
                    updated_at=payment.updated_at.isoformat(),
                )
                for payment in payments
            ]

        except Exception as e:
            logger.error(f"Failed to get payment history: {e}")
            raise PaymentException(f"Failed to get payment history: {str(e)}")
