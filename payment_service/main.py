"""
Payment Service - Main application entry point.
Handles payment processing for the Food Fast e-commerce platform.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from controllers.payment_controller import PaymentController, router as payment_router
from gateways.stripe import StripeGateway
from gateways.momo import MoMoGateway
from gateways.vnpay import VNPayGateway
from promotions.promotion_service import PromotionService
from shared.database.connection import get_database_manager, test_database_connection
from shared.messaging.redis_client import get_redis_manager, test_redis_connection
from utils.logger import get_logger, setup_logging

# Setup logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Initialize services
stripe_gateway = None
momo_gateway = None
vnpay_gateway = None
promotion_service = None
payment_controller = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global \
        stripe_gateway, \
        momo_gateway, \
        vnpay_gateway, \
        promotion_service, \
        payment_controller

    # Startup
    logger.info("Payment Service starting up...")

    try:
        # Initialize database connection
        database_url = os.getenv(
            "DATABASE_URL", "postgresql://admin:password@localhost:5432/food_fast"
        )
        db_manager = get_database_manager(database_url)

        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_manager = get_redis_manager(redis_url)

        # Test connections
        db_connected = await test_database_connection()
        redis_connected = await test_redis_connection()

        if not db_connected:
            logger.error("Failed to connect to database")
            raise Exception("Database connection failed")

        if not redis_connected:
            logger.warning("Failed to connect to Redis - some features may be limited")

        # Initialize payment gateways
        stripe_gateway = StripeGateway()
        momo_gateway = MoMoGateway()
        vnpay_gateway = VNPayGateway()

        # Initialize promotion service
        promotion_service = PromotionService(db_manager)

        # Initialize controller
        payment_controller = PaymentController(
            stripe_gateway, momo_gateway, vnpay_gateway, promotion_service
        )

        logger.info("Payment Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start Payment Service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Payment Service shutting down...")
    try:
        from shared.database.connection import close_database_connections
        from shared.messaging.redis_client import close_redis_connections

        close_database_connections()
        close_redis_connections()
        logger.info("Payment Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Food Fast - Payment Service",
    description="Microservice for payment processing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payment_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Food Fast Payment Service",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = await test_database_connection()
        redis_healthy = await test_redis_connection()

        status = "healthy" if db_healthy else "unhealthy"

        return {
            "status": status,
            "service": "payment-service",
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "payment-service",
                "error": str(e),
            },
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8004))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")
