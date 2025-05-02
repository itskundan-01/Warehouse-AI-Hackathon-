"""
Logging configuration for WarehouseVision AI.
Provides structured logging with different handlers for console and file output.
"""
import os
import sys
import logging
import logging.config
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from src.config.settings import get_settings

# Get settings
settings = get_settings()

# Define log directory
LOG_DIR = Path("./logs")

def setup_logging() -> None:
    """
    Configure logging for the application.
    Sets up console and file handlers with appropriate formats.
    """
    # Create log directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"warehouse_vision_{current_time}.log"
    log_filepath = LOG_DIR / log_filename
    
    # Define logging config
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d %(process)d %(thread)d %(funcName)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "simple",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "detailed",
                "filename": log_filepath,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": True
            }
        }
    }
    
    # Apply the configuration
    logging.config.dictConfig(config)
    logging.info(f"Logging initialized. Log file: {log_filepath}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)