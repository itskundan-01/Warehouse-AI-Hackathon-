"""
Pydantic models for API request and response validation.
These models are separate from the database models and represent the API contract.
"""
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, AnyHttpUrl


# Base models with shared properties
class BaseResponse(BaseModel):
    """Base response model with status information."""
    status: str = "success"
    message: Optional[str] = None


class BaseErrorResponse(BaseResponse):
    """Base error response model."""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    error_code: Optional[str] = None


class PaginatedResponse(BaseResponse):
    """Response model for paginated results."""
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool


# User models
class UserBase(BaseModel):
    """Base model for user data."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Model for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Response model for user data."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []

    class Config:
        from_attributes = True


# Authentication models
class Token(BaseModel):
    """Token model for authentication."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class TokenData(BaseModel):
    """Model for token payload."""
    user_id: UUID
    username: str
    roles: List[str] = []
    exp: datetime


# Gunny Bag models
class GunnyBagCountCreate(BaseModel):
    """Model for creating a new gunny bag count record."""
    count: int = Field(..., gt=0)
    estimated_volume: Optional[float] = None
    location: str
    video_reference: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    bag_metadata: Optional[Dict[str, Any]] = None


class GunnyBagCountResponse(BaseModel):
    """Response model for gunny bag count data."""
    id: UUID
    count: int
    estimated_volume: Optional[float] = None
    location: str
    timestamp: datetime
    video_reference: Optional[str] = None
    confidence_score: Optional[float] = None
    bag_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Vehicle models
class VehicleCreate(BaseModel):
    """Model for creating a new vehicle record."""
    license_plate: str = Field(..., min_length=3, max_length=20)
    vehicle_type: Optional[str] = None
    is_authorized: bool = False
    vehicle_metadata: Optional[Dict[str, Any]] = None


class VehicleResponse(BaseModel):
    """Response model for vehicle data."""
    id: UUID
    license_plate: str
    vehicle_type: Optional[str] = None
    is_authorized: bool
    vehicle_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleEntryCreate(BaseModel):
    """Model for creating a new vehicle entry record."""
    vehicle_id: UUID
    entry_type: str = Field(..., pattern="^(ENTRY|EXIT)$")
    location: Optional[str] = None
    image_path: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class VehicleEntryResponse(BaseModel):
    """Response model for vehicle entry data."""
    id: UUID
    vehicle_id: UUID
    entry_type: str
    timestamp: datetime
    location: Optional[str] = None
    image_path: Optional[str] = None
    confidence_score: Optional[float] = None
    vehicle: VehicleResponse

    class Config:
        from_attributes = True


# Facial Recognition models
class FaceEmbeddingCreate(BaseModel):
    """Model for creating a new face embedding record."""
    user_id: UUID
    embedding_data: bytes
    thumbnail: Optional[bytes] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class FaceEmbeddingResponse(BaseModel):
    """Response model for face embedding data."""
    id: UUID
    user_id: UUID
    thumbnail: Optional[bytes] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Video Event models
class VideoEventCreate(BaseModel):
    """Model for creating a new video event record."""
    event_type: str
    location: Optional[str] = None
    description: Optional[str] = None
    video_segment_start: Optional[float] = None
    video_segment_end: Optional[float] = None
    video_reference: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_anomaly: bool = False
    event_metadata: Optional[Dict[str, Any]] = None
    vector_embedding: Optional[bytes] = None


class VideoEventResponse(BaseModel):
    """Response model for video event data."""
    id: UUID
    event_type: str
    timestamp: datetime
    location: Optional[str] = None
    description: Optional[str] = None
    video_segment_start: Optional[float] = None
    video_segment_end: Optional[float] = None
    video_reference: Optional[str] = None
    confidence_score: Optional[float] = None
    is_anomaly: bool
    event_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


# Query models
class VideoQuery(BaseModel):
    """Model for querying video events."""
    query: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None
    is_anomaly: Optional[bool] = None
    limit: int = 10
    offset: int = 0