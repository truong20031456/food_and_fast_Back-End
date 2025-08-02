from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google")
async def forward_google_login(request: Request):
    """Forward Google OAuth authentication to auth service"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post("http://auth_service:8001/auth/google", json=body)
    return JSONResponse(status_code=response.status_code, content=response.json())


@router.get("/google/auth-url")
async def forward_google_auth_url(request: Request):
    """Forward Google OAuth URL generation to auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://auth_service:8001/auth/google/auth-url",
            params=dict(request.query_params),
        )
    return JSONResponse(status_code=response.status_code, content=response.json())


@router.post("/google/callback")
async def forward_google_callback(request: Request):
    """Forward Google OAuth callback to auth service"""
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth_service:8001/auth/google/callback", json=body
        )
    return JSONResponse(status_code=response.status_code, content=response.json())
