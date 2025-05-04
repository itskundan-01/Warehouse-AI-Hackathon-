"""
Facial Recognition Module for WarehouseVision AI.

This module provides facial recognition capabilities for the warehouse surveillance system,
including face detection, recognition, and authentication management.

Components:
- FaceDetector: Detects and extracts faces from images/video frames
- FaceRecognizer: Recognizes faces and matches them against a database of known personnel
- AuthenticationManager: Handles authentication decisions and access control

Usage:
    from src.modules.facial_recognition import FaceDetector, FaceRecognizer, AuthenticationManager
    from src.modules.facial_recognition import setup_facial_recognition
"""

from .face_detector import FaceDetector
from .face_recognizer import FaceRecognizer
from .auth_manager import AuthenticationManager

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

def setup_facial_recognition(
    db_session_factory,
    config: Optional[Dict[str, Any]] = None
) -> Tuple[FaceDetector, FaceRecognizer, AuthenticationManager]:
    """
    Set up and initialize all facial recognition components.
    
    Args:
        db_session_factory: Database session factory for data access
        config: Configuration options for facial recognition components
        
    Returns:
        Tuple of (FaceDetector, FaceRecognizer, AuthenticationManager)
    """
    # Default configuration
    default_config = {
        'models_directory': str(Path(__file__).parent.parent.parent.parent / "models" / "facial"),
        'detection_method': 'opencv-dnn',
        'recognition_method': 'opencv',  # Changed from 'arcface' to 'opencv'
        'min_detection_confidence': 0.7,
        'min_recognition_confidence': 0.65,
        'enable_gpu': False,
        'access_level_threshold': 2,
        'enable_anti_spoofing': True
    }
    
    # Update with provided config
    if config:
        default_config.update(config)
    
    # Ensure models directory exists
    models_dir = default_config['models_directory']
    os.makedirs(models_dir, exist_ok=True)
    
    # Initialize face detector
    face_detector = FaceDetector(
        method=default_config['detection_method'],
        min_confidence=default_config['min_detection_confidence'],
        enable_gpu=default_config['enable_gpu']
    )
    
    # Initialize face recognizer
    embeddings_db = os.path.join(models_dir, "embeddings_db.pkl")
    face_recognizer = FaceRecognizer(
        method=default_config['recognition_method'],
        recognition_threshold=default_config['min_recognition_confidence'],
        enable_gpu=default_config['enable_gpu'],
        db_path=embeddings_db if os.path.exists(embeddings_db) else None
    )
    
    # Initialize authentication manager
    auth_manager = AuthenticationManager(
        db_session_factory=db_session_factory,
        face_detector=face_detector,
        face_recognizer=face_recognizer,
        config=default_config
    )
    
    logger.info("Facial recognition system initialized")
    return face_detector, face_recognizer, auth_manager