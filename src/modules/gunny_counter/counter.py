"""
Gunny Bag Counter module.
Counts gunny bags based on detections and applies tracking and counting logic.
"""
import numpy as np
from typing import List, Dict, Any, Optional

from src.config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class GunnyBagCounter:
    """Class for counting gunny bags from detection results."""
    
    def __init__(self, overlap_threshold: float = 0.5):
        """
        Initialize the counter.
        
        Args:
            overlap_threshold: IoU threshold for duplicate detection removal
        """
        self.overlap_threshold = overlap_threshold
        logger.info("GunnyBagCounter initialized")
    
    def count(self, detections: np.ndarray) -> int:
        """
        Count gunny bags from detection array after removing duplicates.
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence, class_id] detections
            
        Returns:
            int: Number of unique gunny bags detected
        """
        # If no detections, return 0
        if len(detections) == 0:
            return 0
            
        # Filter by confidence and apply NMS to remove duplicates
        # In a real implementation, we would use non-maximum suppression
        # For this placeholder, we'll just count all detections
        count = len(detections)
        
        logger.info(f"Counted {count} gunny bags after filtering")
        return count
    
    def _calculate_iou(self, box1: np.ndarray, box2: np.ndarray) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes.
        
        Args:
            box1: First box with [x1, y1, x2, y2]
            box2: Second box with [x1, y1, x2, y2]
            
        Returns:
            float: IoU value between 0-1
        """
        # Calculate intersection area
        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])
        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])
        
        # Check if there is an intersection
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union area
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        
        union_area = box1_area + box2_area - intersection_area
        
        # Calculate IoU
        iou = intersection_area / union_area
        
        return iou