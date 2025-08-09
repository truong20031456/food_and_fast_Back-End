"""
Notification Service - Main application entry point.
Handles email, SMS, and push notifications for the Food Fast e-commerce platform.
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

from api.routers.notification_router import router as notification_router
from channels.email import EmailService
from channels.sms import SMSService
from support.chat_service import ChatService

logger = get_logger(__name__)
settings = get_service_settings("notification_service")

# Initialize services
email_service = None
sms_service = None
chat_service = None


async def startup_task():
    """Notification service startup tasks"""
    global email_service, sms_service, chat_service
    
    logger.info("Notification Service starting up...")
    
    try:
        # Initialize notification channels
        email_service = EmailService()
        sms_service = SMSService()
        chat_service = ChatService()
        
        logger.info("Notification Service startup completed")
        
    except Exception as e:
        logger.error(f"Notification Service startup failed: {e}")
        raise


async def shutdown_task():
    """Notification service shutdown tasks"""
    logger.info("Notification Service shutting down...")
    
    try:
        # Cleanup notification services
        if email_service:
            await email_service.cleanup()
        if sms_service:
            await sms_service.cleanup()
        if chat_service:
            await chat_service.cleanup()
            
        logger.info("Notification Service shutdown completed")
        
    except Exception as e:
        logger.error(f"Notification Service shutdown error: {e}")


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="Notification Service",
    settings=settings,
    routers=[notification_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'SERVICE_HOST', '0.0.0.0'),
        port=getattr(settings, 'SERVICE_PORT', 8006),
        reload=getattr(settings, 'DEBUG', False),
        log_level=getattr(settings, 'LOG_LEVEL', 'info').lower(),
    )
