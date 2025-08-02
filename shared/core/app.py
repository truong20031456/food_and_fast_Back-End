"""
FastAPI application factory with standard configuration
"""

from typing import List, Optional, Callable, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
import logging
from datetime import datetime

from .config import BaseServiceSettings
from .database import init_database, get_database_manager
from .exceptions import BaseServiceException, create_http_exception

try:
    from ..utils.redis import init_redis, get_redis_manager
    from ..utils.logging import setup_logging, log_request
    from ..models.base import HealthResponse
except ImportError:
    # Fall back to absolute imports for services
    from shared.utils.redis import init_redis, get_redis_manager
    from shared.utils.logging import setup_logging, log_request
    from shared.models.base import HealthResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and metrics"""

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
            },
        )

        try:
            response = await call_next(request)

            # Calculate request duration
            duration = time.time() - start_time

            # Log request completion
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration": duration,
                    "client_ip": request.client.host,
                },
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": duration,
                    "client_ip": request.client.host,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time
                for req_time in self.requests[client_ip]
                if req_time > minute_ago
            ]
        else:
            self.requests[client_ip] = []

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "message": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": 60,
                },
            )

        # Add current request
        self.requests[client_ip].append(now)

        return await call_next(request)


def create_app(
    service_name: str,
    settings: BaseServiceSettings,
    routers: Optional[List] = None,
    startup_tasks: Optional[List[Callable]] = None,
    shutdown_tasks: Optional[List[Callable]] = None,
    custom_openapi: Optional[Callable] = None,
) -> FastAPI:
    """
    Factory function to create FastAPI application with standard configuration

    Args:
        service_name: Name of the service
        settings: Service settings
        routers: List of router objects to include
        startup_tasks: List of startup tasks
        shutdown_tasks: List of shutdown tasks
        custom_openapi: Custom OpenAPI schema generator

    Returns:
        Configured FastAPI application
    """

    # Setup logging
    setup_logging(service_name, settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup tasks
        logger.info(f"Starting {service_name}...")

        try:
            # Initialize database
            init_database(settings)
            logger.info("Database initialized")

            # Initialize Redis
            init_redis(settings)
            redis_manager = get_redis_manager()
            if await redis_manager.ping():
                logger.info("Redis connected")
            else:
                logger.warning("Redis connection failed")

            # Run custom startup tasks
            if startup_tasks:
                for task in startup_tasks:
                    await task()

            logger.info(f"{service_name} startup completed")

        except Exception as e:
            logger.error(f"Startup failed: {e}", exc_info=True)
            raise

        yield

        # Shutdown tasks
        logger.info(f"Shutting down {service_name}...")

        try:
            # Run custom shutdown tasks
            if shutdown_tasks:
                for task in shutdown_tasks:
                    await task()

            # Close database connections
            db_manager = get_database_manager()
            await db_manager.close()

            # Close Redis connections
            redis_manager = get_redis_manager()
            await redis_manager.close()

            logger.info(f"{service_name} shutdown completed")

        except Exception as e:
            logger.error(f"Shutdown error: {e}", exc_info=True)

    # Create FastAPI app
    app = FastAPI(
        title=settings.API_TITLE or service_name,
        description=settings.API_DESCRIPTION or f"{service_name} API",
        version=settings.SERVICE_VERSION,
        docs_url=settings.DOCS_URL if not settings.is_production else None,
        redoc_url=settings.REDOC_URL if not settings.is_production else None,
        openapi_url=settings.OPENAPI_URL if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Add middleware

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # Configure based on settings
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE
    )

    # Exception handlers

    @app.exception_handler(BaseServiceException)
    async def service_exception_handler(request: Request, exc: BaseServiceException):
        return JSONResponse(
            status_code=500,
            content={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=422,
            content={
                "message": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "details": exc.errors(),
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={"request_id": getattr(request.state, "request_id", None)},
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    # Health check endpoint
    @app.get(settings.HEALTH_CHECK_PATH, response_model=HealthResponse, tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        # Check database
        db_healthy = True
        try:
            db_manager = get_database_manager()
            async with db_manager.get_session_context() as session:
                await session.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_healthy = False

        # Check Redis
        redis_healthy = True
        try:
            redis_manager = get_redis_manager()
            redis_healthy = await redis_manager.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_healthy = False

        # Determine overall health
        is_healthy = db_healthy and redis_healthy

        return HealthResponse(
            status="healthy" if is_healthy else "unhealthy",
            timestamp=datetime.utcnow(),
            service=service_name,
            version=settings.SERVICE_VERSION,
            dependencies={
                "database": "healthy" if db_healthy else "unhealthy",
                "redis": "healthy" if redis_healthy else "unhealthy",
            },
        )

    # Metrics endpoint (if enabled)
    if settings.ENABLE_METRICS:

        @app.get(settings.METRICS_PATH, tags=["Metrics"])
        async def metrics():
            """Prometheus metrics endpoint"""
            try:
                from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

                return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
            except ImportError:
                return JSONResponse(
                    status_code=501,
                    content={
                        "message": "Metrics not available - prometheus_client not installed"
                    },
                )

    # Include routers
    if routers:
        for router in routers:
            if hasattr(router, "prefix") and hasattr(router, "tags"):
                app.include_router(router, prefix=settings.API_PREFIX)
            else:
                app.include_router(router)

    # Custom OpenAPI schema
    if custom_openapi:
        app.openapi = lambda: custom_openapi(app)

    logger.info(f"{service_name} application created")
    return app


def create_custom_openapi(app: FastAPI, settings: BaseServiceSettings):
    """Create custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add custom info
    openapi_schema["info"]["x-service-name"] = settings.SERVICE_NAME
    openapi_schema["info"]["x-environment"] = settings.ENVIRONMENT.value

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema
