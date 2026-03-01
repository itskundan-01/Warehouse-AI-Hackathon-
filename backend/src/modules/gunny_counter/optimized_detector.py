"""
Optimized Gunny Bag Detector
High-performance detector optimized for speed with minimal accuracy loss
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class Detection:
    """Lightweight detection result"""
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    class_id: int
    class_name: str
    center: Tuple[int, int]

@dataclass
class TrackedObject:
    """Optimized tracked object"""
    id: int
    positions: List[Tuple[int, int]]
    frame_numbers: List[int]
    confidence_history: List[float]
    crossed_line: bool = False
    last_update_frame: int = 0

class OptimizedGunnyDetector:
    """
    High-performance gunny bag detector optimized for speed
    Reduces computational overhead while maintaining detection accuracy
    """
    
    def __init__(self, confidence_threshold: float = 0.3, nms_threshold: float = 0.4):
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        
        # Optimized parameters - reduced complexity
        self.min_area = 800  # Minimum detection area
        self.max_area = 50000  # Maximum detection area
        self.min_aspect_ratio = 0.3
        self.max_aspect_ratio = 2.0
        
        # Simplified color ranges (most effective ones only)
        self.gunny_color_ranges = {
            'brown_jute': (np.array([8, 50, 80]), np.array([25, 255, 200])),
            'beige_natural': (np.array([15, 30, 120]), np.array([35, 150, 255])),
            'tan_burlap': (np.array([12, 40, 100]), np.array([28, 180, 220]))
        }
        
        # Optimized morphological kernels (pre-computed)
        self.opening_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.closing_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        
        # Object tracking (optimized)
        self.tracked_objects: Dict[int, TrackedObject] = {}
        self.next_object_id = 1
        self.max_tracking_distance = 100  # Reduced from 150
        self.max_tracking_age = 30  # Frames before removing stale tracks
        
        # Performance optimization flags
        self.use_fast_detection = True
        self.use_simplified_nms = True
        self.cleanup_frequency = 50  # Clean up tracking every N frames
        self.frame_count = 0
        
        print(f"🚀 Optimized Gunny Detector initialized")
        print(f"Color ranges: {len(self.gunny_color_ranges)}")
        print(f"Fast detection: {self.use_fast_detection}")
        print(f"Simplified NMS: {self.use_simplified_nms}")
    
    def detect_gunny_bags_roi(self, frame: np.ndarray) -> List[Detection]:
        """Optimized detection for ROI processing"""
        if self.use_fast_detection:
            return self._fast_color_detection(frame)
        else:
            return self._standard_detection(frame)
    
    def detect_gunny_bags(self, frame: np.ndarray) -> Tuple[List[Detection], List[Detection]]:
        """Legacy interface - returns (bag_detections, empty_human_list)"""
        bag_detections = self.detect_gunny_bags_roi(frame)
        return bag_detections, []  # No human detection for speed
    
    def _fast_color_detection(self, frame: np.ndarray) -> List[Detection]:
        """Fast color-based detection with minimal processing"""
        detections = []
        
        # Convert to HSV once
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Combine all color masks efficiently
        combined_mask = None
        for color_name, (lower, upper) in self.gunny_color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            if combined_mask is None:
                combined_mask = mask
            else:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Single morphological operation pass
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, self.opening_kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, self.closing_kernel)
        
        # Find contours with reduced precision
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Quick filtering and detection creation
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Quick aspect ratio check
                aspect_ratio = w / h if h > 0 else 0
                if self.min_aspect_ratio <= aspect_ratio <= self.max_aspect_ratio:
                    
                    # Fast confidence calculation
                    area_score = min(area / 5000, 1.0)
                    aspect_score = 1.0 - abs(aspect_ratio - 0.7) * 0.5
                    confidence = (area_score * 0.6 + aspect_score * 0.4) * 0.8
                    
                    if confidence > self.confidence_threshold:
                        detection = Detection(
                            bbox=(x, y, w, h),
                            confidence=confidence,
                            class_id=0,
                            class_name="gunny_bag",
                            center=(x + w//2, y + h//2)
                        )
                        detections.append(detection)
        
        # Fast NMS if enabled
        if self.use_simplified_nms and len(detections) > 1:
            detections = self._fast_nms(detections)
        
        return detections
    
    def _fast_nms(self, detections: List[Detection]) -> List[Detection]:
        """Simplified Non-Maximum Suppression for speed"""
        if len(detections) <= 1:
            return detections
        
        # Sort by confidence (descending)
        detections.sort(key=lambda x: x.confidence, reverse=True)
        
        kept_detections = []
        
        for detection in detections:
            # Check overlap with already kept detections
            keep = True
            x1, y1, w1, h1 = detection.bbox
            
            for kept in kept_detections:
                x2, y2, w2, h2 = kept.bbox
                
                # Fast overlap check (simplified IoU)
                overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = overlap_x * overlap_y
                
                union_area = w1 * h1 + w2 * h2 - overlap_area
                iou = overlap_area / union_area if union_area > 0 else 0
                
                if iou > self.nms_threshold:
                    keep = False
                    break
            
            if keep:
                kept_detections.append(detection)
        
        return kept_detections
    
    def update_tracking(self, detections: List[Detection], frame_number: int):
        """Optimized object tracking"""
        self.frame_count = frame_number
        
        # Clean up stale tracks periodically
        if frame_number % self.cleanup_frequency == 0:
            self._cleanup_stale_tracks(frame_number)
        
        # Quick return if no detections
        if not detections:
            return
        
        # Associate detections with existing tracks
        unmatched_detections = detections.copy()
        
        for obj_id, tracked_obj in self.tracked_objects.items():
            if not tracked_obj.positions:
                continue
                
            last_pos = tracked_obj.positions[-1]
            best_match = None
            best_distance = float('inf')
            
            # Find closest detection
            for detection in unmatched_detections:
                distance = self._fast_distance(last_pos, detection.center)
                if distance < best_distance and distance < self.max_tracking_distance:
                    best_distance = distance
                    best_match = detection
            
            # Update track if match found
            if best_match:
                tracked_obj.positions.append(best_match.center)
                tracked_obj.frame_numbers.append(frame_number)
                tracked_obj.confidence_history.append(best_match.confidence)
                tracked_obj.last_update_frame = frame_number
                
                # Limit history size for memory efficiency
                if len(tracked_obj.positions) > 50:
                    tracked_obj.positions = tracked_obj.positions[-25:]
                    tracked_obj.frame_numbers = tracked_obj.frame_numbers[-25:]
                    tracked_obj.confidence_history = tracked_obj.confidence_history[-25:]
                
                unmatched_detections.remove(best_match)
        
        # Create new tracks for unmatched detections
        for detection in unmatched_detections:
            new_track = TrackedObject(
                id=self.next_object_id,
                positions=[detection.center],
                frame_numbers=[frame_number],
                confidence_history=[detection.confidence],
                last_update_frame=frame_number
            )
            self.tracked_objects[self.next_object_id] = new_track
            self.next_object_id += 1
    
    def check_line_crossings(self, line_x: int) -> List[int]:
        """Fast line crossing detection"""
        new_crossings = []
        
        for obj_id, tracked_obj in self.tracked_objects.items():
            if tracked_obj.crossed_line or len(tracked_obj.positions) < 2:
                continue
            
            # Check last two positions for line crossing
            pos1 = tracked_obj.positions[-2]
            pos2 = tracked_obj.positions[-1]
            
            # Simple crossing detection
            if ((pos1[0] < line_x < pos2[0]) or (pos2[0] < line_x < pos1[0])):
                tracked_obj.crossed_line = True
                new_crossings.append(obj_id)
        
        return new_crossings
    
    def _fast_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Fast distance calculation (Manhattan distance for speed)"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _cleanup_stale_tracks(self, current_frame: int):
        """Remove old, inactive tracks"""
        stale_tracks = []
        
        for obj_id, tracked_obj in self.tracked_objects.items():
            frames_since_update = current_frame - tracked_obj.last_update_frame
            if frames_since_update > self.max_tracking_age:
                stale_tracks.append(obj_id)
        
        for obj_id in stale_tracks:
            del self.tracked_objects[obj_id]
        
        if stale_tracks:
            print(f"   🧹 Cleaned up {len(stale_tracks)} stale tracks")
    
    def get_tracking_stats(self) -> Dict[str, Any]:
        """Get current tracking statistics"""
        crossed_count = sum(1 for obj in self.tracked_objects.values() if obj.crossed_line)
        active_count = len(self.tracked_objects)
        
        return {
            'total_tracks': self.next_object_id - 1,
            'active_tracks': active_count,
            'crossed_line': crossed_count,
            'average_track_length': np.mean([len(obj.positions) for obj in self.tracked_objects.values()]) if self.tracked_objects else 0
        }
    
    def _standard_detection(self, frame: np.ndarray) -> List[Detection]:
        """Standard detection method (fallback)"""
        # This is the fallback method if fast detection is disabled
        return self._fast_color_detection(frame)  # Use fast method as standard for now

# Performance testing utilities
class PerformanceTester:
    """Utility class for testing detector performance"""
    
    @staticmethod
    def benchmark_detector(detector: OptimizedGunnyDetector, test_frames: List[np.ndarray]) -> Dict[str, float]:
        """Benchmark detector performance"""
        print("🔬 Benchmarking detector performance...")
        
        start_time = time.time()
        total_detections = 0
        
        for i, frame in enumerate(test_frames):
            detections = detector.detect_gunny_bags_roi(frame)
            total_detections += len(detections)
            
            if i % 10 == 0:
                elapsed = time.time() - start_time
                fps = (i + 1) / elapsed if elapsed > 0 else 0
                print(f"   Frame {i+1}/{len(test_frames)} - {fps:.1f} FPS")
        
        end_time = time.time()
        processing_time = end_time - start_time
        avg_fps = len(test_frames) / processing_time if processing_time > 0 else 0
        
        results = {
            'total_frames': len(test_frames),
            'processing_time': processing_time,
            'average_fps': avg_fps,
            'total_detections': total_detections,
            'detections_per_frame': total_detections / len(test_frames) if test_frames else 0
        }
        
        print(f"\n📊 Benchmark Results:")
        print(f"   Frames processed: {results['total_frames']}")
        print(f"   Processing time: {results['processing_time']:.2f}s")
        print(f"   Average FPS: {results['average_fps']:.1f}")
        print(f"   Total detections: {results['total_detections']}")
        print(f"   Avg detections/frame: {results['detections_per_frame']:.2f}")
        
        return results
