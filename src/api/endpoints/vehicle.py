"""
API endpoints for Vehicle Recognition module.
Provides endpoints for license plate detection and vehicle authentication.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import (
    BaseResponse,
    BaseErrorResponse,
    VehicleCreate,
    VehicleResponse,
    VehicleEntryCreate,
    VehicleEntryResponse
)
from src.core.utils import paginate, handle_error, save_uploaded_file, ensure_directory_exists
from src.database.operations import vehicle_repository
from src.modules.vehicle_recognition.plate_detector import LicensePlateDetector
from src.modules.vehicle_recognition.ocr import LicensePlateOCR
from src.modules.vehicle_recognition.vehicle_tracker import VehicleTracker
from src.database.operations import get_db

# Create router
router = APIRouter()


@router.post(
    "/detect",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": BaseErrorResponse, "description": "Bad request"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def detect_vehicle(
    image: UploadFile = File(...),
    location: str = Form(...),
    entry_type: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect a vehicle license plate from an uploaded image and register the vehicle.
    
    Args:
        image: Uploaded image file containing vehicle with license plate
        location: Location identifier where the image was taken
        entry_type: Type of entry event (ENTRY or EXIT)
        db: Database session
        
    Returns:
        VehicleResponse: The detected and registered vehicle information
    """
    try:
        # Create directory for storing images
        image_dir = ensure_directory_exists("./data/images/vehicles")
        
        # Save uploaded image
        image_path = save_uploaded_file(
            await image.read(),
            image_dir,
            f"vehicle_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        
        # Initialize detectors
        plate_detector = LicensePlateDetector()
        ocr = LicensePlateOCR()
        
        # Detect license plate
        plate_box = plate_detector.detect(image_path)
        
        if plate_box is None:
            handle_error(
                "No license plate detected in the image",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="NO_LICENSE_PLATE"
            )
        
        # Extract license plate text
        license_plate = ocr.extract_text(image_path, plate_box)
        
        if not license_plate:
            handle_error(
                "Could not read license plate text",
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="UNREADABLE_LICENSE_PLATE"
            )
            
        # Check if vehicle exists
        vehicle = await vehicle_repository.get_by_license_plate(db, license_plate=license_plate)
        
        # If vehicle doesn't exist, create it
        if not vehicle:
            vehicle = await vehicle_repository.create(
                db,
                obj_in=VehicleCreate(
                    license_plate=license_plate,
                    vehicle_type="Unknown",  # In a real system, we would detect vehicle type
                    is_authorized=False,  # Set to false until authorized by admin
                    vehicle_metadata={
                        "first_seen_location": location,
                        "first_seen_date": datetime.now().isoformat()
                    }
                )
            )
        
        # Record entry/exit event
        entry = await vehicle_repository.create_entry(
            db,
            obj_in=VehicleEntryCreate(
                vehicle_id=vehicle.id,
                entry_type=entry_type,
                location=location,
                image_path=image_path,
                confidence_score=plate_detector.last_confidence
            )
        )
        
        return vehicle
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        handle_error(f"Failed to process vehicle detection: {str(e)}")


@router.get(
    "/vehicles",
    response_model=List[VehicleResponse],
    responses={
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def list_vehicles(
    is_authorized: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List vehicles with optional filtering.
    
    Args:
        is_authorized: Optional filter by authorization status
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[VehicleResponse]: List of vehicle records
    """
    try:
        vehicles = await vehicle_repository.get_filtered(
            db, 
            is_authorized=is_authorized, 
            skip=skip, 
            limit=limit
        )
        return vehicles
    
    except Exception as e:
        handle_error(f"Failed to retrieve vehicles: {str(e)}")


@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleResponse,
    responses={
        404: {"model": BaseErrorResponse, "description": "Vehicle not found"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def get_vehicle(
    vehicle_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific vehicle by ID.
    
    Args:
        vehicle_id: UUID of the vehicle
        db: Database session
        
    Returns:
        VehicleResponse: The vehicle record
    """
    try:
        vehicle = await vehicle_repository.get(db, vehicle_id)
        
        if not vehicle:
            handle_error(
                f"Vehicle with ID {vehicle_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="VEHICLE_NOT_FOUND"
            )
            
        return vehicle
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        handle_error(f"Failed to retrieve vehicle: {str(e)}")


@router.get(
    "/entries/{vehicle_id}",
    response_model=List[VehicleEntryResponse],
    responses={
        404: {"model": BaseErrorResponse, "description": "Vehicle not found"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def get_vehicle_entries(
    vehicle_id: UUID = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get entry/exit records for a specific vehicle.
    
    Args:
        vehicle_id: UUID of the vehicle
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[VehicleEntryResponse]: List of vehicle entry records
    """
    try:
        # Check if vehicle exists
        vehicle = await vehicle_repository.get(db, vehicle_id)
        
        if not vehicle:
            handle_error(
                f"Vehicle with ID {vehicle_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="VEHICLE_NOT_FOUND"
            )
        
        entries = await vehicle_repository.get_entries(
            db, 
            vehicle_id=vehicle_id, 
            skip=skip, 
            limit=limit
        )
        
        return entries
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        handle_error(f"Failed to retrieve vehicle entries: {str(e)}")


@router.patch(
    "/authorize/{vehicle_id}",
    response_model=VehicleResponse,
    responses={
        404: {"model": BaseErrorResponse, "description": "Vehicle not found"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def authorize_vehicle(
    vehicle_id: UUID = Path(...),
    authorize: bool = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Authorize or unauthorize a vehicle.
    
    Args:
        vehicle_id: UUID of the vehicle
        authorize: Whether to authorize (true) or unauthorize (false) the vehicle
        db: Database session
        
    Returns:
        VehicleResponse: The updated vehicle record
    """
    try:
        vehicle = await vehicle_repository.get(db, vehicle_id)
        
        if not vehicle:
            handle_error(
                f"Vehicle with ID {vehicle_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="VEHICLE_NOT_FOUND"
            )
        
        # Update authorization status
        vehicle = await vehicle_repository.update_authorization(db, vehicle_id=vehicle_id, authorize=authorize)
        
        return vehicle
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        handle_error(f"Failed to update vehicle authorization: {str(e)}")


# Define database session dependency
async def get_db():
    """
    Get database session for dependency injection.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.orm import sessionmaker
    
    from src.config.settings import get_settings
    
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW
    )
    
    # Create sessionmaker
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    # Create and yield a session
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()