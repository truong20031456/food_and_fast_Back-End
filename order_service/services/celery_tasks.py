
from celery import Celery
import os
from datetime import datetime, timedelta

# Celery configuration
celery_app = Celery(
    "order_service",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'cleanup-abandoned-carts': {
            'task': 'services.celery_tasks.cleanup_abandoned_carts',
            'schedule': timedelta(hours=1),  # Run every hour
        },
        'update-order-statuses': {
            'task': 'services.celery_tasks.update_order_statuses',
            'schedule': timedelta(minutes=5),  # Run every 5 minutes
        },
    }
)

@celery_app.task
def send_order_confirmation_email(order_id: int, user_email: str):
    """Send order confirmation email"""
    try:
        # Import here to avoid circular imports
        from core.database import SessionLocal
        from services.orders.order_service import OrderService
        
        db = SessionLocal()
        order = OrderService.get_order_by_id(db=db, order_id=order_id)
        
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        # Here you would integrate with your email service
        # For now, we'll just log the action
        print(f"Sending confirmation email for order {order.order_number} to {user_email}")
        
        # Email content would include:
        # - Order number
        # - Order items
        # - Total amount
        # - Delivery address
        # - Estimated delivery time
        
        db.close()
        return {"status": "success", "message": f"Confirmation email sent for order {order.order_number}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task
def send_order_status_update(order_id: int, user_email: str, new_status: str):
    """Send order status update notification"""
    try:
        from core.database import SessionLocal
        from services.orders.order_service import OrderService
        
        db = SessionLocal()
        order = OrderService.get_order_by_id(db=db, order_id=order_id)
        
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        print(f"Sending status update email for order {order.order_number} to {user_email}: {new_status}")
        
        # Email content would include:
        # - Order number
        # - New status
        # - Estimated delivery time (if applicable)
        # - Tracking information (if applicable)
        
        db.close()
        return {"status": "success", "message": f"Status update email sent for order {order.order_number}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task
def cleanup_abandoned_carts():
    """Clean up abandoned carts (older than 24 hours)"""
    try:
        from core.database import SessionLocal
        from models.cart import Cart
        from sqlalchemy import and_
        
        db = SessionLocal()
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Find abandoned carts
        abandoned_carts = db.query(Cart).filter(
            and_(
                Cart.status == "active",
                Cart.updated_at < cutoff_time
            )
        ).all()
        
        count = 0
        for cart in abandoned_carts:
            cart.status = "abandoned"
            count += 1
        
        db.commit()
        db.close()
        
        return {"status": "success", "message": f"Marked {count} carts as abandoned"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task
def update_order_statuses():
    """Auto-update order statuses based on time"""
    try:
        from core.database import SessionLocal
        from models.order import Order
        from services.orders.order_service import OrderService
        
        db = SessionLocal()
        now = datetime.now()
        
        # Auto-confirm orders that have been pending for more than 5 minutes
        pending_orders = db.query(Order).filter(
            and_(
                Order.status == "pending",
                Order.payment_status == "paid",
                Order.created_at < now - timedelta(minutes=5)
            )
        ).all()
        
        confirmed_count = 0
        for order in pending_orders:
            OrderService.update_order_status(db, order.id, "confirmed")
            confirmed_count += 1
        
        # Auto-update preparing orders to out_for_delivery after estimated prep time
        preparing_orders = db.query(Order).filter(
            and_
                Order.status == "preparing",
                Order.confirmed_at < now - timedelta(minutes=20)  # 20 min prep time
            )
        ).all()
        
        out_for_delivery_count = 0
        for order in preparing_orders:
            OrderService.update_order_status(db, order.id, "out_for_delivery")
            out_for_delivery_count += 1
        
        db.close()
        
        return {
            "status": "success", 
            "message": f"Confirmed {confirmed_count} orders, {out_for_delivery_count} out for delivery"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task
def process_payment(order_id: int, payment_method: str, payment_details: dict):
    """Process payment for an order"""
    try:
        from core.database import SessionLocal
        from services.orders.order_service import OrderService
        
        db = SessionLocal()
        order = OrderService.get_order_by_id(db=db, order_id=order_id)
        
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        # Here you would integrate with payment gateway
        # For simulation, we'll just mark as paid after a delay
        import time
        time.sleep(2)  # Simulate payment processing
        
        # Update payment status
        OrderService.update_payment_status(db, order_id, "paid")
        
        # Trigger order confirmation email
        send_order_confirmation_email.delay(order_id, "user@example.com")
        
        db.close()
        return {"status": "success", "message": f"Payment processed for order {order.order_number}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task
def notify_restaurant(order_id: int):
    """Notify restaurant about new order"""
    try:
        from core.database import SessionLocal
        from services.orders.order_service import OrderService
        
        db = SessionLocal()
        order = OrderService.get_order_by_id(db=db, order_id=order_id)
        
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        # Here you would integrate with restaurant notification system
        print(f"Notifying restaurant about order {order.order_number}")
        
        # Start preparing the order
        OrderService.update_order_status(db, order_id, "preparing")
        
        db.close()
        return {"status": "success", "message": f"Restaurant notified about order {order.order_number}"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}