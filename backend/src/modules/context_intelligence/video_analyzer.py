"""
Video Analyzer for Contextual Intelligence.
Analyzes video frames to extract contextual information and understand activities.
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.config.logging_config import get_logger

logger = get_logger(__name__)

class VideoAnalyzer:
    """Analyzes video frames for contextual understanding."""
    
    def __init__(self):
        """Initialize the video analyzer."""
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=True, history=500, varThreshold=50
        )
        self.motion_threshold = 1000  # Minimum contour area for motion detection
        logger.info("VideoAnalyzer initialized")
    
    def analyze_frame(self, frame: np.ndarray, timestamp: float) -> Dict[str, Any]:
        """
        Analyze a video frame for contextual information.
        
        Args:
            frame: OpenCV frame as numpy array
            timestamp: Timestamp in seconds from video start
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis = {
                "timestamp": timestamp,
                "motion_detected": False,
                "motion_areas": [],
                "brightness": 0,
                "activity_level": 0,
                "objects_detected": [],
                "scene_description": ""
            }
            
            # Basic frame analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            analysis["brightness"] = np.mean(gray)
            
            # Motion detection
            motion_mask = self.background_subtractor.apply(frame)
            contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_areas = []
            total_motion_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.motion_threshold:
                    x, y, w, h = cv2.boundingRect(contour)
                    motion_areas.append({
                        "x": int(x), "y": int(y), 
                        "width": int(w), "height": int(h),
                        "area": int(area)
                    })
                    total_motion_area += area
            
            if motion_areas:
                analysis["motion_detected"] = True
                analysis["motion_areas"] = motion_areas
                analysis["activity_level"] = min(len(motion_areas) * 2, 10)  # Scale 0-10
            
            # Object detection (simplified)
            analysis["objects_detected"] = self._detect_objects(frame)
            
            # Scene description
            analysis["scene_description"] = self._generate_scene_description(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return {"error": str(e), "timestamp": timestamp}
    
    def _detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect objects in the frame using edge detection and contours."""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            objects = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 2000:  # Filter small objects
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        "type": self._classify_object(w, h, area),
                        "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        "area": int(area),
                        "confidence": min(area / 10000, 1.0)  # Normalized confidence
                    })
            
            return objects[:10]  # Limit to top 10 objects
            
        except Exception as e:
            logger.error(f"Error detecting objects: {str(e)}")
            return []
    
    def _classify_object(self, width: int, height: int, area: int) -> str:
        """Simple object classification based on dimensions."""
        aspect_ratio = width / height if height > 0 else 1
        
        if area > 20000:
            if aspect_ratio > 2:
                return "vehicle"
            else:
                return "large_object"
        elif area > 5000:
            if 0.5 < aspect_ratio < 2:
                return "person"
            elif aspect_ratio > 2:
                return "package"
            else:
                return "equipment"
        else:
            return "small_object"
    
    def _generate_scene_description(self, analysis: Dict[str, Any]) -> str:
        """Generate a textual description of the scene."""
        descriptions = []
        
        # Brightness description
        brightness = analysis["brightness"]
        if brightness < 50:
            descriptions.append("Low light conditions")
        elif brightness > 200:
            descriptions.append("Bright lighting")
        else:
            descriptions.append("Normal lighting")
        
        # Motion description
        if analysis["motion_detected"]:
            motion_count = len(analysis["motion_areas"])
            if motion_count == 1:
                descriptions.append("Single motion area detected")
            else:
                descriptions.append(f"{motion_count} motion areas detected")
            
            activity_level = analysis["activity_level"]
            if activity_level > 7:
                descriptions.append("High activity")
            elif activity_level > 3:
                descriptions.append("Moderate activity")
            else:
                descriptions.append("Low activity")
        else:
            descriptions.append("No significant motion")
        
        # Object descriptions
        objects = analysis["objects_detected"]
        if objects:
            object_types = list(set([obj["type"] for obj in objects]))
            descriptions.append(f"Objects detected: {', '.join(object_types)}")
        
        return "; ".join(descriptions)


class EventDetector:
    """Detects specific events in video sequences."""
    
    def __init__(self):
        """Initialize the event detector."""
        self.frame_buffer = []
        self.buffer_size = 30  # 30 frames for event detection
        self.events = []
        logger.info("EventDetector initialized")
    
    def process_frame(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process frame analysis to detect events.
        
        Args:
            analysis: Frame analysis from VideoAnalyzer
            
        Returns:
            List of detected events
        """
        self.frame_buffer.append(analysis)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
        
        detected_events = []
        
        # Event detection logic
        detected_events.extend(self._detect_motion_events())
        detected_events.extend(self._detect_object_events())
        detected_events.extend(self._detect_anomaly_events())
        
        return detected_events
    
    def _detect_motion_events(self) -> List[Dict[str, Any]]:
        """Detect motion-based events."""
        if len(self.frame_buffer) < 10:
            return []
        
        events = []
        recent_frames = self.frame_buffer[-10:]
        
        # Sudden motion increase
        motion_levels = [frame.get("activity_level", 0) for frame in recent_frames]
        if len(motion_levels) >= 2:
            current_motion = motion_levels[-1]
            prev_motion = motion_levels[-2]
            
            if current_motion > 5 and prev_motion <= 2:
                events.append({
                    "type": "sudden_motion",
                    "timestamp": recent_frames[-1]["timestamp"],
                    "description": "Sudden increase in motion detected",
                    "severity": "medium",
                    "confidence": 0.8
                })
        
        return events
    
    def _detect_object_events(self) -> List[Dict[str, Any]]:
        """Detect object-based events."""
        if len(self.frame_buffer) < 5:
            return []
        
        events = []
        recent_frame = self.frame_buffer[-1]
        
        # New object appearance
        objects = recent_frame.get("objects_detected", [])
        for obj in objects:
            if obj["type"] == "person" and obj["confidence"] > 0.7:
                events.append({
                    "type": "person_detected",
                    "timestamp": recent_frame["timestamp"],
                    "description": f"Person detected at ({obj['bbox']['x']}, {obj['bbox']['y']})",
                    "severity": "low",
                    "confidence": obj["confidence"]
                })
        
        return events
    
    def _detect_anomaly_events(self) -> List[Dict[str, Any]]:
        """Detect anomalous events."""
        if len(self.frame_buffer) < 15:
            return []
        
        events = []
        recent_frames = self.frame_buffer[-15:]
        
        # Unusual lighting changes
        brightness_values = [frame.get("brightness", 128) for frame in recent_frames]
        brightness_change = max(brightness_values) - min(brightness_values)
        
        if brightness_change > 100:
            events.append({
                "type": "lighting_anomaly",
                "timestamp": recent_frames[-1]["timestamp"],
                "description": "Unusual lighting change detected",
                "severity": "low",
                "confidence": 0.6
            })
        
        return events


class QueryProcessor:
    """Processes natural language queries about video content."""
    
    def __init__(self):
        """Initialize the query processor."""
        self.analysis_history = []
        self.events_history = []
        logger.info("QueryProcessor initialized")
    
    def add_analysis(self, analysis: Dict[str, Any], events: List[Dict[str, Any]]):
        """Add frame analysis and events to history."""
        self.analysis_history.append(analysis)
        self.events_history.extend(events)
        
        # Keep only recent history
        if len(self.analysis_history) > 1000:
            self.analysis_history = self.analysis_history[-1000:]
        if len(self.events_history) > 500:
            self.events_history = self.events_history[-500:]
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about the video content.
        
        Args:
            query: Natural language query
            
        Returns:
            Query response with relevant information
        """
        query_lower = query.lower()
        
        try:
            # Motion-related queries
            if any(word in query_lower for word in ["motion", "movement", "activity"]):
                return self._handle_motion_query(query_lower)
            
            # Object-related queries
            elif any(word in query_lower for word in ["person", "people", "object", "vehicle"]):
                return self._handle_object_query(query_lower)
            
            # Event-related queries
            elif any(word in query_lower for word in ["event", "incident", "anomaly", "alert"]):
                return self._handle_event_query(query_lower)
            
            # Time-related queries
            elif any(word in query_lower for word in ["when", "time", "timestamp"]):
                return self._handle_time_query(query_lower)
            
            # General summary
            else:
                return self._handle_summary_query()
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "message": "Error processing query",
                "error": str(e)
            }
    
    def _handle_motion_query(self, query: str) -> Dict[str, Any]:
        """Handle motion-related queries."""
        motion_frames = [f for f in self.analysis_history if f.get("motion_detected", False)]
        
        if not motion_frames:
            return {
                "success": True,
                "message": "No significant motion detected in the analyzed video.",
                "count": 0
            }
        
        avg_activity = np.mean([f.get("activity_level", 0) for f in motion_frames])
        
        return {
            "success": True,
            "message": f"Motion detected in {len(motion_frames)} frames with average activity level {avg_activity:.1f}",
            "count": len(motion_frames),
            "average_activity": round(avg_activity, 2),
            "timestamps": [f["timestamp"] for f in motion_frames[:10]]  # First 10
        }
    
    def _handle_object_query(self, query: str) -> Dict[str, Any]:
        """Handle object-related queries."""
        all_objects = []
        for frame in self.analysis_history:
            all_objects.extend(frame.get("objects_detected", []))
        
        if not all_objects:
            return {
                "success": True,
                "message": "No objects detected in the analyzed video.",
                "count": 0
            }
        
        # Count by type
        object_counts = {}
        for obj in all_objects:
            obj_type = obj["type"]
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
        
        return {
            "success": True,
            "message": f"Detected {len(all_objects)} objects across {len(object_counts)} categories",
            "total_objects": len(all_objects),
            "object_types": object_counts
        }
    
    def _handle_event_query(self, query: str) -> Dict[str, Any]:
        """Handle event-related queries."""
        if not self.events_history:
            return {
                "success": True,
                "message": "No events detected in the analyzed video.",
                "count": 0
            }
        
        # Count by type
        event_counts = {}
        for event in self.events_history:
            event_type = event["type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "success": True,
            "message": f"Detected {len(self.events_history)} events across {len(event_counts)} categories",
            "total_events": len(self.events_history),
            "event_types": event_counts,
            "recent_events": self.events_history[-5:]  # Last 5 events
        }
    
    def _handle_time_query(self, query: str) -> Dict[str, Any]:
        """Handle time-related queries."""
        if not self.analysis_history:
            return {
                "success": True,
                "message": "No analysis data available.",
                "duration": 0
            }
        
        timestamps = [f["timestamp"] for f in self.analysis_history]
        duration = max(timestamps) - min(timestamps) if timestamps else 0
        
        return {
            "success": True,
            "message": f"Video analysis covers {duration:.1f} seconds",
            "duration": round(duration, 2),
            "frames_analyzed": len(self.analysis_history),
            "start_time": min(timestamps),
            "end_time": max(timestamps)
        }
    
    def _handle_summary_query(self) -> Dict[str, Any]:
        """Handle general summary queries."""
        if not self.analysis_history:
            return {
                "success": True,
                "message": "No analysis data available for summary.",
                "summary": {}
            }
        
        # Calculate summary statistics
        motion_count = len([f for f in self.analysis_history if f.get("motion_detected", False)])
        avg_brightness = np.mean([f.get("brightness", 128) for f in self.analysis_history])
        total_objects = sum(len(f.get("objects_detected", [])) for f in self.analysis_history)
        
        summary = {
            "frames_analyzed": len(self.analysis_history),
            "motion_frames": motion_count,
            "average_brightness": round(avg_brightness, 2),
            "total_objects_detected": total_objects,
            "total_events": len(self.events_history)
        }
        
        return {
            "success": True,
            "message": "Video analysis summary generated",
            "summary": summary
        }
