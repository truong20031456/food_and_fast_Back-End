# Legacy configuration file - now using shared configuration
# This file is kept for backward compatibility

import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from core.config import get_service_settings

# Get standardized settings for Auth Service
settings = get_service_settings(
    "auth_service",
    # Auth service specific overrides
    SECRET_KEY=os.getenv("idi"),
    DATABASE_URL="postgresql+asyncpg://truong:truong123@localhost:5432/auth_service_db",
)
# Auth-specific settings (extend base settings)
class AuthSettings:
    def __init__(self, base_settings):
        self.base = base_settings
        
        # Auth-specific configurations
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
        
        # Email settings (optional)
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    
    def __getattr__(self, name):
        # Delegate to base settings if attribute not found
        return getattr(self.base, name)

# Create enhanced settings instance
settings = AuthSettings(get_service_settings("auth_service"))

# Export commonly used settings for backward compatibility
DATABASE_URL = settings.DATABASE_URL
DATABASE_ECHO = settings.DATABASE_ECHO
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
REDIS_URL = settings.REDIS_URL
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS 