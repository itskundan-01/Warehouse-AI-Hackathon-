"""
Authentication Manager for Facial Recognition System.

This module manages the authentication and authorization processes based on
facial recognition results. It handles:
- Access control decisions based on personnel identity and access levels
- Authentication logging and history tracking
- Alerting for unauthorized access attempts
- Integration with the system's security policies
"""

import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import os
import threading

from sqlalchemy.orm import Session
from sqlalchemy import func

# Local imports - relative to project structure
from ...database.models import (
    PersonnelRecord, FacialDetection, Event, 
    EventType, AuditLog, User
)
from ...core.security import SecurityManager
from .face_detector import FaceDetector
from .face_recognizer import FaceRecognizer

# Configure logger
logger = logging.getLogger(__name__)

class AuthenticationManager:
    """
    Manages authentication and authorization using facial recognition.
    Acts as a bridge between the facial recognition module and security systems.
    """
    
    def __init__(
        self,
        face_recognizer: Optional[FaceRecognizer] = None,
        face_detector: Optional[FaceDetector] = None,
        security_manager: Optional[SecurityManager] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the authentication manager.
        
        Args:
            face_recognizer: FaceRecognizer instance (or None to create a new one)
            face_detector: FaceDetector instance (or None to create a new one)
            security_manager: SecurityManager instance for authentication policies
            config: Configuration options for the authentication manager
        """
        self.security_manager = security_manager
        
        # Default configuration
        self.config = {
            'min_recognition_confidence': 0.65,
            'access_level_threshold': 2,  # Minimum access level required
            'auth_logging_enabled': True,
            'alert_on_unauthorized': True,
            'reauth_interval_minutes': 60,  # Re-authentication required after this time
            'concurrent_auth_limit': 3,  # Max number of concurrent authentications per person
            'enable_anti_spoofing': True,
            'models_directory': str(Path(__file__).parent.parent.parent.parent / "models" / "facial")
        }
        
        # Update with provided config
        if config:
            self.config.update(config)
            
        # Initialize face recognizer if not provided
        if face_recognizer is None:
            models_dir = self.config['models_directory']
            embeddings_db = os.path.join(models_dir, "embeddings_db.pkl")
            
            self.face_recognizer = FaceRecognizer(
                method="arcface",
                model_path=os.path.join(models_dir, "arcface_resnet100.onnx"),
                recognition_threshold=self.config['min_recognition_confidence'],
                enable_gpu=False,  # Can make configurable
                db_path=embeddings_db if os.path.exists(embeddings_db) else None
            )
        else:
            self.face_recognizer = face_recognizer
            
        # Initialize face detector if not provided
        if face_detector is None:
            self.face_detector = FaceDetector(
                method="opencv-dnn",
                enable_gpu=False  # Can make configurable
            )
        else:
            self.face_detector = face_detector
            
        # For tracking recent authentications (for rate limiting)
        self.recent_auths = {}  # {personnel_id: [timestamp1, timestamp2, ...]}
        self.auth_lock = threading.Lock()
        
        logger.info("Authentication Manager initialized")
        
    def authenticate_face(
        self,
        db: Session,
        face_image,
        location: str,
        camera_id: str,
        check_anti_spoofing: bool = True
    ) -> Dict[str, Any]:
        """
        Authenticate a person based on facial recognition.
        
        Args:
            db: Database session
            face_image: Image containing a face to authenticate
            location: Physical location where authentication is happening
            camera_id: ID of the camera that captured the image
            check_anti_spoofing: Whether to perform anti-spoofing checks
            
        Returns:
            Authentication result dictionary
        """
        start_time = time.time()
        
        # Initialize result structure
        result = {
            'authenticated': False,
            'personnel_id': None,
            'confidence': 0.0,
            'name': None,
            'access_level': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time': 0,
            'location': location,
            'camera_id': camera_id,
            'error': None
        }
        
        try:
            # Check for face spoofing if enabled
            if check_anti_spoofing and self.config['enable_anti_spoofing']:
                anti_spoof_result = self.face_recognizer.implement_anti_spoofing(face_image)
                if not anti_spoof_result['is_real']:
                    result['error'] = "Potential presentation attack detected"
                    result['processing_time'] = time.time() - start_time
                    self._log_auth_event(result, db_session=db, is_spoof_attempt=True)
                    return result
            
            # Perform face recognition
            recognition_result = self.face_recognizer.detect_and_recognize(face_image)
            
            # Update result with recognition data
            result['confidence'] = recognition_result.get('similarity', 0.0)
            
            # If no match or below threshold
            if not recognition_result.get('is_match', False) or recognition_result.get('id') is None:
                result['error'] = "No matching personnel record found"
                result['processing_time'] = time.time() - start_time
                self._log_auth_event(result, db_session=db, is_unauthorized=True)
                return result
            
            # Get personnel details from database
            personnel_id = recognition_result['id']
            personnel = db.query(PersonnelRecord).filter(
                PersonnelRecord.employee_id == personnel_id,
                PersonnelRecord.is_active == True
            ).first()
            
            if not personnel:
                result['error'] = f"Personnel record inactive or not found: {personnel_id}"
                result['processing_time'] = time.time() - start_time
                self._log_auth_event(result, db_session=db, is_unauthorized=True)
                return result
            
            # Update result with personnel data
            result['personnel_id'] = personnel.employee_id
            result['name'] = personnel.name
            result['access_level'] = personnel.access_level
            
            # Check if access level is sufficient
            if personnel.access_level < self.config['access_level_threshold']:
                result['error'] = "Insufficient access level"
                result['processing_time'] = time.time() - start_time
                self._log_auth_event(result, db_session=db, is_unauthorized=True)
                return result
            
            # Check for concurrent authentication limits
            if not self._check_auth_rate_limit(personnel.employee_id):
                result['error'] = "Authentication rate limit exceeded"
                result['processing_time'] = time.time() - start_time
                self._log_auth_event(result, db_session=db, is_unauthorized=True)
                return result
            
            # All checks passed, authentication successful
            result['authenticated'] = True
            result['processing_time'] = time.time() - start_time
            
            # Log the successful facial detection
            detection = FacialDetection(
                personnel_id=personnel.id,
                detection_time=datetime.utcnow(),
                confidence_score=result['confidence'],
                location=location,
                camera_id=camera_id,
                is_authorized=True
            )
            db.add(detection)
            db.flush()
            
            # Log authentication event
            self._log_auth_event(result, db_session=db)
            
            return result
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            result['error'] = f"Authentication error: {str(e)}"
            result['processing_time'] = time.time() - start_time
            return result

    def register_personnel(
        self,
        db: Session,
        face_image,
        employee_id: str,
        name: str,
        department: str = "",
        access_level: int = 1,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new personnel face in the system.
        
        Args:
            db: Database session
            face_image: Face image to register
            employee_id: Employee ID for the personnel
            name: Full name of the personnel
            department: Department the personnel belongs to
            access_level: Access permission level (higher = more access)
            user_id: ID of the user performing the registration
            
        Returns:
            Registration result
        """
        start_time = time.time()
        result = {
            'success': False,
            'employee_id': employee_id,
            'name': name,
            'processing_time': 0,
            'error': None
        }
        
        try:
            # Extract face and generate embedding
            faces = self.face_detector.detect_and_extract_faces(face_image)
            if not faces:
                result['error'] = "No face detected in the image"
                result['processing_time'] = time.time() - start_time
                return result
            
            # Use the first detected face (assuming one face per registration)
            face_data = faces[0]
            embedding = self.face_recognizer.get_face_embedding(face_data['face_image'])
            
            # Save to database
            # Check if employee_id already exists
            existing = db.query(PersonnelRecord).filter(
                PersonnelRecord.employee_id == employee_id
            ).first()
            
            if existing:
                result['error'] = f"Employee ID {employee_id} already exists"
                result['processing_time'] = time.time() - start_time
                return result
            
            # Create new personnel record
            personnel = PersonnelRecord(
                employee_id=employee_id,
                name=name,
                department=department,
                access_level=access_level,
                face_embedding=embedding.tolist(),  # Convert to list for JSON storage
                is_active=True
            )
            db.add(personnel)
            db.flush()
            
            # Log the registration
            if user_id:
                log_entry = AuditLog(
                    user_id=user_id,
                    action="personnel_registration",
                    entity_type="personnel",
                    entity_id=personnel.id,
                    details=f"Registered {name} (ID: {employee_id})"
                )
                db.add(log_entry)
            
            # Add to face recognizer database
            self.face_recognizer.add_to_database(
                employee_id,
                embedding,
                auto_save=True
            )
            
            result['success'] = True
            result['processing_time'] = time.time() - start_time
            return result
                
        except Exception as e:
            logger.error(f"Personnel registration error: {str(e)}")
            result['error'] = f"Registration error: {str(e)}"
            result['processing_time'] = time.time() - start_time
            return result
            
    def deactivate_personnel(
        self,
        db: Session,
        employee_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deactivate a personnel record.
        
        Args:
            db: Database session
            employee_id: ID of the employee to deactivate
            user_id: ID of the user performing the deactivation
            
        Returns:
            Deactivation result
        """
        result = {
            'success': False,
            'employee_id': employee_id,
            'error': None
        }
        
        try:
            personnel = db.query(PersonnelRecord).filter(
                PersonnelRecord.employee_id == employee_id
            ).first()
            
            if not personnel:
                result['error'] = f"Personnel with ID {employee_id} not found"
                return result
            
            # Update record
            personnel.is_active = False
            
            # Log the deactivation
            if user_id:
                log_entry = AuditLog(
                    user_id=user_id,
                    action="personnel_deactivation",
                    entity_type="personnel",
                    entity_id=personnel.id,
                    details=f"Deactivated {personnel.name} (ID: {employee_id})"
                )
                db.add(log_entry)
            
            # Remove from face recognizer database
            self.face_recognizer.remove_from_database(
                employee_id,
                auto_save=True
            )
            
            result['success'] = True
            return result
                
        except Exception as e:
            logger.error(f"Personnel deactivation error: {str(e)}")
            result['error'] = f"Deactivation error: {str(e)}"
            return result
            
    def update_access_level(
        self,
        db: Session,
        employee_id: str,
        new_access_level: int,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a personnel's access level.
        
        Args:
            db: Database session
            employee_id: ID of the employee to update
            new_access_level: New access level to assign
            user_id: ID of the user performing the update
            
        Returns:
            Update result
        """
        result = {
            'success': False,
            'employee_id': employee_id,
            'old_access_level': None,
            'new_access_level': new_access_level,
            'error': None
        }
        
        try:
            personnel = db.query(PersonnelRecord).filter(
                PersonnelRecord.employee_id == employee_id
            ).first()
            
            if not personnel:
                result['error'] = f"Personnel with ID {employee_id} not found"
                return result
            
            result['old_access_level'] = personnel.access_level
            
            # Update record
            personnel.access_level = new_access_level
            
            # Log the update
            if user_id:
                log_entry = AuditLog(
                    user_id=user_id,
                    action="access_level_update",
                    entity_type="personnel",
                    entity_id=personnel.id,
                    details=f"Updated access level for {personnel.name} from {result['old_access_level']} to {new_access_level}"
                )
                db.add(log_entry)
            
            result['success'] = True
            return result
                
        except Exception as e:
            logger.error(f"Access level update error: {str(e)}")
            result['error'] = f"Update error: {str(e)}"
            return result
            
    def get_authentication_history(
        self,
        db: Session,
        employee_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get authentication history, optionally filtered.
        
        Args:
            db: Database session
            employee_id: Filter by employee ID
            start_time: Filter by start time
            end_time: Filter by end time
            location: Filter by location
            limit: Maximum number of results to return
            
        Returns:
            List of authentication history records
        """
        try:
            query = db.query(FacialDetection)
            
            if employee_id:
                query = query.join(PersonnelRecord).filter(
                    PersonnelRecord.employee_id == employee_id
                )
                
            if start_time:
                query = query.filter(FacialDetection.detection_time >= start_time)
                
            if end_time:
                query = query.filter(FacialDetection.detection_time <= end_time)
                
            if location:
                query = query.filter(FacialDetection.location == location)
            
            # Order by most recent first
            query = query.order_by(FacialDetection.detection_time.desc()).limit(limit)
            
            detections = query.all()
            
            # Convert to dictionaries
            result = []
            for detection in detections:
                personnel_name = detection.personnel.name if detection.personnel else "Unknown"
                employee_id = detection.personnel.employee_id if detection.personnel else None
                
                result.append({
                    'id': str(detection.id),
                    'personnel_id': employee_id,
                    'name': personnel_name,
                    'detection_time': detection.detection_time.isoformat(),
                    'confidence': detection.confidence_score,
                    'location': detection.location,
                    'camera_id': detection.camera_id,
                    'is_authorized': detection.is_authorized,
                })
            
            return result
                
        except Exception as e:
            logger.error(f"Error retrieving authentication history: {str(e)}")
            return []
            
    def get_unauthorized_access_attempts(
        self,
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get unauthorized access attempts.
        
        Args:
            db: Database session
            start_time: Filter by start time
            end_time: Filter by end time
            location: Filter by location
            limit: Maximum number of results to return
            
        Returns:
            List of unauthorized access attempts
        """
        try:
            query = db.query(FacialDetection).filter(
                FacialDetection.is_authorized == False
            )
            
            if start_time:
                query = query.filter(FacialDetection.detection_time >= start_time)
                
            if end_time:
                query = query.filter(FacialDetection.detection_time <= end_time)
                
            if location:
                query = query.filter(FacialDetection.location == location)
            
            # Order by most recent first
            query = query.order_by(FacialDetection.detection_time.desc()).limit(limit)
            
            detections = query.all()
            
            # Convert to dictionaries
            result = []
            for detection in detections:
                result.append({
                    'id': str(detection.id),
                    'detection_time': detection.detection_time.isoformat(),
                    'confidence': detection.confidence_score,
                    'location': detection.location,
                    'camera_id': detection.camera_id,
                    'thumbnail_path': detection.thumbnail_path,
                })
            
            return result
                
        except Exception as e:
            logger.error(f"Error retrieving unauthorized access attempts: {str(e)}")
            return []
    
    def _log_auth_event(
        self, 
        auth_result: Dict[str, Any], 
        db_session: Session,
        is_unauthorized: bool = False,
        is_spoof_attempt: bool = False
    ) -> None:
        """
        Log authentication events to the database.
        
        Args:
            auth_result: Authentication result dictionary
            db_session: Existing database session
            is_unauthorized: Whether this was an unauthorized access attempt
            is_spoof_attempt: Whether this was a spoofing attempt
        """
        if not self.config['auth_logging_enabled']:
            return
            
        try:
            # Determine event type
            if is_spoof_attempt:
                event_type = EventType.ANOMALY_DETECTED
                description = f"Potential spoofing attempt detected at {auth_result['location']}"
                severity = 2  # Critical
            elif is_unauthorized:
                event_type = EventType.UNAUTHORIZED_PERSON
                description = f"Unauthorized access attempt at {auth_result['location']}"
                severity = 1  # Warning
            else:
                # Don't log authorized access as events to reduce noise
                return
            
            # Create event
            event = Event(
                timestamp=datetime.utcnow(),
                event_type=event_type,
                description=description,
                location=auth_result['location'],
                camera_id=auth_result['camera_id'],
                severity=severity,
                is_resolved=False,
                meta_data={
                    'confidence': auth_result['confidence'],
                    'processing_time': auth_result['processing_time'],
                    'error': auth_result['error']
                }
            )
            db_session.add(event)
            db_session.commit()
                
        except Exception as e:
            logger.error(f"Error logging authentication event: {str(e)}")
            
    def _check_auth_rate_limit(self, personnel_id: str) -> bool:
        """
        Check if authentication requests are within allowed rate limits.
        
        Args:
            personnel_id: Personnel ID to check
            
        Returns:
            True if within limits, False if exceeded
        """
        with self.auth_lock:
            now = time.time()
            
            # Initialize if not present
            if personnel_id not in self.recent_auths:
                self.recent_auths[personnel_id] = []
            
            # Remove entries older than reauth interval
            cutoff = now - (self.config['reauth_interval_minutes'] * 60)
            self.recent_auths[personnel_id] = [
                t for t in self.recent_auths[personnel_id] if t > cutoff
            ]
            
            # Check if concurrent limit is exceeded
            if len(self.recent_auths[personnel_id]) >= self.config['concurrent_auth_limit']:
                return False
                
            # Add current timestamp
            self.recent_auths[personnel_id].append(now)
            return True
            
    def sync_database_with_recognizer(self, db: Session) -> Dict[str, Any]:
        """
        Synchronize the database personnel records with face recognizer embeddings.
        
        Args:
            db: Database session
            
        Returns:
            Synchronization results
        """
        result = {
            'success': True,
            'db_count': 0,
            'recognizer_count': 0,
            'added': 0,
            'removed': 0,
            'errors': []
        }
        
        try:
            # Get all active personnel
            personnel = db.query(PersonnelRecord).filter(
                PersonnelRecord.is_active == True,
                PersonnelRecord.face_embedding != None  # Must have an embedding
            ).all()
            
            result['db_count'] = len(personnel)
            result['recognizer_count'] = len(self.face_recognizer.embeddings_db)
            
            # Add missing entries to recognizer
            for person in personnel:
                if person.employee_id not in self.face_recognizer.embeddings_db:
                    try:
                        embedding = np.array(person.face_embedding)
                        self.face_recognizer.add_to_database(person.employee_id, embedding)
                        result['added'] += 1
                    except Exception as e:
                        result['errors'].append(f"Error adding {person.employee_id}: {str(e)}")
            
            # Remove entries from recognizer that aren't in database
            db_ids = set(p.employee_id for p in personnel)
            recognizer_ids = set(self.face_recognizer.embeddings_db.keys())
            
            for person_id in recognizer_ids - db_ids:
                try:
                    self.face_recognizer.remove_from_database(person_id)
                    result['removed'] += 1
                except Exception as e:
                    result['errors'].append(f"Error removing {person_id}: {str(e)}")
            
            # Save the database
            if result['added'] > 0 or result['removed'] > 0:
                self.face_recognizer.save_embeddings_db(self.face_recognizer.db_path)
            
            if result['errors']:
                result['success'] = False
                
            return result
                
        except Exception as e:
            logger.error(f"Error synchronizing database: {str(e)}")
            result['success'] = False
            result['errors'].append(str(e))
            return result

class AuthenticationManagerWrapper:
    """Wrapper class for AuthenticationManager to avoid FastAPI typing issues."""
    
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
    
    def register_personnel(self, db, face_image, employee_id, name, department, access_level, user_id):
        """Wrapper for register_personnel to avoid AsyncSession type issues."""
        return self.auth_manager.register_personnel(
            db=db,
            face_image=face_image,
            employee_id=employee_id,
            name=name,
            department=department,
            access_level=access_level,
            user_id=user_id
        )
    
    def authenticate_face(self, db, face_image, location, camera_id):
        """Wrapper for authenticate_face to avoid AsyncSession type issues."""
        return self.auth_manager.authenticate_face(
            db=db,
            face_image=face_image,
            location=location,
            camera_id=camera_id
        )
    
    def update_access_level(self, db, employee_id, new_access_level, user_id):
        """Wrapper for update_access_level to avoid AsyncSession type issues."""
        return self.auth_manager.update_access_level(
            db=db, 
            employee_id=employee_id,
            new_access_level=new_access_level,
            user_id=user_id
        )
    
    def deactivate_personnel(self, db, employee_id, user_id):
        """Wrapper for deactivate_personnel to avoid AsyncSession type issues."""
        return self.auth_manager.deactivate_personnel(
            db=db,
            employee_id=employee_id,
            user_id=user_id
        )
    
    def get_authentication_history(self, db, employee_id=None, start_time=None, end_time=None, location=None, limit=100):
        """Wrapper for get_authentication_history to avoid AsyncSession type issues."""
        return self.auth_manager.get_authentication_history(
            db=db,
            employee_id=employee_id,
            start_time=start_time,
            end_time=end_time,
            location=location,
            limit=limit
        )
    
    def get_unauthorized_access_attempts(self, db, start_time=None, location=None, limit=100):
        """Wrapper for get_unauthorized_access_attempts to avoid AsyncSession type issues."""
        return self.auth_manager.get_unauthorized_access_attempts(
            db=db,
            start_time=start_time,
            location=location,
            limit=limit
        )
    
    def sync_database_with_recognizer(self, db):
        """Wrapper for sync_database_with_recognizer to avoid AsyncSession type issues."""
        return self.auth_manager.sync_database_with_recognizer(db=db)