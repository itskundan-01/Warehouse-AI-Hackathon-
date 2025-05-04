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
from ...database.operations import get_db
from ...database.models import User
from ...modules.facial_recognition.auth_manager import AuthenticationManager
from ...modules.facial_recognition.face_detector import FaceDetector
from ...modules.facial_recognition.face_recognizer import FaceRecognizer
from ...core.security import get_current_active_user

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
    current_user: User = Depends(get_current_active_user),
):
    """Register a new personnel with facial recognition."""
    # Get db session without type annotations
    async for db in get_db():
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
            
            # Register personnel
            result = face_auth_manager.register_personnel(
                db=db,
                face_image=face_image,
                employee_id=request.employee_id,
                name=request.name,
                department=request.department,
                access_level=request.access_level,
                user_id=str(current_user.id)
            )
            
            if not result.get('success', False):
                raise HTTPException(
                    status_code=400, 
                    detail=result.get('error', 'Unknown error during registration')
                )
            
            return {
                "message": f"Personnel {request.name} registered successfully",
                "employee_id": request.employee_id,
                "processing_time": result.get('processing_time', 0)
            }
        finally:
            await db.close()

@router.get("/personnel", response_model=None)
async def list_personnel(
    department: Optional[str] = None,
    is_active: bool = True,
    current_user: User = Depends(get_current_active_user),
):
    """List personnel records with optional filtering."""
    async for db in get_db():
        try:
            from sqlalchemy.future import select
            stmt = select(db.get_bind().registry.metadata.tables['personnel_records'])
            if department:
                stmt = stmt.where(db.get_bind().registry.metadata.tables['personnel_records'].c.department == department)
            stmt = stmt.where(db.get_bind().registry.metadata.tables['personnel_records'].c.is_active == is_active)
            result = await db.execute(stmt)
            personnel = result.mappings().all()
            return list(personnel)
        finally:
            await db.close()

@router.post("/authenticate", response_model=None)
async def authenticate_face(request: AuthenticationRequest):
    """Authenticate a person using facial recognition."""
    async for db in get_db():
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
            
            # Authenticate first face
            face_data = faces[0]
            result = face_auth_manager.authenticate_face(
                db=db,
                face_image=face_data['face_image'],
                location=request.location,
                camera_id=request.camera_id
            )
            
            return {
                "authenticated": result.get('authenticated', False),
                "personnel_id": result.get('personnel_id'),
                "name": result.get('name'),
                "access_level": result.get('access_level'),
                "confidence": result.get('confidence', 0),
                "processing_time": result.get('processing_time', 0),
                "timestamp": result.get('timestamp'),
                "message": result.get('error') if 'error' in result else None
            }
        finally:
            await db.close()

@router.post("/sync", response_model=None)
async def sync_database(current_user: User = Depends(get_current_active_user)):
    """Synchronize database with face recognizer."""
    async for db in get_db():
        try:
            result = face_auth_manager.sync_database_with_recognizer(db=db)
            
            if not result.get('success', False):
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": "Synchronization failed",
                        "errors": result.get('errors', []),
                        "details": result
                    }
                )
            
            return {
                "message": "Database synchronized successfully",
                "db_count": result.get('db_count', 0),
                "recognizer_count": result.get('recognizer_count', 0),
                "added": result.get('added', 0),
                "removed": result.get('removed', 0)
            }
        finally:
            await db.close()
