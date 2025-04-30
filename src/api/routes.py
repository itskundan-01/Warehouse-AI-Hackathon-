from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="WarehouseVision AI",
    description="AI-powered surveillance system for warehouses",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing basic information"""
    return {
        "message": "WarehouseVision AI API",
        "version": "0.1.0",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Import and include router endpoints
try:
    from src.api.endpoints.gunny import router as gunny_router
    app.include_router(gunny_router, prefix="/api/gunny", tags=["Gunny Bag Counter"])
except ImportError as e:
    logger.warning(f"Could not import gunny router: {str(e)}")

try:
    from src.api.endpoints.vehicle import router as vehicle_router
    app.include_router(vehicle_router, prefix="/api/vehicle", tags=["Vehicle Recognition"])
except ImportError as e:
    logger.warning(f"Could not import vehicle router: {str(e)}")

try:
    from src.api.endpoints.facial import router as facial_router
    app.include_router(facial_router, prefix="/api/facial", tags=["Facial Recognition"])
except ImportError as e:
    logger.warning(f"Could not import facial router: {str(e)}")

try:
    from src.api.endpoints.contextual import router as contextual_router
    app.include_router(contextual_router, prefix="/api/contextual", tags=["Contextual Intelligence"])
except ImportError as e:
    logger.warning(f"Could not import contextual router: {str(e)}")

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"}
    )

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("API server starting up")

# Add shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("API server shutting down")
