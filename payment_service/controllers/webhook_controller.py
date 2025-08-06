"""
Webhook Controller - Handles payment gateway webhooks
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from sqlalchemy.orm import Session

from services.payment_service import PaymentService, PaymentException
from gateways.stripe import StripeGateway
from gateways.momo import MoMoGateway
from gateways.vnpay import VNPayGateway
from promotions.promotion_service import PromotionService
from core.database import get_db
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Dependency to create PaymentService instance."""
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


@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="stripe-signature"),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """
    Handle Stripe webhooks.

    Args:
        request: HTTP request containing webhook payload
        stripe_signature: Stripe webhook signature header
        payment_service: Payment service instance

    Returns:
        Success response
    """
    try:
        # Get webhook payload
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        # Verify webhook signature
        stripe_gateway = StripeGateway()
        if not stripe_gateway.verify_webhook_signature(payload_str, stripe_signature):
            logger.error("Invalid Stripe webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Parse webhook event
        import json

        event = json.loads(payload_str)

        # Handle different event types
        await _handle_stripe_event(event, payment_service)

        return {"status": "success"}

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/momo")
async def handle_momo_webhook(
    request: Request, payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Handle MoMo webhooks.

    Args:
        request: HTTP request containing webhook payload
        payment_service: Payment service instance

    Returns:
        Success response
    """
    try:
        # Get webhook payload
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        # Parse webhook data (MoMo specific format)
        import json

        webhook_data = json.loads(payload_str)

        # Handle MoMo webhook
        await _handle_momo_event(webhook_data, payment_service)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling MoMo webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/vnpay")
async def handle_vnpay_webhook(
    request: Request, payment_service: PaymentService = Depends(get_payment_service)
):
    """
    Handle VNPay webhooks.

    Args:
        request: HTTP request containing webhook payload
        payment_service: Payment service instance

    Returns:
        Success response
    """
    try:
        # Get webhook payload
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        # Parse webhook data (VNPay specific format)
        import json

        webhook_data = json.loads(payload_str)

        # Handle VNPay webhook
        await _handle_vnpay_event(webhook_data, payment_service)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling VNPay webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def _handle_stripe_event(event: Dict[str, Any], payment_service: PaymentService):
    """
    Handle specific Stripe webhook events.

    Args:
        event: Stripe webhook event data
        payment_service: Payment service instance
    """
    event_type = event.get("type")
    payment_intent = event.get("data", {}).get("object", {})
    payment_intent_id = payment_intent.get("id")

    logger.info(f"Processing Stripe webhook: {event_type} for {payment_intent_id}")

    try:
        if event_type == "payment_intent.succeeded":
            # Payment succeeded
            await _update_payment_status(
                payment_service, payment_intent_id, "completed"
            )

        elif event_type == "payment_intent.payment_failed":
            # Payment failed
            await _update_payment_status(payment_service, payment_intent_id, "failed")

        elif event_type == "payment_intent.canceled":
            # Payment canceled
            await _update_payment_status(
                payment_service, payment_intent_id, "cancelled"
            )

        elif event_type == "charge.dispute.created":
            # Dispute created
            await _handle_dispute(payment_service, payment_intent)

        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")

    except Exception as e:
        logger.error(f"Error processing Stripe event {event_type}: {e}")
        raise


async def _handle_momo_event(
    webhook_data: Dict[str, Any], payment_service: PaymentService
):
    """
    Handle MoMo webhook events.

    Args:
        webhook_data: MoMo webhook data
        payment_service: Payment service instance
    """
    # MoMo specific webhook handling logic
    result_code = webhook_data.get("resultCode")
    order_id = webhook_data.get("orderId")

    logger.info(f"Processing MoMo webhook for order {order_id}, result: {result_code}")

    try:
        if result_code == 0:  # Success
            await _update_payment_status(payment_service, order_id, "completed")
        else:  # Failed
            await _update_payment_status(payment_service, order_id, "failed")

    except Exception as e:
        logger.error(f"Error processing MoMo webhook: {e}")
        raise


async def _handle_vnpay_event(
    webhook_data: Dict[str, Any], payment_service: PaymentService
):
    """
    Handle VNPay webhook events.

    Args:
        webhook_data: VNPay webhook data
        payment_service: Payment service instance
    """
    # VNPay specific webhook handling logic
    response_code = webhook_data.get("vnp_ResponseCode")
    txn_ref = webhook_data.get("vnp_TxnRef")

    logger.info(
        f"Processing VNPay webhook for transaction {txn_ref}, response: {response_code}"
    )

    try:
        if response_code == "00":  # Success
            await _update_payment_status(payment_service, txn_ref, "completed")
        else:  # Failed
            await _update_payment_status(payment_service, txn_ref, "failed")

    except Exception as e:
        logger.error(f"Error processing VNPay webhook: {e}")
        raise


async def _update_payment_status(
    payment_service: PaymentService, payment_intent_id: str, new_status: str
):
    """
    Update payment status based on webhook event.

    Args:
        payment_service: Payment service instance
        payment_intent_id: Payment intent ID
        new_status: New payment status
    """
    try:
        # Update payment status in database
        # Note: This would require additional method in PaymentService
        logger.info(f"Updating payment {payment_intent_id} status to {new_status}")

        # TODO: Implement update_payment_status_by_webhook method in PaymentService
        # await payment_service.update_payment_status_by_webhook(payment_intent_id, new_status)

    except Exception as e:
        logger.error(f"Failed to update payment status: {e}")
        raise


async def _handle_dispute(
    payment_service: PaymentService, payment_intent: Dict[str, Any]
):
    """
    Handle payment dispute events.

    Args:
        payment_service: Payment service instance
        payment_intent: Payment intent data
    """
    try:
        payment_intent_id = payment_intent.get("id")
        logger.info(f"Handling dispute for payment {payment_intent_id}")

        # TODO: Implement dispute handling logic
        # - Notify admin
        # - Update payment status
        # - Send notification to user

    except Exception as e:
        logger.error(f"Failed to handle dispute: {e}")
        raise
