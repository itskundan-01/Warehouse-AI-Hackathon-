import os
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any

def get_project_root() -> Path:
    """Returns project root folder."""
    return Path(__file__).parent.parent.parent

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the specified name.
    
    Args:
        name (str): Name for the logger, typically __name__
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Avoid adding handlers if they already exist
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def ensure_dir(directory: str) -> str:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory (str): Directory path
        
    Returns:
        str: Directory path
    """
    os.makedirs(directory, exist_ok=True)
    return directory

def get_env_variable(name: str, default: Optional[str] = None) -> str:
    """
    Get environment variable or return default value.
    
    Args:
        name (str): Environment variable name
        default (Optional[str]): Default value if environment variable is not set
        
    Returns:
        str: Value of environment variable or default
    """
    return os.environ.get(name, default)

def check_dependencies() -> Dict[str, bool]:
    """
    Check if optional dependencies are installed.
    
    Returns:
        Dict[str, bool]: Dictionary of dependencies and their availability
    """
    dependencies = {
        'torch': False,
        'cv2': False,
        'ultralytics': False,
        'paddleocr': False,
        'insightface': False,
        'elasticsearch': False,
    }
    
    # Try to import each dependency
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies

def get_device() -> str:
    """
    Get the device to use for ML models (CUDA, MPS, or CPU).
    
    Returns:
        str: Device name ('cuda', 'mps', 'cpu')
    """
    try:
        import torch
        
        if torch.cuda.is_available():
            return 'cuda'
        elif hasattr(torch, 'backends') and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            # For Apple Silicon Macs
            return 'mps'
        else:
            return 'cpu'
    except ImportError:
        # If torch is not available, default to CPU
        return 'cpu'
