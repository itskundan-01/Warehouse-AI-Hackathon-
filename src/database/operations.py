"""
Database operations for WarehouseVision AI.
Implements repository pattern for database access.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union, AsyncGenerator
import uuid

from sqlalchemy import desc, or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from . import AsyncSessionLocal

# Database dependency for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and yield an async database session.
    This function is used as a dependency in FastAPI routes.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, db_session: Session, model_class):
        self.db = db_session
        self.model_class = model_class
    
    def get_by_id(self, entity_id: uuid.UUID):
        return self.db.query(self.model_class).filter(self.model_class.id == entity_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def create(self, **kwargs):
        entity = self.model_class(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, entity_id: uuid.UUID, **kwargs):
        entity = self.get_by_id(entity_id)
        if not entity:
            return None
        
        for key, value in kwargs.items():
            setattr(entity, key, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, entity_id: uuid.UUID) -> bool:
        entity = self.get_by_id(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def count(self) -> int:
        return self.db.query(self.model_class).count()


class UserRepository(BaseRepository):
    """Repository for User model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.User)
    
    def get_by_username(self, username: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.email == email).first()
    
    def update_last_login(self, user_id: uuid.UUID) -> Optional[models.User]:
        return self.update(user_id, last_login=datetime.utcnow())
    
    def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[models.User]:
        search_term = f"%{query}%"
        return self.db.query(models.User).filter(
            or_(
                models.User.username.ilike(search_term),
                models.User.email.ilike(search_term),
                models.User.full_name.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()
    
    def get_users_by_role(self, role: models.UserRole, skip: int = 0, limit: int = 100) -> List[models.User]:
        return self.db.query(models.User).filter(models.User.role == role).offset(skip).limit(limit).all()


class PersonnelRepository(BaseRepository):
    """Repository for PersonnelRecord model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.PersonnelRecord)
    
    def get_by_employee_id(self, employee_id: str) -> Optional[models.PersonnelRecord]:
        return self.db.query(models.PersonnelRecord).filter(
            models.PersonnelRecord.employee_id == employee_id
        ).first()
    
    def search_personnel(self, query: str, skip: int = 0, limit: int = 100) -> List[models.PersonnelRecord]:
        search_term = f"%{query}%"
        return self.db.query(models.PersonnelRecord).filter(
            or_(
                models.PersonnelRecord.name.ilike(search_term),
                models.PersonnelRecord.employee_id.ilike(search_term),
                models.PersonnelRecord.department.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()
    
    def get_by_department(self, department: str, skip: int = 0, limit: int = 100) -> List[models.PersonnelRecord]:
        return self.db.query(models.PersonnelRecord).filter(
            models.PersonnelRecord.department == department
        ).offset(skip).limit(limit).all()
    
    def get_by_access_level(self, access_level: int, skip: int = 0, limit: int = 100) -> List[models.PersonnelRecord]:
        return self.db.query(models.PersonnelRecord).filter(
            models.PersonnelRecord.access_level >= access_level
        ).offset(skip).limit(limit).all()


class FacialDetectionRepository(BaseRepository):
    """Repository for FacialDetection model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.FacialDetection)
    
    def get_by_personnel_id(self, personnel_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.FacialDetection]:
        return self.db.query(models.FacialDetection).filter(
            models.FacialDetection.personnel_id == personnel_id
        ).order_by(desc(models.FacialDetection.detection_time)).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_time: datetime, end_time: datetime, 
                         skip: int = 0, limit: int = 100) -> List[models.FacialDetection]:
        return self.db.query(models.FacialDetection).filter(
            and_(
                models.FacialDetection.detection_time >= start_time,
                models.FacialDetection.detection_time <= end_time
            )
        ).order_by(desc(models.FacialDetection.detection_time)).offset(skip).limit(limit).all()
    
    def get_unauthorized_detections(self, skip: int = 0, limit: int = 100) -> List[models.FacialDetection]:
        return self.db.query(models.FacialDetection).filter(
            models.FacialDetection.is_authorized == False
        ).order_by(desc(models.FacialDetection.detection_time)).offset(skip).limit(limit).all()


