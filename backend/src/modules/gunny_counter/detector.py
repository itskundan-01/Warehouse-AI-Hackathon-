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
                logger.warning(f"Model file not found at {self.model_path}. Using fallback detection.")
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
