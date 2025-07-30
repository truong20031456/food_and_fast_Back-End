from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

from core.database import engine, Base, init_db, close_db
from core.config import settings
from controllers import (
    product_router,
    category_router,
    inventory_router,
    review_router,
    search_router,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    await init_db()
    logger.info("Product Service started successfully")
    yield
    # Close database connections
    await close_db()
    logger.info("Product Service shutting down...")


app = FastAPI(
    title="Product Service",
    description="FastAPI Product Service for Food & Fast E-Commerce",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])
app.include_router(search_router, prefix="/search", tags=["Search"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "product-service", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Product Service API", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
