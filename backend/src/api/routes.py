"""
Main FastAPI application module with route definitions.
Sets up the FastAPI application with middleware, exception handlers, and API routes.
"""
import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.api.endpoints import gunny, vehicle, facial, contextual
from src.config.settings import get_settings
from src.config.logging_config import setup_logging, get_logger

# Create logger
logger = get_logger(__name__)

# Initialize settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered surveillance system for warehouse management with computer vision capabilities",
    version="0.1.0",
    docs_url="/docs",  # Make docs available at root path
    redoc_url="/redoc",  # Make redoc available at root path
    openapi_url="/openapi.json",  # Make OpenAPI schema available at root path
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
setup_logging()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log requests and measure response time.
    """
    start_time = time.time()
    
    # Get client IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = forwarded_for.split(',')[0] if forwarded_for else request.client.host
    
    # Log request details
    logger.info(
        f"Request started: {request.method} {request.url.path} from {client_ip}"
    )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"status={response.status_code} "
            f"time={process_time:.3f}s"
        )
        
        # Add custom header with processing time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        return response
    except Exception as e:
        # Log any unhandled exceptions
        process_time = time.time() - start_time
        logger.exception(
            f"Request failed: {request.method} {request.url.path} "
            f"error={str(e)} "
            f"time={process_time:.3f}s"
        )
        
        # Return a 500 response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Internal server error",
                "detail": str(e) if settings.ENVIRONMENT != "production" else None,
            },
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors consistently.
    """
    # Log validation errors
    logger.warning(
        f"Validation error for {request.method} {request.url.path}: {exc.errors()}"
    )
    
    # Return a 422 response with error details
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "message": "Validation error",
            "detail": exc.errors(),
        },
    )


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "description": "AI-powered surveillance system for warehouse management",
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }


# Include API routers
app.include_router(
    gunny.router, 
    prefix=f"{settings.API_V1_PREFIX}/gunny", 
    tags=["Gunny Bag Counter"]
)
app.include_router(
    vehicle.router, 
    prefix=f"{settings.API_V1_PREFIX}/vehicle", 
    tags=["Vehicle Recognition"]
)
app.include_router(
    facial.router, 
    prefix=f"{settings.API_V1_PREFIX}/facial", 
    tags=["Facial Recognition"]
)
app.include_router(
    contextual.router, 
    prefix=f"{settings.API_V1_PREFIX}/context", 
    tags=["Contextual Intelligence"]
)
app.include_router(
    contextual.router, 
    prefix=f"{settings.API_V1_PREFIX}/contextual", 
    tags=["Contextual Intelligence"]
)
