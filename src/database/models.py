from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String, 
    Float, Text, Table, Enum, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

Base = declarative_base()

# Association tables
user_role_association = Table(
    'user_role_association', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    users = relationship("User", secondary=user_role_association, back_populates="roles")
    
    def __repr__(self):
        return f"<Role(name='{self.name}')>"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    roles = relationship("Role", secondary=user_role_association, back_populates="users")
    face_embeddings = relationship("FaceEmbedding", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    embedding_data = Column(LargeBinary, nullable=False)  # Store vector embedding
    thumbnail = Column(LargeBinary)  # Small image for reference
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="face_embeddings")
    
    def __repr__(self):
        return f"<FaceEmbedding(user_id='{self.user_id}')>"

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_plate = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(50))
    is_authorized = Column(Boolean, default=False)
    metadata = Column(JSONB)  # Additional vehicle information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    entries = relationship("VehicleEntry", back_populates="vehicle")
    
    def __repr__(self):
        return f"<Vehicle(license_plate='{self.license_plate}')>"

class VehicleEntry(Base):
    __tablename__ = "vehicle_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    entry_type = Column(Enum("ENTRY", "EXIT", name="entry_type"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(100))
    image_path = Column(String(255))  # Path to stored image
    confidence_score = Column(Float)
    
    vehicle = relationship("Vehicle", back_populates="entries")
    
    def __repr__(self):
        return f"<VehicleEntry(vehicle_id='{self.vehicle_id}', entry_type='{self.entry_type}')>"

class GunnyBagCount(Base):
    __tablename__ = "gunny_bag_counts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    count = Column(Integer, nullable=False)
    estimated_volume = Column(Float)  # Cubic meters
    location = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    video_reference = Column(String(255))  # Reference to video clip
    confidence_score = Column(Float)
    metadata = Column(JSONB)  # Additional information
    
    def __repr__(self):
        return f"<GunnyBagCount(count={self.count}, location='{self.location}')>"

class VideoEvent(Base):
    __tablename__ = "video_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(100))
    description = Column(Text)
    video_segment_start = Column(Float)  # Time in seconds
    video_segment_end = Column(Float)  # Time in seconds
    video_reference = Column(String(255))  # Reference to video file
    confidence_score = Column(Float)
    is_anomaly = Column(Boolean, default=False)
    metadata = Column(JSONB)  # Additional event information
    vector_embedding = Column(LargeBinary)  # For semantic search
    
    def __repr__(self):
        return f"<VideoEvent(event_type='{self.event_type}', timestamp='{self.timestamp}')>"

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45))
    details = Column(JSONB)
    
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', user_id='{self.user_id}')>"

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    path = Column(String(255), nullable=False)
    framework = Column(String(50))
    task = Column(String(50))
    metrics = Column(JSONB)  # Performance metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)
    metadata = Column(JSONB)  # Additional model information
    
    def __repr__(self):
        return f"<ModelRegistry(model_name='{self.model_name}', version='{self.version}')>"
