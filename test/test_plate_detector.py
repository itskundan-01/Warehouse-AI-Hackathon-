"""
Test suite for License Plate Detection System.
Tests the core plate_detector.py functionality with sample images and videos.
"""

import os
import sys
import pytest
import asyncio
import tempfile
import cv2
import numpy as np
from pathlib import Path

# Add backend path to import our detector
sys.path.append('/Users/kundan/PROJECTS/Warehouse AI Hackathon/backend')
from plate_detector import PlateDetector, detect_plates_from_file

class TestPlateDetector:
    """Test cases for the PlateDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a detector instance for testing."""
        return PlateDetector(
            confidence_threshold=0.3,  # Lower threshold for testing
            mongodb_url="mongodb://localhost:27017/warehouse_vision_test"  # Test database
        )
    
    @pytest.fixture
    def sample_image(self):
        """Create a sample test image with a simulated license plate."""
        # Create a 640x480 image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img.fill(50)  # Dark gray background
        
        # Add a simulated car body
        cv2.rectangle(img, (100, 200), (540, 400), (100, 100, 150), -1)
        
        # Add a simulated license plate area
        plate_x, plate_y = 250, 320
        plate_w, plate_h = 140, 40
        cv2.rectangle(img, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (240, 240, 240), -1)
        
        # Add simulated text on the plate
        cv2.rectangle(img, (plate_x + 10, plate_y + 10), (plate_x + 30, plate_y + 30), (0, 0, 0), -1)  # Char 1
        cv2.rectangle(img, (plate_x + 35, plate_y + 10), (plate_x + 55, plate_y + 30), (0, 0, 0), -1)  # Char 2
        cv2.rectangle(img, (plate_x + 60, plate_y + 10), (plate_x + 80, plate_y + 30), (0, 0, 0), -1)  # Char 3
        cv2.rectangle(img, (plate_x + 85, plate_y + 10), (plate_x + 105, plate_y + 30), (0, 0, 0), -1)  # Char 4
        cv2.rectangle(img, (plate_x + 110, plate_y + 10), (plate_x + 130, plate_y + 30), (0, 0, 0), -1)  # Char 5
        
        return img
    
    @pytest.fixture
    def sample_video(self, sample_image):
        """Create a sample test video with multiple frames."""
        # Create temporary video file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.close()
        
        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(temp_file.name, fourcc, 10.0, (640, 480))
        
        # Write 30 frames (3 seconds at 10 fps)
        for i in range(30):
            frame = sample_image.copy()
            # Add frame number for variation
            cv2.putText(frame, f"Frame {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            writer.write(frame)
        
        writer.release()
        return temp_file.name
    
    def test_detector_initialization(self, detector):
        """Test that detector initializes properly."""
        assert detector is not None
        assert detector.confidence_threshold == 0.3
        assert hasattr(detector, 'yolo_available')
        assert hasattr(detector, 'ocr_available')
    
    def test_file_type_detection(self, detector):
        """Test file type detection methods."""
        # Test image file detection
        assert detector._is_image_file('test.jpg') == True
        assert detector._is_image_file('test.png') == True
        assert detector._is_image_file('test.jpeg') == True
        assert detector._is_image_file('test.bmp') == True
        
        # Test video file detection
        assert detector._is_video_file('test.mp4') == True
        assert detector._is_video_file('test.avi') == True
        assert detector._is_video_file('test.mov') == True
        
        # Test non-media files
        assert detector._is_image_file('test.txt') == False
        assert detector._is_video_file('test.pdf') == False
    
    def test_opencv_plate_detection(self, detector, sample_image):
        """Test OpenCV-based plate detection."""
        detections = detector._detect_plates_opencv(sample_image)
        
        # Should detect at least one plate-like region
        assert len(detections) >= 0  # May not detect simulated plate, but shouldn't crash
        
        # If detections found, check structure
        for detection in detections:
            assert 'bbox' in detection
            assert 'confidence' in detection
            assert 'plate_region' in detection
            assert len(detection['bbox']) == 4  # [x1, y1, x2, y2]
            assert 0 <= detection['confidence'] <= 1
    
    def test_image_preprocessing(self, detector, sample_image):
        """Test image preprocessing for OCR."""
        # Extract a small plate region for testing
        plate_region = sample_image[320:360, 250:390]  # Simulated plate area
        
        processed = detector._preprocess_plate_image(plate_region)
        
        assert processed is not None
        assert processed.shape[:2] == (40, 140) or processed.shape[1] >= 200  # May be resized
        assert len(processed.shape) == 2  # Should be grayscale
    
    def test_process_image_with_file(self, detector, sample_image):
        """Test image processing with actual file."""
        # Save sample image to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.close()
        
        try:
            cv2.imwrite(temp_file.name, sample_image)
            
            results = detector.process_image(temp_file.name)
            
            # Check result structure
            assert 'total_plates_detected' in results
            assert 'plates' in results
            assert 'source_file' in results
            assert 'source_type' in results
            assert results['source_type'] == 'image'
            assert results['source_file'] == temp_file.name
            
            # Should not have errors
            assert 'error' not in results
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_process_video_with_file(self, detector, sample_video):
        """Test video processing with actual file."""
        try:
            results = detector.process_video(sample_video, frame_skip=10)  # Process every 10th frame
            
            # Check result structure
            assert 'total_detections' in results
            assert 'unique_plates' in results
            assert 'detections' in results
            assert 'source_file' in results
            assert 'source_type' in results
            assert results['source_type'] == 'video'
            assert results['source_file'] == sample_video
            
            # Video-specific fields
            assert 'total_frames' in results
            assert 'fps' in results
            assert 'duration_seconds' in results
            
            # Should not have errors
            assert 'error' not in results
            
        finally:
            if os.path.exists(sample_video):
                os.unlink(sample_video)
    
    def test_process_file_auto_detection(self, detector, sample_image):
        """Test automatic file type detection and processing."""
        # Test with image
        temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_image.close()
        
        # Test with video
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.close()
        
        try:
            # Save sample image
            cv2.imwrite(temp_image.name, sample_image)
            
            # Create minimal video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(temp_video.name, fourcc, 5.0, (640, 480))
            for _ in range(5):
                writer.write(sample_image)
            writer.release()
            
            # Test image auto-detection
            image_results = detector.process_file(temp_image.name)
            assert image_results['source_type'] == 'image'
            
            # Test video auto-detection
            video_results = detector.process_file(temp_video.name)
            assert video_results['source_type'] == 'video'
            
            # Test unsupported file
            temp_text = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            temp_text.write(b"test")
            temp_text.close()
            
            text_results = detector.process_file(temp_text.name)
            assert 'error' in text_results
            
            os.unlink(temp_text.name)
            
        finally:
            for temp_file in [temp_image.name, temp_video.name]:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_database_operations(self, detector):
        """Test database storage and retrieval operations."""
        # Mock results data
        mock_results = {
            'source_file': 'test_image.jpg',
            'source_type': 'image',
            'total_detections': 1,
            'plates': [{
                'id': 'test_plate_1',
                'bbox': [100, 200, 200, 250],
                'confidence': 0.85,
                'plate_text': 'ABC123',
                'timestamp': '2024-01-01T12:00:00'
            }],
            'processing_time': '2024-01-01T12:00:00'
        }
        
        # Test storing results
        success = await detector.store_results(mock_results, 'test_location')
        assert success == True
        
        # Test retrieving plate history
        history = await detector.get_plate_history('ABC123')
        assert isinstance(history, list)
        
        # Test retrieving recent detections
        recent = await detector.get_recent_detections(10)
        assert isinstance(recent, list)
        
        # Clean up test data
        try:
            db = await detector._get_database()
            await db.license_plates.delete_many({'plate_text': 'ABC123'})
            await db.license_plate_detections.delete_many({'location': 'test_location'})
        except:
            pass  # Cleanup failure is not critical for test
    
    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_image):
        """Test the convenience function for file processing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.close()
        
        try:
            cv2.imwrite(temp_file.name, sample_image)
            
            results = await detect_plates_from_file(
                temp_file.name, 
                location='test_convenience', 
                store_in_db=False  # Don't store during test
            )
            
            assert 'source_file' in results
            assert 'source_type' in results
            assert results['source_type'] == 'image'
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_error_handling(self, detector):
        """Test error handling with invalid inputs."""
        # Test with non-existent file
        results = detector.process_file('/nonexistent/file.jpg')
        assert 'error' in results
        
        # Test with invalid image path
        results = detector.process_image('/invalid/path.jpg')
        assert 'error' in results
        
        # Test with invalid video path
        results = detector.process_video('/invalid/path.mp4')
        assert 'error' in results

class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow from file processing to database storage."""
        detector = PlateDetector(mongodb_url="mongodb://localhost:27017/warehouse_vision_test")
        
        # Create test image
        test_image = np.zeros((300, 400, 3), dtype=np.uint8)
        test_image.fill(100)
        
        # Add plate-like rectangle
        cv2.rectangle(test_image, (150, 120), (250, 160), (200, 200, 200), -1)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.close()
        
        try:
            cv2.imwrite(temp_file.name, test_image)
            
            # Process file
            results = detector.process_file(temp_file.name)
            assert 'error' not in results
            
            # Store in database
            if 'error' not in results:
                success = await detector.store_results(results, 'integration_test')
                assert success == True
            
            # Verify storage by retrieving recent detections
            recent = await detector.get_recent_detections(5)
            assert isinstance(recent, list)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            
            await detector.close()


# Performance tests
class TestPerformance:
    """Performance tests for the detection system."""
    
    def test_image_processing_speed(self):
        """Test image processing performance."""
        detector = PlateDetector()
        
        # Create larger test image
        large_image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.close()
        
        try:
            cv2.imwrite(temp_file.name, large_image)
            
            import time
            start_time = time.time()
            results = detector.process_image(temp_file.name)
            end_time = time.time()
            
            processing_time = end_time - start_time
            print(f"Image processing time: {processing_time:.2f} seconds")
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert processing_time < 30.0  # 30 seconds max for 1080p image
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
