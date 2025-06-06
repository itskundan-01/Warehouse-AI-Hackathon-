"""
API endpoints for Gunny Bag Counter module.
Provides endpoints for counting, tracking, and managing gunny bags in the warehouse.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import os
import cv2
import asyncio
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, UploadFile, Query, Path, HTTPException, status, Form
from fastapi.responses import JSONResponse, StreamingResponse

from src.database import db  # Use the MongoDB client directly
from src.modules.gunny_counter.detector import GunnyBagDetector
from src.modules.gunny_counter.counter import GunnyBagCounter
from src.modules.gunny_counter.volumetric import VolumetricEstimator

# Create router
router = APIRouter()

# Thread pool for video processing
executor = ThreadPoolExecutor(max_workers=4)


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


@router.post(
    "/process-video", 
    response_model=None,
    status_code=status.HTTP_201_CREATED
)
async def process_gunny_video(
    location: str = Form(...),
    video: UploadFile = File(...)
):
    """
    Process a video file to count gunny bags throughout the video.
    Returns real-time analysis results with timestamps.
    """
    try:
        # Create directory for storing videos
        video_dir = "./data/videos/gunny"
        os.makedirs(video_dir, exist_ok=True)
        
        # Save uploaded video
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"gunny_{location}_{timestamp}.mp4"
        video_path = f"{video_dir}/{video_filename}"
        
        with open(video_path, "wb") as video_file:
            video_file.write(await video.read())
        
        # Process video in background
        result = await asyncio.get_event_loop().run_in_executor(
            executor, process_video_for_gunny_bags, video_path, location
        )
        
        return {
            "status": "success",
            "message": "Video processed successfully",
            "data": result,
            "video_file": video_filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process video: {str(e)}"
        )


@router.get("/stream-analysis/{location}")
async def stream_gunny_analysis(location: str):
    """
    Stream real-time gunny bag analysis from CCTV feed.
    """
    try:
        return StreamingResponse(
            generate_gunny_analysis_stream(location),
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis stream: {str(e)}"
        )


def process_video_for_gunny_bags(video_path: str, location: str):
    """
    Process video file for gunny bag detection and counting.
    """
    detector = GunnyBagDetector()
    counter = GunnyBagCounter()
    volumetric = VolumetricEstimator()
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    results = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process every 30th frame (approximately 1 frame per second for 30fps video)
        if frame_count % 30 == 0:
            detections_list = detector.detect_from_frame(frame)
            # Convert to numpy array format expected by counter
            detections = np.array([[d["bbox"][0], d["bbox"][1], d["bbox"][2], d["bbox"][3], d["confidence"], d["class_id"]] for d in detections_list]) if detections_list else np.array([])
            count = counter.count(detections)
            volume = volumetric.estimate_volume(detections)
            
            timestamp_seconds = frame_count / fps
            
            result = {
                "timestamp": timestamp_seconds,
                "frame_number": frame_count,
                "gunny_count": count,
                "estimated_volume": volume,
                "detections": len(detections) if len(detections) > 0 else 0,
                "location": location
            }
            results.append(result)
        
        frame_count += 1
    
    cap.release()
    
    # Convert numpy data types to Python native types for MongoDB compatibility
    clean_results = []
    for result in results:
        clean_result = {
            "timestamp": float(result["timestamp"]),
            "frame_number": int(result["frame_number"]),
            "gunny_count": int(result["gunny_count"]) if isinstance(result["gunny_count"], (np.integer, np.floating)) else result["gunny_count"],
            "estimated_volume": float(result["estimated_volume"]) if isinstance(result["estimated_volume"], (np.floating, np.integer)) else result["estimated_volume"],
            "detections": int(result["detections"]),
            "location": str(result["location"])
        }
        clean_results.append(clean_result)
    
    # Save to database
    summary = {
        "location": location,
        "video_file": video_path,
        "total_frames": int(total_frames),
        "fps": float(fps),
        "duration_seconds": float(total_frames / fps),
        "analysis_results": clean_results,
        "max_count": int(max([r["gunny_count"] for r in clean_results])) if clean_results else 0,
        "avg_count": float(sum([r["gunny_count"] for r in clean_results]) / len(clean_results)) if clean_results else 0.0,
        "timestamp": datetime.utcnow(),
        "processing_type": "video_analysis"
    }
    
    # Store in database using proper async context
    try:
        # Get current event loop or create a new one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        collection = loop.run_until_complete(get_gunny_collection())
        result = loop.run_until_complete(collection.insert_one(summary))
        processing_id = str(result.inserted_id)
    except Exception as db_error:
        print(f"Database error: {db_error}")
        # If database fails, still return processing results
        processing_id = "local_processing"
    
    # Return response without MongoDB ObjectId
    response = {
        "success": True,
        "processing_id": processing_id,
        "location": summary["location"],
        "total_frames": summary["total_frames"],
        "fps": summary["fps"],
        "duration_seconds": summary["duration_seconds"],
        "max_count": summary["max_count"],
        "avg_count": summary["avg_count"],
        "analysis_results": summary["analysis_results"][:10],  # Limit results in response for performance
        "total_analysis_frames": len(summary["analysis_results"]),
        "processing_type": summary["processing_type"]
    }
    
    return response


async def generate_gunny_analysis_stream(location: str):
    """
    Generate real-time analysis stream for gunny bags.
    """
    detector = GunnyBagDetector()
    counter = GunnyBagCounter()
    
    # Simulate real-time CCTV feed processing
    # In production, this would connect to actual CCTV cameras
    while True:
        try:
            # Simulate frame processing
            # In real implementation, get frame from CCTV feed
            await asyncio.sleep(1)  # 1 second interval
            
            # Mock data for demonstration
            current_time = datetime.utcnow()
            mock_result = {
                "timestamp": current_time.isoformat(),
                "location": location,
                "gunny_count": 15,  # This would be actual detection result
                "estimated_volume": 45.5,
                "status": "operational",
                "confidence": 0.92
            }
            
            yield f"data: {str(mock_result)}\n\n"
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {str(error_data)}\n\n"
            break