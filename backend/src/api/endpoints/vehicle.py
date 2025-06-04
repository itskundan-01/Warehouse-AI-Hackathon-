"""
API endpoints for Vehicle Recognition module.
Provides endpoints for license plate detection and vehicle authentication.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import os

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse

from src.modules.vehicle_recognition.plate_detector import LicensePlateDetector
from src.modules.vehicle_recognition.ocr import LicensePlateOCR
from src.modules.vehicle_recognition.vehicle_tracker import VehicleTracker
from src.database import db  # Use the MongoDB client directly

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
    try:
        # Create directory for storing images
        image_dir = "./data/images/vehicles"
        os.makedirs(image_dir, exist_ok=True)
        image_path = f"vehicle_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(f"{image_dir}/{image_path}", "wb") as image_file:
            image_file.write(await image.read())
        # Initialize detectors
        plate_detector = LicensePlateDetector()
        ocr = LicensePlateOCR()
        # Detect license plate
        plate_box = plate_detector.detect(f"{image_dir}/{image_path}")
        if plate_box is None:
            return JSONResponse(
                status_code=400,
                content={"detail": "No license plate detected in the image"}
            )
        # Extract license plate text
        license_plate = ocr.extract_text(f"{image_dir}/{image_path}", plate_box)
        if not license_plate:
            return JSONResponse(
                status_code=400,
                content={"detail": "Could not read license plate text"}
            )
        # Check if vehicle exists
        collection = db["vehicles"]
        vehicle = await collection.find_one({"license_plate": license_plate})
        # If vehicle doesn't exist, create it
        if not vehicle:
            vehicle_doc = {
                "license_plate": license_plate,
                "location": location,
                "image_path": image_path,
                "entry_type": entry_type,
                "created_at": datetime.utcnow(),
                "last_seen": datetime.utcnow(),
                "is_authorized": False
            }
            result = await collection.insert_one(vehicle_doc)
            vehicle = await collection.find_one({"_id": result.inserted_id})
        else:
            # Update last_seen and image_path
            await collection.update_one(
                {"_id": vehicle["_id"]},
                {"$set": {"last_seen": datetime.utcnow(), "image_path": image_path}}
            )
            vehicle = await collection.find_one({"_id": vehicle["_id"]})
        # Record entry/exit event (optional: implement if you have a vehicle_entries collection)
        # entry_collection = db["vehicle_entries"]
        # await entry_collection.insert_one({ ... })
        vehicle["_id"] = str(vehicle["_id"])
        return vehicle
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to process vehicle detection: {str(e)}"}
        )

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
    try:
        collection = db["vehicles"]
        query = {}
        if is_authorized is not None:
            query["is_authorized"] = is_authorized
        cursor = collection.find(query).skip(skip).limit(limit).sort("last_seen", -1)
        vehicles = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            vehicles.append(doc)
        return vehicles
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to retrieve vehicles: {str(e)}"}
        )

@router.get(
    "/vehicles/{vehicle_id}",
    response_model=None
)
async def get_vehicle(
    vehicle_id: str = Path(...)
):
    """
    Get a specific vehicle by ID.
    """
    from bson import ObjectId
    try:
        collection = db["vehicles"]
        vehicle = await collection.find_one({"_id": ObjectId(vehicle_id)})
        if not vehicle:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Vehicle with ID {vehicle_id} not found"}
            )
        vehicle["_id"] = str(vehicle["_id"])
        return vehicle
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to retrieve vehicle: {str(e)}"}
        )