# Legacy settings file - now using shared configuration
# This file is kept for backward compatibility

import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from core.config import get_service_settings

# Get standardized settings for API Gateway
settings = get_service_settings(
    "api_gateway",
    # Override specific defaults for API Gateway
    SECRET_KEY="api-gateway-secret-key-change-in-production",
    DATABASE_URL="sqlite+aiosqlite:///./api_gateway.db",  # Optional local DB for gateway
)

# Export commonly used settings for backward compatibility
HOST = settings.SERVICE_HOST
PORT = settings.SERVICE_PORT
AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
USER_SERVICE_URL = settings.USER_SERVICE_URL
PRODUCT_SERVICE_URL = settings.PRODUCT_SERVICE_URL
ORDER_SERVICE_URL = settings.ORDER_SERVICE_URL
PAYMENT_SERVICE_URL = settings.PAYMENT_SERVICE_URL
NOTIFICATION_SERVICE_URL = settings.NOTIFICATION_SERVICE_URL
ANALYTICS_SERVICE_URL = settings.ANALYTICS_SERVICE_URL
RATE_LIMIT_PER_MINUTE = settings.RATE_LIMIT_PER_MINUTE
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
REQUEST_TIMEOUT = settings.REQUEST_TIMEOUT
HEALTH_CHECK_TIMEOUT = settings.HEALTH_CHECK_TIMEOUT
