# Legacy database configuration - now using shared database management
# This file is kept for backward compatibility

import sys
import os
from typing import AsyncGenerator
import logging

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from core.database import get_database_manager, get_db_session, init_database
from models.base import Base
from .config import settings

logger = logging.getLogger(__name__)

# Initialize database with auth service settings
try:
    db_manager = init_database(settings.base if hasattr(settings, 'base') else settings)
    engine = db_manager.engine
    SessionLocal = db_manager.session_factory
except RuntimeError:
    # Database might already be initialized
    db_manager = get_database_manager()
    engine = db_manager.engine
    SessionLocal = db_manager.session_factory

# Legacy function for backward compatibility
async def get_db() -> AsyncGenerator:
    """Legacy database session dependency"""
    async for session in get_db_session():
        yield session

# Legacy initialization function
async def init_db():
    """Initialize database tables asynchronously"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Legacy connection check function
async def check_db_connection():
    """Check database connection asynchronously"""
    try:
        async with engine.connect() as connection:
            await connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
