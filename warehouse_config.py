#!/usr/bin/env python3
"""
Configuration and settings for the Warehouse AI System
"""

import os
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class WarehouseConfig:
    """Production configuration for AP Civil Supply warehouses"""
    
    # === INPUT SETTINGS ===
    # Frame processing
    FRAME_SAMPLING_RATE: int = 2  # Process every 2nd frame (reduces load)
    MAX_FPS: int = 8  # Max processing rate (warehouse doesn't need high FPS)
    FRAME_BUFFER_SIZE: int = 30
    
    # Input resolution (balance between quality and performance)
    INPUT_RESOLUTION: Tuple[int, int] = (1280, 720)  # 720p - good for license plates
    AUTO_RESIZE: bool = True
    
    # === DETECTION SETTINGS ===
    # Motion detection (skip static frames)
    MOTION_THRESHOLD: float = 0.05  # Lower = more sensitive (trucks move slowly)
    
    # Vehicle detection confidence
    VEHICLE_CONFIDENCE: float = 0.7
    
    # === API SETTINGS ===
    # Gemini API configuration
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    API_RATE_LIMIT: int = 90  # Stay under 100/hour limit
    API_TIMEOUT: int = 15  # Longer timeout for warehouse internet
    
    # === STORAGE SETTINGS ===
    # Where to save detections
    OUTPUT_DIRECTORY: str = "warehouse_detections"
    SAVE_DETECTIONS: bool = True
    SAVE_FRAMES: bool = True  # Save actual frames with detections
    
    # === PERFORMANCE SETTINGS ===
    # System performance
    ENABLE_GPU: bool = False  # Most warehouse systems won't have GPU
    NUM_THREADS: int = 2  # Conservative threading
    
    # Memory management
    MAX_MEMORY_MB: int = 1024  # 1GB limit
    CLEANUP_INTERVAL: int = 300  # Clean up every 5 minutes
    
    # === WAREHOUSE SPECIFIC SETTINGS ===
    # Operating hours (24/7 but useful for logging)
    OPERATING_HOURS: Tuple[int, int] = (0, 24)  # 24/7 operation
    
    # Alert thresholds
    MAX_VEHICLES_PER_HOUR: int = 50  # Alert if too many vehicles
    MIN_CONFIDENCE_ALERT: float = 0.8  # Alert on low confidence detections
    
    # Regional settings for Indian license plates
    EXPECTED_STATES: list = None
    
    def __post_init__(self):
        if self.EXPECTED_STATES is None:
            self.EXPECTED_STATES = [
                "AP",  # Andhra Pradesh (primary)
                "TS",  # Telangana
                "KA",  # Karnataka
                "TN",  # Tamil Nadu
                "OR",  # Odisha
                "WB",  # West Bengal
            ]
    
    # License plate format validation
    PLATE_MIN_LENGTH: int = 6
    PLATE_MAX_LENGTH: int = 12
    
    @classmethod
    def for_live_stream(cls):
        """Optimized configuration for live RTSP streams"""
        config = cls()
        config.FRAME_SAMPLING_RATE = 3  # More aggressive sampling for live
        config.MAX_FPS = 5  # Lower FPS for continuous operation
        config.MOTION_THRESHOLD = 0.03  # More sensitive for slow vehicles
        return config
    
    @classmethod
    def for_video_analysis(cls):
        """Configuration optimized for video file analysis"""
        config = cls()
        config.FRAME_SAMPLING_RATE = 1  # Process more frames for accuracy
        config.MAX_FPS = 15  # Higher FPS for offline processing
        config.MOTION_THRESHOLD = 0.1  # Less sensitive for recorded video
        return config
    
    @classmethod
    def for_image_batch(cls):
        """Configuration for batch image processing"""
        config = cls()
        config.FRAME_SAMPLING_RATE = 1  # Process all images
        config.MOTION_THRESHOLD = 0.0  # No motion detection for images
        config.INPUT_RESOLUTION = (1920, 1080)  # Higher res for images
        return config

# === CAMERA PRESETS ===
WAREHOUSE_CAMERAS = {
    "main_gate": {
        "url": "rtsp://192.168.1.100:554/stream1",
        "description": "Main warehouse gate camera",
        "position": "entrance",
        "priority": "high"
    },
    "loading_dock_1": {
        "url": "rtsp://192.168.1.101:554/stream1", 
        "description": "Loading dock 1 camera",
        "position": "loading_area",
        "priority": "medium"
    },
    "loading_dock_2": {
        "url": "rtsp://192.168.1.102:554/stream1",
        "description": "Loading dock 2 camera", 
        "position": "loading_area",
        "priority": "medium"
    },
    "exit_gate": {
        "url": "rtsp://192.168.1.103:554/stream1",
        "description": "Exit gate camera",
        "position": "exit",
        "priority": "high"
    }
}

# === EXAMPLE USAGE ===
if __name__ == "__main__":
    print("🚛 Warehouse AI Configuration")
    print("=" * 40)
    
    # Live stream config
    live_config = WarehouseConfig.for_live_stream()
    print(f"Live Stream Config:")
    print(f"  - Sampling Rate: {live_config.FRAME_SAMPLING_RATE}")
    print(f"  - Max FPS: {live_config.MAX_FPS}")
    print(f"  - Motion Threshold: {live_config.MOTION_THRESHOLD}")
    print()
    
    # Video analysis config
    video_config = WarehouseConfig.for_video_analysis()
    print(f"Video Analysis Config:")
    print(f"  - Sampling Rate: {video_config.FRAME_SAMPLING_RATE}")
    print(f"  - Max FPS: {video_config.MAX_FPS}")
    print(f"  - Resolution: {video_config.INPUT_RESOLUTION}")
    print()
    
    # Available cameras
    print("Available Warehouse Cameras:")
    for name, camera in WAREHOUSE_CAMERAS.items():
        print(f"  - {name}: {camera['description']} ({camera['priority']} priority)")
