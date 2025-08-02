"""
Shared core modules
"""
from .database import get_database_manager, get_db_session, init_database
from .config import get_service_settings