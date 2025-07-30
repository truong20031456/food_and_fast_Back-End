from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductListResponse,
)
from schemas.common import MessageResponse
from modules.catalog.catalog_service import CatalogService

router = APIRouter()


async def get_catalog_service(db: AsyncSession = Depends(get_db)) -> CatalogService:
    """Get CatalogService instance"""
    return CatalogService(db)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Create a new product"""
    try:
        product = await catalog_service.create_product(product_data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int, catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Get product by ID"""
    product = await catalog_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/slug/{slug}", response_model=ProductRead)
async def get_product_by_slug(
    slug: str, catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Get product by slug"""
    product = await catalog_service.get_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Update product"""
    product = await catalog_service.update_product(product_id, product_data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int, catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Delete product"""
    success = await catalog_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.get("/", response_model=ProductListResponse)
async def list_products(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    is_featured: Optional[bool] = Query(None),
    is_published: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """List products with filters"""
    return await catalog_service.list_products(
        limit=limit,
        offset=offset,
        search=search,
        category_id=category_id,
        is_featured=is_featured,
        is_published=is_published,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
    )
