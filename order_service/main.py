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

from controllers.cart_controller import router as cart_router
from controllers.order_controller import router as order_router
from core.database import engine, Base

logger = get_logger(__name__)
settings = get_service_settings("order_service")


async def startup_task():
    """Order service startup tasks"""
    logger.info("Order Service starting up...")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


async def shutdown_task():
    """Order service shutdown tasks"""
    logger.info("Order Service shutting down...")


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="Order Service",
    settings=settings,
    routers=[cart_router, order_router],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)

# Add service-specific routes with prefixes
app.include_router(cart_router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["Orders"])


@app.get("/")
async def root():
    return {"message": "Food Fast Order Service", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
    )
