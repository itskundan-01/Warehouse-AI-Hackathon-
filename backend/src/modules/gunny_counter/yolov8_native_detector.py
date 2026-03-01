"""
YOLOv8 Native Gunny Bag Detector
Advanced implementation using YOLOv8 architecture principles with OpenCV backend
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import json
import os
from pathlib import Path

@dataclass
class Detection:
    """Detection result structure matching YOLOv8 output format"""
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    class_id: int
    class_name: str
    center: Tuple[int, int]

@dataclass
class TrackedObject:
    """Tracked object for multi-frame analysis"""
    id: int
    detections: List[Detection]
    positions: List[Tuple[int, int]]
    frame_numbers: List[int]
    confidence_history: List[float]
    crossed_line: bool = False
    associated_human: Optional[int] = None

class YOLOv8NativeGunnyDetector:
    """
    YOLOv8-inspired Gunny Bag Detector using native OpenCV
    Implements YOLOv8 architecture principles without PyTorch dependency
    """
    
    def __init__(self, confidence_threshold: float = 0.5, nms_threshold: float = 0.4):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        
        # YOLOv8-inspired anchor system
        self.anchor_sizes = [(32, 32), (64, 64), (96, 96), (128, 128), (160, 160)]
        self.stride_sizes = [8, 16, 32]
        
        # Enhanced detection parameters
        self.detection_scales = [0.8, 1.0, 1.2, 1.5]
        self.rotation_angles = [0, 15, 30, 45, -15, -30]
        
        # Object tracking
        self.tracked_objects: Dict[int, TrackedObject] = {}
        self.next_object_id = 1
        self.max_tracking_distance = 150
        self.min_tracking_frames = 3
        
        # Human detection
        self.human_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_fullbody.xml'
        )
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'
        )
        
        # Enhanced color ranges for gunny bags (YOLOv8-inspired multi-class approach)
        self.gunny_color_ranges = {
            'brown_jute': {
                'lower': np.array([8, 50, 80]),
                'upper': np.array([25, 255, 200])
            },
            'beige_natural': {
                'lower': np.array([15, 30, 120]),
                'upper': np.array([35, 150, 255])
            },
            'tan_burlap': {
                'lower': np.array([12, 40, 100]),
                'upper': np.array([28, 180, 220])
            },
            'light_brown': {
                'lower': np.array([10, 60, 140]),
                'upper': np.array([30, 200, 255])
            },
            'golden_jute': {
                'lower': np.array([20, 50, 150]),
                'upper': np.array([40, 180, 255])
            }
        }
        
        # YOLOv8-style feature extraction kernels
        self.gabor_kernels = self._create_gabor_kernels()
        self.morphology_kernels = self._create_morphology_kernels()
        
        print(f"YOLOv8 Native Gunny Detector initialized")
        print(f"Confidence threshold: {confidence_threshold}")
        print(f"NMS threshold: {nms_threshold}")
        print(f"Color ranges: {len(self.gunny_color_ranges)}")
        print(f"Gabor kernels: {len(self.gabor_kernels)}")
    
    def _create_gabor_kernels(self) -> List[np.ndarray]:
        """Create Gabor filter kernels for texture detection (YOLOv8-inspired)"""
        kernels = []
        
        # Parameters for jute/burlap texture detection
        frequencies = [0.1, 0.3, 0.5]
        orientations = [0, 30, 60, 90, 120, 150]
        kernel_sizes = [15, 21, 31]
        
        for freq in frequencies:
            for angle in orientations:
                for ksize in kernel_sizes:
                    kernel = cv2.getGaborKernel(
                        (ksize, ksize), 5, np.radians(angle), 
                        2 * np.pi * freq, 0.5, 0, ktype=cv2.CV_32F
                    )
                    kernels.append(kernel)
        
        return kernels
    
    def _create_morphology_kernels(self) -> List[np.ndarray]:
        """Create morphological kernels for shape refinement"""
        kernels = []
        
        # Various kernel shapes and sizes
        sizes = [3, 5, 7, 9]
        shapes = [cv2.MORPH_RECT, cv2.MORPH_ELLIPSE, cv2.MORPH_CROSS]
        
        for size in sizes:
            for shape in shapes:
                kernel = cv2.getStructuringElement(shape, (size, size))
                kernels.append(kernel)
        
        return kernels
    
    def _yolov8_style_preprocessing(self, frame: np.ndarray) -> List[np.ndarray]:
        """YOLOv8-style image preprocessing with multiple scales and augmentations"""
        preprocessed_frames = []
        
        # Original frame
        preprocessed_frames.append(frame)
        
        # Multi-scale processing
        for scale in self.detection_scales:
            if scale != 1.0:
                h, w = frame.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                scaled = cv2.resize(frame, (new_w, new_h))
                if scale > 1.0:
                    # Crop to original size for larger scales
                    start_h = (new_h - h) // 2
                    start_w = (new_w - w) // 2
                    scaled = scaled[start_h:start_h+h, start_w:start_w+w]
                else:
                    # Pad for smaller scales
                    pad_h = (h - new_h) // 2
                    pad_w = (w - new_w) // 2
                    scaled = cv2.copyMakeBorder(
                        scaled, pad_h, h-new_h-pad_h, pad_w, w-new_w-pad_w,
                        cv2.BORDER_CONSTANT, value=[0, 0, 0]
                    )
                preprocessed_frames.append(scaled)
        
        # Color space variations
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        preprocessed_frames.extend([hsv_frame, lab_frame])
        
        return preprocessed_frames
    
    def _multi_scale_detection(self, frame: np.ndarray) -> List[Detection]:
        """YOLOv8-inspired multi-scale detection"""
        all_detections = []
        
        # Process multiple preprocessed versions
        preprocessed_frames = self._yolov8_style_preprocessing(frame)
        
        for i, proc_frame in enumerate(preprocessed_frames):
            # Color-based detection
            color_detections = self._enhanced_color_detection(proc_frame)
            
            # Texture-based detection
            texture_detections = self._gabor_texture_detection(proc_frame)
            
            # Shape-based detection
            shape_detections = self._contour_shape_detection(proc_frame)
            
            # Combine detections with confidence weighting
            frame_detections = color_detections + texture_detections + shape_detections
            
            # Adjust confidence based on preprocessing method
            confidence_multiplier = 1.0 if i == 0 else 0.8  # Original frame gets highest weight
            for detection in frame_detections:
                detection.confidence *= confidence_multiplier
            
            all_detections.extend(frame_detections)
        
        return all_detections
    
    def _enhanced_color_detection(self, frame: np.ndarray) -> List[Detection]:
        """Enhanced color-based detection with multiple color spaces"""
        detections = []
        
        # Convert to HSV if not already
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        else:
            hsv = frame
        
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        # Apply all color ranges
        for color_name, color_range in self.gunny_color_ranges.items():
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # Morphological operations for noise reduction
            for kernel in self.morphology_kernels[:4]:  # Use first 4 kernels
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate confidence based on area, aspect ratio, and color match
                aspect_ratio = w / h if h > 0 else 0
                area_score = min(area / 10000, 1.0)  # Normalize area score
                aspect_score = 1.0 - abs(aspect_ratio - 0.7) if 0.3 <= aspect_ratio <= 1.5 else 0.3
                
                confidence = (area_score * 0.4 + aspect_score * 0.6) * 0.8
                
                if confidence > self.confidence_threshold:
                    detection = Detection(
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        class_id=0,
                        class_name="gunny_bag",
                        center=(x + w//2, y + h//2)
                    )
                    detections.append(detection)
        
        return detections
    
    def _gabor_texture_detection(self, frame: np.ndarray) -> List[Detection]:
        """Gabor filter-based texture detection for jute/burlap patterns"""
        detections = []
        
        # Convert to grayscale if needed
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Apply Gabor filters
        gabor_responses = []
        for kernel in self.gabor_kernels:
            filtered = cv2.filter2D(gray, cv2.CV_8UC3, kernel)
            gabor_responses.append(filtered)
        
        # Combine responses (take maximum response at each pixel)
        combined_response = np.zeros_like(gray)
        for response in gabor_responses:
            combined_response = np.maximum(combined_response, response)
        
        # Threshold and find contours
        _, binary = cv2.threshold(combined_response, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 800:  # Minimum area for texture-based detection
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate texture confidence
                roi = combined_response[y:y+h, x:x+w]
                texture_strength = np.mean(roi) / 255.0
                area_score = min(area / 8000, 1.0)
                
                confidence = (texture_strength * 0.6 + area_score * 0.4) * 0.7
                
                if confidence > self.confidence_threshold:
                    detection = Detection(
                        bbox=(x, y, w, h),
                        confidence=confidence,
                        class_id=0,
                        class_name="gunny_bag",
                        center=(x + w//2, y + h//2)
                    )
                    detections.append(detection)
        
        return detections
    
    def _contour_shape_detection(self, frame: np.ndarray) -> List[Detection]:
        """Contour-based shape detection for bag-like objects"""
        detections = []
        
        # Edge detection
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
        
        # Multiple edge detection approaches
        edges1 = cv2.Canny(gray, 50, 150)
        edges2 = cv2.Canny(gray, 30, 100)
        edges_combined = cv2.bitwise_or(edges1, edges2)
        
        # Morphological operations to connect edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        edges_combined = cv2.morphologyEx(edges_combined, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(edges_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 600:
                # Shape analysis
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Score based on shape characteristics typical of bags
                    shape_score = 0.5
                    if 0.4 <= aspect_ratio <= 1.2:  # Reasonable aspect ratio for bags
                        shape_score += 0.3
                    if 0.1 <= circularity <= 0.8:  # Not too circular, not too irregular
                        shape_score += 0.2
                    
                    area_score = min(area / 6000, 1.0)
                    confidence = (shape_score * 0.7 + area_score * 0.3) * 0.6
                    
                    if confidence > self.confidence_threshold:
                        detection = Detection(
                            bbox=(x, y, w, h),
                            confidence=confidence,
                            class_id=0,
                            class_name="gunny_bag",
                            center=(x + w//2, y + h//2)
                        )
                        detections.append(detection)
        
        return detections
    
    def _yolov8_nms(self, detections: List[Detection]) -> List[Detection]:
        """YOLOv8-style Non-Maximum Suppression"""
        if not detections:
            return []
        
        # Convert to format needed for cv2.dnn.NMSBoxes
        boxes = []
        confidences = []
        
        for detection in detections:
            x, y, w, h = detection.bbox
            boxes.append([x, y, w, h])
            confidences.append(detection.confidence)
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes, confidences, 
            self.confidence_threshold, 
            self.nms_threshold
        )
        
        # Return filtered detections
        if len(indices) > 0:
            indices = indices.flatten()
            return [detections[i] for i in indices]
        
        return []
    
    def detect_humans(self, frame: np.ndarray) -> List[Detection]:
        """Detect humans in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        humans = []
        
        # Full body detection
        bodies = self.human_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 100)
        )
        
        for (x, y, w, h) in bodies:
            confidence = 0.8  # Base confidence for Haar cascade
            detection = Detection(
                bbox=(x, y, w, h),
                confidence=confidence,
                class_id=1,
                class_name="human",
                center=(x + w//2, y + h//2)
            )
            humans.append(detection)
        
        # Face detection for additional human confirmation
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        for (x, y, w, h) in faces:
            # Estimate full body from face
            body_w = w * 3
            body_h = h * 6
            body_x = max(0, x - body_w // 3)
            body_y = y
            
            confidence = 0.7
            detection = Detection(
                bbox=(body_x, body_y, body_w, body_h),
                confidence=confidence,
                class_id=1,
                class_name="human",
                center=(body_x + body_w//2, body_y + body_h//2)
            )
            humans.append(detection)
        
        # Apply NMS to human detections
        return self._yolov8_nms(humans)
    
    def associate_humans_with_bags(self, humans: List[Detection], bags: List[Detection]) -> List[Detection]:
        """Associate detected bags with nearby humans"""
        associated_bags = []
        
        for bag in bags:
            bag_center = bag.center
            closest_human = None
            min_distance = float('inf')
            
            for human in humans:
                human_center = human.center
                distance = np.sqrt(
                    (bag_center[0] - human_center[0])**2 + 
                    (bag_center[1] - human_center[1])**2
                )
                
                if distance < min_distance:
                    min_distance = distance
                    closest_human = human
            
            # If bag is close enough to a human, mark as associated
            if closest_human and min_distance < 150:  # Distance threshold
                bag.confidence *= 1.2  # Boost confidence for human-associated bags
                bag.confidence = min(bag.confidence, 1.0)  # Cap at 1.0
            
            associated_bags.append(bag)
        
        return associated_bags
    
    def detect_gunny_bags(self, frame: np.ndarray) -> Tuple[List[Detection], List[Detection]]:
        """Main detection method combining all approaches"""
        # Multi-scale detection
        bag_detections = self._multi_scale_detection(frame)
        
        # Apply NMS to bag detections
        bag_detections = self._yolov8_nms(bag_detections)
        
        # Detect humans
        human_detections = self.detect_humans(frame)
        
        # Associate bags with humans
        bag_detections = self.associate_humans_with_bags(human_detections, bag_detections)
        
        return bag_detections, human_detections
    
    def update_tracking(self, detections: List[Detection], frame_number: int):
        """Update object tracking across frames"""
        # Match detections to existing tracked objects
        for detection in detections:
            matched = False
            
            for obj_id, tracked_obj in self.tracked_objects.items():
                if tracked_obj.frame_numbers and len(tracked_obj.positions) > 0:
                    last_pos = tracked_obj.positions[-1]
                    distance = np.sqrt(
                        (detection.center[0] - last_pos[0])**2 + 
                        (detection.center[1] - last_pos[1])**2
                    )
                    
                    if distance < self.max_tracking_distance:
                        # Update existing object
                        tracked_obj.detections.append(detection)
                        tracked_obj.positions.append(detection.center)
                        tracked_obj.frame_numbers.append(frame_number)
                        tracked_obj.confidence_history.append(detection.confidence)
                        matched = True
                        break
            
            if not matched:
                # Create new tracked object
                new_obj = TrackedObject(
                    id=self.next_object_id,
                    detections=[detection],
                    positions=[detection.center],
                    frame_numbers=[frame_number],
                    confidence_history=[detection.confidence]
                )
                self.tracked_objects[self.next_object_id] = new_obj
                self.next_object_id += 1
        
        # Remove old tracked objects
        objects_to_remove = []
        for obj_id, tracked_obj in self.tracked_objects.items():
            if tracked_obj.frame_numbers and frame_number - tracked_obj.frame_numbers[-1] > 30:
                objects_to_remove.append(obj_id)
        
        for obj_id in objects_to_remove:
            del self.tracked_objects[obj_id]
    
    def check_line_crossings(self, line_x: int) -> List[TrackedObject]:
        """Check which objects have crossed the detection line"""
        crossings = []
        
        for tracked_obj in self.tracked_objects.values():
            if len(tracked_obj.positions) >= 2 and not tracked_obj.crossed_line:
                # Check if object crossed the line
                for i in range(1, len(tracked_obj.positions)):
                    prev_x = tracked_obj.positions[i-1][0]
                    curr_x = tracked_obj.positions[i][0]
                    
                    # Check for crossing in either direction
                    if (prev_x < line_x < curr_x) or (curr_x < line_x < prev_x):
                        tracked_obj.crossed_line = True
                        crossings.append(tracked_obj)
                        break
        
        return crossings
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """Get tracking statistics"""
        total_objects = len(self.tracked_objects)
        crossed_objects = sum(1 for obj in self.tracked_objects.values() if obj.crossed_line)
        active_objects = sum(1 for obj in self.tracked_objects.values() 
                           if len(obj.frame_numbers) >= self.min_tracking_frames)
        
        return {
            'total_tracked_objects': total_objects,
            'crossed_line': crossed_objects,
            'active_objects': active_objects,
            'tracking_threshold': self.max_tracking_distance,
            'min_tracking_frames': self.min_tracking_frames
        }
