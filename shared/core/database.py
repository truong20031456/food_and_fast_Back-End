"""
Database connection and session management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
import logging

from .config import BaseServiceSettings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self, settings: BaseServiceSettings):
        self.settings = settings
        self.engine = None
        self.session_factory = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup async database engine"""
        engine_kwargs = {
            "echo": self.settings.DATABASE_ECHO,
            "pool_pre_ping": True,
        }
        
        # Use NullPool for SQLite (testing)
        if "sqlite" in self.settings.DATABASE_URL:
            engine_kwargs["poolclass"] = NullPool
        else:
            engine_kwargs.update({
                "pool_size": self.settings.DATABASE_POOL_SIZE,
                "max_overflow": self.settings.DATABASE_MAX_OVERFLOW,
                "pool_timeout": 30,
                "pool_recycle": 3600,
            })
        
        self.engine = create_async_engine(
            self.settings.DATABASE_URL,
            **engine_kwargs
        )
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        
        logger.info(f"Database engine created for {self.settings.SERVICE_NAME}")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_session_context(self) -> AsyncSession:
        """Get database session context manager"""
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
_db_manager: DatabaseManager = None


def init_database(settings: BaseServiceSettings) -> DatabaseManager:
    """Initialize database manager"""
    global _db_manager
    _db_manager = DatabaseManager(settings)
    return _db_manager


def get_database_manager() -> DatabaseManager:
    """Get current database manager"""
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session