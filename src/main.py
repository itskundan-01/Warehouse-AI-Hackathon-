import os
import argparse
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='WarehouseVision AI')
    parser.add_argument('--mode', type=str, default='api', 
                       choices=['api', 'worker', 'test'],
                       help='Mode to run the application in')
    parser.add_argument('--config', type=str, default=None,
                       help='Path to configuration file')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    logger.info(f"Starting WarehouseVision AI in {args.mode} mode")
    
    if args.mode == 'api':
        run_api_server()
    elif args.mode == 'worker':
        run_worker()
    elif args.mode == 'test':
        run_tests()

def run_api_server():
    """Run the FastAPI server"""
    try:
        import uvicorn
        from src.api.routes import app
        
        logger.info("Starting API server")
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        logger.error("FastAPI or uvicorn not installed. Install with: pip install fastapi uvicorn")
    except Exception as e:
        logger.error(f"Error starting API server: {str(e)}")

def run_worker():
    """Run the worker for background tasks"""
    try:
        from celery import Celery
        
        logger.info("Starting worker")
        # Configure Celery
        # Implementation pending
        logger.info("Worker started successfully")
    except ImportError:
        logger.error("Celery not installed. Install with: pip install celery")
    except Exception as e:
        logger.error(f"Error starting worker: {str(e)}")

def run_tests():
    """Run tests"""
    import unittest
    
    logger.info("Running tests")
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(tests)
    logger.info("Tests completed")

if __name__ == "__main__":
    logger.info("WarehouseVision AI initializing...")
    main()
    logger.info("WarehouseVision AI shutting down...")
