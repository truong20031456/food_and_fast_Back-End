from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
import httpx
import asyncio
from typing import Dict, List
import logging
from contextlib import asynccontextmanager
import time
import json
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.openmetrics.exposition import generate_latest as generate_latest_openmetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently in progress',
    ['method', 'endpoint']
)

SERVICE_HEALTH = Gauge(
    'service_health_status',
    'Health status of downstream services',
    ['service_name']
)

from config.settings import settings

# Service registry
SERVICES = {
    "auth": settings.AUTH_SERVICE_URL,
    "user": settings.USER_SERVICE_URL, 
    "product": settings.PRODUCT_SERVICE_URL,
    "order": settings.ORDER_SERVICE_URL,
    "payment": settings.PAYMENT_SERVICE_URL,
    "notification": settings.NOTIFICATION_SERVICE_URL,
    "analytics": settings.ANALYTICS_SERVICE_URL
}

# Route mappings
ROUTE_MAPPINGS = {
    "/auth": "auth",
    "/users": "user",
    "/products": "product",
    "/orders": "order",
    "/payments": "payment",
    "/notifications": "notification",
    "/analytics": "analytics"
}

# Health check cache
service_health_cache = {}
CACHE_DURATION = 30  # seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("API Gateway starting up...")
    await check_all_services_health()
    yield
    # Shutdown
    logger.info("API Gateway shutting down...")

app = FastAPI(
    title="Food & Fast API Gateway",
    description="API Gateway for Food & Fast E-Commerce Microservices",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

class RateLimiter:
    def __init__(self, requests_per_minute: int = None):
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.requests = {}
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [req_time for req_time in self.requests[client_ip] if req_time > minute_ago]
        else:
            self.requests[client_ip] = []
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()

async def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

async def check_service_health(service_name: str, service_url: str) -> bool:
    """Check if a service is healthy"""
    try:
        async with httpx.AsyncClient(timeout=settings.HEALTH_CHECK_TIMEOUT) as client:
            response = await client.get(f"{service_url}/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Health check failed for {service_name}: {e}")
        return False

async def check_all_services_health():
    """Check health of all services"""
    tasks = []
    for service_name, service_url in SERVICES.items():
        tasks.append(check_service_health(service_name, service_url))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for service_name, is_healthy in zip(SERVICES.keys(), results):
        service_health_cache[service_name] = {
            "healthy": is_healthy,
            "timestamp": time.time()
        }
        # Update Prometheus metrics
        SERVICE_HEALTH.labels(service_name=service_name).set(1 if is_healthy else 0)
        status = "healthy" if is_healthy else "unhealthy"
        logger.info(f"Service {service_name}: {status}")

async def get_service_url(path: str) -> str:
    """Get service URL for a given path"""
    for route_prefix, service_name in ROUTE_MAPPINGS.items():
        if path.startswith(route_prefix):
            if service_name in SERVICES:
                return SERVICES[service_name]
    raise HTTPException(status_code=404, detail="Service not found")

async def forward_request(request: Request, service_url: str) -> JSONResponse:
    """Forward request to appropriate service"""
    # Get request body
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
        except Exception:
            body = None
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    # Build target URL
    target_url = f"{service_url}{request.url.path}"
    if request.url.query:
        target_url += f"?{request.url.query}"
    
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except httpx.RequestError as e:
        logger.error(f"Request failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = await get_client_ip(request)
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    response = await call_next(request)
    return response

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Metrics and logging middleware"""
    start_time = time.time()
    
    # Increment active requests
    ACTIVE_REQUESTS.labels(method=request.method, endpoint=request.url.path).inc()
    
    try:
        response = await call_next(request)
        
        process_time = time.time() - start_time
        client_ip = await get_client_ip(request)
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(process_time)
        
        logger.info(
            f"{client_ip} - {request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.4f}s"
        )
        
        return response
    
    finally:
        # Decrement active requests
        ACTIVE_REQUESTS.labels(method=request.method, endpoint=request.url.path).dec()

@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": service_health_cache
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/services")
async def list_services():
    """List all available services"""
    return {
        "services": list(SERVICES.keys()),
        "routes": ROUTE_MAPPINGS
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(request: Request, path: str):
    """Proxy all requests to appropriate services"""
    try:
        service_url = await get_service_url(f"/{path}")
        return await forward_request(request, service_url)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