class VehicleRepository(BaseRepository):
    """Repository for Vehicle model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.Vehicle)
    
    def get_by_license_plate(self, license_plate: str) -> Optional[models.Vehicle]:
        return self.db.query(models.Vehicle).filter(
            models.Vehicle.license_plate == license_plate
        ).first()
    
    def get_authorized_vehicles(self, skip: int = 0, limit: int = 100) -> List[models.Vehicle]:
        return self.db.query(models.Vehicle).filter(
            models.Vehicle.is_authorized == True
        ).offset(skip).limit(limit).all()
    
    def search_vehicles(self, query: str, skip: int = 0, limit: int = 100) -> List[models.Vehicle]:
        search_term = f"%{query}%"
        return self.db.query(models.Vehicle).filter(
            or_(
                models.Vehicle.license_plate.ilike(search_term),
                models.Vehicle.owner_name.ilike(search_term),
                models.Vehicle.vehicle_type.ilike(search_term),
                models.Vehicle.notes.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()


class VehicleDetectionRepository(BaseRepository):
    """Repository for VehicleDetection model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.VehicleDetection)
    
    def get_by_vehicle_id(self, vehicle_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.VehicleDetection]:
        return self.db.query(models.VehicleDetection).filter(
            models.VehicleDetection.vehicle_id == vehicle_id
        ).order_by(desc(models.VehicleDetection.detection_time)).offset(skip).limit(limit).all()
    
    def get_by_license_plate(self, license_plate: str, skip: int = 0, limit: int = 100) -> List[models.VehicleDetection]:
        return self.db.query(models.VehicleDetection).filter(
            models.VehicleDetection.license_plate_text == license_plate
        ).order_by(desc(models.VehicleDetection.detection_time)).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_time: datetime, end_time: datetime, 
                         skip: int = 0, limit: int = 100) -> List[models.VehicleDetection]:
        return self.db.query(models.VehicleDetection).filter(
            and_(
                models.VehicleDetection.detection_time >= start_time,
                models.VehicleDetection.detection_time <= end_time
            )
        ).order_by(desc(models.VehicleDetection.detection_time)).offset(skip).limit(limit).all()
    
    def get_entries(self, skip: int = 0, limit: int = 100) -> List[models.VehicleDetection]:
        return self.db.query(models.VehicleDetection).filter(
            models.VehicleDetection.is_entry == True
        ).order_by(desc(models.VehicleDetection.detection_time)).offset(skip).limit(limit).all()
    
    def get_exits(self, skip: int = 0, limit: int = 100) -> List[models.VehicleDetection]:
        return self.db.query(models.VehicleDetection).filter(
            models.VehicleDetection.is_entry == False
        ).order_by(desc(models.VehicleDetection.detection_time)).offset(skip).limit(limit).all()


class GunnyBagCountRepository(BaseRepository):
    """Repository for GunnyBagCount model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.GunnyBagCount)
    
    def get_by_date_range(self, start_time: datetime, end_time: datetime, 
                         skip: int = 0, limit: int = 100) -> List[models.GunnyBagCount]:
        return self.db.query(models.GunnyBagCount).filter(
            and_(
                models.GunnyBagCount.timestamp >= start_time,
                models.GunnyBagCount.timestamp <= end_time
            )
        ).order_by(desc(models.GunnyBagCount.timestamp)).offset(skip).limit(limit).all()
    
    def get_by_location(self, location: str, skip: int = 0, limit: int = 100) -> List[models.GunnyBagCount]:
        return self.db.query(models.GunnyBagCount).filter(
            models.GunnyBagCount.location == location
        ).order_by(desc(models.GunnyBagCount.created_at)).offset(skip).limit(limit).all()
    
    def get_latest_by_location(self, location: str) -> Optional[models.GunnyBagCount]:
        return self.db.query(models.GunnyBagCount).filter(
            models.GunnyBagCount.location == location
        ).order_by(desc(models.GunnyBagCount.created_at)).first()
    
    def get_counts_by_date_range(self, start_time: datetime, end_time: datetime, 
                              skip: int = 0, limit: int = 100) -> List[models.GunnyBagCount]:
        return self.db.query(models.GunnyBagCount).filter(
            and_(
                models.GunnyBagCount.created_at >= start_time,
                models.GunnyBagCount.created_at <= end_time
            )
        ).order_by(desc(models.GunnyBagCount.created_at)).offset(skip).limit(limit).all()
    
    def get_by_camera_id(self, camera_id: str, skip: int = 0, limit: int = 100) -> List[models.GunnyBagCount]:
        return self.db.query(models.GunnyBagCount).filter(
            models.GunnyBagCount.camera_id == camera_id
        ).order_by(desc(models.GunnyBagCount.timestamp)).offset(skip).limit(limit).all()
    
    def get_latest_counts(self, limit: int = 10) -> List[models.GunnyBagCount]:
        return self.db.query(models.GunnyBagCount).order_by(
            desc(models.GunnyBagCount.timestamp)
        ).limit(limit).all()


class EventRepository(BaseRepository):
    """Repository for Event model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.Event)
    
    def get_by_event_type(self, event_type: models.EventType, skip: int = 0, limit: int = 100) -> List[models.Event]:
        return self.db.query(models.Event).filter(
            models.Event.event_type == event_type
        ).order_by(desc(models.Event.timestamp)).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_time: datetime, end_time: datetime, 
                         skip: int = 0, limit: int = 100) -> List[models.Event]:
        return self.db.query(models.Event).filter(
            and_(
                models.Event.timestamp >= start_time,
                models.Event.timestamp <= end_time
            )
        ).order_by(desc(models.Event.timestamp)).offset(skip).limit(limit).all()
    
    def get_by_severity(self, severity: int, skip: int = 0, limit: int = 100) -> List[models.Event]:
        return self.db.query(models.Event).filter(
            models.Event.severity >= severity
        ).order_by(desc(models.Event.timestamp)).offset(skip).limit(limit).all()
    
    def get_unresolved_events(self, skip: int = 0, limit: int = 100) -> List[models.Event]:
        return self.db.query(models.Event).filter(
            models.Event.is_resolved == False
        ).order_by(desc(models.Event.timestamp)).offset(skip).limit(limit).all()


