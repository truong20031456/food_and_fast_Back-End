import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/user_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "your-super-secret-jwt-key-here-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
    GOOGLE_CLIENT_SECRET: str = os.getenv(
        "GOOGLE_CLIENT_SECRET", "your-google-client-secret"
    )
    GOOGLE_REDIRECT_URI: str = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8002/users/google/callback"
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "your-super-secret-key-here-change-in-production"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")


settings = Settings()


def get_settings():
    return settings
