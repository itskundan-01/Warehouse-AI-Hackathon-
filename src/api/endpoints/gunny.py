"""
API endpoints for Gunny Bag Counter module.
Provides endpoints for counting, tracking, and managing gunny bags in the warehouse.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, File, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse

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
    response_model=None,
    status_code=status.HTTP_201_CREATED
)
async def count_gunny_bags(
    location: str,
    image: UploadFile = File(...)
):
    """
    Count gunny bags in an uploaded image and save the results.
    """
    async for db in get_db():
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
                bag_count=count,
                estimated_volume=estimated_volume,
                location=location,
                video_reference=image_path,
                confidence_score=detector.last_confidence,
                bag_metadata={"detection_boxes": detections.tolist()}
            )
            
            return gunny_count
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to process gunny bag count: {str(e)}"}
            )
        finally:
            await db.close()


@router.get(
    "/counts",
    response_model=None
)
async def list_gunny_bag_counts(
    location: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List gunny bag counts with optional filtering by location.
    """
    async for db in get_db():
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
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to retrieve gunny bag counts: {str(e)}"}
            )
        finally:
            await db.close()


@router.get(
    "/counts/{count_id}",
    response_model=None
)
async def get_gunny_bag_count(
    count_id: UUID = Path(...)
):
    """
    Get a specific gunny bag count by ID.
    """
    async for db in get_db():
        try:
            # Initialize repository with the current database session
            repo = GunnyBagCountRepository(db)
            
            count = await repo.get_by_id(count_id)
            
            if not count:
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Gunny bag count with ID {count_id} not found"}
                )
                
            return count
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to retrieve gunny bag count: {str(e)}"}
            )
        finally:
            await db.close()


@router.get(
    "/latest/{location}",
    response_model=None
)
async def get_latest_gunny_bag_count(
    location: str = Path(...)
):
    """
    Get the latest gunny bag count for a specific location.
    """
    async for db in get_db():
        try:
            # Initialize repository with the current database session
            repo = GunnyBagCountRepository(db)
            
            latest_count = await repo.get_latest_by_location(location)
            
            if not latest_count:
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"No gunny bag counts found for location {location}"}
                )
                
            return latest_count
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to retrieve latest gunny bag count: {str(e)}"}
            )
        finally:
            await db.close()