class AuditLogRepository(BaseRepository):
    """Repository for AuditLog model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.AuditLog)
    
    def get_by_user_id(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
        return self.db.query(models.AuditLog).filter(
            models.AuditLog.user_id == user_id
        ).order_by(desc(models.AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_time: datetime, end_time: datetime, 
                         skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
        return self.db.query(models.AuditLog).filter(
            and_(
                models.AuditLog.timestamp >= start_time,
                models.AuditLog.timestamp <= end_time
            )
        ).order_by(desc(models.AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    def get_by_action(self, action: str, skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
        return self.db.query(models.AuditLog).filter(
            models.AuditLog.action == action
        ).order_by(desc(models.AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    def get_by_entity_type_and_id(self, entity_type: str, entity_id: uuid.UUID, 
                                 skip: int = 0, limit: int = 100) -> List[models.AuditLog]:
        return self.db.query(models.AuditLog).filter(
            and_(
                models.AuditLog.entity_type == entity_type,
                models.AuditLog.entity_id == entity_id
            )
        ).order_by(desc(models.AuditLog.timestamp)).offset(skip).limit(limit).all()


class ContextualQueryRepository(BaseRepository):
    """Repository for ContextualQuery model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.ContextualQuery)
    
    def get_by_user_id(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.ContextualQuery]:
        return self.db.query(models.ContextualQuery).filter(
            models.ContextualQuery.user_id == user_id
        ).order_by(desc(models.ContextualQuery.timestamp)).offset(skip).limit(limit).all()
    
    def search_queries(self, query: str, skip: int = 0, limit: int = 100) -> List[models.ContextualQuery]:
        search_term = f"%{query}%"
        return self.db.query(models.ContextualQuery).filter(
            models.ContextualQuery.query_text.ilike(search_term)
        ).order_by(desc(models.ContextualQuery.timestamp)).offset(skip).limit(limit).all()
    
    def get_recent_queries(self, limit: int = 10) -> List[models.ContextualQuery]:
        return self.db.query(models.ContextualQuery).order_by(
            desc(models.ContextualQuery.timestamp)
        ).limit(limit).all()


class VideoSegmentRepository(BaseRepository):
    """Repository for VideoSegment model operations."""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, models.VideoSegment)
    
    def get_by_camera_id(self, camera_id: str, skip: int = 0, limit: int = 100) -> List[models.VideoSegment]:
        return self.db.query(models.VideoSegment).filter(
            models.VideoSegment.camera_id == camera_id
        ).order_by(desc(models.VideoSegment.start_time)).offset(skip).limit(limit).all()
    
    def get_by_date_range(self, start_time: datetime, end_time: datetime, 
                         skip: int = 0, limit: int = 100) -> List[models.VideoSegment]:
        return self.db.query(models.VideoSegment).filter(
            or_(
                and_(
                    models.VideoSegment.start_time >= start_time,
                    models.VideoSegment.start_time <= end_time
                ),
                and_(
                    models.VideoSegment.end_time >= start_time,
                    models.VideoSegment.end_time <= end_time
                )
            )
        ).order_by(desc(models.VideoSegment.start_time)).offset(skip).limit(limit).all()
    
    def search_by_tags(self, tags: List[str], skip: int = 0, limit: int = 100) -> List[models.VideoSegment]:
        # PostgreSQL JSON array containment
        query = self.db.query(models.VideoSegment)
        
        for tag in tags:
            query = query.filter(models.VideoSegment.tags.contains([tag]))
        
        return query.order_by(desc(models.VideoSegment.start_time)).offset(skip).limit(limit).all()


# Repository instances for use throughout the application
user_repository = UserRepository(None)
personnel_repository = PersonnelRepository(None)
facial_detection_repository = FacialDetectionRepository(None)
vehicle_repository = VehicleRepository(None)
vehicle_detection_repository = VehicleDetectionRepository(None)
gunny_repository = GunnyBagCountRepository(None)