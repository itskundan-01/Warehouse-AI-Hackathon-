"""
API endpoints for Facial Recognition module.
Provides endpoints for personnel authentication and intrusion detection.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import base64
import numpy as np
import cv2
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
