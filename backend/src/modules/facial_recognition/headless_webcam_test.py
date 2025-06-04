#!/usr/bin/env python3
"""
Headless Webcam Face Detection Test Script

This script tests face detection with your webcam and saves the results
as image files without requiring GUI support.
"""

import cv2
import numpy as np
import sys
import os
import time
from datetime import datetime
from pathlib import Path
import logging

# Add the project root directory to the Python path
root_dir = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root_dir))

# Import the FaceDetector class
from src.modules.facial_recognition.face_detector import FaceDetector

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_face_detection():
    """Test face detection using webcam and save results as images."""
    
    # Create output directory for saved images
    output_dir = root_dir / "data" / "webcam_test"
    output_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Images will be saved to {output_dir}")
    
    # Initialize face detector with MTCNN
    detector = FaceDetector(method="mtcnn")
    logger.info(f"Initialized face detector with method: {detector.method}")
    
    # Open webcam
    cap = None
    for i in range(3):  # Try camera indices 0, 1, 2
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                logger.info(f"Successfully opened camera with index {i}")
                break
        except Exception as e:
            logger.error(f"Failed to open camera {i}: {str(e)}")
            continue
    
    if cap is None or not cap.isOpened():
        logger.error("Failed to open any camera")
        return False
    
    logger.info("Webcam test started. Will capture 5 frames with 1 second interval...")
    
    # Process frames from webcam
    frame_count = 0
    face_count = 0
    max_frames = 5  # Capture 5 frames for testing
    
    while frame_count < max_frames:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to grab frame from webcam")
            break
        
        frame_count += 1
        timestamp = datetime.now().strftime("%H%M%S")
        
        # Save original frame
        orig_path = output_dir / f"frame_{timestamp}_original.jpg"
        cv2.imwrite(str(orig_path), frame)
        logger.info(f"Saved original frame to {orig_path}")
        
        # Try to detect faces using our modified detector
        try:
            # Create a method that simulates face detection
            faces = []
            
            # Try using the detector if available
            if hasattr(detector, 'detect_faces'):
                faces = detector.detect_faces(frame)
                logger.info(f"Detected {len(faces)} faces using {detector.method}")
            else:
                logger.error("detect_faces method not available in detector")
                # Create a simple fallback face detector using Haar cascades
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_rects = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                
                # Convert to the format expected by our processing code
                for (x, y, w, h) in face_rects:
                    faces.append({
                        'bbox': [x, y, w, h],
                        'confidence': 0.9  # Default confidence
                    })
                logger.info(f"Detected {len(faces)} faces using fallback Haar cascade")
                
            # Create a copy of frame for drawing face rectangles
            annotated_frame = frame.copy()
            
            # Process detected faces
            for i, face in enumerate(faces):
                # Get face box coordinates
                if 'bbox' in face:
                    bbox = face['bbox']
                    if len(bbox) == 4:
                        # Format might be [x, y, w, h] or [x1, y1, x2, y2]
                        if bbox[2] < bbox[0] or bbox[3] < bbox[1]:  # It's [x1, y1, x2, y2]
                            x, y = bbox[0], bbox[1]
                            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                        else:  # It's [x, y, w, h]
                            x, y, w, h = bbox
                            
                        # Draw rectangle on annotated frame
                        cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        
                        # Add confidence text if available
                        if 'confidence' in face:
                            conf_text = f"{face['confidence']:.2f}"
                            cv2.putText(annotated_frame, conf_text, (x, y - 10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
                        # Extract and save just the face region
                        face_img = frame[y:y+h, x:x+w]
                        face_path = output_dir / f"frame_{timestamp}_face_{i}.jpg"
                        cv2.imwrite(str(face_path), face_img)
                        face_count += 1
                        logger.info(f"Saved face {i} to {face_path}")
            
            # Save annotated frame
            annotated_path = output_dir / f"frame_{timestamp}_annotated.jpg"
            cv2.imwrite(str(annotated_path), annotated_frame)
            logger.info(f"Saved annotated frame to {annotated_path}")
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Wait before capturing next frame
        time.sleep(1)
    
    # Release webcam
    cap.release()
    
    logger.info(f"Test completed. Processed {frame_count} frames and detected {face_count} faces.")
    logger.info(f"Results saved to {output_dir}")
    
    return True

if __name__ == "__main__":
    if test_face_detection():
        print("Face detection test completed successfully.")
    else:
        print("Face detection test failed.")