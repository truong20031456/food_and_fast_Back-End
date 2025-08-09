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
<<<<<<< HEAD
from services.elasticsearch_analytics_service import es_analytics_service
from core.config import settings
from core.database import db_manager, init_db, close_db
from core.elasticsearch_client import es_client
from utils.logger import get_logger

# Setup logging
# setup_logging(level=settings.log_level)
=======
from core.database import init_db, close_db

>>>>>>> main
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
<<<<<<< HEAD
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

=======
        
>>>>>>> main
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
<<<<<<< HEAD
        # Close Elasticsearch connection
        if es_client.is_connected:
            await es_client.disconnect()
            logger.info("Elasticsearch disconnected")
        
        # Close database connection
=======
        # Close database connections
>>>>>>> main
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

<<<<<<< HEAD
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


=======
>>>>>>> main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=getattr(settings, 'SERVICE_HOST', '0.0.0.0'),
        port=getattr(settings, 'SERVICE_PORT', 8007),
        reload=getattr(settings, 'DEBUG', False),
        log_level=getattr(settings, 'LOG_LEVEL', 'info').lower(),
    )
