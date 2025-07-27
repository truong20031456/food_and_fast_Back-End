from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from models.product import Product
from models.category import Category
from models.product_image import ProductImage
from schemas.product import ProductCreate, ProductUpdate, ProductRead, ProductListResponse
from schemas.category import CategoryCreate, CategoryUpdate, CategoryRead, CategoryListResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class CatalogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Product methods
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        try:
            # Check if product with same SKU exists
            existing_product = await self.get_product_by_sku(product_data.sku)
            if existing_product:
                raise ValueError(f"Product with SKU {product_data.sku} already exists")

            # Check if product with same slug exists
            existing_slug = await self.get_product_by_slug(product_data.slug)
            if existing_slug:
                raise ValueError(f"Product with slug {product_data.slug} already exists")

            # Create product
            product = Product(**product_data.dict())
            self.db.add(product)
            await self.db.commit()
            await self.db.refresh(product)
            
            logger.info(f"Product created successfully: {product.name}")
            return product

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create product: {e}")
            raise

    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        try:
            result = await self.db.execute(
                select(Product)
                .options(selectinload(Product.images))
                .where(Product.id == product_id, Product.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get product: {e}")
            return None

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        try:
            result = await self.db.execute(
                select(Product).where(Product.sku == sku, Product.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get product by SKU: {e}")
            return None

    async def get_product_by_slug(self, slug: str) -> Optional[Product]:
        """Get product by slug"""
        try:
            result = await self.db.execute(
                select(Product)
                .options(selectinload(Product.images))
                .where(Product.slug == slug, Product.is_deleted == False)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get product by slug: {e}")
            return None

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        try:
            product = await self.get_product(product_id)
            if not product:
                return None

            # Update fields
            update_data = product_data.dict(exclude_unset=True)
            if update_data:
                await self.db.execute(
                    update(Product)
                    .where(Product.id == product_id)
                    .values(**update_data, updated_at=datetime.now(timezone.utc))
                )
                await self.db.commit()
                await self.db.refresh(product)

            return product

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update product: {e}")
            return None

    async def delete_product(self, product_id: int) -> bool:
        """Soft delete product"""
        try:
            result = await self.db.execute(
                update(Product)
                .where(Product.id == product_id)
                .values(is_deleted=True, updated_at=datetime.now(timezone.utc))
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete product: {e}")
            return False

    async def list_products(
        self,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_featured: Optional[bool] = None,
        is_published: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> ProductListResponse:
        """List products with filters"""
        try:
            # Build query
            query = select(Product).where(Product.is_deleted == False)
            
            # Add filters
            if search:
                search_filter = or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
                query = query.where(search_filter)
            
            if category_id:
                query = query.where(Product.category_id == category_id)
            
            if is_featured is not None:
                query = query.where(Product.is_featured == is_featured)
            
            if is_published is not None:
                query = query.where(Product.is_published == is_published)
            
            if min_price is not None:
                query = query.where(Product.price >= min_price)
            
            if max_price is not None:
                query = query.where(Product.price <= max_price)

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Add sorting and pagination
            if hasattr(Product, sort_by):
                sort_column = getattr(Product, sort_by)
                if sort_order == "desc":
                    sort_column = sort_column.desc()
                query = query.order_by(sort_column)
            
            query = query.offset(offset).limit(limit)
            query = query.options(selectinload(Product.images))

            # Execute query
            result = await self.db.execute(query)
            products = result.scalars().all()

            # Calculate pagination
            pages = (total + limit - 1) // limit
            page = (offset // limit) + 1

            return ProductListResponse(
                total=total,
                page=page,
                size=limit,
                pages=pages,
                products=products
            )

        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            return ProductListResponse(total=0, page=1, size=limit, pages=0, products=[])

    # Category methods
    async def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        try:
            # Check if category with same slug exists
            existing_category = await self.get_category_by_slug(category_data.slug)
            if existing_category:
                raise ValueError(f"Category with slug {category_data.slug} already exists")

            category = Category(**category_data.dict())
            self.db.add(category)
            await self.db.commit()
            await self.db.refresh(category)
            
            logger.info(f"Category created successfully: {category.name}")
            return category

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create category: {e}")
            raise

    async def get_category(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        try:
            result = await self.db.execute(
                select(Category)
                .options(selectinload(Category.children))
                .where(Category.id == category_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get category: {e}")
            return None

    async def get_category_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug"""
        try:
            result = await self.db.execute(
                select(Category).where(Category.slug == slug)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get category by slug: {e}")
            return None

    async def list_categories(self, parent_id: Optional[int] = None) -> CategoryListResponse:
        """List categories"""
        try:
            query = select(Category)
            
            if parent_id is not None:
                query = query.where(Category.parent_id == parent_id)
            else:
                query = query.where(Category.parent_id.is_(None))
            
            query = query.order_by(Category.sort_order, Category.name)
            query = query.options(selectinload(Category.children))

            result = await self.db.execute(query)
            categories = result.scalars().all()

            return CategoryListResponse(
                total=len(categories),
                categories=categories
            )

        except Exception as e:
            logger.error(f"Failed to list categories: {e}")
            return CategoryListResponse(total=0, categories=[])

    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Update category"""
        try:
            category = await self.get_category(category_id)
            if not category:
                return None

            # Update fields
            update_data = category_data.dict(exclude_unset=True)
            if update_data:
                await self.db.execute(
                    update(Category)
                    .where(Category.id == category_id)
                    .values(**update_data, updated_at=datetime.now(timezone.utc))
                )
                await self.db.commit()
                await self.db.refresh(category)

            return category

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update category: {e}")
            return None

    async def delete_category(self, category_id: int) -> bool:
        """Soft delete category"""
        try:
            result = await self.db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(is_deleted=True, updated_at=datetime.now(timezone.utc))
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete category: {e}")
            return False
