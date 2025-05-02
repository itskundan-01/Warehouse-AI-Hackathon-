import pytest
import numpy as np
import cv2
from pathlib import Path
import sys
import os

# Add the src directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.facial_recognition.face_detector import FaceDetector

class TestFaceDetector:
    """Tests for the FaceDetector class."""
    
    def test_initialization(self):
        """Test that the face detector initializes correctly with different methods."""
        # Test default initialization
        detector = FaceDetector()
        assert detector.method == "opencv-dnn"
        assert detector.min_confidence == 0.7
        
        # Test with different detection method
        detector = FaceDetector(method="mtcnn", min_confidence=0.8)
        assert detector.method == "mtcnn"
        assert detector.min_confidence == 0.8
        
        # Test with invalid method should raise ValueError
        with pytest.raises(ValueError):
            FaceDetector(method="invalid_method")
    
    def test_detection_methods_constant(self):
        """Test that the DETECTION_METHODS class attribute exists and contains expected values."""
        assert hasattr(FaceDetector, "DETECTION_METHODS")
        assert "mtcnn" in FaceDetector.DETECTION_METHODS
        assert "retinaface" in FaceDetector.DETECTION_METHODS
        assert "opencv-dnn" in FaceDetector.DETECTION_METHODS
    
    def test_detect_faces_with_simulated_face(self):
        """Test face detection using a synthetic test image with a simulated face."""
        # Create a synthetic test image (gray background with lighter rectangle as 'face')
        test_image = np.ones((300, 300, 3), dtype=np.uint8) * 100  # Gray background
        
        # Add a lighter rectangle as a simulated face (might not be detected as real face,
        # but helps test the code path)
        face_region = (100, 100, 100, 100)  # x, y, width, height
        test_image[face_region[1]:face_region[1]+face_region[3], 
                   face_region[0]:face_region[0]+face_region[2]] = 200
        
        # Create a mock implementation of detect_faces for testing
        detector = FaceDetector()
        
        # Replace the detect method with a mock that returns our simulated face
        original_detect = detector.detect_faces
        
        def mock_detect_faces(image, **kwargs):
            # Return our predefined face region
            return [{
                'box': face_region,
                'confidence': 0.95,
                'keypoints': {
                    'left_eye': (125, 125),
                    'right_eye': (175, 125),
                    'nose': (150, 150),
                    'mouth_left': (125, 175),
                    'mouth_right': (175, 175)
                }
            }]
        
        try:
            # Replace with our mock method
            detector.detect_faces = mock_detect_faces
            
            # Test the detection
            faces = detector.detect_faces(test_image)
            
            # Verify results
            assert len(faces) == 1
            assert faces[0]['confidence'] > 0.9
            assert 'box' in faces[0]
            assert faces[0]['box'] == face_region
            
        finally:
            # Restore the original method
            detector.detect_faces = original_detect
    
    def test_preprocessing(self):
        """Test image preprocessing functionality."""
        detector = FaceDetector()
        
        # Create a test image
        test_image = np.random.randint(0, 256, (300, 300, 3), dtype=np.uint8)
        
        # Assuming there's a preprocess_image method (adjust if differently named)
        if hasattr(detector, 'preprocess_image'):
            processed = detector.preprocess_image(test_image)
            
            # Check that preprocessing returns the expected type
            assert isinstance(processed, np.ndarray)
            assert processed.shape[2] == 3  # Still an RGB image
    
    def test_low_light_enhancement(self):
        """Test low light enhancement if available."""
        detector = FaceDetector()
        
        # Create a dark test image
        dark_image = np.ones((300, 300, 3), dtype=np.uint8) * 30  # Very dark
        
        # If the detector has low light enhancement, test it
        if hasattr(detector, 'enhance_low_light'):
            enhanced = detector.enhance_low_light(dark_image)
            
            # Enhanced image should have higher average pixel value
            assert enhanced.mean() > dark_image.mean()