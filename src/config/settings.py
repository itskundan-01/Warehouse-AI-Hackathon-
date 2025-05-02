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
    
    # Database settings
    DATABASE_URL: str = "mysql+pymysql://root:ImKundan@localhost:3306/warehouse_vision"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
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
    
    # Advanced settings
    WORKER_CONCURRENCY: int = 2
    
    class Config:
        """Pydantic config for Settings class."""
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings as a singleton.
    
    Returns:
        Settings: Application settings
    """
    return Settings()