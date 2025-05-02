#!/usr/bin/env python3
"""Test script for face detector to verify our fix works correctly."""

import cv2
import numpy as np
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Import the FaceDetector from the local module
from src.modules.facial_recognition.face_detector import FaceDetector, DETECTION_METHODS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_detector_test")

def test_face_detector():
    """Test the face detector with different configurations"""
    try:
        # Create a test image (simple 640x480 blank image with a rectangle that simulates a face)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Draw a rectangle to simulate a face (x, y, width, height)
        face_x, face_y, face_w, face_h = 250, 150, 120, 150
        cv2.rectangle(img, (face_x, face_y), (face_x + face_w, face_y + face_h), (255, 255, 255), -1)
        
        logger.info("Created test image with a simulated face")
        
        # Initialize the face detector with default settings (should fall back to haar)
        detector = FaceDetector()
        logger.info(f"Testing face detector with method: {detector.detection_method}")
        
        # Detect faces
        detected_faces = detector.detect_faces(img)
        
        # Log results
        if len(detected_faces) > 0:
            logger.info(f"Successfully detected {len(detected_faces)} face(s)")
            for i, face in enumerate(detected_faces):
                logger.info(f"Face {i+1}: {face}")
        else:
            logger.warning("No faces detected with default detector")
            
        # Try each available detection method
        for method in DETECTION_METHODS:
            try:
                logger.info(f"Testing with detection method: {method}")
                detector = FaceDetector(detection_method=method)
                faces = detector.detect_faces(img)
                logger.info(f"Method {method} detected {len(faces)} face(s)")
            except Exception as e:
                logger.error(f"Failed to detect with {method}: {str(e)}")
                
        logger.info("Face detector test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during face detection test: {str(e)}", exc_info=True)
        logger.error("Face detector test failed")
        return False

if __name__ == "__main__":
    test_face_detector()