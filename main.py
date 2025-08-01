import sys
import os

# Add parent directory and shared modules to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.core.app import create_app
from shared.core.config import get_service_settings
from shared.utils.logging import get_logger

from app.routers import gateway, auth
from app.core.startup import startup_task

logger = get_logger(__name__)
settings = get_service_settings("api_gateway")


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="API Gateway",
    settings=settings,
    routers=[gateway.router, auth.router],
    startup_tasks=[startup_task],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.value.lower(),
    )
