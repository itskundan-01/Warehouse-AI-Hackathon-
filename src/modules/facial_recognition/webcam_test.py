#!/usr/bin/env python3
"""
Webcam Face Detection Test Script

This script tests the face detection system using your laptop's webcam.
It will help verify that the MTCNN face detector is working properly
after fixing the API compatibility issue.
"""

import cv2
import sys
import logging
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Import the FaceDetector from the local module
from src.modules.facial_recognition.face_detector import FaceDetector

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("webcam_test")

def test_webcam_face_detection():
    """
    Test face detection using the laptop webcam.
    
    Press 'q' to quit the test.
    Press 'm' to cycle through different detection methods.
    """
    # Available detection methods
    methods = ["opencv-dnn", "mtcnn", "haar"]
    current_method_index = 0
    
    # Initialize the face detector with default settings
    detector = FaceDetector(method=methods[current_method_index])
    logger.info(f"Starting with detection method: {methods[current_method_index]}")
    
    # Open webcam
    cap = cv2.VideoCapture(0)  # 0 is usually the default webcam
    if not cap.isOpened():
        logger.error("Could not open webcam. Please check your camera connection.")
        return False
        
    logger.info("Webcam test started. Press 'q' to quit, 'm' to change detection method.")
    
    # FPS calculation variables
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to grab frame from webcam")
            break
            
        # Calculate FPS
        fps_frame_count += 1
        fps_current_time = time.time()
        time_diff = fps_current_time - fps_start_time
        
        if time_diff >= 1.0:
            fps = fps_frame_count / time_diff
            fps_start_time = fps_current_time
            fps_frame_count = 0
            
        # Start time for processing
        start_time = time.time()
        
        # Detect faces
        try:
            faces = detector.detect_faces(frame)
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Draw faces on the frame
            for face in faces:
                # Extract bbox [x, y, width, height]
                x, y, w, h = face['bbox']
                confidence = face['confidence']
                
                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Add confidence text
                label = f"{confidence:.2f}"
                cv2.putText(frame, label, (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add method and FPS info to the frame
            method_text = f"Method: {methods[current_method_index]}"
            cv2.putText(frame, method_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                       
            fps_text = f"FPS: {fps:.1f}, Processing: {processing_time:.1f}ms"
            cv2.putText(frame, fps_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                       
            face_count_text = f"Faces: {len(faces)}"
            cv2.putText(frame, face_count_text, (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                       
            # Display help text
            cv2.putText(frame, "Press 'q' to quit, 'm' to change method", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
        except Exception as e:
            logger.error(f"Error during face detection: {str(e)}")
            error_text = f"Error: {str(e)}"
            cv2.putText(frame, error_text, (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Show frame
        cv2.imshow("Webcam Face Detection Test", frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        # Quit if 'q' is pressed
        if key == ord('q'):
            logger.info("Quitting webcam test")
            break
            
        # Change method if 'm' is pressed
        if key == ord('m'):
            current_method_index = (current_method_index + 1) % len(methods)
            detector = FaceDetector(method=methods[current_method_index])
            logger.info(f"Switched to detection method: {methods[current_method_index]}")
    
    # Release webcam and close all windows
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    test_webcam_face_detection()