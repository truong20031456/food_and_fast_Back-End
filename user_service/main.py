from fastapi import FastAPI
from app.controllers.user_router import router as user_router

app = FastAPI(title="User Service")

app.include_router(user_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "user_service"}
