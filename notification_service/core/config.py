"""
Configuration Management - Notification Service.
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
    database: str = Field(default="notification_db", env="DB_NAME")

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


class EmailSettings(BaseSettings):
    """Email service configuration settings."""

    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: str = Field(default="", env="SMTP_USERNAME")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    from_email: str = Field(default="noreply@foodfast.com", env="FROM_EMAIL")
    from_name: str = Field(default="Food Fast", env="FROM_NAME")


class SMSSettings(BaseSettings):
    """SMS service configuration settings."""

    provider: str = Field(default="twilio", env="SMS_PROVIDER")
    account_sid: str = Field(default="", env="SMS_ACCOUNT_SID")
    auth_token: str = Field(default="", env="SMS_AUTH_TOKEN")
    from_number: str = Field(default="", env="SMS_FROM_NUMBER")


class NotificationSettings(BaseSettings):
    """Notification service specific settings."""

    max_retries: int = Field(default=3, env="NOTIFICATION_MAX_RETRIES")
    retry_delay: int = Field(default=300, env="NOTIFICATION_RETRY_DELAY")
    rate_limit: int = Field(default=100, env="NOTIFICATION_RATE_LIMIT")
    template_cache_ttl: int = Field(default=3600, env="NOTIFICATION_TEMPLATE_CACHE_TTL")
    batch_size: int = Field(default=50, env="NOTIFICATION_BATCH_SIZE")


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = Field(default="Notification Service", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Service ports
    port: int = Field(default=8005, env="PORT")

    # External service URLs
    user_service_url: str = Field(
        default="http://localhost:8006", env="USER_SERVICE_URL"
    )
    order_service_url: str = Field(
        default="http://localhost:8003", env="ORDER_SERVICE_URL"
    )

    # Database and Redis
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()

    # Email and SMS
    email: EmailSettings = EmailSettings()
    sms: SMSSettings = SMSSettings()

    # Notification specific
    notification: NotificationSettings = NotificationSettings()

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
