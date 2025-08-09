"""
Payment Service - Main application entry point.
Handles payment processing for the Food Fast e-commerce platform.
"""

import sys
import os

# Add shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared_code.core.app import create_app
from shared_code.core.config import get_service_settings
from shared_code.utils.logging import get_logger

from api.routers.payment_controller import router as payment_router
from gateways.stripe import StripeGateway
from gateways.momo import MoMoGateway
from gateways.vnpay import VNPayGateway
from promotions.promotion_service import PromotionService

logger = get_logger(__name__)
settings = get_service_settings("payment_service")

# Initialize services
stripe_gateway = None
momo_gateway = None
vnpay_gateway = None
promotion_service = None


async def startup_task():
    """Payment service startup tasks"""
    global stripe_gateway, momo_gateway, vnpay_gateway, promotion_service
    
    logger.info("Payment Service starting up...")
    
    try:
        # Initialize payment gateways
        stripe_gateway = StripeGateway()
        momo_gateway = MoMoGateway()
        vnpay_gateway = VNPayGateway()
        
        # Initialize promotion service
        promotion_service = PromotionService()
        
        logger.info("Payment Service startup completed")
        
    except Exception as e:
        logger.error(f"Payment Service startup failed: {e}")
        raise


async def shutdown_task():
    """Payment service shutdown tasks"""
    logger.info("Payment Service shutting down...")
    
    try:
        # Cleanup payment gateways
        if stripe_gateway:
            await stripe_gateway.cleanup()
        if momo_gateway:
            await momo_gateway.cleanup()
        if vnpay_gateway:
            await vnpay_gateway.cleanup()
            
        logger.info("Payment Service shutdown completed")
        
    except Exception as e:
        logger.error(f"Payment Service shutdown error: {e}")


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="Payment Service",
    settings=settings,
    routers=[payment_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'SERVICE_HOST', '0.0.0.0'),
        port=getattr(settings, 'SERVICE_PORT', 8005),
        reload=getattr(settings, 'DEBUG', False),
        log_level=getattr(settings, 'LOG_LEVEL', 'info').lower(),
    )
