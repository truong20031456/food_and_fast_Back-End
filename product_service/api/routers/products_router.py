"""
Products Router - Consolidated router for products, categories, and inventory management.
"""

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
from schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRead,
    CategoryListResponse,
)
from schemas.inventory import (
    InventoryUpdate,
    InventoryRead,
    StockAlert,
)
from schemas.common import MessageResponse
from modules.catalog.catalog_service import CatalogService
from modules.inventory.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1", tags=["products"])


async def get_catalog_service(db: AsyncSession = Depends(get_db)) -> CatalogService:
    """Get CatalogService instance"""
    return CatalogService(db)


async def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    """Get InventoryService instance"""
    return InventoryService(db)


# =============================================================================
# PRODUCT ENDPOINTS
# =============================================================================

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Create a new product"""
    try:
        product = await catalog_service.create_product(product_data)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create product")


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Get products with filtering and pagination"""
    try:
        products = await catalog_service.get_products(
            page=page, size=size, category_id=category_id, search=search
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve products")


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Get a specific product by ID"""
    try:
        product = await catalog_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve product")


@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Update a product"""
    try:
        product = await catalog_service.update_product(product_id, product_data)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product")


@router.delete("/products/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Delete a product"""
    try:
        success = await catalog_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return MessageResponse(message="Product deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete product")


# =============================================================================
# CATEGORY ENDPOINTS  
# =============================================================================

@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Create a new category"""
    try:
        category = await catalog_service.create_category(category_data)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create category")


@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Get categories with pagination"""
    try:
        categories = await catalog_service.get_categories(page=page, size=size)
        return categories
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve categories")


@router.get("/categories/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Get a specific category by ID"""
    try:
        category = await catalog_service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve category")


@router.put("/categories/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Update a category"""
    try:
        category = await catalog_service.update_category(category_id, category_data)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update category")


@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),
):
    """Delete a category"""
    try:
        success = await catalog_service.delete_category(category_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return MessageResponse(message="Category deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete category")


# =============================================================================
# INVENTORY ENDPOINTS
# =============================================================================

@router.get("/products/{product_id}/inventory", response_model=InventoryRead)
async def get_product_inventory(
    product_id: int,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Get inventory for a specific product"""
    try:
        inventory = await inventory_service.get_inventory(product_id)
        if not inventory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
        return inventory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve inventory")


@router.put("/products/{product_id}/inventory", response_model=InventoryRead)
async def update_product_inventory(
    product_id: int,
    inventory_data: InventoryUpdate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Update inventory for a specific product"""
    try:
        inventory = await inventory_service.update_inventory(product_id, inventory_data)
        if not inventory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return inventory
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update inventory")


@router.get("/inventory/alerts")
async def get_stock_alerts(
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Get low stock alerts"""
    try:
        alerts = await inventory_service.get_low_stock_alerts()
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stock alerts")


@router.post("/inventory/bulk-update")
async def bulk_update_inventory(
    updates: list[dict],
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Bulk update inventory for multiple products"""
    try:
        results = await inventory_service.bulk_update_inventory(updates)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update inventory")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "product_service"}
