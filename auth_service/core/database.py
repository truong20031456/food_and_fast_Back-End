"""
Auth Service database configuration
"""

import sys
import os

# Add path for shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from shared_code.core.database import (
    DatabaseManager,
    init_database,
    get_database_manager,
    get_db_session,
)
from .config import settings


def init_auth_database() -> DatabaseManager:
    """
    Initialize auth service database

    Returns:
        DatabaseManager instance
    """
    return init_database(settings)


# Export commonly used functions
__all__ = [
    "DatabaseManager",
    "init_database",
    "get_database_manager",
    "get_db_session",
    "init_auth_database",
]
