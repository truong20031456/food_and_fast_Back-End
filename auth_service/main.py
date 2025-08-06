# Auth Service Main


from fastapi import FastAPI, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.app import create_app
from core.config import get_service_settings
from core.database import get_database_manager
from models.base import Base
from controllers import (
    auth_router,
    user_router,
    token_router,
    password_router,
    profile_router,
)

# Get service settings
settings = get_service_settings("auth_service")

# Import models to ensure they're registered
from models import user  # This ensures User model is registered


async def startup_task():
    """Create database tables on startup"""
    db_manager = get_database_manager()

    # Create tables
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Create the FastAPI app with standardized configuration
app = create_app(
    service_name="Auth Service",
    settings=settings,
    routers=[auth_router, user_router, token_router, password_router, profile_router],
    startup_tasks=[startup_task],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.SERVICE_HOST,
        port=settings.SERVICE_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.value.lower(),
    )
