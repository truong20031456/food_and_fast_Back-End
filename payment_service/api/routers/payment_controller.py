"""
Payment Controller - Handles HTTP requests for payment endpoints.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from services.payment_service import (
    PaymentService,
    PaymentException,
    InvalidPaymentMethodException,
    InsufficientFundsException,
)
from gateways.stripe import StripeGateway
from gateways.momo import MoMoGateway
from gateways.vnpay import VNPayGateway
from promotions.promotion_service import PromotionService
from schemas.payment import (
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentConfirmationRequest,
    PaymentStatusResponse,
    PaymentMethodResponse,
    RefundRequest,
    RefundResponse,
)
from core.database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """
    Dependency to create PaymentService instance.
    """
    stripe_gateway = StripeGateway()
    momo_gateway = MoMoGateway()
    vnpay_gateway = VNPayGateway()
    promotion_service = PromotionService()

    return PaymentService(
        db=db,
        stripe_gateway=stripe_gateway,
        momo_gateway=momo_gateway,
        vnpay_gateway=vnpay_gateway,
        promotion_service=promotion_service,
    )


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    request: PaymentIntentRequest,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Create payment intent.

    Args:
        request: Payment intent request data
        payment_service: Payment service instance

    Returns:
        PaymentIntentResponse: Created payment intent details

    Raises:
        HTTPException: If payment creation fails
    """
    try:
        result = await payment_service.create_payment_intent(request)
        return result

    except InvalidPaymentMethodException as e:
        logger.error(f"Invalid payment method: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentException as e:
        logger.error(f"Payment error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating payment intent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/confirm", response_model=PaymentStatusResponse)
async def confirm_payment(
    request: PaymentConfirmationRequest,
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Confirm payment.

    Args:
        request: Payment confirmation request
        payment_service: Payment service instance

    Returns:
        PaymentStatusResponse: Updated payment status
    """
    try:
        result = await payment_service.confirm_payment(request)
        return result

    except PaymentException as e:
        logger.error(f"Payment confirmation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error confirming payment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{payment_intent_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_intent_id: str,
    payment_method: str = Query(..., description="Payment method used"),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get payment status.

    Args:
        payment_intent_id: Payment intent ID
        payment_method: Payment method used
        payment_service: Payment service instance

    Returns:
        PaymentStatusResponse: Current payment status
    """
    try:
        result = await payment_service.get_payment_status(
            payment_intent_id, payment_method
        )
        return result

    except PaymentException as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting payment status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/methods/available", response_model=PaymentMethodResponse)
async def get_available_payment_methods():
    """
    Get available payment methods.

    Returns:
        PaymentMethodResponse: List of available payment methods
    """
    try:
        return PaymentMethodResponse(
            payment_methods=[
                {
                    "id": "stripe",
                    "name": "Credit Card",
                    "description": "Pay with credit or debit card",
                    "supported_currencies": ["USD", "EUR", "GBP"],
                },
                {
                    "id": "momo",
                    "name": "MoMo",
                    "description": "Pay with MoMo wallet",
                    "supported_currencies": ["VND"],
                },
                {
                    "id": "vnpay",
                    "name": "VNPay",
                    "description": "Pay with VNPay",
                    "supported_currencies": ["VND"],
                },
            ]
        )
    except Exception as e:
        logger.error(f"Failed to get payment methods: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment methods")


@router.post("/refund/{payment_intent_id}", response_model=RefundResponse)
async def refund_payment(
    payment_intent_id: str,
    refund_request: RefundRequest,
    payment_method: str = Query(..., description="Payment method used"),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Refund payment.

    Args:
        payment_intent_id: Payment intent ID
        refund_request: Refund request details
        payment_method: Payment method used
        payment_service: Payment service instance

    Returns:
        RefundResponse: Refund details
    """
    try:
        result = await payment_service.refund_payment(
            payment_intent_id, payment_method, refund_request
        )
        return result

    except PaymentException as e:
        logger.error(f"Refund error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing refund: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history")
async def get_payment_history(
    order_id: Optional[str] = Query(None, description="Filter by order ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(20, description="Maximum records to return"),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Get payment history with optional filters.

    Args:
        order_id: Filter by order ID
        user_id: Filter by user ID
        skip: Number of records to skip
        limit: Maximum records to return
        payment_service: Payment service instance

    Returns:
        List of payment records
    """
    try:
        result = await payment_service.get_payment_history(
            order_id=order_id, user_id=user_id, skip=skip, limit=limit
        )
        return {"payments": result, "total": len(result)}

    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
