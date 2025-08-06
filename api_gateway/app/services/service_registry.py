# Import config to setup paths
from app import config

import asyncio
from typing import Dict, Optional
from datetime import datetime
import logging

from shared_code.utils.redis import get_redis_manager
from shared_code.utils.logging import get_logger
from app.config import settings
import httpx

logger = get_logger(__name__)


class ServiceRegistry:
    def __init__(self):
        self.services = {
            "auth": settings.AUTH_SERVICE_URL,
            "user": settings.USER_SERVICE_URL,
            "product": settings.PRODUCT_SERVICE_URL,
            "order": settings.ORDER_SERVICE_URL,
            "payment": settings.PAYMENT_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL,
            "analytics": settings.ANALYTICS_SERVICE_URL,
        }

        self.route_mappings = {
            "/auth": "auth",
            "/users": "user",
            "/products": "product",
            "/orders": "order",
            "/payments": "payment",
            "/notifications": "notification",
            "/analytics": "analytics",
        }

        # Pre-sort route mappings for faster lookup (longest first)
        self._sorted_route_mappings = sorted(
            self.route_mappings.items(), key=lambda x: len(x[0]), reverse=True
        )

        self.health_cache = {}
        self.cache_duration = 30  # seconds
        self.circuit_breakers = {}  # Track failed services

    def get_service_url(self, service_name: str) -> Optional[str]:
        return self.services.get(service_name)

    def get_service_by_path(self, path: str) -> Optional[str]:
        # Use pre-sorted mappings for faster lookup
        for route_prefix, service_name in self._sorted_route_mappings:
            if path.startswith(route_prefix):
                return self.get_service_url(service_name)
        return None

    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy with caching and circuit breaker"""
        cache_key = f"health:{service_name}"

        # Check cache first
        redis_manager = get_redis_manager()
        cached_health = await redis_manager.get(cache_key)
        if cached_health is not None:
            return cached_health

        # Circuit breaker: Skip health check if service has failed recently
        if service_name in self.circuit_breakers:
            last_failure = self.circuit_breakers[service_name]
            if (
                datetime.now() - last_failure
            ).total_seconds() < 60:  # 1 minute cooldown
                logger.debug(f"Circuit breaker open for {service_name}")
                await redis_manager.set(
                    cache_key, False, expire=10
                )  # Short cache for failed services
                return False

        # Check actual health
        service_url = self.get_service_url(service_name)
        if not service_url:
            return False

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(settings.HEALTH_CHECK_TIMEOUT, connect=2.0)
            ) as client:
                response = await client.get(f"{service_url}/health")
                is_healthy = response.status_code == 200

                if is_healthy:
                    # Reset circuit breaker on success
                    self.circuit_breakers.pop(service_name, None)
                    await redis_manager.set(cache_key, True, expire=self.cache_duration)
                else:
                    self.circuit_breakers[service_name] = datetime.now()
                    await redis_manager.set(cache_key, False, expire=10)

                return is_healthy

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            self.circuit_breakers[service_name] = datetime.now()
            await redis_manager.set(cache_key, False, expire=10)
            return False

    async def get_healthy_services(self) -> Dict[str, bool]:
        """Get health status of all services"""
        health_status = {}
        tasks = []

        for service_name in self.services.keys():
            tasks.append(self.check_service_health(service_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for service_name, is_healthy in zip(self.services.keys(), results):
            if isinstance(is_healthy, Exception):
                health_status[service_name] = False
            else:
                health_status[service_name] = is_healthy

        return health_status


service_registry = ServiceRegistry()
