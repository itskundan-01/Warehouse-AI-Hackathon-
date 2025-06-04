#!/usr/bin/env python3
"""
Test script to verify face detection using the webcam without requiring OpenCV GUI.
This script captures frames from the webcam, attempts to detect faces,
and logs results to the terminal. It also saves images with detected faces.
"""

import cv2
import numpy as np
import logging
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Import the FaceDetector from the local module
try:
    from src.modules.facial_recognition.face_detector import FaceDetector
    print("Successfully imported FaceDetector")
except ImportError as e:
    print(f"Error importing FaceDetector: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webcam_face_test")

def test_webcam_face_detection():
    """Test the face detector with webcam input"""
    try:
        # Initialize the face detector with default settings
        detector = FaceDetector()
        logger.info(f"Testing face detector with method: {detector.method}")
        
        # Initialize the webcam
        logger.info("Initializing webcam...")
        cap = cv2.VideoCapture(0)  # 0 is usually the default webcam
        
        if not cap.isOpened():
            logger.error("Failed to open webcam. Please check if it's connected properly.")
            return False
            
        logger.info("Webcam initialized successfully.")
        logger.info("Capturing frames for 20 seconds. Please position yourself in front of the camera.")
        
        # Create output directory for saving images
        output_dir = Path(__file__).parent / "test_output"
        output_dir.mkdir(exist_ok=True)
        logger.info(f"Images with detected faces will be saved to: {output_dir}")
        
        # Capture frames for a limited time (20 seconds)
        start_time = time.time()
        frame_count = 0
        detected_frame_count = 0
        
        while (time.time() - start_time) < 20:  # Run for 20 seconds
            ret, frame = cap.read()
            
            if not ret:
                logger.error("Failed to capture frame.")
                break
                
            frame_count += 1
            
            if frame_count % 10 == 0:  # Process every 10th frame to reduce CPU load
                logger.info(f"Processing frame {frame_count}")
                
                # Detect faces
                try:
                    detected_faces = detector.detect_faces(frame)
                    
                    if detected_faces:
                        detected_frame_count += 1
                        logger.info(f"Detected {len(detected_faces)} face(s) in frame {frame_count}!")
                        
                        # Draw rectangles around detected faces
                        for face in detected_faces:
                            if 'box' in face:
                                x, y, w, h = face['box']
                                confidence = face.get('confidence', 0)
                                
                                # Draw rectangle on a copy of the frame
                                marked_frame = frame.copy()
                                cv2.rectangle(marked_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                
                                # Save image with detection boxes
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"face_detected_{timestamp}_conf_{confidence:.2f}.jpg"
                                output_path = output_dir / filename
                                cv2.imwrite(str(output_path), marked_frame)
                                logger.info(f"Saved image with detection: {output_path}")
                    else:
                        logger.info("No faces detected in this frame.")
                        
                except Exception as e:
                    logger.error(f"Error during face detection: {str(e)}")
        
        # Release the webcam
        cap.release()
        
        # Report results
        logger.info(f"Test completed. Processed {frame_count} frames.")
        logger.info(f"Faces were detected in {detected_frame_count} frames.")
        
        if detected_frame_count > 0:
            logger.info(f"Face detection SUCCESS! Check the images saved in {output_dir}")
            return True
        else:
            logger.info("No faces were detected during the test.")
            logger.info("This could be due to lighting conditions, camera position, or face detection sensitivity.")
            logger.info("Try adjusting your position or lighting and run the test again.")
            return False
            
    except Exception as e:
        logger.error(f"Error during webcam face detection test: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    print("Starting webcam face detection test...")
    result = test_webcam_face_detection()
    print(f"Test {'successful' if result else 'failed or no faces detected'}.")