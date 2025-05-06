#!/usr/bin/env python3
"""
Simple Webcam Face Detection Test Script

This script provides a minimalist approach to test webcam face detection.
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path
import logging

# Add the project root directory to the Python path
root_dir = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root_dir))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_webcam():
    """Simple test to verify the webcam is working properly."""
    
    # Open webcam (try a few indices if the first one doesn't work)
    cap = None
    for i in range(3):  # Try camera indices 0, 1, 2
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                logger.info(f"Successfully opened camera with index {i}")
                break
        except:
            continue
    
    if cap is None or not cap.isOpened():
        logger.error("Failed to open any camera")
        return False
    
    logger.info("Webcam test started. Press 'q' to quit.")
    
    # Process frames from the webcam
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to grab frame from webcam")
            break
            
        # Display the frame
        try:
            cv2.imshow("Webcam Test", frame)
        except cv2.error as e:
            logger.error(f"OpenCV error: {e}")
            logger.error("This likely means you need to install libgtk2.0-dev for GUI support")
            break
            
        # Check for key press (quit on 'q')
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            logger.info("Quitting webcam test")
            break
    
    # Release webcam and close windows
    cap.release()
    cv2.destroyAllWindows()
    
    return True

if __name__ == "__main__":
    if test_webcam():
        print("Webcam test completed successfully.")
    else:
        print("Webcam test failed.")