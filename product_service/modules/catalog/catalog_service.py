"""
Catalog Service for Product Management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from models.product import Product
from models.category import Category
from schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductListResponse,
)
from schemas.category import CategoryCreate, CategoryUpdate, CategoryRead


class CatalogService:
    """Service for managing products and categories"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Product methods
    async def create_product(self, product_data: ProductCreate) -> ProductRead:
        """Create a new product"""
        product = Product(**product_data.dict())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return ProductRead.from_orm(product)

    async def get_product(self, product_id: int) -> Optional[ProductRead]:
        """Get product by ID"""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        return ProductRead.from_orm(product) if product else None

    async def get_product_by_slug(self, slug: str) -> Optional[ProductRead]:
        """Get product by slug"""
        result = await self.db.execute(select(Product).where(Product.slug == slug))
        product = result.scalar_one_or_none()
        return ProductRead.from_orm(product) if product else None

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[ProductRead]:
        """Update product"""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            return None

        for field, value in product_data.dict(exclude_unset=True).items():
            if hasattr(product, field):
                setattr(product, field, value)

        await self.db.commit()
        await self.db.refresh(product)
        return ProductRead.from_orm(product)

    async def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            return False

        await self.db.delete(product)
        await self.db.commit()
        return True

    async def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_active: Optional[bool] = None,
    ) -> ProductListResponse:
        """List products with filters"""
        query = select(Product).options(selectinload(Product.category))

        # Apply filters
        conditions = []
        if category_id:
            conditions.append(Product.category_id == category_id)
        if search:
            conditions.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                )
            )
        if min_price is not None:
            conditions.append(Product.price >= min_price)
        if max_price is not None:
            conditions.append(Product.price <= max_price)
        if is_active is not None:
            conditions.append(Product.is_active == is_active)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(Product.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get products
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        products = result.scalars().all()

        return ProductListResponse(
            products=[ProductRead.from_orm(product) for product in products],
            total=total,
            skip=skip,
            limit=limit,
        )

    # Category methods
    async def create_category(self, category_data: CategoryCreate) -> CategoryRead:
        """Create a new category"""
        category = Category(**category_data.dict())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return CategoryRead.from_orm(category)

    async def get_category(self, category_id: int) -> Optional[CategoryRead]:
        """Get category by ID"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        return CategoryRead.from_orm(category) if category else None

    async def get_category_by_slug(self, slug: str) -> Optional[CategoryRead]:
        """Get category by slug"""
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        category = result.scalar_one_or_none()
        return CategoryRead.from_orm(category) if category else None

    async def update_category(
        self, category_id: int, category_data: CategoryUpdate
    ) -> Optional[CategoryRead]:
        """Update category"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            return None

        for field, value in category_data.dict(exclude_unset=True).items():
            if hasattr(category, field):
                setattr(category, field, value)

        await self.db.commit()
        await self.db.refresh(category)
        return CategoryRead.from_orm(category)

    async def delete_category(self, category_id: int) -> bool:
        """Delete category"""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            return False

        await self.db.delete(category)
        await self.db.commit()
        return True

    async def list_categories(
        self, parent_id: Optional[int] = None
    ) -> List[CategoryRead]:
        """List categories"""
        query = select(Category)
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)

        result = await self.db.execute(query)
        categories = result.scalars().all()
        return [CategoryRead.from_orm(category) for category in categories]
