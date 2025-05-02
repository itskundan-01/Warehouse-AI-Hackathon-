"""
Database connection setup for WarehouseVision AI.
Creates SQLAlchemy async engine and session factory.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.settings import get_settings

settings = get_settings()

# Convert synchronous URL to asynchronous URL
# mysql+pymysql:// -> mysql+asyncmy://
database_url = settings.DATABASE_URL
if database_url.startswith('mysql+pymysql://'):
    database_url = database_url.replace('mysql+pymysql://', 'mysql+asyncmy://')

# Create SQLAlchemy async engine
engine = create_async_engine(
    database_url,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Create session factory for async sessions
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Base class for models
Base = declarative_base()

# For backward compatibility during migration
SessionLocal = AsyncSessionLocal