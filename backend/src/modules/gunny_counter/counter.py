"""
Gunny Bag Counter module.
Counts gunny bags based on detections and applies tracking and counting logic.
Enhanced with line-crossing detection capabilities.
"""
import numpy as np
from typing import List, Dict, Any, Optional

from src.config.logging_config import get_logger
from .gunny_tracker import GunnyBagTracker
from .improved_detector import ImprovedGunnyBagDetector

# Initialize logger
logger = get_logger(__name__)

class GunnyBagCounter:
    """Class for counting gunny bags from detection results with line-crossing tracking."""
    
    def __init__(self, 
                 overlap_threshold: float = 0.5,
                 enable_line_crossing: bool = True,
                 use_improved_detector: bool = True):
        """
        Initialize the counter.
        
        Args:
            overlap_threshold: IoU threshold for duplicate detection removal
            enable_line_crossing: Whether to enable line-crossing detection
            use_improved_detector: Whether to use the improved gunny bag detector
        """
        self.overlap_threshold = overlap_threshold
        self.enable_line_crossing = enable_line_crossing
        self.use_improved_detector = use_improved_detector
        
        # Initialize tracker if line-crossing is enabled
        self.tracker = GunnyBagTracker() if enable_line_crossing else None
        
        # Initialize improved detector if enabled
        self.improved_detector = ImprovedGunnyBagDetector() if use_improved_detector else None
        
        logger.info(f"GunnyBagCounter initialized with line_crossing={enable_line_crossing}, improved_detector={use_improved_detector}")
    
    def count(self, detections: np.ndarray = None, frame: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Count gunny bags from detection array or frame.
        
        Args:
            detections: Optional array of [x1, y1, x2, y2, confidence, class_id] detections
            frame: Optional frame for detection and line-crossing analysis
            
        Returns:
            Dict[str, Any]: Counting results including static count and crossing count
        """
        # If improved detector is enabled and frame is provided, use it for detection
        if self.use_improved_detector and self.improved_detector and frame is not None:
            improved_detections = self.improved_detector.detect(frame)
            logger.info(f"Used improved detector to find {len(improved_detections)} gunny bags")
            
            # Convert improved detector format (list of dicts) to numpy array format
            if improved_detections:
                detections = np.array([[
                    det['bbox'][0], det['bbox'][1], det['bbox'][2], det['bbox'][3],
                    det['confidence'], det['class_id']
                ] for det in improved_detections])
            else:
                detections = np.array([])
        
        # If no detections, return appropriate response
        if detections is None or len(detections) == 0:
            result = {
                'static_count': 0,
                'crossing_count': 0 if self.tracker else None,
                'total_tracked': 0 if self.tracker else None,
                'crossing_line_detected': self.tracker.crossing_line is not None if self.tracker else None
            }
            return result
            
        # Filter by confidence and apply NMS to remove duplicates
        filtered_detections = self._apply_non_maximum_suppression(detections, self.overlap_threshold)
        static_count = len(filtered_detections)
        
        result = {
            'static_count': static_count,
            'crossing_count': None,
            'total_tracked': None,
            'crossing_line_detected': None
        }
        
        # If line-crossing tracking is enabled and frame is provided
        if self.enable_line_crossing and self.tracker and frame is not None:
            tracking_results = self.tracker.update(filtered_detections, frame)
            result.update({
                'crossing_count': tracking_results['crossed_count'],
                'total_tracked': tracking_results['total_bags_tracked'],
                'crossing_line_detected': tracking_results['crossing_line'] is not None,
                'active_tracks': tracking_results['active_tracks']
            })
            
            logger.info(f"Static count: {static_count}, Crossing count: {tracking_results['crossed_count']}")
        else:
            logger.info(f"Static count: {static_count}")
        
        return result
    
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
    
    def get_crossing_count(self) -> int:
        """
        Get the total count of bags that have crossed the line.
        
        Returns:
            int: Total crossing count, 0 if tracking is disabled
        """
        if self.tracker:
            return self.tracker.get_crossing_count()
        return 0
    
    def reset_crossing_count(self) -> None:
        """
        Reset the crossing count to zero.
        """
        if self.tracker:
            self.tracker.reset_count()
            logger.info("Crossing count reset")
    
    def get_tracking_visualization(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Get frame with tracking visualization overlays.
        
        Args:
            frame: Input frame
            
        Returns:
            Optional[np.ndarray]: Frame with tracking info or None if tracking disabled
        """
        if self.tracker and frame is not None:
            return self.tracker.draw_tracking_info(frame)
        return None
    
    def is_line_crossing_enabled(self) -> bool:
        """
        Check if line-crossing detection is enabled.
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.enable_line_crossing and self.tracker is not None