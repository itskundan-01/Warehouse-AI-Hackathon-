"""
API endpoints for Facial Recognition module.
Provides endpoints for personnel authentication and intrusion detection.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Form, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Dict, Any, Optional
import base64
import numpy as np
import cv2
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

# Local imports
from src.database import db  # Use the MongoDB client directly
from ...modules.facial_recognition.auth_manager import AuthenticationManager
from ...modules.facial_recognition.face_detector import FaceDetector
from ...modules.facial_recognition.face_recognizer import FaceRecognizer

# Create router
router = APIRouter()

# Initialize models
face_detector = FaceDetector(method="opencv-dnn")
face_recognizer = FaceRecognizer(method="arcface")

# Create authentication manager
face_auth_manager = AuthenticationManager(
    face_detector=face_detector,
    face_recognizer=face_recognizer
)

# Simple dependency for auth manager
def get_auth_manager():
    return face_auth_manager

# Pydantic models for request/response data
class PersonnelRegistrationRequest(BaseModel):
    employee_id: str = Field(..., description="Employee ID")
    name: str = Field(..., description="Full name of the personnel")
    department: str = Field("", description="Department name")
    access_level: int = Field(1, description="Access level (higher = more access)")
    face_image_base64: str = Field(..., description="Base64 encoded face image")

class PersonnelUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the personnel")
    department: Optional[str] = Field(None, description="Department name")
    access_level: Optional[int] = Field(None, description="Access level")
    is_active: Optional[bool] = Field(None, description="Active status")

class AuthenticationRequest(BaseModel):
    face_image_base64: str = Field(..., description="Base64 encoded face image")
    location: str = Field("main-entrance", description="Authentication location")
    camera_id: str = Field(..., description="Camera ID that captured the image")

class AuthenticationHistoryRequest(BaseModel):
    employee_id: Optional[str] = Field(None, description="Filter by employee ID")
    location: Optional[str] = Field(None, description="Filter by location")
    start_time: Optional[datetime] = Field(None, description="Filter by start time")
    end_time: Optional[datetime] = Field(None, description="Filter by end time")
    limit: int = Field(100, description="Maximum number of results to return")

# Thread pool for video processing
executor = ThreadPoolExecutor(max_workers=4)

@router.get("/")
async def facial_root():
    """Root endpoint for facial recognition."""
    return {
        "message": "Facial Recognition module API",
        "status": "Active",
    }

@router.post("/personnel", response_model=None)
async def register_personnel(
    request: PersonnelRegistrationRequest,
    # current_user: User = Depends(get_current_active_user),
):
    """Register a new personnel with facial recognition."""
    try:
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.face_image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if face_image is None:
                raise HTTPException(status_code=400, detail="Invalid image data")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error decoding image: {str(e)}")
        # Register personnel (replace with MongoDB logic)
        collection = db["personnel_records"]
        doc = {
            "employee_id": request.employee_id,
            "name": request.name,
            "department": request.department,
            "access_level": request.access_level,
            "face_image_base64": request.face_image_base64,
            "is_active": True,
            "created_at": datetime.utcnow(),
        }
        result = await collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return {
            "message": f"Personnel {request.name} registered successfully",
            "employee_id": request.employee_id,
            "personnel_id": doc["_id"]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to register personnel: {str(e)}"}
        )

@router.get("/personnel", response_model=None)
async def list_personnel(
    department: Optional[str] = None,
    is_active: bool = True,
    # current_user: User = Depends(get_current_active_user),
):
    """List personnel records with optional filtering."""
    try:
        collection = db["personnel_records"]
        query = {"is_active": is_active}
        if department:
            query["department"] = department
        cursor = collection.find(query)
        personnel = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            personnel.append(doc)
        return personnel
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to list personnel: {str(e)}"}
        )

@router.post("/authenticate", response_model=None)
async def authenticate_face(request: AuthenticationRequest):
    """Authenticate a person using facial recognition."""
    try:
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.face_image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            face_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if face_image is None:
                raise HTTPException(status_code=400, detail="Invalid image data")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error decoding image: {str(e)}")
        # First detect faces in the image
        faces = face_detector.detect_and_extract_faces(face_image)
        if not faces:
            return JSONResponse(
                status_code=400,
                content={"message": "No face detected in the image"}
            )
        # Authenticate first face (replace with MongoDB logic as needed)
        face_data = faces[0]
        # Example: search for personnel by face (stub)
        # In production, use face embedding matching
        collection = db["personnel_records"]
        personnel = await collection.find_one({"employee_id": "stub"})
        return {
            "authenticated": bool(personnel),
            "personnel_id": str(personnel["_id"]) if personnel else None,
            "name": personnel["name"] if personnel else None,
            "access_level": personnel["access_level"] if personnel else None,
            "confidence": 0.99 if personnel else 0,
            "processing_time": 0.1,
            "timestamp": datetime.utcnow().isoformat(),
            "message": None if personnel else "Not found"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to authenticate face: {str(e)}"}
        )

@router.post("/sync", response_model=None)
async def sync_database():
    """Synchronize database with face recognizer."""
    try:
        # Example: count personnel records
        collection = db["personnel_records"]
        db_count = await collection.count_documents({})
        return {
            "message": "Database synchronized successfully",
            "db_count": db_count,
            "recognizer_count": 0,
            "added": 0,
            "removed": 0
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Failed to sync database: {str(e)}"}
        )

@router.post("/process-video")
async def process_facial_video(
    location: str = Form(...),
    video: UploadFile = File(...)
):
    """
    Process a video file to detect and recognize faces throughout the video.
    """
    try:
        # Create directory for storing videos
        video_dir = "./data/videos/facial"
        os.makedirs(video_dir, exist_ok=True)
        
        # Save uploaded video
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"facial_{location}_{timestamp}.mp4"
        video_path = f"{video_dir}/{video_filename}"
        
        with open(video_path, "wb") as video_file:
            video_file.write(await video.read())
        
        # Process video in background
        result = await asyncio.get_event_loop().run_in_executor(
            executor, process_video_for_faces, video_path, location
        )
        
        return {
            "status": "success",
            "message": "Video processed successfully",
            "data": result,
            "video_file": video_filename
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process video: {str(e)}"
        )


@router.get("/stream-recognition/{location}")
async def stream_facial_recognition(location: str):
    """
    Stream real-time facial recognition from CCTV feed.
    """
    try:
        return StreamingResponse(
            generate_facial_recognition_stream(location),
            media_type="application/json"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start recognition stream: {str(e)}"
        )


def process_video_for_faces(video_path: str, location: str):
    """
    Process video file for face detection and recognition.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    results = []
    frame_count = 0
    detected_persons = {}
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process every 30th frame (approximately 1 frame per second for 30fps video)
        if frame_count % 30 == 0:
            # Detect faces in frame
            faces = face_detector.detect_faces_in_frame(frame)
            
            for face in faces:
                # Try to recognize the face
                person_id, confidence = face_recognizer.recognize_face_from_detection(frame, face)
                
                timestamp_seconds = float(frame_count / fps)
                
                # Determine if this is an authorized person
                is_authorized = person_id is not None and confidence > 0.7
                
                if person_id:
                    if person_id not in detected_persons:
                        detected_persons[person_id] = {
                            "first_seen": timestamp_seconds,
                            "last_seen": timestamp_seconds,
                            "confidence_scores": [float(confidence) if confidence is not None else 0.0],
                            "detection_count": 1
                        }
                    else:
                        detected_persons[person_id]["last_seen"] = timestamp_seconds
                        detected_persons[person_id]["confidence_scores"].append(
                            float(confidence) if confidence is not None else 0.0
                        )
                        detected_persons[person_id]["detection_count"] += 1
                
                result = {
                    "timestamp": timestamp_seconds,
                    "frame_number": int(frame_count),
                    "person_id": person_id,
                    "confidence": float(confidence) if confidence is not None else 0.0,
                    "is_authorized": is_authorized,
                    "bbox": [int(x) for x in face.get("bbox", [0, 0, 0, 0])],
                    "location": location,
                    "alert_type": "unauthorized_access" if not is_authorized else "authorized_access"
                }
                results.append(result)
        
        frame_count += 1
    
    cap.release()
    
    # Calculate summary statistics
    unauthorized_detections = [r for r in results if not r["is_authorized"]]
    authorized_detections = [r for r in results if r["is_authorized"]]
    
    summary = {
        "location": location,
        "video_file": video_path,
        "total_frames": total_frames,
        "fps": fps,
        "duration_seconds": total_frames / fps,
        "detected_persons": detected_persons,
        "all_detections": results,
        "authorized_detections": len(authorized_detections),
        "unauthorized_detections": len(unauthorized_detections),
        "unique_persons": len(detected_persons),
        "total_face_detections": len(results),
        "timestamp": datetime.utcnow(),
        "processing_type": "video_analysis"
    }
    
    # Store in database
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        collection = db["facial_recognition"]
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
        "authorized_detections": summary["authorized_detections"],
        "unauthorized_detections": summary["unauthorized_detections"],
        "unique_persons": summary["unique_persons"],
        "total_face_detections": summary["total_face_detections"],
        "detected_persons": summary["detected_persons"],
        "processing_type": summary["processing_type"],
        "timestamp": summary["timestamp"].isoformat()
    }
    
    return response


async def generate_facial_recognition_stream(location: str):
    """
    Generate real-time facial recognition stream.
    """
    # Simulate real-time CCTV feed processing
    while True:
        try:
            await asyncio.sleep(3)  # 3 second interval
            
            # Mock data for demonstration
            current_time = datetime.utcnow()
            mock_result = {
                "timestamp": current_time.isoformat(),
                "location": location,
                "person_id": "EMP001",  # This would be actual recognition result
                "person_name": "John Doe",
                "confidence": 0.87,
                "is_authorized": True,
                "access_level": 2,
                "department": "Warehouse Operations"
            }
            
            yield f"data: {str(mock_result)}\n\n"
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {str(error_data)}\n\n"
            break
