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
from src.modules.gunny_counter.improved_detector import ImprovedGunnyBagDetector

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
        improved_detector = ImprovedGunnyBagDetector()
        counter = GunnyBagCounter(enable_line_crossing=True, use_improved_detector=True)  # Enable enhanced detection
        volumetric = VolumetricEstimator()
        
        # Read the image for processing
        img_array = cv2.imread(f"{image_dir}/{image_path}")
        
        # Use improved detector for better accuracy
        detections = improved_detector.detect(img_array)
        
        # Fallback to original detector if improved detector finds nothing
        if len(detections) == 0:
            detections = detector.detect(f"{image_dir}/{image_path}")
            detector_used = "original"
        else:
            detector_used = "improved"
        
        count_results = counter.count(detections, img_array)  # Pass frame for line detection
        estimated_volume = volumetric.estimate_volume(detections)
        
        collection = await get_gunny_collection()
        doc = {
            "static_count": count_results['static_count'],
            "crossing_count": count_results.get('crossing_count'),
            "total_tracked": count_results.get('total_tracked'),
            "crossing_line_detected": count_results.get('crossing_line_detected'),
            "estimated_volume": estimated_volume,
            "location": location,
            "image_path": image_path,
            "confidence_score": getattr(detector, 'last_confidence', None),
            "detector_used": detector_used,
            "bag_metadata": {
                "detection_boxes": getattr(detections, 'tolist', lambda: detections)(),
                "line_crossing_enabled": counter.enable_line_crossing,
                "improved_detector_enabled": counter.use_improved_detector,
                "red_line_coordinates": improved_detector.get_red_line()
            },
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
            "success": True,
            "status": "success",
            "message": "Video processed successfully",
            "processing_id": result.get("processing_id", f"gunny_{location}_{timestamp}"),
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


@router.post(
    "/count-with-tracking", 
    response_model=None,
    status_code=status.HTTP_201_CREATED
)
async def count_gunny_bags_with_line_crossing(
    location: str,
    image: UploadFile = File(...),
    return_visualization: bool = Query(False, description="Return image with tracking visualization")
):
    """
    Count gunny bags with enhanced line-crossing detection and tracking.
    Specifically designed to detect red vertical line and count bags crossing it.
    """
    try:
        # Create directory for storing images
        image_dir = "./data/images/gunny"
        os.makedirs(image_dir, exist_ok=True)
        image_path = f"gunny_tracking_{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        full_image_path = f"{image_dir}/{image_path}"
        
        with open(full_image_path, "wb") as image_file:
            image_file.write(await image.read())
        
        # Initialize modules with line-crossing enabled
        detector = GunnyBagDetector()
        improved_detector = ImprovedGunnyBagDetector()
        counter = GunnyBagCounter(enable_line_crossing=True, use_improved_detector=True)
        volumetric = VolumetricEstimator()
        
        # Read the image for processing
        img_array = cv2.imread(full_image_path)
        if img_array is None:
            raise HTTPException(
                status_code=400,
                detail="Could not read the uploaded image"
            )
        
        # Use improved detector for better accuracy
        detections = improved_detector.detect(img_array)
        
        # Fallback to original detector if improved detector finds nothing
        if len(detections) == 0:
            detections = detector.detect(full_image_path)
            detector_used = "original"
        else:
            detector_used = "improved"
        
        # Count with line-crossing detection
        count_results = counter.count(detections, img_array)
        
        # Estimate volume
        estimated_volume = volumetric.estimate_volume(detections)
        
        # Prepare response data
        response_data = {
            "static_count": count_results['static_count'],
            "crossing_count": count_results.get('crossing_count', 0),
            "total_tracked": count_results.get('total_tracked', 0),
            "active_tracks": count_results.get('active_tracks', 0),
            "crossing_line_detected": count_results.get('crossing_line_detected', False),
            "estimated_volume": estimated_volume,
            "location": location,
            "image_path": image_path,
            "detector_used": detector_used,
            "confidence_score": getattr(detector, 'last_confidence', None),
            "line_crossing_enabled": counter.enable_line_crossing,
            "red_line_coordinates": improved_detector.get_red_line(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add visualization if requested
        if return_visualization:
            vis_frame = counter.get_tracking_visualization(img_array)
            if vis_frame is not None:
                # Save visualization image
                vis_path = f"vis_{image_path}"
                vis_full_path = f"{image_dir}/{vis_path}"
                cv2.imwrite(vis_full_path, vis_frame)
                response_data["visualization_path"] = vis_path
        
        # Save to database
        collection = await get_gunny_collection()
        doc = {
            **response_data,
            "bag_metadata": {
                "detection_boxes": getattr(detections, 'tolist', lambda: detections)(),
                "line_crossing_enabled": True,
                "tracking_method": "red_line_crossing"
            },
            "timestamp": datetime.utcnow()
        }
        
        result = await collection.insert_one(doc)
        response_data["_id"] = str(result.inserted_id)
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process gunny bag tracking: {str(e)}"
        )


@router.post(
    "/reset-crossing-count",
    response_model=None
)
async def reset_crossing_count():
    """
    Reset the line-crossing count to zero.
    Useful for starting a new counting session.
    """
    try:
        # Create a temporary counter to reset (in real implementation, 
        # this would be managed by a persistent service)
        counter = GunnyBagCounter(enable_line_crossing=True)
        counter.reset_crossing_count()
        
        return {
            "status": "success",
            "message": "Crossing count reset to zero",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset crossing count: {str(e)}"
        )


def process_video_for_gunny_bags(video_path: str, location: str):
    """
    Process video file for gunny bag detection and counting with line-crossing tracking.
    """
    detector = GunnyBagDetector()
    improved_detector = ImprovedGunnyBagDetector()
    counter = GunnyBagCounter(enable_line_crossing=True, use_improved_detector=True)  # Enable enhanced detection
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
            
        frame_count += 1
        
        # Process every 30th frame (approximately 1 second at 30fps)
        if frame_count % 30 == 0:
            try:
                # Use improved detector for better accuracy
                detections = improved_detector.detect(frame)
                
                # Fallback to original detector if improved detector finds nothing
                if len(detections) == 0:
                    # Save frame temporarily for original detector
                    temp_frame_path = f"./data/temp_frame_{frame_count}.jpg"
                    cv2.imwrite(temp_frame_path, frame)
                    detections = detector.detect(temp_frame_path)
                    # Clean up temp file
                    if os.path.exists(temp_frame_path):
                        os.remove(temp_frame_path)
                    detector_used = "original"
                else:
                    detector_used = "improved"
                
                count_results = counter.count(detections, frame)
                estimated_volume = volumetric.estimate_volume(detections)
                
                # Calculate timestamp in video
                timestamp_seconds = frame_count / fps
                
                frame_result = {
                    "frame_number": frame_count,
                    "timestamp_seconds": timestamp_seconds,
                    "static_count": count_results['static_count'],
                    "crossing_count": count_results.get('crossing_count', 0),
                    "total_tracked": count_results.get('total_tracked', 0),
                    "crossing_line_detected": count_results.get('crossing_line_detected', False),
                    "estimated_volume": estimated_volume,
                    "detector_used": detector_used,
                    "location": location
                }
                
                results.append(frame_result)
                    
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                continue
    
    cap.release()
    
    # Calculate summary statistics
    if results:
        max_static_count = max(r['static_count'] for r in results)
        final_crossing_count = counter.get_crossing_count()
        avg_volume = sum(r['estimated_volume'] for r in results) / len(results)
        
        summary = {
            "total_frames_processed": len(results),
            "max_static_count": max_static_count,
            "final_crossing_count": final_crossing_count,
            "average_estimated_volume": avg_volume,
            "video_duration_seconds": total_frames / fps if fps > 0 else 0,
            "line_crossing_detected": any(r['crossing_line_detected'] for r in results),
            "frame_results": results
        }
    else:
        summary = {
            "total_frames_processed": 0,
            "max_static_count": 0,
            "final_crossing_count": 0,
            "average_estimated_volume": 0,
            "video_duration_seconds": 0,
            "line_crossing_detected": False,
            "frame_results": []
        }
    
    return summary


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