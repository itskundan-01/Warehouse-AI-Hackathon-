"""
Application settings configuration for WarehouseVision AI.
Loads configuration from environment variables with sensible defaults.
"""
import os
import secrets
from functools import lru_cache
from typing import List, Optional, Dict, Any, Union

from pydantic import BaseModel, validator, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project settings
    PROJECT_NAME: str = "WarehouseVision AI"
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Security settings
    JWT_SECRET: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000"]
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    
    # Database settings
    DATABASE_URL: str = "mysql+pymysql://root:ImKundan@localhost:3306/warehouse_vision"
    DB_USER: str = "root"
    DB_PASSWORD: str = "ImKundan"
    DB_NAME: str = "warehouse_vision"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str = "secure_redis_password"
    
    # RabbitMQ settings
    RABBITMQ_URL: str = "amqp://warehouse_user:secure_rabbitmq_password@rabbitmq:5672/"
    RABBITMQ_USER: str = "warehouse_user"
    RABBITMQ_PASSWORD: str = "secure_rabbitmq_password"
    
    # ELK Stack settings
    ELASTIC_PASSWORD: str = "secure_elastic_password"
    
    # HashiCorp Vault settings
    VAULT_DEV_ROOT_TOKEN_ID: str = "dev_token_for_warehouse_vision"
    
    # Storage settings
    UPLOAD_DIR: str = "./data/uploads"
    MODEL_REGISTRY: str = "./data/models"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Feature flags
    ENABLE_FACIAL_RECOGNITION: bool = True
    ENABLE_VEHICLE_RECOGNITION: bool = True
    ENABLE_GUNNY_BAG_COUNTER: bool = True
    ENABLE_CONTEXTUAL_INTELLIGENCE: bool = True
    
    # Worker settings
    WORKER_CONCURRENCY: int = 2
    WORKERS_PER_CORE: str = "1"
    MAX_WORKERS: str = "4"
    WORKER_TIMEOUT: str = "120"
    
    class Config:
        """Pydantic config for Settings class."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in the settings


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings as a singleton.
    
    Returns:
        Settings: Application settings
    """
    return Settings()