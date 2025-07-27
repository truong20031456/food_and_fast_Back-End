# Auth Service Main

from fastapi import FastAPI
from controllers import (
    auth_router,
    user_router,
    token_router,
    password_router,
    profile_router,
)
from core.database import engine, Base
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist (async)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Auth Service",
    description="FastAPI Authentication Service",
    version="1.0.0",
    lifespan=lifespan,
)

# Include all routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["User Management"])
app.include_router(token_router, prefix="/tokens", tags=["Token Management"])
app.include_router(password_router, prefix="/passwords", tags=["Password Management"])
app.include_router(profile_router, prefix="/profile", tags=["Profile Management"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "auth_service"}
