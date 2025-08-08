"""
Analytics Service - Main application entry point.
Provides analytics and reporting capabilities for the Food Fast e-commerce platform.
"""

import os
import sys
from contextlib import asynccontextmanager

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "shared"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from controllers.analytics_controller import (
    AnalyticsController,
    router as analytics_router,
)
from services.analytics_service import AnalyticsService
from services.sales_report import SalesReportService
from services.elasticsearch_analytics_service import es_analytics_service
from core.config import settings
from core.database import db_manager, init_db, close_db
from core.elasticsearch_client import es_client
from utils.logger import get_logger

# Setup logging
# setup_logging(level=settings.log_level)
logger = get_logger(__name__)

# Initialize services
analytics_service = None
sales_report_service = None
analytics_controller = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global analytics_service, sales_report_service, analytics_controller

    # Startup
    logger.info("Analytics Service starting up...")

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Test database connection
        db_healthy = await db_manager.health_check()
        if not db_healthy:
            logger.error("Failed to connect to database")
            raise Exception("Database connection failed")

        # Initialize Elasticsearch
        try:
            await es_client.connect()
            await es_analytics_service.initialize_indices()
            logger.info("Elasticsearch initialized successfully")
        except Exception as e:
            logger.warning(f"Elasticsearch initialization failed: {e}")
            logger.warning("Analytics service will continue with database-only mode")

        # Initialize services
        analytics_service = AnalyticsService(db_manager)
        sales_report_service = SalesReportService(db_manager)

        # Initialize controller
        analytics_controller = AnalyticsController(
            analytics_service, sales_report_service
        )

        logger.info("Analytics Service started successfully")

    except Exception as e:
        logger.error(f"Failed to start Analytics Service: {e}")
        raise

    yield

    # Shutdown
    logger.info("Analytics Service shutting down...")
    try:
        # Close Elasticsearch connection
        if es_client.is_connected:
            await es_client.disconnect()
            logger.info("Elasticsearch disconnected")
        
        # Close database connection
        await close_db()
        logger.info("Analytics Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Food Fast - Analytics Service",
    description="Microservice for analytics and reporting",
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
app.include_router(analytics_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Food Fast Analytics Service",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = await db_manager.health_check()
        es_healthy = await es_client.health_check() if es_client.is_connected else False

        status = "healthy" if db_healthy else "unhealthy"

        return {
            "status": status,
            "service": "analytics-service",
            "database": "connected" if db_healthy else "disconnected",
            "elasticsearch": "connected" if es_healthy else "disconnected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "analytics-service",
                "error": str(e),
            },
        )


if __name__ == "__main__":
    port = settings.port
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
