# Import config to setup paths
from app import config

from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from datetime import datetime

from app.services.service_registry import service_registry
from app.services.request_forwarder import forward_request
from app.schemas.responses import ErrorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google")
async def forward_google_login(request: Request):
    """Forward Google OAuth authentication to auth service"""
    try:
        auth_service_url = service_registry.get_service_url("auth")
        if not auth_service_url:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    detail="Authentication service unavailable",
                    error_code="AUTH_SERVICE_UNAVAILABLE",
                    timestamp=datetime.utcnow(),
                ).dict(),
            )

        # Check if auth service is healthy
        is_healthy = await service_registry.check_service_health("auth")
        if not is_healthy:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    detail="Authentication service is unhealthy",
                    error_code="AUTH_SERVICE_UNHEALTHY",
                    timestamp=datetime.utcnow(),
                ).dict(),
            )

        return await forward_request(request, auth_service_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail="Internal server error during authentication",
                error_code="AUTH_INTERNAL_ERROR",
                timestamp=datetime.utcnow(),
            ).dict(),
        )


@router.get("/google/auth-url")
async def forward_google_auth_url(request: Request):
    """Forward Google OAuth URL generation to auth service"""
    try:
        auth_service_url = service_registry.get_service_url("auth")
        if not auth_service_url:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    detail="Authentication service unavailable",
                    error_code="AUTH_SERVICE_UNAVAILABLE",
                    timestamp=datetime.utcnow(),
                ).dict(),
            )

        # Check if auth service is healthy
        is_healthy = await service_registry.check_service_health("auth")
        if not is_healthy:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    detail="Authentication service is unhealthy",
                    error_code="AUTH_SERVICE_UNHEALTHY",
                    timestamp=datetime.utcnow(),
                ).dict(),
            )

        return await forward_request(request, auth_service_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail="Internal server error during authentication",
                error_code="AUTH_INTERNAL_ERROR",
                timestamp=datetime.utcnow(),
            ).dict(),
        )


@router.post("/google/callback")
async def forward_google_callback(request: Request):
    """Forward Google OAuth callback to auth service"""
    try:
        auth_service_url = service_registry.get_service_url("auth")
        if not auth_service_url:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    detail="Authentication service unavailable",
                    error_code="AUTH_SERVICE_UNAVAILABLE",
                    timestamp=datetime.utcnow(),
                ).dict(),
            )

        # Check if auth service is healthy
        is_healthy = await service_registry.check_service_health("auth")
        if not is_healthy:
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    detail="Authentication service is unhealthy",
                    error_code="AUTH_SERVICE_UNHEALTHY",
                    timestamp=datetime.utcnow(),
                ).dict(),
            )

        return await forward_request(request, auth_service_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail="Internal server error during authentication",
                error_code="AUTH_INTERNAL_ERROR",
                timestamp=datetime.utcnow(),
            ).dict(),
        )
