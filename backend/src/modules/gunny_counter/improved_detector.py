import cv2
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ImprovedGunnyBagDetector:
    """Enhanced detector specifically for gunny bags with better object classification."""
    
    def __init__(self):
        """Initialize the improved gunny bag detector."""
        # Adjusted red line coordinates - moved 7% to the right and extended 15% lower
        # Original line: (122, 122) to (122, 996), height = 996 - 122 = 874
        # Extended 15% lower: 874 * 0.15 = 131, so new bottom: 996 + 131 = 1127
        # But video height is 1440, so clamp to 1400 for safety
        self.red_line_coords = (301, 122, 301, min(1127, 1400))
        
        # Gunny bag color ranges in HSV
        self.gunny_hsv_ranges = [
            # Brown range
            ([8, 50, 20], [20, 255, 200]),
            # Tan/beige range  
            ([15, 30, 50], [35, 255, 255]),
            # Light brown range
            ([10, 40, 40], [25, 180, 180])
        ]
        
        # Size constraints for gunny bags
        self.min_area = 2000
        self.max_area = 15000
        self.min_aspect_ratio = 0.3
        self.max_aspect_ratio = 2.5
        
        # Human detection parameters
        self.human_cascade = None
        self._load_human_detector()
        
        # Human-bag association parameters
        self.human_bag_distance_threshold = 150  # pixels
        self.human_min_area = 5000
        self.human_max_area = 50000
        
        # Crossing detection properties
        self.crossing_line = self.red_line_coords  # Use the same line for crossing detection
        self.tracked_objects = {}  # Track objects across frames for crossing detection
        
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect gunny bags in the frame using multiple detection methods.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List[Dict]: List of detected gunny bag information
        """
        try:
            # Apply multiple detection methods
            color_detections = self._detect_by_color(frame)
            edge_detections = self._detect_by_edges(frame)
            texture_detections = self._detect_by_texture(frame)
            
            # Combine all detections
            all_detections = color_detections + edge_detections + texture_detections
            
            if not all_detections:
                return []
            
            # Convert to numpy array for NMS
            detections_array = np.array(all_detections)
            
            # Apply Non-Maximum Suppression
            filtered_detections = self._apply_nms(detections_array, iou_threshold=0.3)
            
            # Filter and classify detections
            final_detections = self._filter_and_classify(frame, filtered_detections)
            
            return final_detections
            
        except Exception as e:
            logger.error(f"Error in gunny bag detection: {str(e)}")
            return []
    
    def _detect_by_color(self, frame: np.ndarray) -> List[List[float]]:
        """
        Detect gunny bags based on color characteristics.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List[List[float]]: List of detections [x1, y1, x2, y2, confidence, class_id]
        """
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for lower, upper in self.gunny_hsv_ranges:
            # Create mask for this color range
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            # Morphological operations to clean up mask
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if self.min_area <= area <= self.max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    if self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio:
                        confidence = min(area / self.max_area, 1.0) * 0.8
                        detections.append([x, y, x+w, y+h, confidence, 0])
        
        return detections
    
    def _detect_by_edges(self, frame: np.ndarray) -> List[List[float]]:
        """
        Detect gunny bags based on edge characteristics.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List[List[float]]: List of detections [x1, y1, x2, y2, confidence, class_id]
        """
        detections = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if self.min_area <= area <= self.max_area:
                # Approximate contour to polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular (4-8 vertices)
                if 4 <= len(approx) <= 8:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    if self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio:
                        confidence = min(area / self.max_area, 1.0) * 0.6
                        detections.append([x, y, x+w, y+h, confidence, 1])
        
        return detections
    
    def _detect_by_texture(self, frame: np.ndarray) -> List[List[float]]:
        """
        Detect gunny bags based on texture characteristics.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List[List[float]]: List of detections [x1, y1, x2, y2, confidence, class_id]
        """
        detections = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply Otsu thresholding
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                if self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio:
                    # Analyze texture in the region
                    roi = gray[y:y+h, x:x+w]
                    if roi.size > 0:
                        # Calculate variance of Laplacian (texture measure)
                        laplacian_var = cv2.Laplacian(roi, cv2.CV_64F).var()
                        texture_score = min(laplacian_var / 1000.0, 1.0)
                        
                        if texture_score > 0.1:  # Minimum texture threshold
                            confidence = texture_score * 0.7
                            detections.append([x, y, x+w, y+h, confidence, 2])
        
        return detections
    
    def _classify_object(self, roi: np.ndarray) -> float:
        """
        Classify whether the detected object is a gunny bag.
        
        Args:
            roi: Region of interest containing the detected object
            
        Returns:
            float: Classification score (0-1, higher means more likely to be a gunny bag)
        """
        if roi is None or roi.size == 0:
            return 0.0
        
        # Analyze color characteristics (40% weight)
        color_score = self._analyze_color_features(roi)
        
        # Analyze shape characteristics (30% weight)  
        shape_score = self._analyze_shape_features(roi)
        
        # Analyze texture characteristics (30% weight)
        texture_score = self._analyze_texture_features(roi)
        
        # Weighted combination
        final_score = (color_score * 0.4 + shape_score * 0.3 + texture_score * 0.3)
        
        return min(final_score, 1.0)
    
    def _analyze_color_features(self, roi: np.ndarray) -> float:
        """
        Analyze color characteristics to determine if it's a gunny bag.
        
        Args:
            roi: Region of interest
            
        Returns:
            float: Color score (0-1)
        """
        try:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            total_pixels = roi.shape[0] * roi.shape[1]
            matching_pixels = 0
            
            for lower, upper in self.gunny_hsv_ranges:
                mask = cv2.inRange(hsv_roi, np.array(lower), np.array(upper))
                matching_pixels += np.count_nonzero(mask)
            
            color_ratio = matching_pixels / total_pixels if total_pixels > 0 else 0
            return min(color_ratio * 2.0, 1.0)  # Boost score if good color match
            
        except Exception as e:
            logger.error(f"Error in color analysis: {str(e)}")
            return 0.0
    
    def _analyze_shape_features(self, roi: np.ndarray) -> float:
        """
        Analyze shape characteristics to determine if it's a gunny bag.
        
        Args:
            roi: Region of interest
            
        Returns:
            float: Shape score (0-1)
        """
        try:
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return 0.0
            
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate shape features
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            if perimeter == 0:
                return 0.0
            
            # Circularity (4π*area/perimeter²)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            # Gunny bags are not very circular, so lower circularity is better
            shape_score = 1.0 - min(circularity, 1.0)
            
            return shape_score
            
        except Exception as e:
            logger.error(f"Error in shape analysis: {str(e)}")
            return 0.0
    
    def _analyze_texture_features(self, roi: np.ndarray) -> float:
        """
        Analyze texture characteristics to determine if it's a gunny bag.
        
        Args:
            roi: Region of interest
            
        Returns:
            float: Texture score (0-1)
        """
        try:
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Calculate variance of Laplacian (edge density)
            laplacian_var = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
            
            # Calculate local binary pattern-like texture measure
            # Simple approximation using standard deviation
            texture_std = np.std(gray_roi)
            
            # Combine measures
            edge_score = min(laplacian_var / 500.0, 1.0)
            texture_score = min(texture_std / 50.0, 1.0)
            
            return (edge_score + texture_score) / 2.0
            
        except Exception as e:
            logger.error(f"Error in texture analysis: {str(e)}")
            return 0.0
    
    def _apply_nms(self, detections: np.ndarray, iou_threshold: float = 0.3) -> np.ndarray:
        """
        Apply Non-Maximum Suppression to remove overlapping detections.
        
        Args:
            detections: Array of detections [x1, y1, x2, y2, confidence, class_id]
            iou_threshold: IoU threshold for suppression
            
        Returns:
            np.ndarray: Filtered detections
        """
        if len(detections) == 0:
            return np.array([])
        
        # Extract coordinates and scores
        x1 = detections[:, 0]
        y1 = detections[:, 1]
        x2 = detections[:, 2]
        y2 = detections[:, 3]
        scores = detections[:, 4]
        
        # Calculate areas
        areas = (x2 - x1) * (y2 - y1)
        
        # Sort by confidence score
        indices = np.argsort(scores)[::-1]
        
        keep = []
        while len(indices) > 0:
            # Keep the detection with highest confidence
            current = indices[0]
            keep.append(current)
            
            if len(indices) == 1:
                break
            
            # Calculate IoU with remaining detections
            other_indices = indices[1:]
            
            xx1 = np.maximum(x1[current], x1[other_indices])
            yy1 = np.maximum(y1[current], y1[other_indices])
            xx2 = np.minimum(x2[current], x2[other_indices])
            yy2 = np.minimum(y2[current], y2[other_indices])
            
            # Calculate intersection area
            intersection = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
            
            # Calculate IoU
            union = areas[current] + areas[other_indices] - intersection
            iou = intersection / union
            
            # Keep detections with IoU below threshold
            indices = other_indices[iou <= iou_threshold]
        
        return detections[keep]
    
    def _filter_and_classify(self, frame: np.ndarray, detections: np.ndarray) -> List[Dict]:
        """Filter detections and classify as gunny bags vs other objects."""
        if len(detections) == 0:
            return []
        
        final_detections = []
        
        for detection in detections:
            x1, y1, x2, y2, confidence, class_id = detection
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Extract ROI
            roi = frame[y1:y2, x1:x2]
            
            if roi.size == 0:
                continue
            
            # Classify the detection
            classification_score = self._classify_object(roi)
            
            # Only keep detections that are likely gunny bags
            if classification_score > 0.3:
                final_detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(confidence),
                    'classification_score': float(classification_score),
                    'class_id': int(class_id),
                    'center': [(x1 + x2) // 2, (y1 + y2) // 2]
                })
        
        return final_detections
    
    def get_red_line(self, frame: np.ndarray = None) -> Tuple[int, int, int, int]:
        """
        Return fixed red line coordinates based on frameImage.png analysis.
        This ensures consistency across all video frames.
        
        Args:
            frame: Input frame (for scaling if needed)
            
        Returns:
            Tuple[int, int, int, int]: Red line coordinates (x1, y1, x2, y2)
        """
        return self.red_line_coords
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict], 
                       crossing_line: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Draw detected gunny bags and the red counting line on the frame.
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            crossing_line: Red line coordinates
            
        Returns:
            np.ndarray: Frame with drawn detections
        """
        result_frame = frame.copy()
        
        # Draw red counting line
        x1, y1, x2, y2 = crossing_line
        cv2.line(result_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        # Draw detections
        for detection in detections:
            bbox = detection['bbox']
            confidence = detection['confidence']
            classification_score = detection['classification_score']
            
            x1, y1, x2, y2 = bbox
            
            # Draw bounding box
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence and classification scores
            label = f"Gunny: {confidence:.2f} | Class: {classification_score:.2f}"
            cv2.putText(result_frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return result_frame
    
    def draw_human_bag_detections(self, frame: np.ndarray, human_detections: List[Dict], 
                                 bag_detections: List[Dict], associations: List[Dict]) -> np.ndarray:
        """
        Draw human detections, bag detections, and their associations on the frame.
        
        Args:
            frame: Input frame
            human_detections: List of human detections
            bag_detections: List of bag detections  
            associations: List of human-bag associations
            
        Returns:
            np.ndarray: Frame with drawn detections and associations
        """
        result_frame = frame.copy()
        
        # Draw detection line
        x1, y1, x2, y2 = self.crossing_line
        cv2.line(result_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        
        # Draw human detections in blue
        for human in human_detections:
            x1, y1, x2, y2 = human['bbox']
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(result_frame, f"Human: {human['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # Draw bag detections in green
        for bag in bag_detections:
            x1, y1, x2, y2 = bag['bbox']
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(result_frame, f"Bag: {bag['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Draw associations with connecting lines
        for association in associations:
            human_center = association['human']['center']
            bag_center = association['bag']['center']
            
            # Draw line connecting human and bag
            cv2.line(result_frame, 
                    (human_center[0], human_center[1]), 
                    (bag_center[0], bag_center[1]), 
                    (0, 255, 255), 2)  # Yellow line
            
            # Draw association info
            mid_x = (human_center[0] + bag_center[0]) // 2
            mid_y = (human_center[1] + bag_center[1]) // 2
            cv2.putText(result_frame, f"Dist: {association['distance']:.0f}", 
                       (mid_x, mid_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        return result_frame
    
    def _load_human_detector(self):
        """Load human detection model/cascade."""
        try:
            # Try to load OpenCV's HOG descriptor for human detection
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            logger.info("HOG human detector loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load HOG detector: {e}")
            self.hog = None
    
    def detect_humans(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect humans in the frame using HOG descriptor.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List[Dict]: List of detected human information
        """
        if self.hog is None:
            logger.warning("HOG human detector not initialized")
            return []
        
        try:
            # Resize frame for faster detection (optional)
            frame_resized = cv2.resize(frame, (640, 480))
            
            # Detect people in the frame
            boxes, weights = self.hog.detectMultiScale(frame_resized, winStride=(8, 8))
            
            detections = []
            for (x, y, w, h) in boxes:
                # Scale back the coordinates to original frame
                x = int(x * (frame.shape[1] / 640))
                y = int(y * (frame.shape[0] / 480))
                w = int(w * (frame.shape[1] / 640))
                h = int(h * (frame.shape[0] / 480))
                
                area = w * h
                
                if self.human_min_area <= area <= self.human_max_area:
                    detections.append({
                        'bbox': [x, y, x+w, y+h],
                        'confidence': float(weights[0]),
                        'class_id': 0,  # Human class ID
                        'center': [x + w // 2, y + h // 2]
                    })
            
            return detections
            
        except Exception as e:
            logger.error(f"Error in human detection: {str(e)}")
            return []
    
    def associate_humans_bags(self, human_detections: List[Dict], bag_detections: List[Dict]) -> List[Dict]:
        """
        Associate detected humans with gunny bags based on proximity.
        
        Args:
            human_detections: List of detected human information
            bag_detections: List of detected gunny bag information
            
        Returns:
            List[Dict]: List of associations with human and bag information
        """
        associations = []
        
        for human in human_detections:
            hx1, hy1, hx2, hy2 = human['bbox']
            human_center = human['center']
            
            for bag in bag_detections:
                bx1, by1, bx2, by2 = bag['bbox']
                bag_center = bag['center']
                
                # Calculate distance between human and bag centers
                distance = np.linalg.norm(np.array(human_center) - np.array(bag_center))
                
                if distance <= self.human_bag_distance_threshold:
                    associations.append({
                        'human': human,
                        'bag': bag,
                        'distance': distance
                    })
        
        return associations
    
    def detect_crossings_with_humans(self, frame: np.ndarray, detection_results: Dict) -> Dict:
        """
        Detect gunny bag crossings carried by humans across the detection line.
        
        Args:
            frame: Current frame
            detection_results: Detection results containing bags and humans
            
        Returns:
            Dict: Crossing information with counts and associations
        """
        crossings = {
            'left_to_right': 0,
            'right_to_left': 0,
            'total': 0,
            'associations': []
        }
        
        # Get detection line coordinates
        x1, y1, x2, y2 = self.crossing_line
        line_x = x1  # Vertical line x-coordinate
        
        # Get human and bag detections
        human_detections = self.detect_humans(frame)
        bag_detections = detection_results.get('detections', [])
        
        # Associate humans with bags
        associations = self.associate_humans_bags(human_detections, bag_detections)
        
        # Check for crossings based on human-bag associations
        for association in associations:
            human = association['human']
            bag = association['bag']
            
            # Use human center for crossing detection (person carrying the bag)
            human_center_x = human['center'][0]
            
            # Create a unique ID for this association to track over frames
            association_id = f"h_{human['center'][0]}_{human['center'][1]}_b_{bag['center'][0]}_{bag['center'][1]}"
            
            # Check if human (with bag) crosses the line
            if association_id not in self.tracked_objects:
                # New association - initialize tracking
                self.tracked_objects[association_id] = {
                    'last_position': human_center_x,
                    'crossed': False,
                    'association': association,
                    'type': 'human_bag'
                }
            else:
                # Existing association - check for crossing
                last_x = self.tracked_objects[association_id]['last_position']
                current_x = human_center_x
                
                # Check if crossed the line
                if not self.tracked_objects[association_id]['crossed']:
                    if (last_x < line_x < current_x):  # Left to right
                        crossings['left_to_right'] += 1
                        crossings['total'] += 1
                        crossings['associations'].append({
                            'type': 'left_to_right',
                            'human': human,
                            'bag': bag,
                            'frame_position': len(self.tracked_objects)
                        })
                        self.tracked_objects[association_id]['crossed'] = True
                        logger.info(f"Human-bag crossing detected (L->R): Association {association_id}")
                        
                    elif (last_x > line_x > current_x):  # Right to left
                        crossings['right_to_left'] += 1
                        crossings['total'] += 1
                        crossings['associations'].append({
                            'type': 'right_to_left',
                            'human': human,
                            'bag': bag,
                            'frame_position': len(self.tracked_objects)
                        })
                        self.tracked_objects[association_id]['crossed'] = True
                        logger.info(f"Human-bag crossing detected (R->L): Association {association_id}")
                
                # Update position
                self.tracked_objects[association_id]['last_position'] = current_x
        
        return crossings
