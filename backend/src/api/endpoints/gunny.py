"""
API endpoints for Gunny Bag Counter module.
Provides endpoints for counting, tracking, and managing gunny bags in the warehouse.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import os

from fastapi import APIRouter, File, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse

from src.database import db  # Use the MongoDB client directly
from src.modules.gunny_counter.detector import GunnyBagDetector
from src.modules.gunny_counter.counter import GunnyBagCounter
from src.modules.gunny_counter.volumetric import VolumetricEstimator

# Create router
router = APIRouter()


# Helper to get the collection
async def get_gunny_collection():
    return db["gunny_bag_counts"]


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
    try:
        # Create directory for storing images
        image_dir = "./data/images/gunny"
        os.makedirs(image_dir, exist_ok=True)
        image_path = f"gunny_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(f"{image_dir}/{image_path}", "wb") as image_file:
            image_file.write(await image.read())
        detector = GunnyBagDetector()
        counter = GunnyBagCounter()
        volumetric = VolumetricEstimator()
        detections = detector.detect(image_path)
        count = counter.count(detections)
        estimated_volume = volumetric.estimate_volume(detections)
        collection = await get_gunny_collection()
        doc = {
            "bag_count": count,
            "estimated_volume": estimated_volume,
            "location": location,
            "image_path": image_path,
            "confidence_score": getattr(detector, 'last_confidence', None),
            "bag_metadata": {"detection_boxes": getattr(detections, 'tolist', lambda: detections)()},
            "timestamp": datetime.utcnow()
        }
        result = await collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to process gunny bag count: {str(e)}"}
        )


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
    try:
        collection = await get_gunny_collection()
        query = {"location": location} if location else {}
        cursor = collection.find(query).skip(skip).limit(limit).sort("timestamp", -1)
        counts = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            counts.append(doc)
        return counts
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to retrieve gunny bag counts: {str(e)}"}
        )


@router.get(
    "/counts/{count_id}",
    response_model=None
)
async def get_gunny_bag_count(
    count_id: str = Path(...)
):
    """
    Get a specific gunny bag count by ID.
    """
    from bson import ObjectId
    try:
        collection = await get_gunny_collection()
        doc = await collection.find_one({"_id": ObjectId(count_id)})
        if not doc:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Gunny bag count with ID {count_id} not found"}
            )
        doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to retrieve gunny bag count: {str(e)}"}
        )


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
    try:
        collection = await get_gunny_collection()
        doc = await collection.find_one({"location": location}, sort=[("timestamp", -1)])
        if not doc:
            return JSONResponse(
                status_code=404,
                content={"detail": f"No gunny bag counts found for location {location}"}
            )
        doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to retrieve latest gunny bag count: {str(e)}"}
        )