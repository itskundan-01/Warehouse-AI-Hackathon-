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
import numpy as np

# Local imports - relative to project structure
# from ...database.models import (
#     PersonnelRecord, FacialDetection, Event, 
#     EventType, AuditLog, User
# )
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
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the authentication manager.
        
        Args:
            face_recognizer: FaceRecognizer instance (or None to create a new one)
            face_detector: FaceDetector instance (or None to create a new one)
            config: Configuration options for the authentication manager
        """
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
        
    async def authenticate_face(
        self,
        db,
        face_image,
        location: str,
        camera_id: str,
        check_anti_spoofing: bool = True
    ) -> dict:
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
        import time
        result = {"authenticated": False}
        start_time = time.time()
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
            recognition_result = self.face_recognizer.recognize(face_image)
            if not recognition_result or recognition_result.get('confidence', 0) < self.config['min_recognition_confidence']:
                result['error'] = "Face not recognized or low confidence"
                result['processing_time'] = time.time() - start_time
                # Optionally log event
                return result
            
            # Get personnel details from MongoDB
            personnel_id = recognition_result['id']
            personnel = await db["personnel_records"].find_one({"employee_id": personnel_id, "is_active": True})
            if not personnel:
                result['error'] = f"Personnel record inactive or not found: {personnel_id}"
                result['processing_time'] = time.time() - start_time
                # Optionally log event
                return result
            
            # Update result with personnel data
            result['personnel_id'] = personnel['employee_id']
            result['name'] = personnel['name']
            result['access_level'] = personnel['access_level']
            
            # Check if access level is sufficient
            if personnel['access_level'] < self.config['access_level_threshold']:
                result['error'] = "Insufficient access level"
                result['processing_time'] = time.time() - start_time
                # Optionally log event
                return result
            
            # Check for concurrent authentication limits
            if not self._check_auth_rate_limit(personnel['employee_id']):
                result['error'] = "Authentication rate limit exceeded"
                result['processing_time'] = time.time() - start_time
                # Optionally log event
                return result
            
            # All checks passed, authentication successful
            result['authenticated'] = True
            result['processing_time'] = time.time() - start_time
            
            # Log the successful facial detection in MongoDB
            detection_doc = {
                "personnel_id": personnel['_id'],
                "detection_time": datetime.utcnow(),
                "confidence_score": result['confidence'],
                "location": location,
                "camera_id": camera_id,
                "is_authorized": True
            }
            await db["facial_detections"].insert_one(detection_doc)
            # Optionally log authentication event
            return result
        except Exception as e:
            import logging
            logging.error(f"Authentication error: {str(e)}")
            result['error'] = f"Authentication error: {str(e)}"
            result['processing_time'] = time.time() - start_time
            return result

    async def register_personnel(
        self,
        db,
        face_image,
        employee_id: str,
        name: str,
        department: str = "",
        access_level: int = 1,
        user_id: Optional[str] = None
    ) -> dict:
        import time
        result = {
            'success': False,
            'employee_id': employee_id,
            'name': name,
            'processing_time': 0,
            'error': None
        }
        try:
            faces = self.face_detector.detect_and_extract_faces(face_image)
            if not faces:
                result['error'] = "No face detected in the image"
                result['processing_time'] = time.time() - time.time()
                return result
            face_data = faces[0]
            embedding = self.face_recognizer.get_face_embedding(face_data['face_image'])
            # Check if employee_id already exists
            existing = await db["personnel_records"].find_one({"employee_id": employee_id})
            if existing:
                result['error'] = f"Employee ID {employee_id} already exists"
                result['processing_time'] = time.time() - time.time()
                return result
            doc = {
                "employee_id": employee_id,
                "name": name,
                "department": department,
                "access_level": access_level,
                "face_embedding": embedding.tolist(),
                "is_active": True
            }
            await db["personnel_records"].insert_one(doc)
            # Add to face recognizer database
            self.face_recognizer.add_to_database(
                employee_id,
                embedding,
                auto_save=True
            )
            result['success'] = True
            result['processing_time'] = time.time() - time.time()
            return result
        except Exception as e:
            import logging
            logging.error(f"Personnel registration error: {str(e)}")
            result['error'] = f"Registration error: {str(e)}"
            result['processing_time'] = time.time() - time.time()
            return result

    async def deactivate_personnel(
        self,
        db,
        employee_id: str,
        user_id: Optional[str] = None
    ) -> dict:
        result = {
            'success': False,
            'employee_id': employee_id,
            'error': None
        }
        try:
            update_result = await db["personnel_records"].update_one(
                {"employee_id": employee_id},
                {"$set": {"is_active": False}}
            )
            if update_result.modified_count == 0:
                result['error'] = f"Employee ID {employee_id} not found or already inactive"
                return result
            result['success'] = True
            return result
        except Exception as e:
            import logging
            logging.error(f"Deactivate personnel error: {str(e)}")
            result['error'] = f"Deactivation error: {str(e)}"
            return result
            
    async def update_access_level(
        self,
        db,
        employee_id: str,
        new_access_level: int,
        user_id: Optional[str] = None
    ) -> dict:
        result = {
            'success': False,
            'employee_id': employee_id,
            'old_access_level': None,
            'new_access_level': new_access_level,
            'error': None
        }
        try:
            personnel = await db["personnel_records"].find_one({"employee_id": employee_id})
            if not personnel:
                result['error'] = f"Employee ID {employee_id} not found"
                return result
            result['old_access_level'] = personnel.get('access_level')
            update_result = await db["personnel_records"].update_one(
                {"employee_id": employee_id},
                {"$set": {"access_level": new_access_level}}
            )
            if update_result.modified_count == 0:
                result['error'] = f"Failed to update access level for {employee_id}"
                return result
            result['success'] = True
            return result
        except Exception as e:
            import logging
            logging.error(f"Access level update error: {str(e)}")
            result['error'] = f"Update error: {str(e)}"
            return result
            
    async def get_authentication_history(
        self,
        db,
        employee_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        limit: int = 100
    ) -> list:
        try:
            query = {}
            if employee_id:
                query["personnel_id"] = employee_id
            if start_time:
                query["detection_time"] = {"$gte": start_time}
            if end_time:
                if "detection_time" in query:
                    query["detection_time"]["$lte"] = end_time
                else:
                    query["detection_time"] = {"$lte": end_time}
            if location:
                query["location"] = location
            cursor = db["facial_detections"].find(query).sort("detection_time", -1).limit(limit)
            result = []
            async for detection in cursor:
                detection["_id"] = str(detection["_id"])
                result.append(detection)
            return result
        except Exception as e:
            import logging
            logging.error(f"Error retrieving authentication history: {str(e)}")
            return []

    async def get_unauthorized_access_attempts(
        self,
        db,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        limit: int = 100
    ) -> list:
        try:
            query = {"is_authorized": False}
            if start_time:
                query["detection_time"] = {"$gte": start_time}
            if end_time:
                if "detection_time" in query:
                    query["detection_time"]["$lte"] = end_time
                else:
                    query["detection_time"] = {"$lte": end_time}
            if location:
                query["location"] = location
            cursor = db["facial_detections"].find(query).sort("detection_time", -1).limit(limit)
            result = []
            async for detection in cursor:
                detection["_id"] = str(detection["_id"])
                result.append(detection)
            return result
        except Exception as e:
            import logging
            logging.error(f"Error retrieving unauthorized access attempts: {str(e)}")
            return []
    
    def _log_auth_event(
        self, 
        auth_result: Dict[str, Any], 
        db_session,
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
                description = f"Potential spoofing attempt detected at {auth_result['location']}"
                severity = 2  # Critical
            elif is_unauthorized:
                description = f"Unauthorized access attempt at {auth_result['location']}"
                severity = 1  # Warning
            else:
                # Don't log authorized access as events to reduce noise
                return
            
            # Create event
            event = {
                "timestamp": datetime.utcnow(),
                "description": description,
                "location": auth_result['location'],
                "camera_id": auth_result['camera_id'],
                "severity": severity,
                "is_resolved": False,
                "meta_data": {
                    'confidence': auth_result['confidence'],
                    'processing_time': auth_result['processing_time'],
                    'error': auth_result['error']
                }
            }
            db_session["events"].insert_one(event)
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
            
    async def sync_database_with_recognizer(self, db) -> dict:
        try:
            # Example: count personnel records and recognizer db
            db_count = await db["personnel_records"].count_documents({"is_active": True, "face_embedding": {"$ne": None}})
            recognizer_count = len(self.face_recognizer.embeddings_db) if hasattr(self.face_recognizer, 'embeddings_db') else 0
            # Optionally, sync logic here
            return {
                "success": True,
                "db_count": db_count,
                "recognizer_count": recognizer_count,
                "added": 0,
                "removed": 0
            }
        except Exception as e:
            import logging
            logging.error(f"Sync database error: {str(e)}")
            return {"success": False, "error": str(e)}

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