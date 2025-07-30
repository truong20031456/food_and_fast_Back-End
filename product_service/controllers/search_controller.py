from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.product import ProductListResponse
from schemas.common import SearchQuery
from modules.catalog.catalog_service import CatalogService

router = APIRouter()


async def get_catalog_service(db: AsyncSession = Depends(get_db)) -> CatalogService:
    """Get CatalogService instance"""
    return CatalogService(db)


@router.get("/", response_model=ProductListResponse)
async def search_products(
    q: str = Query(..., description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    featured: Optional[bool] = Query(None, description="Filter featured products"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Search products"""
    return await catalog_service.list_products(
        limit=limit,
        offset=offset,
        search=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_featured=featured,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("/advanced", response_model=ProductListResponse)
async def advanced_search(
    search_query: SearchQuery,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Advanced product search"""
    return await catalog_service.list_products(
        limit=limit,
        offset=offset,
        search=search_query.q,
        category_id=search_query.category_id,
        min_price=search_query.min_price,
        max_price=search_query.max_price,
        is_featured=search_query.featured,
        sort_by=sort_by,
        sort_order=sort_order,
    )
