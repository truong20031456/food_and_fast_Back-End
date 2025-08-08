"""
Configuration Management - Analytics Service.
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="postgres", env="DB_USERNAME")
    password: str = Field(default="password", env="DB_PASSWORD")
    database: str = Field(default="analytics_db", env="DB_NAME")

    model_config = {"env_file": ".env", "extra": "ignore"}

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

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def connection_string(self) -> str:
        """Get Redis connection string."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"redis://{self.host}:{self.port}/{self.database}"


class ElasticsearchSettings(BaseSettings):
    """Elasticsearch configuration settings."""

    host: str = Field(default="localhost", alias="ELASTICSEARCH_HOST")
    port: int = Field(default=9200, alias="ELASTICSEARCH_PORT")
    username: Optional[str] = Field(default=None, alias="ELASTICSEARCH_USERNAME")
    password: Optional[str] = Field(default=None, alias="ELASTICSEARCH_PASSWORD")
    api_key: Optional[str] = Field(default=None, alias="ELASTICSEARCH_API_KEY")
    scheme: str = Field(default="http", alias="ELASTICSEARCH_SCHEME")
    verify_certs: bool = Field(default=False, alias="ELASTICSEARCH_VERIFY_CERTS")
    ca_certs: Optional[str] = Field(default=None, alias="ELASTICSEARCH_CA_CERTS")
    
    # Index settings
    analytics_index: str = Field(default="analytics", alias="ELASTICSEARCH_ANALYTICS_INDEX")
    order_index: str = Field(default="orders", alias="ELASTICSEARCH_ORDER_INDEX")
    user_activity_index: str = Field(default="user_activity", alias="ELASTICSEARCH_USER_ACTIVITY_INDEX")
    product_index: str = Field(default="products", alias="ELASTICSEARCH_PRODUCT_INDEX")

    model_config = {
        "env_file": ".env", 
        "extra": "ignore",
        "populate_by_name": True
    }

    @property
    def hosts(self) -> List[Dict[str, Any]]:
        """Get Elasticsearch hosts configuration."""
        host_config = {
            'host': self.host,
            'port': self.port,
            'scheme': self.scheme,
        }
        
        # Priority: API Key > Username/Password
        if self.api_key:
            # API Key authentication will be handled in the client
            pass
        elif self.username and self.password:
            host_config['http_auth'] = (self.username, self.password)
            
        return [host_config]

    @property
    def client_config(self) -> Dict[str, Any]:
        """Get additional client configuration."""
        config = {
            'hosts': self.hosts,
            'verify_certs': self.verify_certs,
            'request_timeout': 30,
            'retry_on_timeout': True,
            'max_retries': 3,
        }
        
        # Add API Key if provided
        if self.api_key:
            config['api_key'] = self.api_key
        
        # Add CA certificates if provided
        if self.ca_certs:
            config['ca_certs'] = self.ca_certs
            
        return config


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

    model_config = {"env_file": ".env", "extra": "ignore"}


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
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()

    # Analytics specific
    analytics: AnalyticsSettings = AnalyticsSettings()

    model_config = {"case_sensitive": False, "extra": "ignore", "env_file": ".env"}


# Global settings instance
settings = Settings()
