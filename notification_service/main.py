"""
Notification Service - Main application entry point.
Handles email, SMS, and push notifications for the Food Fast e-commerce platform.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from controllers.notification_controller import (
    NotificationController,
    router as notification_router,
)
from channels.email import EmailService
from channels.sms import SMSService
from support.chat_service import ChatService
from shared.database.connection import get_database_manager, test_database_connection
from shared.messaging.redis_client import get_redis_manager, test_redis_connection
from utils.logger import get_logger, setup_logging

# Setup logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Initialize services
email_service = None
sms_service = None
chat_service = None
notification_controller = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global email_service, sms_service, chat_service, notification_controller

    # Startup
    logger.info("Notification Service starting up...")

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

        # Initialize notification services
        email_service = EmailService(redis_manager)
        sms_service = SMSService(redis_manager)
        chat_service = ChatService(db_manager, redis_manager)

        # Initialize controller
        notification_controller = NotificationController(
            email_service, sms_service, chat_service
        )

        logger.info("Notification Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start Notification Service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Notification Service shutting down...")
    try:
        from shared.database.connection import close_database_connections
        from shared.messaging.redis_client import close_redis_connections

        close_database_connections()
        close_redis_connections()
        logger.info("Notification Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Food Fast - Notification Service",
    description="Microservice for handling notifications",
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
app.include_router(notification_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Food Fast Notification Service",
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
            "service": "notification-service",
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "notification-service",
                "error": str(e),
            },
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8006))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run("main:app", host=host, port=port, reload=True, log_level="info")
