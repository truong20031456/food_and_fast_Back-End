import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/payment_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test_secret_key")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    STRIPE_SECRET_KEY: str = os.getenv(
        "STRIPE_SECRET_KEY", "sk_test_your_stripe_test_key"
    )
    STRIPE_PUBLIC_KEY: str = os.getenv(
        "STRIPE_PUBLIC_KEY", "pk_test_your_stripe_test_key"
    )
    STRIPE_WEBHOOK_SECRET: str = os.getenv(
        "STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret"
    )
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "your_paypal_client_id")
    PAYPAL_CLIENT_SECRET: str = os.getenv(
        "PAYPAL_CLIENT_SECRET", "your_paypal_client_secret"
    )
    MOMO_PARTNER_CODE: str = os.getenv("MOMO_PARTNER_CODE", "your_momo_partner_code")
    MOMO_ACCESS_KEY: str = os.getenv("MOMO_ACCESS_KEY", "your_momo_access_key")
    MOMO_SECRET_KEY: str = os.getenv("MOMO_SECRET_KEY", "your_momo_secret_key")
    MOMO_ENDPOINT: str = os.getenv("MOMO_ENDPOINT", "https://test-payment.momo.vn")


settings = Settings()


def get_settings():
    return settings
