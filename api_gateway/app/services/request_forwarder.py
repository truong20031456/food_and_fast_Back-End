# Import config to setup paths
from app import config

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import httpx

from shared.core.dependencies import CurrentUser
from shared.core.config import get_service_settings
from shared.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_service_settings("api_gateway")


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


async def forward_request(
    request: Request, service_url: str, current_user: Optional[CurrentUser] = None
) -> JSONResponse:
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
    headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")
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
                method=request.method, url=target_url, headers=headers, content=body
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
                headers=response_headers,
            )

    except httpx.TimeoutException:
        logger.error(f"Request timeout for {target_url}")
        raise HTTPException(
            status_code=504, detail="Gateway timeout - service did not respond in time"
        )
    except httpx.ConnectError:
        logger.error(f"Connection failed for {target_url}")
        raise HTTPException(
            status_code=503, detail="Service unavailable - connection failed"
        )
    except httpx.RequestError as e:
        logger.error(f"Request failed for {target_url}: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error forwarding to {target_url}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
