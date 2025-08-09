import sys
import os

# Add parent directory and shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared_code.core.app import create_app
from shared_code.core.config import get_service_settings
from shared_code.utils.logging import get_logger

from api.routers.user_router import router as user_router

logger = get_logger(__name__)
settings = get_service_settings("user_service")


async def startup_task():
    """User service startup tasks"""
    logger.info("User Service starting up...")
    # Initialize database connections, caches, etc.


async def shutdown_task():
    """User service shutdown tasks"""
    logger.info("User Service shutting down...")


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="User Service",
    settings=settings,
    routers=[user_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)
