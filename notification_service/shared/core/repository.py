"""
Base repository pattern for database operations
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from abc import ABC, abstractmethod
import logging

from ..models.base import BaseDBModel, PaginatedResponse, PaginationParams

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseDBModel)


class BaseRepository(Generic[ModelType], ABC):
    """Base repository class with common CRUD operations"""

    def __init__(self, model: type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def create(self, **kwargs) -> ModelType:
        """Create a new instance"""
        instance = self.model(**kwargs)
        self.db_session.add(instance)
        await self.db_session.flush()
        await self.db_session.refresh(instance)
        return instance

    async def get_by_id(
        self, id: str, load_relations: List[str] = None
    ) -> Optional[ModelType]:
        """Get instance by ID"""
        query = select(self.model).where(self.model.id == id)

        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(getattr(self.model, relation)))

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_field(
        self, field_name: str, value: Any, load_relations: List[str] = None
    ) -> Optional[ModelType]:
        """Get instance by a specific field"""
        query = select(self.model).where(getattr(self.model, field_name) == value)

        if load_relations:
            for relation in load_relations:
                query = query.options(selectinload(getattr(self.model, relation)))

        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        filters: Dict[str, Any] = None,
        load_relations: List[str] = None,
        order_by: List[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ModelType]:
        """Get multiple instances with optional filtering and ordering"""
        query = select(self.model)

        # Apply filters
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            if conditions:
                query = query.where(and_(*conditions))

        # Apply relations loading
        if load_relations:
            for relation in load_relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

        # Apply ordering
        if order_by:
            order_clauses = []
            for order in order_by:
                if order.startswith("-"):
                    field_name = order[1:]
                    if hasattr(self.model, field_name):
                        order_clauses.append(getattr(self.model, field_name).desc())
                else:
                    if hasattr(self.model, order):
                        order_clauses.append(getattr(self.model, order))
            if order_clauses:
                query = query.order_by(*order_clauses)

        # Apply pagination
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.db_session.execute(query)
        return result.scalars().all()

    async def get_paginated(
        self,
        pagination: PaginationParams,
        filters: Dict[str, Any] = None,
        load_relations: List[str] = None,
        order_by: List[str] = None,
    ) -> PaginatedResponse:
        """Get paginated results"""
        # Count total records
        count_query = select(func.count(self.model.id))
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            if conditions:
                count_query = count_query.where(and_(*conditions))

        total_result = await self.db_session.execute(count_query)
        total = total_result.scalar()

        # Get paginated items
        items = await self.get_multi(
            filters=filters,
            load_relations=load_relations,
            order_by=order_by,
            limit=pagination.size,
            offset=pagination.offset,
        )

        return PaginatedResponse.create(
            items=items, total=total, page=pagination.page, size=pagination.size
        )

    async def update(self, id: str, **kwargs) -> Optional[ModelType]:
        """Update instance by ID"""
        # Remove None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if not update_data:
            return await self.get_by_id(id)

        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .returning(self.model)
        )

        result = await self.db_session.execute(query)
        updated_instance = result.scalar_one_or_none()

        if updated_instance:
            await self.db_session.refresh(updated_instance)

        return updated_instance

    async def delete(self, id: str) -> bool:
        """Delete instance by ID"""
        query = delete(self.model).where(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.rowcount > 0

    async def delete_multi(self, filters: Dict[str, Any]) -> int:
        """Delete multiple instances by filters"""
        query = delete(self.model)

        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db_session.execute(query)
        return result.rowcount

    async def exists(self, id: str) -> bool:
        """Check if instance exists by ID"""
        query = select(func.count(self.model.id)).where(self.model.id == id)
        result = await self.db_session.execute(query)
        return result.scalar() > 0

    async def exists_by_field(self, field_name: str, value: Any) -> bool:
        """Check if instance exists by field"""
        query = select(func.count(self.model.id)).where(
            getattr(self.model, field_name) == value
        )
        result = await self.db_session.execute(query)
        return result.scalar() > 0

    async def count(self, filters: Dict[str, Any] = None) -> int:
        """Count instances with optional filters"""
        query = select(func.count(self.model.id))

        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db_session.execute(query)
        return result.scalar()

    async def search(
        self,
        search_term: str,
        search_fields: List[str],
        filters: Dict[str, Any] = None,
        pagination: PaginationParams = None,
        load_relations: List[str] = None,
    ) -> List[ModelType] | PaginatedResponse:
        """Search instances by text in specified fields"""
        query = select(self.model)

        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model, field):
                search_conditions.append(
                    getattr(self.model, field).ilike(f"%{search_term}%")
                )

        if search_conditions:
            query = query.where(or_(*search_conditions))

        # Apply additional filters
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    if isinstance(value, list):
                        conditions.append(getattr(self.model, field).in_(value))
                    else:
                        conditions.append(getattr(self.model, field) == value)
            if conditions:
                query = query.where(and_(*conditions))

        # Apply relations loading
        if load_relations:
            for relation in load_relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

        # Return paginated or all results
        if pagination:
            # Count total for pagination
            count_query = select(func.count(self.model.id))
            if search_conditions:
                count_query = count_query.where(or_(*search_conditions))
            if filters:
                filter_conditions = []
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            filter_conditions.append(
                                getattr(self.model, field).in_(value)
                            )
                        else:
                            filter_conditions.append(
                                getattr(self.model, field) == value
                            )
                if filter_conditions:
                    count_query = count_query.where(and_(*filter_conditions))

            total_result = await self.db_session.execute(count_query)
            total = total_result.scalar()

            # Apply pagination to main query
            query = query.offset(pagination.offset).limit(pagination.size)

            result = await self.db_session.execute(query)
            items = result.scalars().all()

            return PaginatedResponse.create(
                items=items, total=total, page=pagination.page, size=pagination.size
            )
        else:
            result = await self.db_session.execute(query)
            return result.scalars().all()


class RepositoryManager:
    """Manager for repository instances"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._repositories = {}

    def get_repository(self, model_class: type[ModelType]) -> BaseRepository[ModelType]:
        """Get or create repository for a model"""
        model_name = model_class.__name__

        if model_name not in self._repositories:
            self._repositories[model_name] = BaseRepository(
                model_class, self.db_session
            )

        return self._repositories[model_name]


async def get_repository_manager(db_session: AsyncSession) -> RepositoryManager:
    """Dependency to get repository manager"""
    return RepositoryManager(db_session)
