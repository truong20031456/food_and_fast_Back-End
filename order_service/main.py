from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import os

from core.database import engine, get_db, Base
from controllers.cart_controller import router as cart_router
from controllers.order_controller import router as order_router

# Create tables only when running the application
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Order Service starting up...")
    yield
    # Shutdown
    print("Order Service shutting down...")


app = FastAPI(
    title="Food Fast - Order Service",
    description="Microservice for managing shopping carts and orders",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cart_router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["Orders"])


@app.get("/")
async def root():
    return {"message": "Food Fast Order Service", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8004)), reload=True
    )
