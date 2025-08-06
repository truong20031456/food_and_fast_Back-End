import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8002, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/user_service_db",
        env="DATABASE_URL",
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")

    # JWT
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-here", env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # Google OAuth (Optional)
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        default=None, env="GOOGLE_CLIENT_SECRET"
    )
    GOOGLE_REDIRECT_URI: Optional[str] = Field(default=None, env="GOOGLE_REDIRECT_URI")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")

    # CORS
    ALLOWED_ORIGINS: str = Field(default="*", env="ALLOWED_ORIGINS")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()

# Export commonly used settings for backward compatibility
DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
