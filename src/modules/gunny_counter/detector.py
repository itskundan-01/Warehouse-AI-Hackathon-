import os
import cv2
import numpy as np
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

import torch
from ultralytics import YOLO

from src.core.utils import get_logger

logger = get_logger(__name__)

class GunnyBagDetector:
    """
    Detector class for gunny bags using YOLOv8
    """
    
    def __init__(self, model_path: str, conf_threshold: float = 0.3, device: str = None):
        """
        Initialize the gunny bag detector
        
        Args:
            model_path (str): Path to YOLOv8 model weights
            conf_threshold (float): Confidence threshold for detections
            device (str, optional): Device to run inference on ('cuda', 'cpu', etc.)
        """
        self.conf_threshold = conf_threshold
        
        # Auto-select device if not specified
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        logger.info(f"Initializing GunnyBagDetector on {self.device}")
        
        try:
            # Load the model
            self.model = YOLO(model_path)
            logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
        
        # Warm up the model
        self._warm_up()
    
    def _warm_up(self, size: Tuple[int, int] = (640, 640)):
        """
        Perform a warm-up inference to initialize the model
        
        Args:
            size (tuple): Input image size for warm-up
        """
        logger.info("Warming up the model...")
        dummy_input = torch.zeros((1, 3, size[0], size[1])).to(self.device)
        
        try:
            # Run inference on dummy input
            dummy_img = np.random.randint(0, 255, (size[0], size[1], 3), dtype=np.uint8)
            self.model(dummy_img, verbose=False)
            logger.info("Model warm-up complete")
        except Exception as e:
            logger.warning(f"Model warm-up failed: {str(e)}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess the image for better detection in challenging lighting conditions
        
        Args:
            image (np.ndarray): Input image in BGR format
            
        Returns:
            np.ndarray: Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        
        # Blend with original image
        alpha = 0.7
        enhanced_image = cv2.addWeighted(image, alpha, enhanced, 1-alpha, 0)
        
        return enhanced_image
    
    def detect(self, image: np.ndarray, enhance: bool = True) -> Dict:
        """
        Detect gunny bags in the input image
        
        Args:
            image (np.ndarray): Input image in BGR format
            enhance (bool): Whether to apply preprocessing enhancements
            
        Returns:
            Dict: Detection results including bounding boxes, classes, and scores
        """
        start_time = time.time()
        
        # Preprocess image if enhancement is requested
        if enhance:
            processed_image = self.preprocess_image(image)
        else:
            processed_image = image
        
        # Run inference
        results = self.model(processed_image, conf=self.conf_threshold, verbose=False)[0]
        
        # Process results
        boxes = results.boxes.cpu().numpy()
        
        # Extract data
        detections = {
            'boxes': boxes.xyxy if len(boxes) > 0 else np.array([]),
            'scores': boxes.conf if len(boxes) > 0 else np.array([]),
            'classes': boxes.cls if len(boxes) > 0 else np.array([]),
            'processing_time': time.time() - start_time
        }
        
        logger.debug(f"Detected {len(detections['boxes'])} gunny bags in {detections['processing_time']:.4f}s")
        
        return detections
    
    def visualize(self, image: np.ndarray, detections: Dict) -> np.ndarray:
        """
        Draw detection results on the image
        
        Args:
            image (np.ndarray): Original image
            detections (Dict): Detection results from detect()
            
        Returns:
            np.ndarray: Image with visualized detections
        """
        output = image.copy()
        
        boxes = detections['boxes']
        scores = detections['scores']
        
        # Draw each detection
        for i, (box, score) in enumerate(zip(boxes, scores)):
            x1, y1, x2, y2 = box.astype(int)
            
            # Draw bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"Gunny Bag: {score:.2f}"
            cv2.putText(output, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw total count
        count = len(boxes)
        cv2.putText(output, f"Count: {count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return output
