# Import config to setup paths
from app import config

from shared_code.utils.logging import get_logger
from app.services.service_registry import service_registry

logger = get_logger(__name__)


async def startup_task():
    """Startup task to check service health"""
    logger.info("Checking service health on startup...")
    health_status = await service_registry.get_healthy_services()
    for service, is_healthy in health_status.items():
        status = "healthy" if is_healthy else "unhealthy"
        logger.info(f"Service {service}: {status}")
