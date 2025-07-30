import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/order_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test_secret_key")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    PAYMENT_SERVICE_URL: str = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003")

settings = Settings() 