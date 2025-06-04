"""
Main entry point for WarehouseVision AI API.
Starts the API server with uvicorn.
"""
import os
import sys
import uvicorn
from src.api.routes import app
from src.config.settings import get_settings
from src.config.logging_config import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Get settings
settings = get_settings()

def main():
    """
    Start the FastAPI application with uvicorn.
    """
    logger.info(f"Starting {settings.PROJECT_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API listening on {settings.API_HOST}:{settings.API_PORT}")
    
    # Run the API with uvicorn
    uvicorn.run(
        "src.api.routes:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT.lower() == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )

if __name__ == "__main__":
    main()
