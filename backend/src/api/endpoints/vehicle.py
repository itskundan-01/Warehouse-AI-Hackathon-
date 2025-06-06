"""
API endpoints for Vehicle Recognition module.
Provides endpoints for license plate detection and vehicle authentication.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import os
import cv2
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, Path, HTTPException, status
from fastapi.responses import JSONResponse

from src.modules.vehicle_recognition.plate_detector import LicensePlateDetector
from src.modules.vehicle_recognition.ocr import LicensePlateOCR
from src.modules.vehicle_recognition.vehicle_tracker import VehicleTracker
from src.database import db  # Use the MongoDB client directly

# Create router
router = APIRouter()

# Thread pool for video processing
executor = ThreadPoolExecutor(max_workers=4)

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

@router.post("/process-video")
async def process_vehicle_video(
    location: str = Form(...),
    video: UploadFile = File(...)
):
    """
    Process a video file to detect vehicles and license plates throughout the video.
    """
    try:
        # Create directory for storing videos
        video_dir = "./data/videos/vehicles"
        os.makedirs(video_dir, exist_ok=True)
        
        # Save uploaded video
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"vehicle_{location}_{timestamp}.mp4"
        video_path = f"{video_dir}/{video_filename}"
        
        with open(video_path, "wb") as video_file:
            video_file.write(await video.read())
        
        # Process video in background
        result = await asyncio.get_event_loop().run_in_executor(
            executor, process_video_for_vehicles, video_path, location
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


@router.get("/stream-detection/{location}")
async def stream_vehicle_detection(location: str):
    """
    Stream real-time vehicle detection from CCTV feed.
    """
    try:
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            generate_vehicle_detection_stream(location),
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start detection stream: {str(e)}"
        )


def process_video_for_vehicles(video_path: str, location: str):
    """
    Process video file for vehicle and license plate detection.
    """
    plate_detector = LicensePlateDetector()
    ocr = LicensePlateOCR()
    tracker = VehicleTracker()
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    results = []
    frame_count = 0
    detected_vehicles = {}
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process every 30th frame (approximately 1 frame per second for 30fps video)
        if frame_count % 30 == 0:
            # Detect license plates in frame
            detections = plate_detector.detect_from_frame(frame)
            
            for detection in detections:
                # Extract license plate text
                plate_text = ocr.extract_text_from_detection(frame, detection)
                
                if plate_text and len(plate_text) > 3:  # Valid plate text
                    timestamp_seconds = frame_count / fps
                    
                    # Track vehicle
                    tracking_data = tracker.update(plate_text, location)
                    vehicle_id = tracking_data.get("tracking_id")
                    
                    if plate_text not in detected_vehicles:
                        detected_vehicles[plate_text] = {
                            "first_seen": timestamp_seconds,
                            "last_seen": timestamp_seconds,
                            "confidence_scores": [float(detection.get("confidence", 0.8))],
                            "vehicle_id": vehicle_id
                        }
                    else:
                        detected_vehicles[plate_text]["last_seen"] = timestamp_seconds
                        detected_vehicles[plate_text]["confidence_scores"].append(
                            float(detection.get("confidence", 0.8))
                        )
                    
                    result = {
                        "timestamp": timestamp_seconds,
                        "frame_number": frame_count,
                        "license_plate": plate_text,
                        "confidence": float(detection.get("confidence", 0.8)),
                        "bbox": [int(x) for x in detection.get("bbox", [0, 0, 0, 0])],
                        "vehicle_id": vehicle_id,
                        "location": location
                    }
                    results.append(result)
        
        frame_count += 1
    
    cap.release()
    
    # Compile summary
    summary = {
        "location": location,
        "video_file": video_path,
        "total_frames": total_frames,
        "fps": fps,
        "duration_seconds": total_frames / fps,
        "detected_vehicles": detected_vehicles,
        "detections": results,
        "unique_vehicles": len(detected_vehicles),
        "total_detections": len(results),
        "timestamp": datetime.utcnow(),
        "processing_type": "video_analysis"
    }
    
    # Store in database
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        collection = db["vehicles"]
        result = loop.run_until_complete(collection.insert_one(summary))
        processing_id = str(result.inserted_id)
    finally:
        loop.close()
    
    # Return response without MongoDB ObjectId
    response = {
        "success": True,
        "processing_id": processing_id,
        "location": summary["location"],
        "total_frames": summary["total_frames"],
        "fps": summary["fps"],
        "duration_seconds": summary["duration_seconds"],
        "detected_vehicles": summary["detected_vehicles"],
        "unique_vehicles": summary["unique_vehicles"],
        "total_detections": summary["total_detections"],
        "detections": summary["detections"],
        "processing_type": summary["processing_type"]
    }
    
    return response


async def generate_vehicle_detection_stream(location: str):
    """
    Generate real-time vehicle detection stream.
    """
    plate_detector = LicensePlateDetector()
    ocr = LicensePlateOCR()
    
    # Simulate real-time CCTV feed processing
    while True:
        try:
            await asyncio.sleep(2)  # 2 second interval
            
            # Mock data for demonstration
            current_time = datetime.utcnow()
            mock_result = {
                "timestamp": current_time.isoformat(),
                "location": location,
                "license_plate": "AP09XY1234",  # This would be actual OCR result
                "vehicle_type": "car",
                "entry_type": "entry",
                "confidence": 0.89,
                "authorized": True
            }
            
            yield f"data: {str(mock_result)}\n\n"
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {str(error_data)}\n\n"
            break