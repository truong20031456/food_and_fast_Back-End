from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import asyncio
from typing import Dict, List
import logging
from contextlib import asynccontextmanager
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service registry
SERVICES = {
    "auth": "http://localhost:8001",
    "user": "http://localhost:8002", 
    "product": "http://localhost:8003",
    "order": "http://localhost:8004",
    "payment": "http://localhost:8005",
    "notification": "http://localhost:8006",
    "analytics": "http://localhost:8007"
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
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
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
        async with httpx.AsyncClient(timeout=5.0) as client:
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
        async with httpx.AsyncClient(timeout=30.0) as client:
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
async def logging_middleware(request: Request, call_next):
    """Logging middleware"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    client_ip = await get_client_ip(request)
    
    logger.info(
        f"{client_ip} - {request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.4f}s"
    )
    
    return response

@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": service_health_cache
    }

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
