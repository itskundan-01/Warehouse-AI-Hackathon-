"""
Vehicle Recognition module for WarehouseVision AI.
"""
from src.modules.vehicle_recognition.plate_detector import LicensePlateDetector
from src.modules.vehicle_recognition.ocr import LicensePlateOCR
from src.modules.vehicle_recognition.vehicle_tracker import VehicleTracker

__all__ = ["LicensePlateDetector", "LicensePlateOCR", "VehicleTracker"]