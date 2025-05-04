"""
Database dependency utilities for FastAPI endpoints.
These utilities avoid FastAPI typing issues with SQLAlchemy.
"""
from typing import Any, Callable, Dict, Generator
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.operations import get_db

def get_typed_db():
    """
    Dependency that returns a database session without type annotations.
    This avoids the FastAPI issue with AsyncSession type.
    """
    async def _db_dependency():
        async for session in get_db():
            yield session
    
    return Depends(_db_dependency)


def db_wrapper(func: Callable):
    """
    Decorator to inject a database session into a function.
    This is an alternative to using Depends(get_db) directly in endpoint params.
    """
    async def wrapper(*args, **kwargs):
        async for session in get_db():
            try:
                kwargs["db"] = session
                return await func(*args, **kwargs)
            finally:
                await session.close()
    
    return wrapper