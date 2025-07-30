"""
Analytics Service - Main application entry point.
Provides analytics and reporting capabilities for the Food Fast e-commerce platform.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from controllers.analytics_controller import AnalyticsController, router as analytics_router
from services.analytics_service import AnalyticsService
from services.sales_report import SalesReportService
from core.config import settings
from core.database import db_manager, init_db, close_db
from utils.logger import get_logger, setup_logging

# Setup logging
setup_logging(level=settings.log_level)
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
        
        # Initialize services
        analytics_service = AnalyticsService(db_manager)
        sales_report_service = SalesReportService(db_manager)
        
        # Initialize controller
        analytics_controller = AnalyticsController(analytics_service, sales_report_service)
        
        logger.info("Analytics Service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start Analytics Service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Analytics Service shutting down...")
    try:
        await close_db()
        logger.info("Analytics Service shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="Food Fast - Analytics Service",
    description="Microservice for analytics and reporting",
    version="1.0.0",
    lifespan=lifespan
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
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = await db_manager.health_check()
        
        status = "healthy" if db_healthy else "unhealthy"
        
        return {
            "status": status,
            "service": "analytics-service",
            "database": "connected" if db_healthy else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "analytics-service",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    port = settings.port
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
