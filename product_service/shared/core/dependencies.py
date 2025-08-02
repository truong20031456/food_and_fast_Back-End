"""
Common dependency injection utilities
"""

from typing import AsyncGenerator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from datetime import datetime
import logging

from .config import BaseServiceSettings, get_service_settings
from .database import get_db_session
from .repository import RepositoryManager, get_repository_manager
from ..utils.redis import get_redis_client, RedisManager
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Security
security = HTTPBearer(auto_error=False)


class ServiceDependencies:
    """Container for service dependencies"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.settings = get_service_settings(service_name)

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async for session in get_db_session():
            yield session

    async def get_redis_client(self) -> RedisManager:
        """Get Redis client"""
        return await get_redis_client()

    async def get_repository_manager(
        self, db_session: AsyncSession = Depends(get_db_session)
    ) -> RepositoryManager:
        """Get repository manager"""
        return await get_repository_manager(db_session)


# Authentication dependencies


class CurrentUser:
    """Current authenticated user information"""

    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        roles: list = None,
        permissions: list = None,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.roles = roles or []
        self.permissions = permissions or []

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions

    def has_any_role(self, roles: list) -> bool:
        """Check if user has any of the specified roles"""
        return any(role in self.roles for role in roles)

    def has_any_permission(self, permissions: list) -> bool:
        """Check if user has any of the specified permissions"""
        return any(perm in self.permissions for perm in permissions)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    settings: BaseServiceSettings = Depends(lambda: get_service_settings("current")),
) -> Optional[CurrentUser]:
    """
    Get current authenticated user from JWT token
    Optional dependency - returns None if no valid token
    """
    if not credentials:
        return None

    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            return None

        # Extract user information
        user_id = payload.get("sub")
        username = payload.get("username")
        email = payload.get("email")
        roles = payload.get("roles", [])
        permissions = payload.get("permissions", [])

        if not user_id:
            return None

        return CurrentUser(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles,
            permissions=permissions,
        )

    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error decoding JWT token: {e}")
        return None


async def require_authentication(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    Require authenticated user
    Raises 401 if not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_roles(*required_roles: str):
    """
    Dependency factory to require specific roles
    """

    async def check_roles(
        current_user: CurrentUser = Depends(require_authentication),
    ) -> CurrentUser:
        if not current_user.has_any_role(list(required_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}",
            )
        return current_user

    return check_roles


def require_permissions(*required_permissions: str):
    """
    Dependency factory to require specific permissions
    """

    async def check_permissions(
        current_user: CurrentUser = Depends(require_authentication),
    ) -> CurrentUser:
        if not current_user.has_any_permission(list(required_permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of permissions: {', '.join(required_permissions)}",
            )
        return current_user

    return check_permissions


def require_owner_or_admin(user_id_field: str = "user_id"):
    """
    Dependency factory to require user to be owner of resource or admin
    """

    async def check_ownership(
        request: Request, current_user: CurrentUser = Depends(require_authentication)
    ) -> CurrentUser:
        # Check if user is admin
        if current_user.has_role("admin"):
            return current_user

        # Get user_id from path parameters
        path_params = request.path_params
        resource_user_id = path_params.get(user_id_field)

        if not resource_user_id:
            # Try to get from query parameters
            query_params = dict(request.query_params)
            resource_user_id = query_params.get(user_id_field)

        if resource_user_id and resource_user_id == current_user.user_id:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources",
        )

    return check_ownership


# Rate limiting dependencies


class RateLimiter:
    """Rate limiting dependency"""

    def __init__(self, requests_per_minute: int = 60, per_user: bool = False):
        self.requests_per_minute = requests_per_minute
        self.per_user = per_user

    async def __call__(
        self,
        request: Request,
        redis_client: RedisManager = Depends(get_redis_client),
        current_user: Optional[CurrentUser] = Depends(get_current_user),
    ):
        """Check rate limit"""
        # Determine rate limit key
        if self.per_user and current_user:
            rate_limit_key = f"rate_limit:user:{current_user.user_id}"
        else:
            client_ip = request.client.host
            rate_limit_key = f"rate_limit:ip:{client_ip}"

        # Get current count
        current_count = await redis_client.get(rate_limit_key) or 0

        if isinstance(current_count, str):
            current_count = int(current_count)

        # Check limit
        if current_count >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": "60"},
            )

        # Increment counter
        await redis_client.increment(rate_limit_key)

        # Set expiration if this is the first request
        if current_count == 0:
            await redis_client.expire(rate_limit_key, 60)


# Pagination dependencies


def get_pagination_params(
    page: int = 1, size: int = 10, max_size: int = 100
) -> Dict[str, int]:
    """Get pagination parameters with validation"""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be >= 1"
        )

    if size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Size must be >= 1"
        )

    if size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Size must be <= {max_size}",
        )

    return {"page": page, "size": size, "offset": (page - 1) * size}


# Search dependencies


def get_search_params(
    q: Optional[str] = None, sort_by: Optional[str] = None, sort_order: str = "asc"
) -> Dict[str, Any]:
    """Get search parameters"""
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_order must be 'asc' or 'desc'",
        )

    return {"query": q, "sort_by": sort_by, "sort_order": sort_order}


# Service health dependencies


async def check_service_health(
    db_session: AsyncSession = Depends(get_db_session),
    redis_client: RedisManager = Depends(get_redis_client),
) -> Dict[str, str]:
    """Check service health"""
    health_status = {"database": "unhealthy", "redis": "unhealthy"}

    # Check database
    try:
        await db_session.execute("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        if await redis_client.ping():
            health_status["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    return health_status


# Request context dependencies


def get_request_id(request: Request) -> str:
    """Get request ID from request state"""
    return getattr(request.state, "request_id", "unknown")


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


def get_user_agent(request: Request) -> str:
    """Get user agent from request headers"""
    return request.headers.get("User-Agent", "unknown")
