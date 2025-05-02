"""
API endpoints for Gunny Bag Counter module.
Provides endpoints for counting, tracking, and managing gunny bags in the warehouse.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import (
    BaseResponse,
    BaseErrorResponse,
    GunnyBagCountCreate,
    GunnyBagCountResponse,
    PaginatedResponse
)
from src.core.utils import paginate, handle_error, save_uploaded_file, ensure_directory_exists
from src.database.operations import GunnyBagCountRepository, get_db
from src.modules.gunny_counter.detector import GunnyBagDetector
from src.modules.gunny_counter.counter import GunnyBagCounter
from src.modules.gunny_counter.volumetric import VolumetricEstimator

# Create router
router = APIRouter()


@router.post(
    "/count", 
    response_model=GunnyBagCountResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": BaseErrorResponse, "description": "Bad request"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def count_gunny_bags(
    location: str,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Count gunny bags in an uploaded image and save the results.
    
    Args:
        location: Location identifier where the image was taken
        image: Uploaded image file containing gunny bags
        db: Database session
        
    Returns:
        GunnyBagCountResponse: The saved gunny bag count information
    """
    try:
        # Create directory for storing images
        image_dir = ensure_directory_exists("./data/images/gunny")
        
        # Save uploaded image
        image_path = save_uploaded_file(
            await image.read(),
            image_dir,
            f"gunny_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )
        
        # Initialize detector and counter
        detector = GunnyBagDetector()
        counter = GunnyBagCounter()
        volumetric = VolumetricEstimator()
        
        # Detect and count gunny bags
        detections = detector.detect(image_path)
        count = counter.count(detections)
        
        # Estimate volume
        estimated_volume = volumetric.estimate_volume(detections)
        
        # Initialize repository with the current database session
        repo = GunnyBagCountRepository(db)
        
        # Create record in database
        gunny_count = await repo.create(
            bag_count=count,  # Changed from count=count to bag_count=count
            estimated_volume=estimated_volume,
            location=location,
            video_reference=image_path,
            confidence_score=detector.last_confidence,
            bag_metadata={"detection_boxes": detections.tolist()}
        )
        
        return gunny_count
    except Exception as e:
        handle_error(f"Failed to process gunny bag count: {str(e)}")


@router.get(
    "/counts",
    response_model=List[GunnyBagCountResponse],
    responses={
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def list_gunny_bag_counts(
    location: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List gunny bag counts with optional filtering by location.
    
    Args:
        location: Optional location filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[GunnyBagCountResponse]: List of gunny bag count records
    """
    try:
        # Initialize repository with the current database session
        repo = GunnyBagCountRepository(db)
        
        if location:
            # Get counts for a specific location
            counts = await repo.get_by_location(location, skip=skip, limit=limit)
        else:
            # Get all counts
            counts = await repo.get_all(skip=skip, limit=limit)
            
        return counts
    except Exception as e:
        handle_error(f"Failed to retrieve gunny bag counts: {str(e)}")


@router.get(
    "/counts/{count_id}",
    response_model=GunnyBagCountResponse,
    responses={
        404: {"model": BaseErrorResponse, "description": "Count not found"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def get_gunny_bag_count(
    count_id: UUID = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific gunny bag count by ID.
    
    Args:
        count_id: UUID of the count record
        db: Database session
        
    Returns:
        GunnyBagCountResponse: The gunny bag count record
    """
    try:
        # Initialize repository with the current database session
        repo = GunnyBagCountRepository(db)
        
        count = await repo.get_by_id(count_id)
        
        if not count:
            handle_error(
                f"Gunny bag count with ID {count_id} not found",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="GUNNY_COUNT_NOT_FOUND"
            )
            
        return count
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        handle_error(f"Failed to retrieve gunny bag count: {str(e)}")


@router.get(
    "/latest/{location}",
    response_model=GunnyBagCountResponse,
    responses={
        404: {"model": BaseErrorResponse, "description": "No counts found for location"},
        500: {"model": BaseErrorResponse, "description": "Internal server error"}
    }
)
async def get_latest_gunny_bag_count(
    location: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest gunny bag count for a specific location.
    
    Args:
        location: Location identifier
        db: Database session
        
    Returns:
        GunnyBagCountResponse: The latest gunny bag count for the location
    """
    try:
        # Initialize repository with the current database session
        repo = GunnyBagCountRepository(db)
        
        latest_count = await repo.get_latest_by_location(location)
        
        if not latest_count:
            handle_error(
                f"No gunny bag counts found for location {location}",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="NO_COUNTS_FOR_LOCATION"
            )
            
        return latest_count
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        handle_error(f"Failed to retrieve latest gunny bag count: {str(e)}")