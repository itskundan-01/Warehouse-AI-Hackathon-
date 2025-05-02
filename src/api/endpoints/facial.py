"""
API endpoints for Facial Recognition module.
Provides endpoints for personnel authentication and intrusion detection.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import base64
import io
import cv2
import numpy as np
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

# Local imports
from ...core.utils import get_db_session
from ...database.models import PersonnelRecord, FacialDetection, User
from ...modules.facial_recognition.auth_manager import AuthenticationManager
from ...modules.facial_recognition.face_detector import FaceDetector
from ...modules.facial_recognition.face_recognizer import FaceRecognizer
from ...core.security import get_current_active_user, oauth2_scheme

# Create router
router = APIRouter()

# Initialize models
face_detector = FaceDetector(method="opencv-dnn")
face_recognizer = FaceRecognizer(method="arcface")

# Create authentication manager
auth_manager = None

def get_auth_manager(db_session=Depends(get_db_session)):
    """Get or initialize authentication manager"""
    global auth_manager
    if auth_manager is None:
        auth_manager = AuthenticationManager(
            db_session_factory=get_db_session,
            face_detector=face_detector,
            face_recognizer=face_recognizer
        )
    return auth_manager

# Pydantic models for request/response data
class PersonnelRegistrationRequest(BaseModel):
    employee_id: str = Field(..., description="Employee ID")
    name: str = Field(..., description="Full name of the personnel")
    department: str = Field("", description="Department name")
    access_level: int = Field(1, description="Access level (higher = more access)")
    face_image_base64: str = Field(..., description="Base64 encoded face image")

class PersonnelUpdateRequest(BaseModel):
    employee_id: str = Field(..., description="Employee ID")
    name: Optional[str] = Field(None, description="Full name of the personnel")
    department: Optional[str] = Field(None, description="Department name")
    access_level: Optional[int] = Field(None, description="Access level (higher = more access)")
    is_active: Optional[bool] = Field(None, description="Whether the personnel is active")

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
    """
    Root endpoint for facial recognition.
    """
    return {
        "message": "Facial Recognition module API",
        "status": "Active",
        "supported_endpoints": [
            "/personnel", 
            "/personnel/{employee_id}",
            "/authenticate",
            "/history",
            "/unauthorized"
        ]
    }

@router.post("/personnel", status_code=201)
async def register_personnel(
    request: PersonnelRegistrationRequest,
    current_user: User = Depends(get_current_active_user),
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Register a new personnel with facial recognition.
    """
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
    result = auth_manager.register_personnel(
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

@router.get("/personnel", response_model=List[Dict[str, Any]])
async def list_personnel(
    department: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    List personnel records with optional filtering.
    """
    query = db.query(PersonnelRecord)
    
    if department:
        query = query.filter(PersonnelRecord.department == department)
    
    query = query.filter(PersonnelRecord.is_active == is_active)
    
    personnel = query.all()
    
    result = []
    for p in personnel:
        result.append({
            "employee_id": p.employee_id,
            "name": p.name,
            "department": p.department,
            "access_level": p.access_level,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        })
    
    return result

@router.get("/personnel/{employee_id}")
async def get_personnel(
    employee_id: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details for a specific personnel record.
    """
    personnel = db.query(PersonnelRecord).filter(
        PersonnelRecord.employee_id == employee_id
    ).first()
    
    if not personnel:
        raise HTTPException(status_code=404, detail=f"Personnel with ID {employee_id} not found")
    
    # Count detections in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    detection_count = db.query(FacialDetection).filter(
        FacialDetection.personnel_id == personnel.id,
        FacialDetection.detection_time >= thirty_days_ago
    ).count()
    
    # Get last detection
    last_detection = db.query(FacialDetection).filter(
        FacialDetection.personnel_id == personnel.id
    ).order_by(FacialDetection.detection_time.desc()).first()
    
    return {
        "employee_id": personnel.employee_id,
        "name": personnel.name,
        "department": personnel.department,
        "access_level": personnel.access_level,
        "is_active": personnel.is_active,
        "created_at": personnel.created_at.isoformat() if personnel.created_at else None,
        "updated_at": personnel.updated_at.isoformat() if personnel.updated_at else None,
        "detection_count_30d": detection_count,
        "last_detected": last_detection.detection_time.isoformat() if last_detection else None,
        "last_location": last_detection.location if last_detection else None
    }

@router.put("/personnel/{employee_id}")
async def update_personnel(
    employee_id: str,
    request: PersonnelUpdateRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Update a personnel record.
    """
    personnel = db.query(PersonnelRecord).filter(
        PersonnelRecord.employee_id == employee_id
    ).first()
    
    if not personnel:
        raise HTTPException(status_code=404, detail=f"Personnel with ID {employee_id} not found")
    
    # Update fields if provided
    if request.name is not None:
        personnel.name = request.name
    
    if request.department is not None:
        personnel.department = request.department
    
    if request.access_level is not None:
        # Use auth_manager to update access level
        result = auth_manager.update_access_level(
            employee_id=employee_id,
            new_access_level=request.access_level,
            user_id=str(current_user.id)
        )
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Failed to update access level')
            )
    
    if request.is_active is not None and request.is_active != personnel.is_active:
        if request.is_active:
            # Reactivate
            personnel.is_active = True
        else:
            # Deactivate using auth_manager
            result = auth_manager.deactivate_personnel(
                employee_id=employee_id,
                user_id=str(current_user.id)
            )
            
            if not result.get('success', False):
                raise HTTPException(
                    status_code=400, 
                    detail=result.get('error', 'Failed to deactivate personnel')
                )
    
    # Update timestamp
    personnel.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Personnel {employee_id} updated successfully",
        "employee_id": employee_id
    }

@router.delete("/personnel/{employee_id}")
async def deactivate_personnel(
    employee_id: str,
    current_user: User = Depends(get_current_active_user),
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Deactivate (soft delete) a personnel record.
    """
    result = auth_manager.deactivate_personnel(
        employee_id=employee_id,
        user_id=str(current_user.id)
    )
    
    if not result.get('success', False):
        raise HTTPException(
            status_code=404 if "not found" in result.get('error', '') else 400, 
            detail=result.get('error', 'Failed to deactivate personnel')
        )
    
    return {
        "message": f"Personnel {employee_id} deactivated successfully",
        "employee_id": employee_id
    }

@router.post("/authenticate")
async def authenticate_face(
    request: AuthenticationRequest,
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Authenticate a person using facial recognition.
    """
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
    result = auth_manager.authenticate_face(
        face_image=face_data['face_image'],
        location=request.location,
        camera_id=request.camera_id
    )
    
    # Remove potentially sensitive data
    if 'error' in result and not result['authenticated']:
        return {
            "authenticated": False,
            "message": result.get('error', 'Authentication failed'),
            "confidence": result.get('confidence', 0),
            "processing_time": result.get('processing_time', 0)
        }
    
    # Success case
    return {
        "authenticated": True,
        "personnel_id": result.get('personnel_id'),
        "name": result.get('name'),
        "access_level": result.get('access_level'),
        "confidence": result.get('confidence', 0),
        "processing_time": result.get('processing_time', 0),
        "timestamp": result.get('timestamp')
    }

@router.post("/history")
async def authentication_history(
    request: AuthenticationHistoryRequest,
    current_user: User = Depends(get_current_active_user),
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Get authentication history with optional filtering.
    """
    history = auth_manager.get_authentication_history(
        employee_id=request.employee_id,
        start_time=request.start_time,
        end_time=request.end_time,
        location=request.location,
        limit=request.limit
    )
    
    return {
        "count": len(history),
        "results": history
    }

@router.get("/unauthorized")
async def unauthorized_access(
    days: int = Query(7, description="Number of days to look back"),
    location: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Get unauthorized access attempts.
    """
    start_time = datetime.utcnow() - timedelta(days=days)
    
    attempts = auth_manager.get_unauthorized_access_attempts(
        start_time=start_time,
        location=location,
        limit=100
    )
    
    return {
        "count": len(attempts),
        "results": attempts
    }

@router.post("/sync")
async def sync_database(
    current_user: User = Depends(get_current_active_user),
    auth_manager: AuthenticationManager = Depends(get_auth_manager)
):
    """
    Synchronize database with face recognizer.
    """
    result = auth_manager.sync_database_with_recognizer()
    
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