"""
Utility functions for WarehouseVision AI.
Contains helper functions used across the application.
"""
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union, AsyncGenerator

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging_config import get_logger
from src.database.operations import get_db

# Set up logger for this module
logger = get_logger(__name__)

# Type variable for generic functions
T = TypeVar('T')


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.
    This is an alias for get_db from database.operations for backward compatibility.
    """
    async for db in get_db():
        yield db


def generate_uuid() -> uuid.UUID:
    """
    Generate a new UUID.
    
    Returns:
        UUID: A new random UUID
    """
    return uuid.uuid4()


def now() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        datetime: Current UTC datetime
    """
    return datetime.utcnow()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for file system operations.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters with underscore
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # Remove any leading/trailing whitespace
    sanitized = sanitized.strip()
    # If filename is empty after sanitization, use a default name
    if not sanitized:
        sanitized = f"file_{generate_uuid().hex[:8]}"
    return sanitized


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path: Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_uploaded_file(file_data: bytes, directory: Union[str, Path], filename: str) -> str:
    """
    Save uploaded file data to disk.
    
    Args:
        file_data: Binary file data
        directory: Directory to save the file in
        filename: Name for the saved file
        
    Returns:
        str: Path to the saved file
    """
    # Ensure directory exists
    dir_path = ensure_directory_exists(directory)
    
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Create full path
    file_path = dir_path / safe_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_data)
    
    logger.info(f"File saved: {file_path}")
    return str(file_path)


def get_model_path(model_name: str, version: Optional[str] = None) -> Path:
    """
    Get the path to a model file.
    
    Args:
        model_name: Name of the model
        version: Version of the model (default: latest)
        
    Returns:
        Path: Path to the model file
    """
    # Get model directory from settings
    from src.config.settings import get_settings
    settings = get_settings()
    
    base_path = Path(settings.MODEL_REGISTRY)
    
    # If version is specified, use it, otherwise look for the latest
    if version:
        model_path = base_path / model_name / version
    else:
        model_dir = base_path / model_name
        
        # Find all version directories
        if not model_dir.exists():
            raise FileNotFoundError(f"Model {model_name} not found")
        
        versions = [d for d in model_dir.iterdir() if d.is_dir()]
        if not versions:
            raise FileNotFoundError(f"No versions found for model {model_name}")
        
        # Get latest version (assuming version naming scheme allows string sorting)
        latest = sorted(versions)[-1]
        model_path = latest
    
    # Check if model exists
    if not model_path.exists():
        raise FileNotFoundError(f"Model {model_name} version {version or 'latest'} not found")
    
    return model_path


def paginate(
    items: List[T],
    page: int = 1, 
    page_size: int = 10,
    total_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a paginated response.
    
    Args:
        items: List of items for the current page
        page: Page number (1-indexed)
        page_size: Number of items per page
        total_count: Total count of items (if known)
        
    Returns:
        Dict: Pagination details with items
    """
    # Ensure page and page_size are valid
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    
    # Calculate total if not provided
    total = total_count if total_count is not None else len(items)
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Ensure page doesn't exceed total pages
    if page > total_pages:
        page = total_pages
    
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
    }


def handle_error(
    message: str, 
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    error_code: Optional[str] = None,
    log_error: bool = True
) -> None:
    """
    Handle application errors consistently.
    
    Args:
        message: Error message to show to the user
        status_code: HTTP status code
        error_code: Internal error code for reference
        log_error: Whether to log the error
        
    Raises:
        HTTPException: With the provided details
    """
    if log_error:
        logger.error(f"Error {error_code or 'UNKNOWN'}: {message}")
    
    raise HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "error_code": error_code,
        }
    )


def format_bytes(size: int) -> str:
    """
    Format a size in bytes to a human-readable string.
    
    Args:
        size: Size in bytes
        
    Returns:
        str: Human-readable size string (e.g., "5.2 MB")
    """
    power = 2**10  # 1024
    n = 0
    labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    
    while size > power:
        size /= power
        n += 1
    
    return f"{size:.1f} {labels[n]}"


def array_to_bytes(array: np.ndarray) -> bytes:
    """
    Convert a NumPy array to bytes for storage.
    
    Args:
        array: NumPy array to convert
        
    Returns:
        bytes: Byte representation of the array
    """
    return array.tobytes()


def bytes_to_array(data: bytes, dtype=np.float32, shape: Optional[Tuple[int, ...]] = None) -> np.ndarray:
    """
    Convert bytes back to a NumPy array.
    
    Args:
        data: Byte data to convert
        dtype: NumPy data type of the array
        shape: Shape of the array (if None, 1D array is returned)
        
    Returns:
        np.ndarray: NumPy array from bytes
    """
    array = np.frombuffer(data, dtype=dtype)
    
    if shape:
        array = array.reshape(shape)
    
    return array