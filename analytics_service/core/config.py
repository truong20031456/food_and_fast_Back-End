"""
Configuration Management - Analytics Service.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="postgres", env="DB_USERNAME")
    password: str = Field(default="password", env="DB_PASSWORD")
    database: str = Field(default="analytics_db", env="DB_NAME")

    @property
    def connection_string(self) -> str:
        """Get database connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""

    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    database: int = Field(default=0, env="REDIS_DB")

    @property
    def connection_string(self) -> str:
        """Get Redis connection string."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"


class AnalyticsSettings(BaseSettings):
    """Analytics service specific settings."""

    data_retention_days: int = Field(default=365, env="ANALYTICS_DATA_RETENTION_DAYS")
    real_time_tracking: bool = Field(default=True, env="ANALYTICS_REAL_TIME_TRACKING")
    batch_processing_enabled: bool = Field(
        default=True, env="ANALYTICS_BATCH_PROCESSING"
    )
    export_formats: list = Field(
        default=["json", "csv", "excel"], env="ANALYTICS_EXPORT_FORMATS"
    )


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = Field(default="Analytics Service", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Service ports
    port: int = Field(default=8001, env="PORT")

    # External service URLs
    order_service_url: str = Field(
        default="http://localhost:8003", env="ORDER_SERVICE_URL"
    )
    product_service_url: str = Field(
        default="http://localhost:8002", env="PRODUCT_SERVICE_URL"
    )
    user_service_url: str = Field(
        default="http://localhost:8006", env="USER_SERVICE_URL"
    )

    # Database and Redis
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()

    # Analytics specific
    analytics: AnalyticsSettings = AnalyticsSettings()

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
