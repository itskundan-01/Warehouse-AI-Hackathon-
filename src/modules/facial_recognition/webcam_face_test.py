#!/usr/bin/env python3
"""
Webcam Face Detection Test Script for WarehouseVision AI.

This script uses your laptop's camera to test the face detection functionality.
It displays the video feed with detected faces highlighted by rectangles.
Press 'q' to quit the application.
"""

import cv2
import numpy as np
import logging
import os
import sys
from pathlib import Path
import time

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Import the FaceDetector from the local module
from src.modules.facial_recognition.face_detector import FaceDetector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webcam_face_test")

def main():
    """Run face detection on webcam feed"""
    
    # Initialize face detector
    logger.info("Initializing face detector...")
    detector = FaceDetector(min_confidence=0.5)
    logger.info(f"Using detection method: {detector.method}")
    
    # Initialize webcam
    logger.info("Opening webcam...")
    cap = cv2.VideoCapture(0)  # 0 is usually the default camera
    
    if not cap.isOpened():
        logger.error("Could not open webcam. Please check your camera connection.")
        return False
    
    # Get camera properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    logger.info(f"Camera resolution: {frame_width}x{frame_height}")
    
    # Create window
    window_name = "WarehouseVision AI - Face Detection Test"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Performance tracking
    frame_count = 0
    start_time = time.time()
    fps_display_interval = 30  # Update FPS display every 30 frames
    
    logger.info("Starting video capture. Press 'q' to quit.")
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to capture frame from camera")
                break
                
            # Mirror the image (so it works like a mirror)
            frame = cv2.flip(frame, 1)
            
            # Process every other frame to improve performance
            if frame_count % 2 == 0:
                # Detect faces
                faces = detector.detect_faces(frame)
                
                # Draw bounding boxes around faces
                for face in faces:
                    if detector.method == "haar":
                        # Haar cascades return (x, y, w, h) directly
                        x, y, w, h = face
                        conf = 1.0  # Confidence not available for Haar
                    else:
                        # Other methods return a dictionary with 'box' and 'confidence'
                        try:
                            x, y, w, h = face.get('box', face)
                            conf = face.get('confidence', 0.0)
                        except:
                            # Just in case the format is unexpected
                            continue
                    
                    # Draw rectangle
                    color = (0, 255, 0)  # Green
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    
                    # Display confidence
                    if conf < 1.0:  # Only display if it's not the default
                        conf_text = f"{conf:.2f}"
                        cv2.putText(
                            frame, conf_text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                        )
            
            # Calculate and display FPS
            frame_count += 1
            if frame_count % fps_display_interval == 0:
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time
                fps_text = f"FPS: {fps:.2f}"
                cv2.putText(
                    frame, fps_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
                )
                
                # Log detected faces
                if len(faces) > 0:
                    logger.info(f"Detected {len(faces)} face(s)")
            
            # Display the detection method being used
            method_text = f"Method: {detector.method}"
            cv2.putText(
                frame, method_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2
            )
            
            # Display the resulting frame
            cv2.imshow(window_name, frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("User requested exit")
                break
    
    except Exception as e:
        logger.error(f"Error during webcam face detection: {str(e)}", exc_info=True)
    
    finally:
        # Release resources
        logger.info("Cleaning up resources...")
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Test complete")
    
    return True

if __name__ == "__main__":
    main()