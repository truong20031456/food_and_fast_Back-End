"""
Base configuration for all services
"""

import os
from typing import Optional, List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator, root_validator
from dotenv import load_dotenv
from enum import Enum

load_dotenv()


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseServiceSettings(BaseSettings):
    """Base settings for all services"""

    # Environment
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")

    # Service info
    SERVICE_NAME: str = Field(env="SERVICE_NAME")
    SERVICE_VERSION: str = Field(default="1.0.0", env="SERVICE_VERSION")
    SERVICE_HOST: str = Field(default="0.0.0.0", env="SERVICE_HOST")
    SERVICE_PORT: int = Field(env="SERVICE_PORT")

    # Database
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")

    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(
        env="JWT_SECRET_KEY"
    )  # Shared across all services for JWT validation
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        default=None, env="GOOGLE_CLIENT_SECRET"
    )
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default=None, env="GOOGLE_REDIRECT_URI")
    GOOGLE_AUTH_URL: str = Field(
        default="https://accounts.google.com/o/oauth2/v2/auth", env="GOOGLE_AUTH_URL"
    )
    GOOGLE_TOKEN_URL: str = Field(
        default="https://oauth2.googleapis.com/token", env="GOOGLE_TOKEN_URL"
    )
    GOOGLE_USERINFO_URL: str = Field(
        default="https://www.googleapis.com/oauth2/v2/userinfo",
        env="GOOGLE_USERINFO_URL",
    )

    # CORS - More secure defaults
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS",
    )
    ALLOWED_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="ALLOWED_METHODS"
    )
    ALLOWED_HEADERS: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")

    # Logging
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")

    # API Documentation
    API_TITLE: Optional[str] = None
    API_DESCRIPTION: Optional[str] = None
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    DOCS_URL: str = Field(default="/docs", env="DOCS_URL")
    REDOC_URL: str = Field(default="/redoc", env="REDOC_URL")
    OPENAPI_URL: str = Field(default="/openapi.json", env="OPENAPI_URL")

    # Health Check
    HEALTH_CHECK_PATH: str = Field(default="/health", env="HEALTH_CHECK_PATH")

    # Metrics
    METRICS_PATH: str = Field(default="/metrics", env="METRICS_PATH")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")

    # External Services (for API Gateway)
    AUTH_SERVICE_URL: Optional[str] = Field(default=None, env="AUTH_SERVICE_URL")
    USER_SERVICE_URL: Optional[str] = Field(default=None, env="USER_SERVICE_URL")
    PRODUCT_SERVICE_URL: Optional[str] = Field(default=None, env="PRODUCT_SERVICE_URL")
    ORDER_SERVICE_URL: Optional[str] = Field(default=None, env="ORDER_SERVICE_URL")
    PAYMENT_SERVICE_URL: Optional[str] = Field(default=None, env="PAYMENT_SERVICE_URL")
    NOTIFICATION_SERVICE_URL: Optional[str] = Field(
        default=None, env="NOTIFICATION_SERVICE_URL"
    )
    ANALYTICS_SERVICE_URL: Optional[str] = Field(
        default=None, env="ANALYTICS_SERVICE_URL"
    )

    # Timeouts
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_METHODS", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip().upper() for method in v.split(",")]
        return v

    @validator("ALLOWED_HEADERS", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @validator("DEBUG", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v

    @validator("SERVICE_PORT")
    def validate_port(cls, v):
        if not (1024 <= v <= 65535):
            raise ValueError("Port must be between 1024 and 65535")
        return v

    @validator("DATABASE_POOL_SIZE")
    def validate_pool_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Database pool size must be between 1 and 100")
        return v

    @validator("RATE_LIMIT_PER_MINUTE")
    def validate_rate_limit(cls, v):
        if v < 1 or v > 10000:
            raise ValueError("Rate limit must be between 1 and 10000")
        return v

    @root_validator
    def validate_security_settings(cls, values):
        """Validate security-related settings"""
        environment = values.get("ENVIRONMENT")

        # In production, ensure secure settings
        if environment == Environment.PRODUCTION:
            if values.get("DEBUG", False):
                raise ValueError("DEBUG must be False in production")

            if values.get("ALLOWED_ORIGINS") == ["*"]:
                raise ValueError("ALLOWED_ORIGINS cannot be ['*'] in production")

            if not values.get("SECRET_KEY") or len(values.get("SECRET_KEY", "")) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters in production"
                )

        return values

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == Environment.STAGING

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def service_url(self) -> str:
        return f"http://{self.SERVICE_HOST}:{self.SERVICE_PORT}"

    @property
    def secure_service_url(self) -> str:
        """Get HTTPS URL for production"""
        if self.is_production:
            return f"https://{self.SERVICE_HOST}:{self.SERVICE_PORT}"
        return self.service_url

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


def get_service_settings(service_name: str, **kwargs) -> BaseServiceSettings:
    """Factory function to create service-specific settings"""

    # Set service-specific defaults
    defaults = {
        "api_gateway": {
            "SERVICE_NAME": "API Gateway",
            "SERVICE_PORT": 8000,
            "API_TITLE": "Food & Fast API Gateway",
            "API_DESCRIPTION": "API Gateway for Food & Fast E-Commerce Platform",
        },
        "auth_service": {
            "SERVICE_NAME": "Auth Service",
            "SERVICE_PORT": 8001,
            "API_TITLE": "Authentication Service",
            "API_DESCRIPTION": "Authentication and authorization service",
        },
        "user_service": {
            "SERVICE_NAME": "User Service",
            "SERVICE_PORT": 8002,
            "API_TITLE": "User Management Service",
            "API_DESCRIPTION": "User profile and account management service",
        },
        "product_service": {
            "SERVICE_NAME": "Product Service",
            "SERVICE_PORT": 8003,
            "API_TITLE": "Product Catalog Service",
            "API_DESCRIPTION": "Product catalog, inventory, and search service",
        },
        "order_service": {
            "SERVICE_NAME": "Order Service",
            "SERVICE_PORT": 8004,
            "API_TITLE": "Order Management Service",
            "API_DESCRIPTION": "Order processing and cart management service",
        },
        "payment_service": {
            "SERVICE_NAME": "Payment Service",
            "SERVICE_PORT": 8005,
            "API_TITLE": "Payment Processing Service",
            "API_DESCRIPTION": "Payment processing and gateway integration service",
        },
        "notification_service": {
            "SERVICE_NAME": "Notification Service",
            "SERVICE_PORT": 8006,
            "API_TITLE": "Notification Service",
            "API_DESCRIPTION": "Email, SMS, and push notification service",
        },
        "analytics_service": {
            "SERVICE_NAME": "Analytics Service",
            "SERVICE_PORT": 8007,
            "API_TITLE": "Analytics Service",
            "API_DESCRIPTION": "Analytics and reporting service",
        },
    }

    service_defaults = defaults.get(service_name, {})
    service_defaults.update(kwargs)

    # Override environment variables with service defaults
    for key, value in service_defaults.items():
        if key not in os.environ:
            os.environ[key] = str(value)

    return BaseServiceSettings()
