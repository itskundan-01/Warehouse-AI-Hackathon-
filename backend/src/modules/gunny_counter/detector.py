"""
Gunny Bag Detector module.
Detects gunny bags in images using computer vision techniques.
"""
import os
import numpy as np
import cv2
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class GunnyBagDetector:
    """Class for detecting gunny bags in images."""
    
    def __init__(self, confidence_threshold: float = 0.5, model_path: Optional[str] = None):
        """Initialize the detector with confidence threshold."""
        self.confidence_threshold = confidence_threshold
        self.last_confidence = 0.0
        
        # Initialize YOLOv8 model path
        if model_path is None:
            # Use models directory relative to project root
            models_dir = Path(__file__).parent.parent.parent.parent / "models" / "gunny"
            self.model_path = str(models_dir / "yolov8n.pt")
        else:
            self.model_path = model_path
        
        # Initialize model
        self._initialize_model()
        
        logger.info("GunnyBagDetector initialized")
    
    def _initialize_model(self):
        """Initialize the YOLO model for bag detection."""
        try:
            # Try to import ultralytics - if not available, we'll fall back to simulated data
            from ultralytics import YOLO
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found at {self.model_path}. Attempting to download YOLOv8n...")
                # Download YOLOv8n model if not available
                try:
                    self.model = YOLO('yolov8n.pt')  # This will auto-download
                    logger.info("YOLOv8n model downloaded and loaded successfully")
                    return
                except Exception as download_error:
                    logger.warning(f"Failed to download model: {download_error}. Using fallback detection.")
                    self.model = None
                    return
                
            # Load YOLOv8 model
            self.model = YOLO(self.model_path)
            logger.info(f"YOLOv8 model loaded from {self.model_path}")
            
        except ImportError:
            logger.warning("Ultralytics package not installed. Using fallback detection.")
            self.model = None
    
    def detect(self, image_path: str) -> np.ndarray:
        """
        Detect gunny bags in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            np.ndarray: Array of [x1, y1, x2, y2, confidence, class_id] detections
        """
        logger.info(f"Detecting gunny bags in image: {image_path}")
        
        try:
            # Check if we have a YOLOv8 model
            if self.model is not None:
                return self._detect_with_yolo(image_path)
            else:
                # Fallback to simulated detection
                return self._simulate_detection(image_path)
                
        except Exception as e:
            logger.error(f"Error detecting gunny bags: {str(e)}")
            self.last_confidence = 0.0
            return np.array([])
    
    def _detect_with_yolo(self, image_path: str) -> np.ndarray:
        """
        Detect gunny bags using YOLOv8.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            np.ndarray: Array of [x1, y1, x2, y2, confidence, class_id] detections
        """
        # Check if image exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return np.array([])
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return np.array([])
        
        # Run inference
        results = self.model(image, conf=self.confidence_threshold)
        
        # Process results
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Get confidence and class
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                
                # Add detection if it's a gunny bag (class 0)
                if cls == 0 and conf >= self.confidence_threshold:
                    detections.append([x1, y1, x2, y2, conf, cls])
        
        # Convert to numpy array
        if detections:
            detections = np.array(detections)
            # Store average confidence
            self.last_confidence = float(np.mean(detections[:, 4]))
            logger.info(f"Detected {len(detections)} gunny bags with avg confidence {self.last_confidence:.2f}")
        else:
            detections = np.array([])
            self.last_confidence = 0.0
            logger.info("No gunny bags detected")
        
        return detections
    
    def _simulate_detection(self, image_path: str) -> np.ndarray:
        """
        Simulate gunny bag detections when model is not available.
        
        Args:
            image_path: Path to the image file (unused in simulation)
            
        Returns:
            np.ndarray: Simulated detections
        """
        logger.warning("Using simulated gunny bag detection")
        
        # Simulate 3-7 gunny bag detections
        num_detections = np.random.randint(3, 8)
        
        # Create random detections
        detections = []
        for _ in range(num_detections):
            x1 = np.random.uniform(0.1, 0.7)
            y1 = np.random.uniform(0.1, 0.7)
            w = np.random.uniform(0.1, 0.3)
            h = np.random.uniform(0.1, 0.3)
            x2 = min(x1 + w, 0.99)
            y2 = min(y1 + h, 0.99)
            confidence = np.random.uniform(0.5, 0.99)
            class_id = 0
            
            detections.append([x1, y1, x2, y2, confidence, class_id])
        
        detections = np.array(detections)
        
        # Store average confidence
        self.last_confidence = float(np.mean(detections[:, 4]))
        
        logger.info(f"Simulated {len(detections)} gunny bags with avg confidence {self.last_confidence:.2f}")
        return detections
    
    def detect_from_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect gunny bags in a video frame.
        
        Args:
            frame: OpenCV frame/image as numpy array
            
        Returns:
            List of detection dictionaries with bbox, confidence, etc.
        """
        try:
            if self.model is not None:
                # Use actual YOLO model for detection
                results = self.model(frame)
                detections = []
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for i, box in enumerate(boxes):
                            # Extract bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = box.conf[0].cpu().numpy()
                            class_id = int(box.cls[0].cpu().numpy())
                            
                            # Filter by confidence threshold
                            if confidence >= self.confidence_threshold:
                                detection = {
                                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                    "confidence": float(confidence),
                                    "class_id": class_id,
                                    "width": int(x2 - x1),
                                    "height": int(y2 - y1),
                                    "area": int((x2 - x1) * (y2 - y1))
                                }
                                detections.append(detection)
                
                self.last_confidence = np.mean([d["confidence"] for d in detections]) if detections else 0.0
                logger.debug(f"Detected {len(detections)} gunny bags in frame")
                return detections
            else:
                # Fallback to simulated detection for demo purposes
                return self._simulate_frame_detections(frame)
                
        except Exception as e:
            logger.error(f"Error detecting gunny bags in frame: {str(e)}")
            return self._simulate_frame_detections(frame)
    
    def _simulate_frame_detections(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Simulate gunny bag detections for demo purposes.
        Uses simple computer vision techniques to detect bag-like objects.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detections = []
            min_area = 5000  # Minimum area for a gunny bag
            max_area = 50000  # Maximum area for a gunny bag
            
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                
                # Filter by area (gunny bags should be medium-sized objects)
                if min_area < area < max_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Calculate aspect ratio (gunny bags are roughly rectangular)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Filter by aspect ratio (0.5 to 2.0 for gunny bags)
                    if 0.5 <= aspect_ratio <= 2.0:
                        # Calculate confidence based on area and aspect ratio
                        area_score = min(area / max_area, 1.0)
                        aspect_score = 1.0 - abs(aspect_ratio - 1.0)  # Closer to square = higher score
                        confidence = (area_score + aspect_score) / 2.0
                        
                        if confidence >= self.confidence_threshold:
                            detection = {
                                "bbox": [x, y, x + w, y + h],
                                "confidence": float(confidence),
                                "class_id": 0,  # Assume single class for gunny bags
                                "width": w,
                                "height": h,
                                "area": int(area)
                            }
                            detections.append(detection)
            
            self.last_confidence = np.mean([d["confidence"] for d in detections]) if detections else 0.0
            logger.debug(f"Simulated detection: {len(detections)} gunny bags found")
            return detections
            
        except Exception as e:
            logger.error(f"Error in simulated detection: {str(e)}")
            return []
