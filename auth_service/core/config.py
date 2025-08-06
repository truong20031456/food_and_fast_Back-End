"""
Auth Service specific configuration
"""

import sys
import os

# Add path for shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from shared_code.core.config import BaseServiceSettings, get_service_settings


def get_auth_service_settings() -> BaseServiceSettings:
    """
    Get Auth Service specific settings

    Returns:
        Configured BaseServiceSettings for auth service
    """
    return get_service_settings("auth_service")


# Create global settings instance
settings = get_auth_service_settings()
