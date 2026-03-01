"""
FastAPI endpoints for License Plate Detection and Tracking.
Handles file uploads and provides detection results via REST API.
"""

import os
import shutil
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status, Query
from fastapi.responses import JSONResponse
import aiofiles

# Import our core detector
import sys
sys.path.append('/Users/kundan/PROJECTS/Warehouse AI Hackathon/backend')
from plate_detector import PlateDetector

# Create router
router = APIRouter(prefix="/api/v1/plates", tags=["License Plate Detection"])

# Global detector instance (initialized once)
detector_instance = None

def get_detector() -> PlateDetector:
    """Get or create detector instance."""
    global detector_instance
    if detector_instance is None:
        detector_instance = PlateDetector(
            confidence_threshold=0.5,
            mongodb_url="mongodb://localhost:27017/warehouse_vision"
        )
    return detector_instance

@router.post("/detect", summary="Detect license plates from uploaded file")
async def detect_plates(
    file: UploadFile = File(..., description="Image or video file to process"),
    location: str = Form("unknown", description="Location where detection was performed"),
    store_results: bool = Form(True, description="Whether to store results in database")
):
    """
    Upload an image or video file and detect license plates.
    
    - **file**: Image (jpg, png, etc.) or video (mp4, avi, etc.) file
    - **location**: Location identifier for the detection
    - **store_results**: Whether to save results to MongoDB
    
    Returns detection results including plate numbers, confidence scores, and bounding boxes.
    """
    detector = get_detector()
    temp_file_path = None
    
    try:
        # Validate file type
        if not file.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine file type"
            )
        
        # Check if file type is supported
        supported_image_types = ["image/jpeg", "image/png", "image/jpg", "image/bmp", "image/tiff"]
        supported_video_types = ["video/mp4", "video/avi", "video/mov", "video/mkv", "video/wmv"]
        
        is_image = file.content_type in supported_image_types
        is_video = file.content_type in supported_video_types
        
        if not (is_image or is_video):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. "
                       f"Supported types: {supported_image_types + supported_video_types}"
            )
        
        # Create temporary file
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file_path = temp_file.name
            
            # Save uploaded file
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
        
        # Process the file
        if is_image:
            results = detector.process_image(temp_file_path)
        else:  # is_video
            results = detector.process_video(temp_file_path, frame_skip=30)
        
        # Store results in database if requested
        if store_results and 'error' not in results:
            await detector.store_results(results, location)
        
        # Prepare response
        response_data = {
            "success": True,
            "file_type": "image" if is_image else "video",
            "original_filename": file.filename,
            "location": location,
            "processing_timestamp": datetime.utcnow().isoformat(),
            **results
        }
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection processing failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass

@router.get("/history/{plate_text}", summary="Get detection history for a license plate")
async def get_plate_history(
    plate_text: str,
    limit: int = Query(50, ge=1, le=500, description="Maximum number of records to return")
):
    """
    Get detection history for a specific license plate number.
    
    - **plate_text**: License plate number to search for
    - **limit**: Maximum number of records to return (1-500)
    
    Returns list of detection records for the specified plate.
    """
    detector = get_detector()
    
    try:
        records = await detector.get_plate_history(plate_text)
        
        # Limit results
        if len(records) > limit:
            records = records[:limit]
        
        return {
            "success": True,
            "plate_text": plate_text,
            "total_records": len(records),
            "records": records
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve plate history: {str(e)}"
        )

@router.get("/recent", summary="Get recent license plate detections")
async def get_recent_detections(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of records to return"),
    location: Optional[str] = Query(None, description="Filter by location")
):
    """
    Get recent license plate detections across all locations.
    
    - **limit**: Maximum number of records to return (1-500)
    - **location**: Optional location filter
    
    Returns list of recent detection records.
    """
    detector = get_detector()
    
    try:
        records = await detector.get_recent_detections(limit)
        
        # Filter by location if specified
        if location:
            records = [r for r in records if r.get('location', '').lower() == location.lower()]
        
        return {
            "success": True,
            "total_records": len(records),
            "limit": limit,
            "location_filter": location,
            "records": records
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent detections: {str(e)}"
        )

