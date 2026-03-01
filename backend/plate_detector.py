"""
Vehicle Number Plate Detection and Tracking System
Single core file for comprehensive license plate detection using YOLOv8 and EasyOCR.
Handles both image and video processing with MongoDB integration.
"""

import os
import cv2
import numpy as np
import easyocr
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import mimetypes

# YOLOv8 for object detection
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("YOLOv8 not available. Using fallback detection methods.")

# MongoDB async driver
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlateDetector:
    """
    Comprehensive license plate detection and tracking system.
    Handles both images and videos with automatic file type detection.
    """
    
    def __init__(self, 
                 confidence_threshold: float = 0.5,
                 mongodb_url: str = "mongodb://localhost:27017/warehouse_vision",
                 model_path: Optional[str] = None):
        """
        Initialize the plate detector.
        
        Args:
            confidence_threshold: Minimum confidence for detections (0.0-1.0)
            mongodb_url: MongoDB connection URL
            model_path: Path to custom YOLOv8 model (optional)
        """
        self.confidence_threshold = confidence_threshold
        self.mongodb_url = mongodb_url
        
        # Initialize detection models
        self._initialize_yolo_model(model_path)
        self._initialize_ocr_reader()
        
        # MongoDB connection (will be initialized when needed)
        self.mongo_client = None
        self.db = None
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("PlateDetector initialized successfully")
    
    def _initialize_yolo_model(self, model_path: Optional[str] = None):
        """Initialize YOLOv8 model for vehicle/plate detection."""
        try:
            if YOLO_AVAILABLE:
                if model_path and os.path.exists(model_path):
                    self.yolo_model = YOLO(model_path)
                    logger.info(f"Loaded custom YOLO model from {model_path}")
                else:
                    # Use pre-trained YOLOv8 model
                    self.yolo_model = YOLO('yolov8n.pt')  # Nano version for speed
                    logger.info("Loaded YOLOv8n pre-trained model")
                self.yolo_available = True
            else:
                self.yolo_model = None
                self.yolo_available = False
                logger.warning("YOLOv8 not available. Using OpenCV cascade classifiers.")
                
        except Exception as e:
            logger.error(f"Failed to initialize YOLO model: {e}")
            self.yolo_model = None
            self.yolo_available = False
    
    def _initialize_ocr_reader(self):
        """Initialize EasyOCR reader for text extraction."""
        try:
            # Initialize EasyOCR with English support
            self.ocr_reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if CUDA available
            self.ocr_available = True
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            self.ocr_reader = None
            self.ocr_available = False
    
    async def _get_database(self):
        """Get MongoDB database connection."""
        if not self.mongo_client:
            self.mongo_client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.mongo_client.get_default_database()
        return self.db
    
    def _is_video_file(self, file_path: str) -> bool:
        """Check if file is a video based on MIME type."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith('video/')
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is an image based on MIME type."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type and mime_type.startswith('image/')
    
    def _detect_vehicles_yolo(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect vehicles using YOLOv8."""
        if not self.yolo_available:
            return []
        
        try:
            # Run YOLOv8 inference
            results = self.yolo_model(image, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        # Get class ID and check if it's a vehicle
                        class_id = int(box.cls[0])
                        class_name = self.yolo_model.names[class_id]
                        
                        # Filter for vehicles (car, truck, bus, motorcycle, etc.)
                        vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
                        if class_name.lower() in vehicle_classes:
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = float(box.conf[0])
                            
                            detections.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': confidence,
                                'class': class_name,
                                'vehicle_region': image[int(y1):int(y2), int(x1):int(x2)]
                            })
            
            return detections
            
        except Exception as e:
            logger.error(f"YOLO vehicle detection failed: {e}")
            return []
    
    def _detect_plates_in_vehicle(self, vehicle_region: np.ndarray) -> List[Dict[str, Any]]:
        """Detect license plates within a vehicle region."""
        if vehicle_region.size == 0:
            return []
        
        # Method 1: Use YOLO if available and trained for plates
        if self.yolo_available:
            try:
                results = self.yolo_model(vehicle_region, conf=self.confidence_threshold)
                plate_detections = []
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = float(box.conf[0])
                            
                            # Extract plate region
                            plate_region = vehicle_region[int(y1):int(y2), int(x1):int(x2)]
                            
                            if plate_region.size > 0:
                                plate_detections.append({
                                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                    'confidence': confidence,
                                    'plate_region': plate_region
                                })
                
                if plate_detections:
                    return plate_detections
                    
            except Exception as e:
                logger.debug(f"YOLO plate detection failed, using fallback: {e}")
        
        # Method 2: OpenCV-based plate detection (fallback)
        return self._detect_plates_opencv(vehicle_region)
    
    def _detect_plates_opencv(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect license plates using OpenCV techniques."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Edge detection
            edges = cv2.Canny(filtered, 30, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
            
            plate_detections = []
            
            for contour in contours:
                # Approximate contour
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.018 * perimeter, True)
                
                # License plates typically have 4 corners
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Check aspect ratio (plates are wider than tall)
                    aspect_ratio = w / float(h)
                    if 2.0 < aspect_ratio < 5.5 and w > 50 and h > 15:
                        # Extract plate region
                        plate_region = image[y:y+h, x:x+w]
                        
                        # Calculate confidence based on edge density
                        edge_density = cv2.countNonZero(edges[y:y+h, x:x+w]) / (w * h)
                        confidence = min(edge_density * 2, 1.0)  # Scale to 0-1
                        
                        if confidence > self.confidence_threshold:
                            plate_detections.append({
                                'bbox': [x, y, x+w, y+h],
                                'confidence': confidence,
                                'plate_region': plate_region
                            })
            
            return plate_detections
            
        except Exception as e:
            logger.error(f"OpenCV plate detection failed: {e}")
            return []
    
    def _extract_plate_text(self, plate_region: np.ndarray) -> str:
        """Extract text from license plate region using EasyOCR."""
        if not self.ocr_available or plate_region.size == 0:
            return ""
        
        try:
            # Preprocess image for better OCR
            processed_plate = self._preprocess_plate_image(plate_region)
            
            # Use EasyOCR to extract text
            results = self.ocr_reader.readtext(processed_plate)
            
            # Filter and clean results
            plate_texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only consider high-confidence text
                    # Clean text (remove spaces, special chars)
                    clean_text = ''.join(char.upper() for char in text if char.isalnum())
                    if len(clean_text) >= 4:  # Valid plate should have at least 4 characters
                        plate_texts.append((clean_text, confidence))
            
            # Return the highest confidence text
            if plate_texts:
                plate_texts.sort(key=lambda x: x[1], reverse=True)
                return plate_texts[0][0]
            
            return ""
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return ""
    
    def _preprocess_plate_image(self, plate_region: np.ndarray) -> np.ndarray:
        """Preprocess plate image for better OCR results."""
        try:
            # Convert to grayscale if needed
            if len(plate_region.shape) == 3:
                gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_region.copy()
            
            # Resize to standard size for better OCR
            height, width = gray.shape
            if width < 200:
                scale_factor = 200 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Apply CLAHE for better contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
            
        except Exception as e:
            logger.error(f"Plate preprocessing failed: {e}")
            return plate_region
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process a single image for license plate detection.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with detection results
        """
        logger.info(f"Processing image: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Detect vehicles first
            vehicle_detections = self._detect_vehicles_yolo(image)
            
            # If no vehicles detected, search entire image for plates
            if not vehicle_detections:
                logger.info("No vehicles detected, searching entire image for plates")
                plate_detections = self._detect_plates_opencv(image)
            else:
                # Search for plates within detected vehicles
                plate_detections = []
                for vehicle in vehicle_detections:
                    vehicle_plates = self._detect_plates_in_vehicle(vehicle['vehicle_region'])
                    plate_detections.extend(vehicle_plates)
            
            # Extract text from detected plates
            results = []
            for i, plate in enumerate(plate_detections):
                plate_text = self._extract_plate_text(plate['plate_region'])
                
                if plate_text:  # Only include if text was successfully extracted
                    result = {
                        'id': f"plate_{i}",
                        'bbox': plate['bbox'],
                        'confidence': plate['confidence'],
                        'plate_text': plate_text,
                        'timestamp': datetime.utcnow().isoformat(),
                        'source_file': image_path,
                        'source_type': 'image'
                    }
                    results.append(result)
            
            summary = {
                'total_plates_detected': len(results),
                'plates': results,
                'processing_time': datetime.utcnow().isoformat(),
                'source_file': image_path,
                'source_type': 'image'
            }
            
            logger.info(f"Image processing complete. Found {len(results)} plates with text.")
            return summary
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {
                'error': str(e),
                'total_plates_detected': 0,
                'plates': [],
                'source_file': image_path,
                'source_type': 'image'
            }
    
    def process_video(self, video_path: str, frame_skip: int = 30) -> Dict[str, Any]:
        """
        Process a video file for license plate detection.
        
        Args:
            video_path: Path to the video file
            frame_skip: Process every Nth frame (default: 30, ~1 fps for 30fps video)
            
        Returns:
            Dictionary with detection results
        """
        logger.info(f"Processing video: {video_path}")
        
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            results = []
            frame_count = 0
            unique_plates = set()
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every Nth frame
                if frame_count % frame_skip == 0:
                    timestamp_seconds = frame_count / fps if fps > 0 else frame_count
                    
                    # Detect vehicles in frame
                    vehicle_detections = self._detect_vehicles_yolo(frame)
                    
                    # Search for plates
                    if not vehicle_detections:
                        plate_detections = self._detect_plates_opencv(frame)
                    else:
                        plate_detections = []
                        for vehicle in vehicle_detections:
                            vehicle_plates = self._detect_plates_in_vehicle(vehicle['vehicle_region'])
                            plate_detections.extend(vehicle_plates)
                    
                    # Extract text from detected plates
                    for i, plate in enumerate(plate_detections):
                        plate_text = self._extract_plate_text(plate['plate_region'])
                        
                        if plate_text and len(plate_text) >= 4:
                            unique_plates.add(plate_text)
                            
                            result = {
                                'id': f"frame_{frame_count}_plate_{i}",
                                'frame_number': frame_count,
                                'timestamp_seconds': timestamp_seconds,
                                'bbox': plate['bbox'],
                                'confidence': plate['confidence'],
                                'plate_text': plate_text,
                                'timestamp': datetime.utcnow().isoformat(),
                                'source_file': video_path,
                                'source_type': 'video'
                            }
                            results.append(result)
                
                frame_count += 1
            
            cap.release()
            
            summary = {
                'total_frames': total_frames,
                'processed_frames': frame_count // frame_skip,
                'fps': fps,
                'duration_seconds': duration,
                'total_detections': len(results),
                'unique_plates': list(unique_plates),
                'unique_plate_count': len(unique_plates),
                'detections': results,
                'processing_time': datetime.utcnow().isoformat(),
                'source_file': video_path,
                'source_type': 'video'
            }
            
            logger.info(f"Video processing complete. Found {len(unique_plates)} unique plates in {len(results)} detections.")
            return summary
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return {
                'error': str(e),
                'total_detections': 0,
                'unique_plates': [],
                'detections': [],
                'source_file': video_path,
                'source_type': 'video'
            }
    
    async def store_results(self, results: Dict[str, Any], location: str = "unknown") -> bool:
        """
        Store detection results in MongoDB.
        
        Args:
            results: Detection results from process_image or process_video
            location: Location where detection was performed
            
        Returns:
            Success status
        """
        try:
            db = await self._get_database()
            collection = db.license_plate_detections
            
            # Prepare document for storage
            document = {
                'detection_id': f"{results.get('source_type', 'unknown')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'location': location,
                'source_file': results.get('source_file', ''),
                'source_type': results.get('source_type', 'unknown'),
                'total_detections': results.get('total_detections', 0),
                'unique_plates': results.get('unique_plates', []),
                'unique_plate_count': results.get('unique_plate_count', len(results.get('plates', []))),
                'detections': results.get('plates', results.get('detections', [])),
                'processing_time': results.get('processing_time'),
                'created_at': datetime.utcnow(),
                'metadata': {
                    'confidence_threshold': self.confidence_threshold,
                    'yolo_available': self.yolo_available,
                    'ocr_available': self.ocr_available
                }
            }
            
            # Add video-specific metadata
            if results.get('source_type') == 'video':
                document['video_metadata'] = {
                    'total_frames': results.get('total_frames', 0),
                    'processed_frames': results.get('processed_frames', 0),
                    'fps': results.get('fps', 0),
                    'duration_seconds': results.get('duration_seconds', 0)
                }
            
            # Insert document
            result = await collection.insert_one(document)
            
            # Also store individual plate records for easy querying
            if results.get('plates') or results.get('detections'):
                plates_collection = db.license_plates
                plate_records = []
                
                plates_data = results.get('plates', results.get('detections', []))
                for plate_data in plates_data:
                    if plate_data.get('plate_text'):
                        plate_record = {
                            'plate_text': plate_data['plate_text'],
                            'location': location,
                            'confidence': plate_data.get('confidence', 0.0),
                            'detection_id': str(result.inserted_id),
                            'source_file': results.get('source_file', ''),
                            'source_type': results.get('source_type', 'unknown'),
                            'bbox': plate_data.get('bbox', []),
                            'timestamp': plate_data.get('timestamp'),
                            'created_at': datetime.utcnow(),
                            'is_verified': False  # Can be updated manually
                        }
                        
                        # Add frame info for video sources
                        if results.get('source_type') == 'video':
                            plate_record['frame_number'] = plate_data.get('frame_number', 0)
                            plate_record['timestamp_seconds'] = plate_data.get('timestamp_seconds', 0)
                        
                        plate_records.append(plate_record)
                
                if plate_records:
                    await plates_collection.insert_many(plate_records)
            
            logger.info(f"Successfully stored detection results in MongoDB: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store results in MongoDB: {e}")
            return False
    
    async def get_plate_history(self, plate_text: str) -> List[Dict[str, Any]]:
        """
        Get detection history for a specific license plate.
        
        Args:
            plate_text: License plate text to search for
            
        Returns:
            List of detection records
        """
        try:
            db = await self._get_database()
            collection = db.license_plates
            
            cursor = collection.find({'plate_text': plate_text}).sort('created_at', -1)
            records = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if 'detection_id' in record:
                    record['detection_id'] = str(record['detection_id'])
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get plate history: {e}")
            return []
    
    async def get_recent_detections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent license plate detections.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent detection records
        """
        try:
            db = await self._get_database()
            collection = db.license_plates
            
            cursor = collection.find().sort('created_at', -1).limit(limit)
            records = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if 'detection_id' in record:
                    record['detection_id'] = str(record['detection_id'])
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get recent detections: {e}")
            return []
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Automatically process a file (image or video) based on its type.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary with detection results
        """
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        if self._is_image_file(file_path):
            return self.process_image(file_path)
        elif self._is_video_file(file_path):
            return self.process_video(file_path)
        else:
            return {'error': f'Unsupported file type: {file_path}'}
    
    async def close(self):
        """Close MongoDB connection and cleanup resources."""
        if self.mongo_client:
            self.mongo_client.close()
        
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)


# Convenience function for quick testing
async def detect_plates_from_file(file_path: str, 
                                location: str = "test", 
                                store_in_db: bool = True) -> Dict[str, Any]:
    """
    Convenience function to detect plates from a file and optionally store in database.
    
    Args:
        file_path: Path to image or video file
        location: Location where detection was performed
        store_in_db: Whether to store results in MongoDB
        
    Returns:
        Detection results
    """
    detector = PlateDetector()
    
    try:
        results = detector.process_file(file_path)
        
        if store_in_db and 'error' not in results:
            await detector.store_results(results, location)
        
        return results
        
    finally:
        await detector.close()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plate_detector.py <image_or_video_path> [location]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    location = sys.argv[2] if len(sys.argv) > 2 else "command_line"
    
    async def main():
        results = await detect_plates_from_file(file_path, location, store_in_db=True)
        print("Detection Results:")
        print(f"File: {results.get('source_file', file_path)}")
        print(f"Type: {results.get('source_type', 'unknown')}")
        
        if 'error' in results:
            print(f"Error: {results['error']}")
        else:
            plates = results.get('plates', results.get('detections', []))
            unique_plates = results.get('unique_plates', [])
            
            print(f"Total detections: {len(plates)}")
            print(f"Unique plates: {len(unique_plates)}")
            
            if unique_plates:
                print("Detected plates:")
                for plate in unique_plates:
                    print(f"  - {plate}")
    
    asyncio.run(main())
