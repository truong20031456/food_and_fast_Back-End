"""
Database Management - Analytics Service.
"""
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database.connection_string.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()


class DatabaseManager:
    """Database manager for analytics service."""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()
    
    async def execute_query(self, query: str, params: dict = None):
        """Execute a raw SQL query."""
        async with self.get_session() as session:
            result = await session.execute(query, params or {})
            return result.fetchall()
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager()