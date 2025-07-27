import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # API Gateway settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Service URLs
    AUTH_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        env="AUTH_SERVICE_URL"
    )
    USER_SERVICE_URL: str = Field(
        default="http://localhost:8002",
        env="USER_SERVICE_URL"
    )
    PRODUCT_SERVICE_URL: str = Field(
        default="http://localhost:8003",
        env="PRODUCT_SERVICE_URL"
    )
    ORDER_SERVICE_URL: str = Field(
        default="http://localhost:8004",
        env="ORDER_SERVICE_URL"
    )
    PAYMENT_SERVICE_URL: str = Field(
        default="http://localhost:8005",
        env="PAYMENT_SERVICE_URL"
    )
    NOTIFICATION_SERVICE_URL: str = Field(
        default="http://localhost:8006",
        env="NOTIFICATION_SERVICE_URL"
    )
    ANALYTICS_SERVICE_URL: str = Field(
        default="http://localhost:8007",
        env="ANALYTICS_SERVICE_URL"
    )
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Security
    TRUSTED_HOSTS: List[str] = Field(default=["*"], env="TRUSTED_HOSTS")
    
    # Timeout settings
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    HEALTH_CHECK_TIMEOUT: int = Field(default=5, env="HEALTH_CHECK_TIMEOUT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from environment


settings = Settings()
