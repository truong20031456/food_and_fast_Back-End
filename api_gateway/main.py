import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from fastapi import FastAPI, Request, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
import httpx
import asyncio
from typing import Dict, List, Optional
import logging
from datetime import datetime

from core.app import create_app
from core.config import get_service_settings
from core.dependencies import get_current_user, CurrentUser
from utils.logging import get_logger
from utils.redis import get_redis_manager

logger = get_logger(__name__)
settings = get_service_settings("api_gateway")

# Service registry with health caching
class ServiceRegistry:
    def __init__(self):
        self.services = {
            "auth": settings.AUTH_SERVICE_URL,
            "user": settings.USER_SERVICE_URL,
            "product": settings.PRODUCT_SERVICE_URL,
            "order": settings.ORDER_SERVICE_URL,
            "payment": settings.PAYMENT_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL,
            "analytics": settings.ANALYTICS_SERVICE_URL
        }
        
        self.route_mappings = {
            "/auth": "auth",
            "/users": "user",
            "/products": "product",
            "/orders": "order",
            "/payments": "payment",
            "/notifications": "notification",
            "/analytics": "analytics"
        }
        
        self.health_cache = {}
        self.cache_duration = 30  # seconds
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        return self.services.get(service_name)
    
    def get_service_by_path(self, path: str) -> Optional[str]:
        for route_prefix, service_name in self.route_mappings.items():
            if path.startswith(route_prefix):
                return self.get_service_url(service_name)
        return None
    
    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy with caching"""
        cache_key = f"health:{service_name}"
        
        # Check cache first
        redis_manager = get_redis_manager()
        cached_health = await redis_manager.get(cache_key)
        if cached_health is not None:
            return cached_health
        
        # Check actual health
        service_url = self.get_service_url(service_name)
        if not service_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=settings.HEALTH_CHECK_TIMEOUT) as client:
                response = await client.get(f"{service_url}/health")
                is_healthy = response.status_code == 200
                
                # Cache result
                await redis_manager.set(cache_key, is_healthy, expire=self.cache_duration)
                return is_healthy
                
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            await redis_manager.set(cache_key, False, expire=self.cache_duration)
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

async def startup_task():
    """Startup task to check service health"""
    logger.info("Checking service health on startup...")
    health_status = await service_registry.get_healthy_services()
    for service, is_healthy in health_status.items():
        status = "healthy" if is_healthy else "unhealthy"
        logger.info(f"Service {service}: {status}")

# Create router for gateway-specific endpoints
gateway_router = APIRouter(tags=["Gateway"])



def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


async def get_service_url_for_path(path: str) -> str:
    """Get service URL for a given path"""
    service_url = service_registry.get_service_by_path(path)
    if not service_url:
        raise HTTPException(status_code=404, detail="Service not found")
    return service_url

async def forward_request(request: Request, service_url: str, current_user: Optional[CurrentUser] = None) -> JSONResponse:
    """Forward request to appropriate service with enhanced error handling"""
    # Get request body
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
        except Exception as e:
            logger.warning(f"Failed to read request body: {e}")
            body = None
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    headers.pop("content-length", None)  # Let httpx handle this
    
    # Add request context headers
    headers["X-Request-ID"] = getattr(request.state, 'request_id', 'unknown')
    headers["X-Client-IP"] = get_client_ip(request)
    
    # Add user context if authenticated
    if current_user:
        headers["X-User-ID"] = current_user.user_id
        headers["X-User-Roles"] = ",".join(current_user.roles)
    
    # Build target URL
    target_url = f"{service_url}{request.url.path}"
    if request.url.query:
        target_url += f"?{request.url.query}"
    
    logger.debug(f"Forwarding {request.method} {target_url}")
    
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.REQUEST_TIMEOUT, connect=5.0)
        ) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body
            )
            
            # Handle different content types
            response_headers = dict(response.headers)
            content_type = response_headers.get("content-type", "")
            
            if "application/json" in content_type:
                try:
                    content = response.json()
                except Exception:
                    content = response.text
            else:
                content = response.text
            
            return JSONResponse(
                content=content,
                status_code=response.status_code,
                headers=response_headers
            )
            
    except httpx.TimeoutException:
        logger.error(f"Request timeout for {target_url}")
        raise HTTPException(
            status_code=504,
            detail="Gateway timeout - service did not respond in time"
        )
    except httpx.ConnectError:
        logger.error(f"Connection failed for {target_url}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - connection failed"
        )
    except httpx.RequestError as e:
        logger.error(f"Request failed for {target_url}: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error forwarding to {target_url}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@gateway_router.get("/services/health")
async def services_health_check():
    """Check health of all downstream services"""
    health_status = await service_registry.get_healthy_services()
    overall_healthy = all(health_status.values())
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": health_status
    }


@gateway_router.get("/services")
async def list_services():
    """List all available services and their routes"""
    return {
        "services": list(service_registry.services.keys()),
        "routes": service_registry.route_mappings,
        "urls": service_registry.services
    }

@gateway_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    request: Request, 
    path: str,
    current_user: Optional[CurrentUser] = Depends(get_current_user)
):
    """Proxy all requests to appropriate services"""
    try:
        service_url = await get_service_url_for_path(f"/{path}")
        return await forward_request(request, service_url, current_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Proxy error for path /{path}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="API Gateway",
    settings=settings,
    routers=[gateway_router],
    startup_tasks=[startup_task]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.value.lower()
    )
