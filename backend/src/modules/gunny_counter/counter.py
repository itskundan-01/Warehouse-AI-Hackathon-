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
        filtered_detections = self._apply_non_maximum_suppression(detections, self.overlap_threshold)
        count = len(filtered_detections)
        
        logger.info(f"Counted {count} gunny bags after filtering")
        return count
    
    def _apply_non_maximum_suppression(self, detections: np.ndarray, iou_threshold: float) -> np.ndarray:
        """
        Apply non-maximum suppression to remove duplicate detections.
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence, class_id] detections
            iou_threshold: IoU threshold for considering detections as duplicates
            
        Returns:
            np.ndarray: Filtered detections after NMS
        """
        if len(detections) == 0:
            return np.array([])
            
        # Extract coordinates, confidences, and class IDs
        x1 = detections[:, 0]
        y1 = detections[:, 1]
        x2 = detections[:, 2]
        y2 = detections[:, 3]
        scores = detections[:, 4]
        
        # Calculate areas of all boxes
        areas = (x2 - x1) * (y2 - y1)
        
        # Sort by confidence
        order = scores.argsort()[::-1]
        
        keep = []
        while order.size > 0:
            # Pick the box with highest confidence
            i = order[0]
            keep.append(i)
            
            # Compute IoU with the rest
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])
            
            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            intersection = w * h
            
            # Calculate IoU
            iou = intersection / (areas[i] + areas[order[1:]] - intersection)
            
            # Drop boxes with IoU higher than threshold
            inds = np.where(iou <= iou_threshold)[0]
            order = order[inds + 1]
        
        # Return filtered detections
        return detections[keep]
    
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