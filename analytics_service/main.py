"""
Analytics Service - Main application entry point.
Provides analytics and reporting capabilities for the Food Fast e-commerce platform.
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

from api.routers.analytics_router import router as analytics_router
from services.analytics_service import AnalyticsService
from services.sales_report import SalesReportService
from core.database import init_db, close_db

logger = get_logger(__name__)
settings = get_service_settings("analytics_service")

# Initialize services
analytics_service = None
sales_report_service = None


async def startup_task():
    """Analytics service startup tasks"""
    global analytics_service, sales_report_service
    
    logger.info("Analytics Service starting up...")
    
    try:
        # Initialize database
        await init_db()
        
        # Initialize services
        analytics_service = AnalyticsService()
        sales_report_service = SalesReportService()
        
        logger.info("Analytics Service startup completed")
        
    except Exception as e:
        logger.error(f"Analytics Service startup failed: {e}")
        raise


async def shutdown_task():
    """Analytics service shutdown tasks"""
    logger.info("Analytics Service shutting down...")
    
    try:
        # Close database connections
        await close_db()
        
        logger.info("Analytics Service shutdown completed")
        
    except Exception as e:
        logger.error(f"Analytics Service shutdown error: {e}")


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="Analytics Service",
    settings=settings,
    routers=[analytics_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'SERVICE_HOST', '0.0.0.0'),
        port=getattr(settings, 'SERVICE_PORT', 8007),
        reload=getattr(settings, 'DEBUG', False),
        log_level=getattr(settings, 'LOG_LEVEL', 'info').lower(),
    )
