"""
Volumetric Estimator module.
Estimates the volume of gunny bags based on detection results.
"""
import numpy as np
import cv2
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from src.config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class VolumetricEstimator:
    """Class for estimating the volume of gunny bags."""
    
    def __init__(self, avg_bag_volume: float = 0.5, calibration_file: Optional[str] = None):
        """
        Initialize the volume estimator.
        
        Args:
            avg_bag_volume: Average volume of one gunny bag in cubic meters
            calibration_file: Path to calibration data file (if None, uses default values)
        """
        self.avg_bag_volume = avg_bag_volume
        
        # Default calibration parameters (pixels to meters at reference distance)
        self.pixel_to_meter_ratio = 0.01  # 1cm per pixel at reference distance
        self.reference_distance = 5.0     # 5 meters reference distance
        self.focal_length = 1000.0        # focal length in pixels
        self.bag_aspect_ratio = 1.8       # height/width ratio for standard bag
        
        # Try to load calibration parameters if file provided
        if calibration_file and os.path.exists(calibration_file):
            self._load_calibration(calibration_file)
        
        logger.info("VolumetricEstimator initialized")
        
    def _load_calibration(self, calibration_file: str) -> None:
        """
        Load calibration parameters from file.
        
        Args:
            calibration_file: Path to calibration data file
        """
        try:
            import json
            with open(calibration_file, 'r') as f:
                calibration = json.load(f)
            
            self.pixel_to_meter_ratio = calibration.get('pixel_to_meter_ratio', self.pixel_to_meter_ratio)
            self.reference_distance = calibration.get('reference_distance', self.reference_distance)
            self.focal_length = calibration.get('focal_length', self.focal_length)
            self.bag_aspect_ratio = calibration.get('bag_aspect_ratio', self.bag_aspect_ratio)
            
            logger.info(f"Loaded calibration parameters from {calibration_file}")
            
        except Exception as e:
            logger.error(f"Failed to load calibration file: {str(e)}")
    
    def estimate_volume(self, detections: np.ndarray, image_path: Optional[str] = None) -> float:
        """
        Estimate the total volume of detected gunny bags.
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence, class_id] detections
            image_path: Optional path to original image for depth estimation
            
        Returns:
            float: Estimated total volume in cubic meters
        """
        # If no detections, return 0
        if len(detections) == 0:
            return 0.0
        
        try:
            # Try to use depth information if image is provided
            if image_path and os.path.exists(image_path):
                return self._estimate_with_depth(detections, image_path)
            else:
                # Fall back to simpler estimation
                return self._estimate_basic(detections)
                
        except Exception as e:
            logger.error(f"Error in volume estimation: {str(e)}")
            # Fall back to basic calculation
            return self._estimate_basic(detections)
    
    def _estimate_with_depth(self, detections: np.ndarray, image_path: str) -> float:
        """
        Estimate volume using image content for depth cues.
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence, class_id] detections
            image_path: Path to the original image
            
        Returns:
            float: Estimated total volume in cubic meters
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return self._estimate_basic(detections)
        
        height, width = image.shape[:2]
        total_volume = 0.0
        
        # Try to estimate depth based on position in image (basic depth heuristic)
        # Lower in frame usually means closer to camera
        for det in detections:
            x1, y1, x2, y2 = det[:4]
            
            # Calculate physical dimensions based on position and size
            box_height = y2 - y1
            box_width = x2 - x1
            
            # Estimate distance based on vertical position in image
            # (closer to bottom of image = closer to camera)
            relative_vertical_pos = (y1 + y2) / (2 * height)
            distance_factor = 1.0 + (1.0 - relative_vertical_pos)
            estimated_distance = self.reference_distance * distance_factor
            
            # Apply perspective scaling based on distance
            scale = self.focal_length / estimated_distance
            real_width = box_width * self.pixel_to_meter_ratio / scale
            real_height = box_height * self.pixel_to_meter_ratio / scale
            
            # Estimate depth using aspect ratio (assuming standard bag dimensions)
            real_depth = real_width * self.bag_aspect_ratio
            
            # Calculate volume
            bag_volume = real_width * real_height * real_depth
            total_volume += bag_volume
            
            logger.debug(f"Bag at position ({x1:.1f},{y1:.1f}) estimated dimensions: "
                        f"{real_width:.2f}m x {real_height:.2f}m x {real_depth:.2f}m, "
                        f"volume: {bag_volume:.3f}m³")
        
        logger.info(f"Estimated total volume with depth cues: {total_volume:.2f} cubic meters")
        return float(total_volume)
    
    def _estimate_basic(self, detections: np.ndarray) -> float:
        """
        Basic volume estimation based on detection size.
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence, class_id] detections
            
        Returns:
            float: Estimated total volume in cubic meters
        """
        # Calculate relative sizes of each bag (normalized area)
        areas = []
        for det in detections:
            x1, y1, x2, y2 = det[:4]
            width = x2 - x1
            height = y2 - y1
            area = width * height
            areas.append(area)
        
        # Convert to numpy array
        areas = np.array(areas)
        
        # Normalize to get relative sizes
        if len(areas) > 1:
            areas = areas / np.mean(areas)
        else:
            areas = np.ones_like(areas)
        
        # Calculate total volume based on count and relative sizes
        # Scale by the average bag volume
        total_volume = np.sum(areas) * self.avg_bag_volume
        
        logger.info(f"Estimated basic volume: {total_volume:.2f} cubic meters")
        return float(total_volume)
    
    def calibrate_from_reference(self, 
                                reference_image_path: str, 
                                reference_dimensions: Tuple[float, float, float],
                                reference_distance: float) -> Dict[str, float]:
        """
        Calibrate the estimator using a reference image with known dimensions.
        
        Args:
            reference_image_path: Path to reference image with known bag
            reference_dimensions: (width, height, depth) in meters of the reference bag
            reference_distance: Distance in meters from camera to reference bag
            
        Returns:
            Dict[str, float]: Updated calibration parameters
        """
        try:
            # Load reference image
            image = cv2.imread(reference_image_path)
            if image is None:
                logger.error(f"Failed to load reference image: {reference_image_path}")
                return {
                    'success': False,
                    'error': 'Failed to load reference image'
                }
            
            # Detect bags in reference image
            # This would typically be done using the detector, but here we'll simulate it
            height, width = image.shape[:2]
            
            # Prompt user to select bag in image or use automatic detection
            # For this implementation, we'll assume a detected bag in the center
            # In a real implementation, this would use actual detection or manual selection
            box_width = width * 0.4
            box_height = height * 0.4
            x1 = (width - box_width) / 2
            y1 = (height - box_height) / 2
            x2 = x1 + box_width
            y2 = y1 + box_height
            
            # Calculate pixel to meter ratio
            ref_width_pixels = box_width
            ref_width_meters = reference_dimensions[0]
            
            # Update calibration parameters
            self.pixel_to_meter_ratio = ref_width_meters / ref_width_pixels
            self.reference_distance = reference_distance
            self.bag_aspect_ratio = reference_dimensions[2] / reference_dimensions[0]
            
            # Calculate focal length using perspective formula
            self.focal_length = (ref_width_pixels * reference_distance) / ref_width_meters
            
            logger.info(f"Calibration updated: pixel_to_meter_ratio={self.pixel_to_meter_ratio:.5f}, "
                       f"focal_length={self.focal_length:.1f}, "
                       f"reference_distance={self.reference_distance}")
            
            # Return updated parameters
            return {
                'success': True,
                'pixel_to_meter_ratio': self.pixel_to_meter_ratio,
                'reference_distance': self.reference_distance,
                'focal_length': self.focal_length,
                'bag_aspect_ratio': self.bag_aspect_ratio
            }
            
        except Exception as e:
            logger.error(f"Calibration error: {str(e)}")
            return {
                'success': False,
                'error': f'Calibration error: {str(e)}'
            }