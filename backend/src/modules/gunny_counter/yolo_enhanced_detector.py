import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class YOLOEnhancedGunnyDetector:
    """
    Enhanced gunny bag detector using YOLO-inspired techniques with OpenCV.
    Implements advanced detection strategies without requiring PyTorch.
    """
    
    def __init__(self):
        """Initialize the YOLO-enhanced detector."""
        # Detection line coordinates (adjusted as per previous requirements)
        self.red_line_coords = (301, 122, 301, min(1127, 1400))
        
        # Enhanced detection parameters inspired by YOLO
        self.confidence_threshold = 0.25
        self.nms_threshold = 0.4
        self.class_confidence_threshold = 0.3
        
        # Multi-scale detection windows (YOLO-inspired grid)
        self.detection_scales = [
            (80, 80),   # Small bags
            (120, 120), # Medium bags
            (160, 160), # Large bags
            (200, 200)  # Extra large bags
        ]
        
        # Enhanced color ranges for gunny bags
        self.enhanced_hsv_ranges = [
            # Brown variations
            ([8, 40, 20], [25, 255, 200]),
            ([15, 30, 50], [35, 180, 180]),
            # Beige/tan variations
            ([20, 20, 80], [40, 120, 200]),
            # Dark brown/muddy
            ([5, 50, 30], [15, 200, 120]),
            # Light brown/khaki
            ([25, 30, 100], [45, 150, 220])
        ]
        
        # Texture analysis parameters
        self.gabor_kernels = self._create_gabor_filters()
        
        # Object tracking for crossing detection
        self.tracked_objects = {}
        self.next_track_id = 0
        self.max_tracking_distance = 100
        
        # Human detection for bag association
        self.human_cascade = self._load_human_detector()
        self.human_bag_distance_threshold = 150
        self.human_min_area = 5000
        self.human_max_area = 50000
        
        # Crossing detection
        self.crossings_detected = []
        
    def _create_gabor_filters(self) -> List[np.ndarray]:
        """Create Gabor filters for texture analysis (YOLO-inspired feature extraction)."""
        filters = []
        for theta in range(0, 180, 30):  # 6 orientations
            for frequency in [0.1, 0.3, 0.5]:  # 3 frequencies
                kernel = cv2.getGaborKernel((31, 31), 5, np.radians(theta), 
                                          2*np.pi*frequency, 0.5, 0, ktype=cv2.CV_32F)
                filters.append(kernel)
        return filters
    
    def _load_human_detector(self):
        """Load human detection cascade."""
        try:
            # Try to load full body cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_fullbody.xml'
            return cv2.CascadeClassifier(cascade_path)
        except:
            logger.warning("Could not load human detector cascade")
            return None
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Enhanced detection using YOLO-inspired multi-scale approach.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List[Dict]: List of detected gunny bag information with confidence scores
        """
        try:
            # Multi-scale detection (YOLO-inspired)
            all_detections = []
            
            # 1. Color-based detection with multiple scales
            color_detections = self._enhanced_color_detection(frame)
            all_detections.extend(color_detections)
            
            # 2. Texture-based detection using Gabor filters
            texture_detections = self._gabor_texture_detection(frame)
            all_detections.extend(texture_detections)
            
            # 3. Shape-based detection with contour analysis
            shape_detections = self._enhanced_shape_detection(frame)
            all_detections.extend(shape_detections)
            
            # 4. Apply YOLO-style NMS
            if all_detections:
                final_detections = self._yolo_style_nms(all_detections)
                
                # 5. Post-process and classify with confidence
                classified_detections = self._classify_detections(frame, final_detections)
                
                return classified_detections
            
            return []
            
        except Exception as e:
            logger.error(f"Error in YOLO-enhanced detection: {str(e)}")
            return []
    
    def _enhanced_color_detection(self, frame: np.ndarray) -> List[Dict]:
        """Enhanced color detection with multiple scales."""
        detections = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for lower, upper in self.enhanced_hsv_ranges:
            # Create mask
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            # Enhanced morphological operations
            kernel_small = np.ones((3,3), np.uint8)
            kernel_large = np.ones((7,7), np.uint8)
            
            # Multi-step morphology for better results
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_small)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_large)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if 1500 <= area <= 20000:  # Expanded area range
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    if 0.2 <= aspect_ratio <= 3.0:  # More flexible aspect ratio
                        # Calculate confidence based on area, aspect ratio, and color match
                        area_confidence = min(area / 15000, 1.0) * 0.4
                        aspect_confidence = 1.0 - abs(aspect_ratio - 1.0) if aspect_ratio <= 2.0 else 0.5
                        color_confidence = 0.6  # Base color confidence
                        
                        total_confidence = (area_confidence + aspect_confidence + color_confidence) / 3.0
                        
                        if total_confidence >= self.confidence_threshold:
                            detections.append({
                                'bbox': [x, y, x+w, y+h],
                                'confidence': total_confidence,
                                'class': 'gunny_bag',
                                'method': 'enhanced_color'
                            })
        
        return detections
    
    def _gabor_texture_detection(self, frame: np.ndarray) -> List[Dict]:
        """Texture-based detection using Gabor filters."""
        detections = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gabor filters and combine responses
        gabor_responses = []
        for kernel in self.gabor_kernels:
            filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
            gabor_responses.append(filtered)
        
        # Combine Gabor responses
        combined_response = np.mean(gabor_responses, axis=0).astype(np.uint8)
        
        # Threshold to find texture regions
        _, texture_mask = cv2.threshold(combined_response, 50, 255, cv2.THRESH_BINARY)
        
        # Find contours in texture regions
        contours, _ = cv2.findContours(texture_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if 2000 <= area <= 18000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                if 0.3 <= aspect_ratio <= 2.5:
                    # Calculate texture confidence
                    roi = combined_response[y:y+h, x:x+w]
                    texture_variance = np.var(roi)
                    texture_confidence = min(texture_variance / 1000, 1.0) * 0.7
                    
                    if texture_confidence >= self.confidence_threshold:
                        detections.append({
                            'bbox': [x, y, x+w, y+h],
                            'confidence': texture_confidence,
                            'class': 'gunny_bag',
                            'method': 'gabor_texture'
                        })
        
        return detections
    
    def _enhanced_shape_detection(self, frame: np.ndarray) -> List[Dict]:
        """Enhanced shape-based detection with better edge analysis."""
        detections = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhanced edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100)
        
        # Dilate edges to connect nearby edges
        kernel = np.ones((3,3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if 1800 <= area <= 16000:
                # Analyze shape properties
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # Calculate hull and solidity
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = area / hull_area if hull_area > 0 else 0
                
                # Calculate extent
                extent = area / (w * h) if (w * h) > 0 else 0
                
                if (0.25 <= aspect_ratio <= 2.8 and 
                    0.3 <= solidity <= 0.95 and 
                    0.3 <= extent <= 0.9):
                    
                    # Calculate shape confidence
                    shape_confidence = (solidity + extent) / 2 * 0.8
                    
                    if shape_confidence >= self.confidence_threshold:
                        detections.append({
                            'bbox': [x, y, x+w, y+h],
                            'confidence': shape_confidence,
                            'class': 'gunny_bag',
                            'method': 'enhanced_shape'
                        })
        
        return detections
    
    def _yolo_style_nms(self, detections: List[Dict]) -> List[Dict]:
        """Apply YOLO-style Non-Maximum Suppression."""
        if not detections:
            return []
        
        # Convert to format suitable for NMS
        boxes = []
        scores = []
        
        for det in detections:
            bbox = det['bbox']
            boxes.append([bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]])  # x, y, w, h
            scores.append(det['confidence'])
        
        boxes = np.array(boxes, dtype=np.float32)
        scores = np.array(scores, dtype=np.float32)
        
        # Apply OpenCV's NMS
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidence_threshold, self.nms_threshold)
        
        if len(indices) > 0:
            indices = indices.flatten()
            return [detections[i] for i in indices]
        
        return []
    
    def _classify_detections(self, frame: np.ndarray, detections: List[Dict]) -> List[Dict]:
        """Final classification and confidence adjustment."""
        classified = []
        
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = bbox
            
            # Extract ROI for further analysis
            roi = frame[y1:y2, x1:x2]
            
            if roi.size == 0:
                continue
            
            # Additional validation checks
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Check for texture patterns typical of gunny bags
            texture_score = self._analyze_texture_patterns(roi_gray)
            
            # Check color distribution
            color_score = self._analyze_color_distribution(roi)
            
            # Combine scores
            final_confidence = (det['confidence'] + texture_score + color_score) / 3.0
            
            if final_confidence >= self.class_confidence_threshold:
                classified.append({
                    'bbox': bbox,
                    'confidence': final_confidence,
                    'class': 'gunny_bag',
                    'method': det['method'],
                    'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                    'area': (x2 - x1) * (y2 - y1)
                })
        
        return classified
    
    def _analyze_texture_patterns(self, roi_gray: np.ndarray) -> float:
        """Analyze texture patterns in ROI."""
        try:
            # Calculate local binary patterns-like features
            h, w = roi_gray.shape
            if h < 10 or w < 10:
                return 0.0
            
            # Calculate gradient magnitude
            grad_x = cv2.Sobel(roi_gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(roi_gray, cv2.CV_64F, 0, 1, ksize=3)
            grad_mag = np.sqrt(grad_x**2 + grad_y**2)
            
            # Texture score based on gradient statistics
            texture_score = np.std(grad_mag) / 255.0
            return min(texture_score, 1.0)
            
        except:
            return 0.0
    
    def _analyze_color_distribution(self, roi: np.ndarray) -> float:
        """Analyze color distribution in ROI."""
        try:
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Check how much of the ROI matches gunny bag colors
            total_pixels = roi.shape[0] * roi.shape[1]
            matching_pixels = 0
            
            for lower, upper in self.enhanced_hsv_ranges:
                mask = cv2.inRange(hsv_roi, np.array(lower), np.array(upper))
                matching_pixels += np.sum(mask > 0)
            
            color_score = min(matching_pixels / total_pixels, 1.0)
            return color_score
            
        except:
            return 0.0
    
    def detect_humans(self, frame: np.ndarray) -> List[Dict]:
        """Detect humans in the frame."""
        humans = []
        
        if self.human_cascade is None:
            return humans
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect humans at multiple scales
        detected = self.human_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 100)
        )
        
        for (x, y, w, h) in detected:
            if w * h > self.human_min_area:
                humans.append({
                    'bbox': [x, y, x+w, y+h],
                    'center': (x + w//2, y + h//2),
                    'confidence': 0.8  # Default confidence for cascade detection
                })
        
        return humans
    
    def associate_humans_with_bags(self, humans: List[Dict], bags: List[Dict]) -> List[Dict]:
        """Associate detected humans with gunny bags."""
        associated_bags = []
        
        for bag in bags:
            bag_center = bag['center']
            min_distance = float('inf')
            associated_human = None
            
            for human in humans:
                human_center = human['center']
                distance = np.sqrt((bag_center[0] - human_center[0])**2 + 
                                 (bag_center[1] - human_center[1])**2)
                
                if distance < min_distance and distance < self.human_bag_distance_threshold:
                    min_distance = distance
                    associated_human = human
            
            if associated_human:
                bag['human_associated'] = True
                bag['human_distance'] = min_distance
                bag['confidence'] *= 1.2  # Boost confidence for human-associated bags
            else:
                bag['human_associated'] = False
                bag['human_distance'] = float('inf')
            
            associated_bags.append(bag)
        
        return associated_bags
    
    def detect_crossings(self, current_detections: List[Dict], frame_number: int) -> int:
        """Detect crossings using enhanced tracking."""
        # Update tracking
        self._update_tracking(current_detections)
        
        # Check for line crossings
        crossings = 0
        line_x = self.red_line_coords[0]
        
        for track_id, track_data in self.tracked_objects.items():
            if len(track_data['positions']) >= 2:
                prev_pos = track_data['positions'][-2]
                curr_pos = track_data['positions'][-1]
                
                # Check if crossed the line
                if ((prev_pos[0] < line_x and curr_pos[0] >= line_x) or 
                    (prev_pos[0] > line_x and curr_pos[0] <= line_x)):
                    
                    if not track_data.get('crossed', False):
                        crossings += 1
                        track_data['crossed'] = True
                        
                        # Log the crossing
                        self.crossings_detected.append({
                            'frame': frame_number,
                            'track_id': track_id,
                            'position': curr_pos,
                            'human_associated': track_data.get('human_associated', False)
                        })
        
        return crossings
    
    def _update_tracking(self, detections: List[Dict]):
        """Update object tracking."""
        # Simple tracking based on distance
        used_detections = set()
        
        # Update existing tracks
        for track_id in list(self.tracked_objects.keys()):
            track = self.tracked_objects[track_id]
            last_pos = track['positions'][-1] if track['positions'] else None
            
            if last_pos is None:
                continue
            
            best_match = None
            best_distance = float('inf')
            
            for i, det in enumerate(detections):
                if i in used_detections:
                    continue
                
                det_center = det['center']
                distance = np.sqrt((last_pos[0] - det_center[0])**2 + 
                                 (last_pos[1] - det_center[1])**2)
                
                if distance < best_distance and distance < self.max_tracking_distance:
                    best_distance = distance
                    best_match = (i, det)
            
            if best_match:
                used_detections.add(best_match[0])
                track['positions'].append(best_match[1]['center'])
                track['last_seen'] = len(track['positions'])
                track['human_associated'] = best_match[1].get('human_associated', False)
                
                # Keep only recent positions
                if len(track['positions']) > 10:
                    track['positions'] = track['positions'][-10:]
            else:
                # Remove old tracks
                if len(track['positions']) > 5:
                    del self.tracked_objects[track_id]
        
        # Create new tracks for unmatched detections
        for i, det in enumerate(detections):
            if i not in used_detections:
                self.tracked_objects[self.next_track_id] = {
                    'positions': [det['center']],
                    'last_seen': 1,
                    'crossed': False,
                    'human_associated': det.get('human_associated', False)
                }
                self.next_track_id += 1
    
    def get_detection_line_coords(self) -> Tuple[int, int, int, int]:
        """Get the detection line coordinates."""
        return self.red_line_coords
    
    def get_crossings_summary(self) -> Dict:
        """Get summary of detected crossings."""
        total_crossings = len(self.crossings_detected)
        human_associated_crossings = sum(1 for c in self.crossings_detected if c['human_associated'])
        
        return {
            'total_crossings': total_crossings,
            'human_associated_crossings': human_associated_crossings,
            'crossings_detail': self.crossings_detected
        }
