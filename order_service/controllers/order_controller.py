from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from services.orders.order_service import OrderService
from schemas.order_schema import (
    OrderResponse,
    OrderCreate,
    OrderUpdate,
    OrderSummary,
    OrderStatusUpdate,
    PaymentStatusUpdate,
)

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    cart_id: int, order_data: OrderCreate, db: Session = Depends(get_db)
):
    """Create order from cart"""
    try:
        order = OrderService.create_order_from_cart(
            db=db, cart_id=cart_id, order_data=order_data
        )
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating order: {str(e)}",
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID"""
    order = OrderService.get_order_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    """Get order by order number"""
    order = OrderService.get_order_by_number(db=db, order_number=order_number)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.get("/user/{user_id}", response_model=List[OrderSummary])
async def get_user_orders(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get orders for a specific user"""
    orders = OrderService.get_user_orders(
        db=db, user_id=user_id, skip=skip, limit=limit
    )
    return orders


@router.get("/", response_model=List[OrderSummary])
async def get_orders_by_status(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get orders by status"""
    if status_filter:
        orders = OrderService.get_orders_by_status(
            db=db, status=status_filter, skip=skip, limit=limit
        )
    else:
        # If no status filter, get all orders (you might want to implement this)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Status filter is required"
        )
    return orders


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)
):
    """Update order status"""
    try:
        order = OrderService.update_order_status(
            db=db, order_id=order_id, status=status_update.status
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{order_id}/payment", response_model=OrderResponse)
async def update_payment_status(
    order_id: int, payment_update: PaymentStatusUpdate, db: Session = Depends(get_db)
):
    """Update payment status"""
    order = OrderService.update_payment_status(
        db=db, order_id=order_id, payment_status=payment_update.payment_status
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int, reason: Optional[str] = None, db: Session = Depends(get_db)
):
    """Cancel an order"""
    try:
        order = OrderService.cancel_order(db=db, order_id=order_id, reason=reason)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{order_id}/delivery-time", response_model=OrderResponse)
async def update_delivery_time(
    order_id: int,
    estimated_time: str,  # ISO format datetime string
    db: Session = Depends(get_db),
):
    """Update estimated delivery time"""
    try:
        from datetime import datetime

        parsed_time = datetime.fromisoformat(estimated_time.replace("Z", "+00:00"))

        order = OrderService.update_delivery_time(
            db=db, order_id=order_id, estimated_time=parsed_time
        )
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {str(e)}",
        )
