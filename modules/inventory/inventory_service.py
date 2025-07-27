from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from typing import Optional, List
from datetime import datetime, timezone

from models.inventory import Inventory
from models.product import Product
from schemas.inventory import InventoryCreate, InventoryUpdate, InventoryRead, InventoryAdjustment
from utils.logger import get_logger

logger = get_logger(__name__)


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inventory(self, inventory_data: InventoryCreate) -> Inventory:
        """Create inventory record for a product"""
        try:
            # Check if inventory already exists for this product
            existing_inventory = await self.get_inventory_by_product_id(inventory_data.product_id)
            if existing_inventory:
                raise ValueError(f"Inventory already exists for product {inventory_data.product_id}")

            # Verify product exists
            product = await self.get_product(inventory_data.product_id)
            if not product:
                raise ValueError(f"Product {inventory_data.product_id} not found")

            inventory = Inventory(**inventory_data.dict())
            self.db.add(inventory)
            await self.db.commit()
            await self.db.refresh(inventory)
            
            logger.info(f"Inventory created for product {inventory_data.product_id}")
            return inventory

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create inventory: {e}")
            raise

    async def get_inventory(self, inventory_id: int) -> Optional[Inventory]:
        """Get inventory by ID"""
        try:
            result = await self.db.execute(
                select(Inventory).where(Inventory.id == inventory_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get inventory: {e}")
            return None

    async def get_inventory_by_product_id(self, product_id: int) -> Optional[Inventory]:
        """Get inventory by product ID"""
        try:
            result = await self.db.execute(
                select(Inventory).where(Inventory.product_id == product_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get inventory by product ID: {e}")
            return None

    async def update_inventory(self, inventory_id: int, inventory_data: InventoryUpdate) -> Optional[Inventory]:
        """Update inventory"""
        try:
            inventory = await self.get_inventory(inventory_id)
            if not inventory:
                return None

            # Update fields
            update_data = inventory_data.dict(exclude_unset=True)
            if update_data:
                await self.db.execute(
                    update(Inventory)
                    .where(Inventory.id == inventory_id)
                    .values(**update_data, updated_at=datetime.now(timezone.utc))
                )
                await self.db.commit()
                await self.db.refresh(inventory)

            return inventory

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update inventory: {e}")
            return None

    async def adjust_inventory(self, product_id: int, adjustment: InventoryAdjustment) -> bool:
        """Adjust inventory quantity"""
        try:
            inventory = await self.get_inventory_by_product_id(product_id)
            if not inventory:
                # Create inventory if it doesn't exist
                inventory_data = InventoryCreate(
                    product_id=product_id,
                    quantity=max(0, adjustment.quantity_change),
                    reserved_quantity=0
                )
                await self.create_inventory(inventory_data)
                return True

            # Calculate new quantity
            new_quantity = inventory.quantity + adjustment.quantity_change
            if new_quantity < 0:
                raise ValueError(f"Insufficient stock. Current: {inventory.quantity}, Requested reduction: {abs(adjustment.quantity_change)}")

            # Update inventory
            await self.db.execute(
                update(Inventory)
                .where(Inventory.id == inventory.id)
                .values(
                    quantity=new_quantity,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()

            logger.info(f"Inventory adjusted for product {product_id}: {adjustment.quantity_change} ({adjustment.reason})")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to adjust inventory: {e}")
            raise

    async def reserve_inventory(self, product_id: int, quantity: int) -> bool:
        """Reserve inventory for order"""
        try:
            inventory = await self.get_inventory_by_product_id(product_id)
            if not inventory:
                raise ValueError(f"No inventory found for product {product_id}")

            if inventory.available_quantity < quantity:
                raise ValueError(f"Insufficient available stock. Available: {inventory.available_quantity}, Requested: {quantity}")

            # Update reserved quantity
            new_reserved = inventory.reserved_quantity + quantity
            await self.db.execute(
                update(Inventory)
                .where(Inventory.id == inventory.id)
                .values(
                    reserved_quantity=new_reserved,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()

            logger.info(f"Inventory reserved for product {product_id}: {quantity}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to reserve inventory: {e}")
            raise

    async def release_inventory(self, product_id: int, quantity: int) -> bool:
        """Release reserved inventory"""
        try:
            inventory = await self.get_inventory_by_product_id(product_id)
            if not inventory:
                raise ValueError(f"No inventory found for product {product_id}")

            if inventory.reserved_quantity < quantity:
                raise ValueError(f"Insufficient reserved stock. Reserved: {inventory.reserved_quantity}, Requested release: {quantity}")

            # Update reserved quantity
            new_reserved = inventory.reserved_quantity - quantity
            await self.db.execute(
                update(Inventory)
                .where(Inventory.id == inventory.id)
                .values(
                    reserved_quantity=new_reserved,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()

            logger.info(f"Inventory released for product {product_id}: {quantity}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to release inventory: {e}")
            raise

    async def consume_inventory(self, product_id: int, quantity: int) -> bool:
        """Consume inventory (reduce both quantity and reserved)"""
        try:
            inventory = await self.get_inventory_by_product_id(product_id)
            if not inventory:
                raise ValueError(f"No inventory found for product {product_id}")

            if inventory.reserved_quantity < quantity:
                raise ValueError(f"Insufficient reserved stock. Reserved: {inventory.reserved_quantity}, Requested: {quantity}")

            # Update both quantity and reserved quantity
            new_quantity = inventory.quantity - quantity
            new_reserved = inventory.reserved_quantity - quantity

            await self.db.execute(
                update(Inventory)
                .where(Inventory.id == inventory.id)
                .values(
                    quantity=new_quantity,
                    reserved_quantity=new_reserved,
                    updated_at=datetime.now(timezone.utc)
                )
            )
            await self.db.commit()

            logger.info(f"Inventory consumed for product {product_id}: {quantity}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to consume inventory: {e}")
            raise

    async def get_low_stock_products(self, limit: int = 50) -> List[Inventory]:
        """Get products with low stock"""
        try:
            result = await self.db.execute(
                select(Inventory)
                .where(Inventory.quantity <= Inventory.low_stock_threshold)
                .order_by(Inventory.quantity)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get low stock products: {e}")
            return []

    async def get_out_of_stock_products(self, limit: int = 50) -> List[Inventory]:
        """Get out of stock products"""
        try:
            result = await self.db.execute(
                select(Inventory)
                .where(Inventory.quantity == 0)
                .order_by(Inventory.updated_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get out of stock products: {e}")
            return []

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        try:
            result = await self.db.execute(
                select(Product).where(Product.id == product_id, Product.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get product: {e}")
            return None
