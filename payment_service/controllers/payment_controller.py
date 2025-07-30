"""
Payment Controller - Handles HTTP requests for payment endpoints.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from gateways.stripe import StripeGateway
from gateways.momo import MoMoGateway
from gateways.vnpay import VNPayGateway
from promotions.promotion_service import PromotionService
from schemas.payment import (
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentConfirmationRequest,
    PaymentStatusResponse,
    PaymentMethodResponse
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])


class PaymentController:
    """Controller for payment endpoints."""
    
    def __init__(self, stripe_gateway: StripeGateway, momo_gateway: MoMoGateway, 
                 vnpay_gateway: VNPayGateway, promotion_service: PromotionService):
        self.stripe_gateway = stripe_gateway
        self.momo_gateway = momo_gateway
        self.vnpay_gateway = vnpay_gateway
        self.promotion_service = promotion_service
    
    @router.post("/create-intent", response_model=PaymentIntentResponse)
    async def create_payment_intent(
        self,
        request: PaymentIntentRequest
    ):
        """Create payment intent."""
        try:
            # Apply promotions if any
            final_amount = await self.promotion_service.apply_promotions(
                request.amount, 
                request.promotion_code
            )
            
            # Create payment intent based on payment method
            if request.payment_method == "stripe":
                intent = await self.stripe_gateway.create_payment_intent(
                    amount=final_amount,
                    currency=request.currency,
                    order_id=request.order_id
                )
            elif request.payment_method == "momo":
                intent = await self.momo_gateway.create_payment_intent(
                    amount=final_amount,
                    currency=request.currency,
                    order_id=request.order_id
                )
            elif request.payment_method == "vnpay":
                intent = await self.vnpay_gateway.create_payment_intent(
                    amount=final_amount,
                    currency=request.currency,
                    order_id=request.order_id
                )
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment method")
            
            return PaymentIntentResponse(
                payment_intent_id=intent["id"],
                amount=final_amount,
                currency=request.currency,
                payment_method=request.payment_method,
                status=intent["status"]
            )
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}")
            raise HTTPException(status_code=500, detail="Failed to create payment intent")
    
    @router.post("/confirm", response_model=PaymentStatusResponse)
    async def confirm_payment(
        self,
        request: PaymentConfirmationRequest
    ):
        """Confirm payment."""
        try:
            # Confirm payment based on payment method
            if request.payment_method == "stripe":
                result = await self.stripe_gateway.confirm_payment(request.payment_intent_id)
            elif request.payment_method == "momo":
                result = await self.momo_gateway.confirm_payment(request.payment_intent_id)
            elif request.payment_method == "vnpay":
                result = await self.vnpay_gateway.confirm_payment(request.payment_intent_id)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment method")
            
            return PaymentStatusResponse(
                payment_intent_id=request.payment_intent_id,
                status=result["status"],
                amount=result.get("amount"),
                currency=result.get("currency")
            )
        except Exception as e:
            logger.error(f"Failed to confirm payment: {e}")
            raise HTTPException(status_code=500, detail="Failed to confirm payment")
    
    @router.get("/{payment_intent_id}", response_model=PaymentStatusResponse)
    async def get_payment_status(
        self,
        payment_intent_id: str,
        payment_method: str = Query(..., description="Payment method used")
    ):
        """Get payment status."""
        try:
            # Get payment status based on payment method
            if payment_method == "stripe":
                status = await self.stripe_gateway.get_payment_status(payment_intent_id)
            elif payment_method == "momo":
                status = await self.momo_gateway.get_payment_status(payment_intent_id)
            elif payment_method == "vnpay":
                status = await self.vnpay_gateway.get_payment_status(payment_intent_id)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment method")
            
            return PaymentStatusResponse(
                payment_intent_id=payment_intent_id,
                status=status["status"],
                amount=status.get("amount"),
                currency=status.get("currency")
            )
        except Exception as e:
            logger.error(f"Failed to get payment status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get payment status")
    
    @router.get("/methods/available", response_model=PaymentMethodResponse)
    async def get_available_payment_methods(self):
        """Get available payment methods."""
        try:
            return PaymentMethodResponse(
                payment_methods=[
                    {
                        "id": "stripe",
                        "name": "Credit Card",
                        "description": "Pay with credit or debit card",
                        "supported_currencies": ["USD", "EUR", "GBP"]
                    },
                    {
                        "id": "momo",
                        "name": "MoMo",
                        "description": "Pay with MoMo wallet",
                        "supported_currencies": ["VND"]
                    },
                    {
                        "id": "vnpay",
                        "name": "VNPay",
                        "description": "Pay with VNPay",
                        "supported_currencies": ["VND"]
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to get payment methods: {e}")
            raise HTTPException(status_code=500, detail="Failed to get payment methods")
    
    @router.post("/refund/{payment_intent_id}")
    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[float] = Query(None, description="Refund amount (full refund if not specified)"),
        payment_method: str = Query(..., description="Payment method used")
    ):
        """Refund payment."""
        try:
            # Process refund based on payment method
            if payment_method == "stripe":
                refund = await self.stripe_gateway.refund_payment(payment_intent_id, amount)
            elif payment_method == "momo":
                refund = await self.momo_gateway.refund_payment(payment_intent_id, amount)
            elif payment_method == "vnpay":
                refund = await self.vnpay_gateway.refund_payment(payment_intent_id, amount)
            else:
                raise HTTPException(status_code=400, detail="Unsupported payment method")
            
            return {
                "refund_id": refund["id"],
                "payment_intent_id": payment_intent_id,
                "amount": refund["amount"],
                "status": refund["status"]
            }
        except Exception as e:
            logger.error(f"Failed to refund payment: {e}")
            raise HTTPException(status_code=500, detail="Failed to refund payment")