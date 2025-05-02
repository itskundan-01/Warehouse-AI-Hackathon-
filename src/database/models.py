"""
SQLAlchemy models for WarehouseVision AI.
Defines the database schema for all entities in the system.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, 
    ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserRole(PyEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    SECURITY = "security"


class EventType(PyEnum):
    VEHICLE_ENTRY = "vehicle_entry"
    VEHICLE_EXIT = "vehicle_exit"
    UNAUTHORIZED_PERSON = "unauthorized_person"
    GUNNY_BAG_COUNT_CHANGE = "gunny_bag_count_change"
    ANOMALY_DETECTED = "anomaly_detected"
    SYSTEM_ERROR = "system_error"


class User(Base):
    """
    User model representing system users with authentication and authorization details.
    """
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    events = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class PersonnelRecord(Base):
    """
    Personnel model for facial recognition and personnel tracking.
    """
    __tablename__ = "personnel_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=True)
    access_level = Column(Integer, nullable=False, default=0)
    face_embedding = Column(JSON, nullable=True)  # Stored as JSON array
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    detections = relationship("FacialDetection", back_populates="personnel")
    
    def __repr__(self):
        return f"<Personnel {self.employee_id}>"


class FacialDetection(Base):
    """
    Record of facial detections in the system.
    """
    __tablename__ = "facial_detections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personnel_id = Column(String(36), ForeignKey("personnel_records.id"), nullable=True)
    detection_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    confidence_score = Column(Float, nullable=False)
    location = Column(String(100), nullable=True)
    camera_id = Column(String(50), nullable=False)
    embedding = Column(JSON, nullable=True)  # For unknown faces
    thumbnail_path = Column(String(255), nullable=True)
    is_authorized = Column(Boolean, nullable=False)
    
    # Relationships
    personnel = relationship("PersonnelRecord", back_populates="detections")
    
    def __repr__(self):
        return f"<FacialDetection {self.id} at {self.detection_time}>"


class Vehicle(Base):
    """
    Vehicle record for tracking and authorization.
    """
    __tablename__ = "vehicles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    license_plate = Column(String(20), nullable=False, unique=True, index=True)
    vehicle_type = Column(String(50), nullable=True)
    owner_name = Column(String(100), nullable=True)
    is_authorized = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    detections = relationship("VehicleDetection", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle {self.license_plate}>"


class VehicleDetection(Base):
    """
    Record of vehicle detections in the system.
    """
    __tablename__ = "vehicle_detections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"), nullable=True)
    detection_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    license_plate_text = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    location = Column(String(100), nullable=False)
    camera_id = Column(String(50), nullable=False)
    is_entry = Column(Boolean, nullable=True)  # True for entry, False for exit, None for unknown
    thumbnail_path = Column(String(255), nullable=True)
    meta_data = Column(JSON, nullable=True)  # Changed from JSONB to JSON for MySQL
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="detections")
    
    def __repr__(self):
        return f"<VehicleDetection {self.license_plate_text} at {self.detection_time}>"


class GunnyBagCount(Base):
    """
    Record of gunny bag counts and volume estimates.
    """
    __tablename__ = "gunny_bag_counts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(100), nullable=False)
    camera_id = Column(String(50), nullable=False)
    bag_count = Column(Integer, nullable=False)
    estimated_volume = Column(Float, nullable=True)  # in cubic meters
    confidence_score = Column(Float, nullable=False)
    image_path = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)  # Changed from JSONB to JSON for MySQL
    
    def __repr__(self):
        return f"<GunnyBagCount {self.bag_count} at {self.timestamp}>"


class Event(Base):
    """
    System events for tracking and alerting.
    """
    __tablename__ = "events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(100), nullable=True)
    camera_id = Column(String(50), nullable=True)
    severity = Column(Integer, nullable=False, default=0)  # 0=info, 1=warning, 2=critical
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    related_entity_id = Column(String(36), nullable=True)  # Generic foreign key
    related_entity_type = Column(String(50), nullable=True)  # Type of the related entity
    meta_data = Column(JSON, nullable=True)  # Changed from JSONB to JSON for MySQL
    
    def __repr__(self):
        return f"<Event {self.event_type} at {self.timestamp}>"


class AuditLog(Base):
    """
    Audit logs for system actions.
    """
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(36), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="events")
    
    def __repr__(self):
        return f"<AuditLog {self.action} at {self.timestamp}>"


class ContextualQuery(Base):
    """
    Record of contextual intelligence queries and results.
    """
    __tablename__ = "contextual_queries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    query_text = Column(Text, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    results = Column(JSON, nullable=True)  # Changed from JSONB to JSON for MySQL
    execution_time = Column(Float, nullable=True)  # in seconds
    
    def __repr__(self):
        return f"<ContextualQuery {self.id} at {self.timestamp}>"


class VideoSegment(Base):
    """
    Indexed video segments for contextual search.
    """
    __tablename__ = "video_segments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    camera_id = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    file_path = Column(String(255), nullable=False)
    duration = Column(Float, nullable=False)  # in seconds
    embedding = Column(JSON, nullable=True)  # Feature vector
    meta_data = Column(JSON, nullable=True)  # Objects, activities detected (Changed from JSONB to JSON)
    tags = Column(JSON, nullable=True)  # Array of tags (Changed from JSONB to JSON)
    
    def __repr__(self):
        return f"<VideoSegment {self.camera_id} {self.start_time}>"
