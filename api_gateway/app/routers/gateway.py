# Import config to setup paths
from app import config

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime

from shared.core.dependencies import get_current_user, CurrentUser
from app.services.service_registry import service_registry
from app.services.request_forwarder import forward_request


router = APIRouter(tags=["Gateway"])


@router.get("/services/health")
async def services_health_check():
    """Check health of all downstream services"""
    health_status = await service_registry.get_healthy_services()
    overall_healthy = all(health_status.values())

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": health_status,
    }


@router.get("/services")
async def list_services():
    """List all available services and their routes"""
    return {
        "services": list(service_registry.services.keys()),
        "routes": service_registry.route_mappings,
        "urls": service_registry.services,
    }


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(
    request: Request,
    path: str,
    current_user: Optional[CurrentUser] = Depends(get_current_user),
):
    """Proxy all requests to appropriate services"""
    try:
        service_url = service_registry.get_service_by_path(f"/{path}")
        if not service_url:
            raise HTTPException(status_code=404, detail="Service not found")

        return await forward_request(request, service_url, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
