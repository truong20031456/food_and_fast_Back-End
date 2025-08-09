"""
Product Service - Main application entry point.
FastAPI Product Service for Food & Fast E-Commerce platform.
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

from api.routers.products_router import router as products_router
from api.routers.reviews_router import router as reviews_router  
from api.routers.search_router import router as search_router
from core.database import init_db, close_db

logger = get_logger(__name__)
settings = get_service_settings("product_service")


async def startup_task():
    """Product service startup tasks"""
    logger.info("Product Service starting up...")
    await init_db()


async def shutdown_task():
    """Product service shutdown tasks"""
    logger.info("Product Service shutting down...")
    await close_db()


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="Product Service",
    settings=settings,
    routers=[
        products_router,
        reviews_router,
        search_router,
    ],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'SERVICE_HOST', '0.0.0.0'),
        port=getattr(settings, 'SERVICE_PORT', 8003),
        reload=getattr(settings, 'DEBUG', False),
        log_level=getattr(settings, 'LOG_LEVEL', 'info').lower(),
    )
