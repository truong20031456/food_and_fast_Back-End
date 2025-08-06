"""
Auth Service Core Module
"""

from .app import create_auth_app
from .config import settings, get_auth_service_settings
from .database import (
    init_auth_database,
    get_database_manager,
    get_db_session,
)
from .dependencies import (
    get_db,
    get_user_service,
    get_token_service,
    get_audit_service,
    get_cache_service,
    get_current_user,
    oauth2_scheme,
)

__all__ = [
    "create_auth_app",
    "settings",
    "get_auth_service_settings",
    "init_auth_database",
    "get_database_manager",
    "get_db_session",
    "get_db",
    "get_user_service",
    "get_token_service",
    "get_audit_service",
    "get_cache_service",
    "get_current_user",
    "oauth2_scheme",
]
