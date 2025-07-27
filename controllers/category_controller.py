from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.database import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryRead, CategoryListResponse
from schemas.common import MessageResponse
from modules.catalog.catalog_service import CatalogService

router = APIRouter()


async def get_catalog_service(db: AsyncSession = Depends(get_db)) -> CatalogService:
    """Get CatalogService instance"""
    return CatalogService(db)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Create a new category"""
    try:
        category = await catalog_service.create_category(category_data)
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Get category by ID"""
    category = await catalog_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/slug/{slug}", response_model=CategoryRead)
async def get_category_by_slug(
    slug: str,
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Get category by slug"""
    category = await catalog_service.get_category_by_slug(slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Update category"""
    category = await catalog_service.update_category(category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """Delete category"""
    success = await catalog_service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}


@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    parent_id: Optional[int] = Query(None),
    catalog_service: CatalogService = Depends(get_catalog_service)
):
    """List categories"""
    return await catalog_service.list_categories(parent_id=parent_id) 