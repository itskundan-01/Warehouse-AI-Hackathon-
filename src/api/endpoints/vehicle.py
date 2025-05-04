"""
API endpoints for Vehicle Recognition module.
Provides endpoints for license plate detection and vehicle authentication.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse

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
    response_model=None,
    status_code=status.HTTP_201_CREATED
)
async def detect_vehicle(
    image: UploadFile = File(...),
    location: str = Form(...),
    entry_type: str = Form(...)
):
    """
    Detect a vehicle license plate from an uploaded image and register the vehicle.
    """
    async for db in get_db():
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
                return JSONResponse(
                    status_code=400,
                    content={"detail": "No license plate detected in the image"}
                )
            
            # Extract license plate text
            license_plate = ocr.extract_text(image_path, plate_box)
            
            if not license_plate:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Could not read license plate text"}
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
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to process vehicle detection: {str(e)}"}
            )
        finally:
            await db.close()


@router.get(
    "/vehicles",
    response_model=None
)
async def list_vehicles(
    is_authorized: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List vehicles with optional filtering.
    """
    async for db in get_db():
        try:
            vehicles = await vehicle_repository.get_filtered(
                db, 
                is_authorized=is_authorized, 
                skip=skip, 
                limit=limit
            )
            return vehicles
        
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to retrieve vehicles: {str(e)}"}
            )
        finally:
            await db.close()


@router.get(
    "/vehicles/{vehicle_id}",
    response_model=None
)
async def get_vehicle(
    vehicle_id: UUID = Path(...)
):
    """
    Get a specific vehicle by ID.
    """
    async for db in get_db():
        try:
            vehicle = await vehicle_repository.get(db, vehicle_id)
            
            if not vehicle:
                return JSONResponse(
                    status_code=404,
                    content={"detail": f"Vehicle with ID {vehicle_id} not found"}
                )
                
            return vehicle
        
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            return JSONResponse(
                status_code=500,
                content={"detail": f"Failed to retrieve vehicle: {str(e)}"}
            )
        finally:
            await db.close()