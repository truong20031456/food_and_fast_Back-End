from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from schemas.inventory import InventoryCreate, InventoryUpdate, InventoryRead, InventoryAdjustment
from schemas.common import MessageResponse
from modules.inventory.inventory_service import InventoryService

router = APIRouter()


async def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    """Get InventoryService instance"""
    return InventoryService(db)


@router.post("/", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    inventory_data: InventoryCreate,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Create inventory record for a product"""
    try:
        inventory = await inventory_service.create_inventory(inventory_data)
        return inventory
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{inventory_id}", response_model=InventoryRead)
async def get_inventory(
    inventory_id: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Get inventory by ID"""
    inventory = await inventory_service.get_inventory(inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.get("/product/{product_id}", response_model=InventoryRead)
async def get_inventory_by_product(
    product_id: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Get inventory by product ID"""
    inventory = await inventory_service.get_inventory_by_product_id(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found for this product")
    return inventory


@router.put("/{inventory_id}", response_model=InventoryRead)
async def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Update inventory"""
    inventory = await inventory_service.update_inventory(inventory_id, inventory_data)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@router.post("/product/{product_id}/adjust", response_model=MessageResponse)
async def adjust_inventory(
    product_id: int,
    adjustment: InventoryAdjustment,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Adjust inventory quantity"""
    try:
        success = await inventory_service.adjust_inventory(product_id, adjustment)
        return {"message": f"Inventory adjusted successfully: {adjustment.quantity_change}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/product/{product_id}/reserve", response_model=MessageResponse)
async def reserve_inventory(
    product_id: int,
    quantity: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Reserve inventory for order"""
    try:
        success = await inventory_service.reserve_inventory(product_id, quantity)
        return {"message": f"Inventory reserved successfully: {quantity}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/product/{product_id}/release", response_model=MessageResponse)
async def release_inventory(
    product_id: int,
    quantity: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Release reserved inventory"""
    try:
        success = await inventory_service.release_inventory(product_id, quantity)
        return {"message": f"Inventory released successfully: {quantity}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/product/{product_id}/consume", response_model=MessageResponse)
async def consume_inventory(
    product_id: int,
    quantity: int,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Consume inventory (reduce both quantity and reserved)"""
    try:
        success = await inventory_service.consume_inventory(product_id, quantity)
        return {"message": f"Inventory consumed successfully: {quantity}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/low-stock/", response_model=list[InventoryRead])
async def get_low_stock_products(
    limit: int = 50,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Get products with low stock"""
    return await inventory_service.get_low_stock_products(limit)


@router.get("/out-of-stock/", response_model=list[InventoryRead])
async def get_out_of_stock_products(
    limit: int = 50,
    inventory_service: InventoryService = Depends(get_inventory_service)
):
    """Get out of stock products"""
    return await inventory_service.get_out_of_stock_products(limit) 