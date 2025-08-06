from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logger = logging.getLogger(__name__)

# Default database URL if no settings available
DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://localhost:5432/food_fast_db"
)


# Create engine with proper configuration
def create_database_engine(
    database_url: str = None,
    echo: bool = False,
    pool_size: int = 10,
    max_overflow: int = 20,
):
    """Create database engine with proper configuration"""
    url = database_url or DEFAULT_DATABASE_URL

    return create_async_engine(
        url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_timeout=30,  # Wait up to 30 seconds for a connection
    )


# Create default engine
engine = create_database_engine()
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)
Base = declarative_base()


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.session_local = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine, class_=AsyncSession
        )

    async def get_db(self):
        async with self.session_local() as session:
            yield session

    async def init_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        """Close database connections"""
        try:
            await self.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


db_manager = DatabaseManager(engine)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_database_manager(database_url: str = None, settings=None):
    """Get database manager with optional custom configuration"""
    if database_url or settings:
        # Create a new database manager with custom configuration
        if settings:
            custom_engine = create_database_engine(
                database_url=database_url or settings.DATABASE_URL,
                echo=settings.DATABASE_ECHO,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
            )
        else:
            custom_engine = create_database_engine(database_url)
        return DatabaseManager(custom_engine)
    return db_manager


async def get_db_session():
    async with SessionLocal() as session:
        yield session


async def test_database_connection() -> bool:
    """Test database connection"""
    try:
        async with SessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def close_database_connections():
    """Close database connections"""
    try:
        if hasattr(engine, "dispose"):
            engine.dispose()
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
