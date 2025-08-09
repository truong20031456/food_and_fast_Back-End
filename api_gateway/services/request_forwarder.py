# Import config to setup paths
from app import config

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import httpx

from shared_code.core.dependencies import CurrentUser
from shared_code.core.config import get_service_settings
from shared_code.utils.logging import get_logger

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

            # Handle different content types properly
            response_headers = dict(response.headers)
            content_type = response_headers.get("content-type", "")

            # Remove problematic headers that could cause issues
            response_headers.pop("content-length", None)
            response_headers.pop("transfer-encoding", None)

            # Handle JSON responses
            if "application/json" in content_type:
                try:
                    content = response.json()
                    return JSONResponse(
                        content=content,
                        status_code=response.status_code,
                        headers=response_headers,
                    )
                except Exception:
                    # Fallback to text if JSON parsing fails
                    from fastapi.responses import Response

                    return Response(
                        content=response.text,
                        status_code=response.status_code,
                        headers=response_headers,
                        media_type=content_type,
                    )

            # Handle binary/file responses (images, PDFs, etc.)
            elif any(
                binary_type in content_type
                for binary_type in [
                    "image/",
                    "application/pdf",
                    "application/octet-stream",
                    "video/",
                    "audio/",
                    "application/zip",
                ]
            ):
                from fastapi.responses import Response

                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=content_type,
                )

            # Handle text responses (HTML, XML, plain text, etc.)
            else:
                from fastapi.responses import Response

                return Response(
                    content=response.text,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=content_type or "text/plain",
                )

    except httpx.TimeoutException:
        logger.error(f"Request timeout for {target_url}")
        from app.models.responses import ErrorResponse
        from datetime import datetime

        raise HTTPException(
            status_code=504,
            detail=ErrorResponse(
                detail="Gateway timeout - service did not respond in time",
                error_code="GATEWAY_TIMEOUT",
                timestamp=datetime.utcnow(),
            ).dict(),
        )
    except httpx.ConnectError:
        logger.error(f"Connection failed for {target_url}")
        from app.models.responses import ErrorResponse
        from datetime import datetime

        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                detail="Service unavailable - connection failed",
                error_code="SERVICE_CONNECTION_FAILED",
                timestamp=datetime.utcnow(),
            ).dict(),
        )
    except httpx.RequestError as e:
        logger.error(f"Request failed for {target_url}: {e}")
        from app.models.responses import ErrorResponse
        from datetime import datetime

        raise HTTPException(
            status_code=503,
            detail=ErrorResponse(
                detail="Service unavailable",
                error_code="SERVICE_REQUEST_FAILED",
                timestamp=datetime.utcnow(),
            ).dict(),
        )
    except Exception as e:
        logger.error(f"Unexpected error forwarding to {target_url}: {e}")
        from app.models.responses import ErrorResponse
        from datetime import datetime

        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                detail="Internal server error",
                error_code="INTERNAL_SERVER_ERROR",
                timestamp=datetime.utcnow(),
            ).dict(),
        )
