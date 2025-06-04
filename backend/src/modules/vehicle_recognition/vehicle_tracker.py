"""
Vehicle Tracker module.
Tracks vehicles across frames and manages vehicle state.
"""
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import uuid

from src.config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class VehicleTracker:
    """
    Class for tracking vehicles across multiple frames.
    Maintains state information about vehicles in the scene.
    """
    
    def __init__(self, max_tracking_time: int = 60):
        """
        Initialize the vehicle tracker.
        
        Args:
            max_tracking_time: Maximum time in seconds to track a vehicle before removing it
        """
        # Dictionary to store vehicle tracking data
        # Key: license plate, Value: tracking data
        self.tracked_vehicles = {}
        
        # Maximum time to track a vehicle (seconds)
        self.max_tracking_time = max_tracking_time
        
        logger.info("VehicleTracker initialized")
    
    def update(self, license_plate: str, location: str) -> Dict[str, Any]:
        """
        Update the tracker with a new vehicle detection.
        
        Args:
            license_plate: License plate text
            location: Current location
            
        Returns:
            Dict[str, Any]: Updated tracking data
        """
        current_time = datetime.now()
        
        # Check if vehicle is already being tracked
        if license_plate in self.tracked_vehicles:
            # Update existing tracking data
            data = self.tracked_vehicles[license_plate]
            data["last_seen_time"] = current_time
            data["last_seen_location"] = location
            data["detections"] += 1
            
            # Calculate time since first seen
            time_diff = (current_time - data["first_seen_time"]).total_seconds()
            data["tracking_duration"] = time_diff
            
            logger.info(f"Updated tracking for vehicle {license_plate} at {location}")
        else:
            # Create new tracking data
            data = {
                "license_plate": license_plate,
                "first_seen_time": current_time,
                "last_seen_time": current_time,
                "first_seen_location": location,
                "last_seen_location": location,
                "detections": 1,
                "tracking_duration": 0.0,
                "tracking_id": str(uuid.uuid4())
            }
            self.tracked_vehicles[license_plate] = data
            
            logger.info(f"Started tracking vehicle {license_plate} at {location}")
        
        # Clean up old tracking data
        self._cleanup()
        
        return data
    
    def get_tracking_data(self, license_plate: str) -> Optional[Dict[str, Any]]:
        """
        Get tracking data for a specific vehicle.
        
        Args:
            license_plate: License plate text
            
        Returns:
            Optional[Dict[str, Any]]: Tracking data if found, None otherwise
        """
        return self.tracked_vehicles.get(license_plate)
    
    def get_all_vehicles(self) -> List[Dict[str, Any]]:
        """
        Get tracking data for all vehicles.
        
        Returns:
            List[Dict[str, Any]]: List of tracking data
        """
        return list(self.tracked_vehicles.values())
    
    def _cleanup(self) -> None:
        """
        Remove vehicles that haven't been seen for a while.
        """
        current_time = datetime.now()
        expired_time = current_time - timedelta(seconds=self.max_tracking_time)
        
        # Identify expired vehicles
        expired_plates = [
            plate for plate, data in self.tracked_vehicles.items()
            if data["last_seen_time"] < expired_time
        ]
        
        # Remove expired vehicles
        for plate in expired_plates:
            logger.info(f"Removing stale tracking data for vehicle {plate}")
            del self.tracked_vehicles[plate]
        
        if expired_plates:
            logger.info(f"Cleaned up {len(expired_plates)} expired vehicle(s)")
    
    def is_vehicle_present(self, license_plate: str) -> bool:
        """
        Check if a vehicle is currently being tracked.
        
        Args:
            license_plate: License plate text
            
        Returns:
            bool: True if vehicle is being tracked, False otherwise
        """
        # Update tracking data to remove expired vehicles
        self._cleanup()
        
        # Check if license plate is in tracked vehicles
        return license_plate in self.tracked_vehicles