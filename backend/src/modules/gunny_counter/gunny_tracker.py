"""
Gunny Bag Tracker module.
Tracks gunny bags across frames and detects line-crossing events.
"""
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import uuid

from src.config.logging_config import get_logger
from .improved_detector import ImprovedGunnyBagDetector

# Initialize logger
logger = get_logger(__name__)

class GunnyBagTracker:
    """
    Class for tracking gunny bags across multiple frames and detecting line crossings.
    Specifically designed to count bags crossing a red vertical line.
    """
    
    def __init__(self, 
                 max_tracking_time: int = 30,
                 min_distance_threshold: float = 50.0,
                 crossing_buffer: int = 5):
        """
        Initialize the gunny bag tracker.
        
        Args:
            max_tracking_time: Maximum time in seconds to track a bag before removing it
            min_distance_threshold: Minimum distance to consider as same bag between frames
            crossing_buffer: Number of pixels buffer around the line for crossing detection
        """
        # Dictionary to store bag tracking data
        # Key: tracking_id, Value: tracking data
        self.tracked_bags = {}
        
        # Maximum time to track a bag (seconds)
        self.max_tracking_time = max_tracking_time
        
        # Distance threshold for matching detections across frames
        self.min_distance_threshold = min_distance_threshold
        
        # Buffer zone around the crossing line
        self.crossing_buffer = crossing_buffer
        
        # Initialize improved detector for fixed red line coordinates
        self.improved_detector = ImprovedGunnyBagDetector()
        
        # Use fixed red line coordinates from improved detector
        self.crossing_line = self.improved_detector.get_red_line()
        
        # Counter for crossed bags
        self.crossed_count = 0
        
        logger.info("GunnyBagTracker initialized")
    
    def detect_red_line(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the fixed red line coordinates from the improved detector.
        This ensures consistent line detection across all frames.
        
        Args:
            frame: Input frame (BGR format) - used for compatibility but not needed
            
        Returns:
            Tuple[int, int, int, int]: Fixed line coordinates (x1, y1, x2, y2)
        """
        # Always return the fixed red line coordinates
        self.crossing_line = self.improved_detector.get_red_line()
        logger.info(f"Using fixed red line coordinates: {self.crossing_line}")
        return self.crossing_line
    
    def _detect_red_line_by_color(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect red vertical line using color-based detection.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Optional[Tuple[int, int, int, int]]: Line coordinates if found
        """
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define range for red color in HSV (more permissive ranges)
        lower_red1 = np.array([0, 50, 50])   # Lower saturation and value
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 50, 50])  # Lower saturation and value
        upper_red2 = np.array([180, 255, 255])
        
        # Create masks for red color
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find the longest vertical contour
        best_line = None
        max_height = 0
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check if it's more vertical than horizontal and has sufficient height
            if h > w * 2 and h > max_height and h > 50:  # Reduced minimum height
                max_height = h
                # Store as (x1, y1, x2, y2) format for vertical line
                best_line = (x + w//2, y, x + w//2, y + h)
        
        return best_line
    
    def _detect_vertical_line_by_edges(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect vertical lines using edge detection and Hough transform.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Optional[Tuple[int, int, int, int]]: Line coordinates if found
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)
        
        # Apply morphological operations to enhance vertical lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))  # Vertical kernel
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Use Hough Line Transform to detect lines
        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, 
                               minLineLength=100, maxLineGap=20)
        
        if lines is None:
            return None
        
        # Find the most prominent vertical line
        best_line = None
        max_length = 0
        height, width = frame.shape[:2]
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate line properties
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            # Check if line is approximately vertical (within 15 degrees)
            if (angle > 75 and angle < 105) and length > max_length and length > height * 0.3:
                max_length = length
                # Ensure line spans from top to bottom of detected region
                best_line = (min(x1, x2), min(y1, y2), min(x1, x2), max(y1, y2))
        
        return best_line
    
    def _create_simulated_line(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Create a simulated vertical line for testing purposes.
        Places the line at 1/4 from the left edge of the frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Optional[Tuple[int, int, int, int]]: Simulated line coordinates
        """
        height, width = frame.shape[:2]
        
        # Place line at 1/4 from left edge
        line_x = width // 4
        
        # Line spans the full height of the frame
        simulated_line = (line_x, 0, line_x, height - 1)
        
        logger.info(f"Created simulated counting line at x={line_x} for testing")
        return simulated_line
    
    def update(self, detections: np.ndarray, frame: np.ndarray) -> Dict[str, Any]:
        """
        Update the tracker with new detections and detect line crossings.
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence, class_id] detections
            frame: Current frame for line detection
            
        Returns:
            Dict[str, Any]: Tracking results including crossing count
        """
        current_time = datetime.now()
        
        # Detect the red line if not already detected
        if self.crossing_line is None:
            self.detect_red_line(frame)
        
        # Convert detections to center points for easier tracking
        detection_centers = []
        for detection in detections:
            x1, y1, x2, y2 = detection[:4]
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            detection_centers.append({
                'center': (center_x, center_y),
                'bbox': (x1, y1, x2, y2),
                'confidence': detection[4]
            })
        
        # Match detections to existing tracks
        self._match_detections_to_tracks(detection_centers, current_time)
        
        # Check for line crossings
        if self.crossing_line:
            new_crossings = self._check_line_crossings()
            self.crossed_count += new_crossings
        
        # Clean up old tracks
        self._cleanup(current_time)
        
        return {
            'total_bags_tracked': len(self.tracked_bags),
            'crossed_count': self.crossed_count,
            'crossing_line': self.crossing_line,
            'active_tracks': len(self.tracked_bags)
        }
    
    def _match_detections_to_tracks(self, detection_centers: List[Dict], current_time: datetime) -> None:
        """
        Match current detections to existing tracks based on distance.
        
        Args:
            detection_centers: List of detection center points and data
            current_time: Current timestamp
        """
        matched_tracks = set()
        matched_detections = set()
        
        # Try to match each detection to existing tracks
        for det_idx, detection in enumerate(detection_centers):
            best_match = None
            min_distance = float('inf')
            
            for track_id, track_data in self.tracked_bags.items():
                if track_id in matched_tracks:
                    continue
                
                # Calculate distance between detection and last known position
                last_pos = track_data['positions'][-1]['center']
                distance = np.sqrt((detection['center'][0] - last_pos[0])**2 + 
                                 (detection['center'][1] - last_pos[1])**2)
                
                if distance < self.min_distance_threshold and distance < min_distance:
                    min_distance = distance
                    best_match = track_id
            
            # Update matched track or create new track
            if best_match:
                self._update_track(best_match, detection, current_time)
                matched_tracks.add(best_match)
                matched_detections.add(det_idx)
            else:
                # Create new track
                self._create_new_track(detection, current_time)
                matched_detections.add(det_idx)
    
    def _create_new_track(self, detection: Dict, current_time: datetime) -> str:
        """
        Create a new track for an unmatched detection.
        
        Args:
            detection: Detection data
            current_time: Current timestamp
            
        Returns:
            str: New track ID
        """
        track_id = str(uuid.uuid4())
        
        self.tracked_bags[track_id] = {
            'track_id': track_id,
            'first_seen': current_time,
            'last_seen': current_time,
            'positions': [{
                'center': detection['center'],
                'bbox': detection['bbox'],
                'time': current_time
            }],
            'crossed_line': False,
            'last_side': self._get_side_of_line(detection['center'])
        }
        
        logger.debug(f"Created new track {track_id} at position {detection['center']}")
        return track_id
    
    def _update_track(self, track_id: str, detection: Dict, current_time: datetime) -> None:
        """
        Update an existing track with new detection.
        
        Args:
            track_id: ID of track to update
            detection: New detection data
            current_time: Current timestamp
        """
        track_data = self.tracked_bags[track_id]
        track_data['last_seen'] = current_time
        track_data['positions'].append({
            'center': detection['center'],
            'bbox': detection['bbox'],
            'time': current_time
        })
        
        # Keep only recent positions (last 10 positions)
        if len(track_data['positions']) > 10:
            track_data['positions'] = track_data['positions'][-10:]
        
        logger.debug(f"Updated track {track_id} at position {detection['center']}")
    
    def _get_side_of_line(self, point: Tuple[float, float]) -> str:
        """
        Determine which side of the crossing line a point is on.
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            str: 'left', 'right', or 'on_line'
        """
        if not self.crossing_line:
            return 'unknown'
        
        line_x = self.crossing_line[0]  # x-coordinate of vertical line
        point_x = point[0]
        
        if abs(point_x - line_x) <= self.crossing_buffer:
            return 'on_line'
        elif point_x < line_x:
            return 'left'
        else:
            return 'right'
    
    def _check_line_crossings(self) -> int:
        """
        Check for line crossings in all active tracks.
        
        Returns:
            int: Number of new crossings detected
        """
        new_crossings = 0
        
        for track_id, track_data in self.tracked_bags.items():
            if track_data['crossed_line']:
                continue  # Already counted this bag
            
            if len(track_data['positions']) < 2:
                continue  # Need at least 2 positions to detect crossing
            
            # Check if bag has crossed from one side to the other
            current_pos = track_data['positions'][-1]['center']
            current_side = self._get_side_of_line(current_pos)
            
            # Update last_side for the track
            if current_side != 'on_line':
                if 'last_side' not in track_data or track_data['last_side'] == 'unknown':
                    track_data['last_side'] = current_side
                elif track_data['last_side'] != current_side:
                    # Crossing detected! 
                    track_data['crossed_line'] = True
                    new_crossings += 1
                    logger.info(f"Line crossing detected for track {track_id}: {track_data['last_side']} -> {current_side}")
        
        return new_crossings
    
    def _cleanup(self, current_time: datetime) -> None:
        """
        Remove tracks that haven't been updated for a while.
        
        Args:
            current_time: Current timestamp
        """
        expired_time = current_time - timedelta(seconds=self.max_tracking_time)
        
        # Identify expired tracks
        expired_tracks = [
            track_id for track_id, track_data in self.tracked_bags.items()
            if track_data['last_seen'] < expired_time
        ]
        
        # Remove expired tracks
        for track_id in expired_tracks:
            logger.debug(f"Removing expired track {track_id}")
            del self.tracked_bags[track_id]
        
        if expired_tracks:
            logger.info(f"Cleaned up {len(expired_tracks)} expired track(s)")
    
    def get_crossing_count(self) -> int:
        """
        Get the total count of bags that have crossed the line.
        
        Returns:
            int: Total crossing count
        """
        return self.crossed_count
    
    def reset_count(self) -> None:
        """
        Reset the crossing count to zero.
        """
        self.crossed_count = 0
        logger.info("Crossing count reset to zero")
    
    def get_active_tracks(self) -> List[Dict[str, Any]]:
        """
        Get information about all active tracks.
        
        Returns:
            List[Dict[str, Any]]: List of active track data
        """
        return list(self.tracked_bags.values())
    
    def draw_tracking_info(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw tracking information on the frame for visualization.
        
        Args:
            frame: Input frame
            
        Returns:
            np.ndarray: Frame with tracking info drawn
        """
        result_frame = frame.copy()
        
        # Draw the crossing line if detected
        if self.crossing_line:
            x1, y1, x2, y2 = self.crossing_line
            cv2.line(result_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red line
            cv2.putText(result_frame, f"Crossed: {self.crossed_count}", 
                       (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Draw active tracks
        for track_data in self.tracked_bags.values():
            if track_data['positions']:
                current_pos = track_data['positions'][-1]
                center = current_pos['center']
                bbox = current_pos['bbox']
                
                # Draw bounding box
                x1, y1, x2, y2 = [int(coord) for coord in bbox]
                color = (0, 255, 0) if track_data['crossed_line'] else (255, 0, 0)
                cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw track ID
                cv2.putText(result_frame, f"ID: {track_data['track_id'][:8]}", 
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                # Draw trajectory
                if len(track_data['positions']) > 1:
                    for i in range(1, len(track_data['positions'])):
                        pt1 = (int(track_data['positions'][i-1]['center'][0]),
                               int(track_data['positions'][i-1]['center'][1]))
                        pt2 = (int(track_data['positions'][i]['center'][0]),
                               int(track_data['positions'][i]['center'][1]))
                        cv2.line(result_frame, pt1, pt2, color, 1)
        
        return result_frame
