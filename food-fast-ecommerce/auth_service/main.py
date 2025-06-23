# Auth Service Main

from fastapi import FastAPI
from controllers.auth_controller import router as auth_router
from core.database import engine, Base
import asyncio

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
async def on_startup():
    # Tạo tables nếu chưa có
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
