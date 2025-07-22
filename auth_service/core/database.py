from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import logging

from .config import settings
from models.base import Base  # Import Base from models.base

logger = logging.getLogger(__name__)

# Async Database engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
)

# Async session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator:
    """
    Async database dependency for FastAPI
    """
    async with SessionLocal() as db:
        try:
            yield db
        except Exception as e:
            logger.error(f"Database error: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


async def init_db():
    """
    Initialize database tables asynchronously
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def check_db_connection():
    """
    Check database connection asynchronously
    """
    try:
        async with engine.connect() as connection:
            await connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