@router.get("/stats", summary="Get detection statistics")
async def get_detection_stats():
    """
    Get overall detection statistics.
    
    Returns statistics about total detections, unique plates, etc.
    """
    detector = get_detector()
    
    try:
        db = await detector._get_database()
        
        # Get statistics from collections
        plates_collection = db.license_plates
        detections_collection = db.license_plate_detections
        
        # Count total detections
        total_detections = await plates_collection.count_documents({})
        
        # Count unique plates
        unique_plates = await plates_collection.distinct('plate_text')
        unique_plate_count = len(unique_plates)
        
        # Count detections by location
        location_pipeline = [
            {'$group': {'_id': '$location', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        location_stats = await plates_collection.aggregate(location_pipeline).to_list(None)
        
        # Count detections by source type
        source_type_pipeline = [
            {'$group': {'_id': '$source_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        source_type_stats = await plates_collection.aggregate(source_type_pipeline).to_list(None)
        
        # Get recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_count = await plates_collection.count_documents({
            'created_at': {'$gte': yesterday}
        })
        
        return {
            "success": True,
            "statistics": {
                "total_detections": total_detections,
                "unique_plates": unique_plate_count,
                "recent_detections_24h": recent_count,
                "detections_by_location": location_stats,
                "detections_by_source_type": source_type_stats
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )

@router.post("/verify/{plate_id}", summary="Verify a license plate detection")
async def verify_plate_detection(
    plate_id: str,
    is_verified: bool = Form(..., description="Whether the detection is verified as correct"),
    corrected_text: Optional[str] = Form(None, description="Corrected plate text if OCR was wrong")
):
    """
    Verify or correct a license plate detection.
    
    - **plate_id**: ID of the plate detection record
    - **is_verified**: Whether the detection is correct
    - **corrected_text**: Corrected plate text if needed
    
    Updates the verification status of a detection record.
    """
    detector = get_detector()
    
    try:
        db = await detector._get_database()
        collection = db.license_plates
        
        # Find the record
        from bson import ObjectId
        try:
            record = await collection.find_one({'_id': ObjectId(plate_id)})
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plate detection record not found"
            )
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plate detection record not found"
            )
        
        # Update record
        update_data = {
            'is_verified': is_verified,
            'verified_at': datetime.utcnow()
        }
        
        if corrected_text:
            update_data['corrected_plate_text'] = corrected_text.upper()
            update_data['original_plate_text'] = record.get('plate_text', '')
        
        await collection.update_one(
            {'_id': ObjectId(plate_id)},
            {'$set': update_data}
        )
        
        return {
            "success": True,
            "plate_id": plate_id,
            "is_verified": is_verified,
            "corrected_text": corrected_text,
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify plate detection: {str(e)}"
        )

@router.delete("/detection/{detection_id}", summary="Delete a detection record")
async def delete_detection(detection_id: str):
    """
    Delete a detection record and all associated plate records.
    
    - **detection_id**: ID of the detection to delete
    
    Removes the detection and all associated plate records from the database.
    """
    detector = get_detector()
    
    try:
        db = await detector._get_database()
        
        # Delete from both collections
        from bson import ObjectId
        
        # Delete from license_plate_detections
        detections_collection = db.license_plate_detections
        detection_result = await detections_collection.delete_one({'_id': ObjectId(detection_id)})
        
        # Delete associated plate records
        plates_collection = db.license_plates
        plates_result = await plates_collection.delete_many({'detection_id': detection_id})
        
        if detection_result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detection record not found"
            )
        
        return {
            "success": True,
            "detection_id": detection_id,
            "deleted_detection_records": detection_result.deleted_count,
            "deleted_plate_records": plates_result.deleted_count,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete detection: {str(e)}"
        )

@router.get("/health", summary="Health check for plate detection service")
async def health_check():
    """
    Check the health status of the plate detection service.
    
    Returns status of detector components and database connectivity.
    """
    try:
        detector = get_detector()
        
        # Test database connection
        db_status = "connected"
        try:
            db = await detector._get_database()
            await db.list_collection_names()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "success": True,
            "service": "License Plate Detection API",
            "status": "healthy",
            "components": {
                "yolo_model": "available" if detector.yolo_available else "unavailable",
                "ocr_reader": "available" if detector.ocr_available else "unavailable",
                "database": db_status
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "service": "License Plate Detection API",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
