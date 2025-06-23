# Auth Service Main

from fastapi import FastAPI
from controllers.auth_controller import router as auth_router
from core.database import engine, Base
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tạo tables nếu chưa có
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
