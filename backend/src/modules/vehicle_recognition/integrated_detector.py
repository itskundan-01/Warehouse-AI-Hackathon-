#!/usr/bin/env python3
"""
Integrated License Plate Detection System
Replaces simulation methods with actual YOLOv8 + EasyOCR detection.
"""

import cv2
import numpy as np
import os
import ssl
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Fix SSL certificate issues for EasyOCR model downloads
ssl._create_default_https_context = ssl._create_unverified_context

from ultralytics import YOLO
import easyocr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Data class for license plate detection result"""
    plate_text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    vehicle_type: str
    vehicle_confidence: float
    quality_score: float

class IntegratedLicensePlateDetector:
    """
    Integrated license plate detector using YOLOv8 + EasyOCR.
    Replaces simulation methods with actual detection.
    """
    
    def __init__(self, 
                 yolo_model_path: str = "yolov8n.pt",
                 confidence_threshold: float = 0.25,
                 ocr_languages: List[str] = ['en']):
        """
        Initialize the integrated detector.
        
        Args:
            yolo_model_path: Path to YOLO model or model name
            confidence_threshold: Minimum confidence for detections
            ocr_languages: Languages for OCR processing
        """
        self.confidence_threshold = confidence_threshold
        self.ocr_languages = ocr_languages
        
        # Initialize YOLO model
        try:
            logger.info(f"Loading YOLO model: {yolo_model_path}")
            self.yolo_model = YOLO(yolo_model_path)
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
        
        # Initialize EasyOCR reader
        try:
            logger.info(f"Initializing EasyOCR with languages: {ocr_languages}")
            self.ocr_reader = easyocr.Reader(ocr_languages, gpu=True)
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            # Fallback to CPU
            try:
                self.ocr_reader = easyocr.Reader(ocr_languages, gpu=False)
                logger.info("EasyOCR initialized with CPU fallback")
            except Exception as e2:
                logger.error(f"Failed to initialize EasyOCR even with CPU: {e2}")
                raise
        
        # License plate patterns for validation
        self.plate_patterns = [
            r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$',  # Standard Indian format: AP39U3451
            r'^[A-Z]{2}\d{2}[A-Z]\d{4}$',       # Alternative format
            r'^[A-Z]{3}\d{4}$',                 # 3 letters + 4 digits
            r'^[A-Z]{2}\d{4}$',                 # 2 letters + 4 digits
            r'^[A-Z]{1}\d{2}[A-Z]{2}\d{4}$',   # Alternative pattern
        ]
        
        logger.info("Integrated License Plate Detector initialized")
    
    def detect(self, image_path: str) -> Optional[Dict]:
        """
        Detect license plate from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Detection result dict or None if no plate detected
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return None
        
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Detect using YOLO
            results = self.yolo_model(image, conf=self.confidence_threshold)
            
            best_detection = None
            best_score = 0
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class and confidence
                        cls = int(box.cls)
                        conf = float(box.conf)
                        
                        # Check if it's a vehicle (car, truck, bus, etc.)
                        vehicle_classes = [2, 3, 5, 7]  # COCO classes for vehicles
                        
                        if cls in vehicle_classes and conf > self.confidence_threshold:
                            # Get bounding box
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            # Extract vehicle region
                            vehicle_region = image[y1:y2, x1:x2]
                            
                            # Try to find license plate in vehicle region
                            plate_result = self._detect_plate_in_vehicle(vehicle_region, (x1, y1))
                            
                            if plate_result:
                                quality_score = self._calculate_quality_score(
                                    plate_result['plate_text'], 
                                    plate_result['confidence']
                                )
                                
                                if quality_score > best_score:
                                    best_score = quality_score
                                    best_detection = {
                                        'plate_text': plate_result['plate_text'],
                                        'confidence': plate_result['confidence'],
                                        'bbox': plate_result['bbox'],
                                        'vehicle_type': self._get_vehicle_type(cls),
                                        'vehicle_confidence': conf,
                                        'quality_score': quality_score
                                    }
            
            # If no vehicle detected, try direct plate detection on whole image
            if best_detection is None:
                plate_result = self._detect_plate_in_vehicle(image, (0, 0))
                if plate_result:
                    quality_score = self._calculate_quality_score(
                        plate_result['plate_text'], 
                        plate_result['confidence']
                    )
                    best_detection = {
                        'plate_text': plate_result['plate_text'],
                        'confidence': plate_result['confidence'],
                        'bbox': plate_result['bbox'],
                        'vehicle_type': 'unknown',
                        'vehicle_confidence': 0.5,
                        'quality_score': quality_score
                    }
            
            return best_detection
            
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return None
    
    def _detect_plate_in_vehicle(self, vehicle_image: np.ndarray, offset: Tuple[int, int]) -> Optional[Dict]:
        """
        Detect license plate within a vehicle region.
        
        Args:
            vehicle_image: Vehicle image region
            offset: Offset coordinates (x, y) for absolute positioning
            
        Returns:
            Plate detection result or None
        """
        try:
            # Multiple preprocessing approaches
            preprocessed_images = self._preprocess_for_ocr(vehicle_image)
            
            best_result = None
            best_score = 0
            
            for preprocessed in preprocessed_images:
                # Run OCR on preprocessed image
                ocr_results = self.ocr_reader.readtext(preprocessed)
                
                if ocr_results:
                    # Combine and filter OCR results
                    combined_text = self._combine_text_fragments(ocr_results)
                    
                    if combined_text:
                        # Validate license plate pattern
                        validated_text = self._validate_license_plate(combined_text)
                        
                        if validated_text:
                            # Calculate confidence from OCR results
                            avg_confidence = np.mean([result[2] for result in ocr_results])
                            
                            quality_score = self._calculate_quality_score(validated_text, avg_confidence)
                            
                            if quality_score > best_score:
                                best_score = quality_score
                                
                                # Get bounding box from OCR results
                                bbox = self._get_combined_bbox(ocr_results, offset)
                                
                                best_result = {
                                    'plate_text': validated_text,
                                    'confidence': avg_confidence,
                                    'bbox': bbox
                                }
            
            return best_result
            
        except Exception as e:
            logger.error(f"Error detecting plate in vehicle: {e}")
            return None
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Apply multiple preprocessing techniques for better OCR.
        
        Args:
            image: Input image
            
        Returns:
            List of preprocessed images
        """
        preprocessed = []
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 1. Original grayscale
        preprocessed.append(gray)
        
        # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        clahe_img = clahe.apply(gray)
        preprocessed.append(clahe_img)
        
        # 3. Binary threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        preprocessed.append(binary)
        
        # 4. Adaptive threshold
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        preprocessed.append(adaptive)
        
        # 5. Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        preprocessed.append(morph)
        
        return preprocessed
    
    def _combine_text_fragments(self, ocr_results: List) -> str:
        """
        Combine OCR text fragments into coherent license plate text.
        Handles both single-line and multi-line license plates.
        
        Args:
            ocr_results: List of OCR results [(bbox, text, confidence), ...]
            
        Returns:
            Combined license plate text
        """
        if not ocr_results:
            return ""
        
        # Filter out low confidence and non-alphanumeric results
        filtered_results = []
        for bbox, text, confidence in ocr_results:
            # Clean text
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
            if len(clean_text) >= 1 and confidence > 0.25:  # Lower threshold for fragments
                filtered_results.append((bbox, clean_text, confidence))
        
        if not filtered_results:
            return ""
        
        # Try different combination strategies
        combinations = [
            # Strategy 1: Multi-line spatial combination (for 2-line plates)
            self._multiline_spatial_combination(filtered_results),
            
            # Strategy 2: Horizontal combination (for single line plates)
            self._horizontal_combination(filtered_results),
            
            # Strategy 3: Pattern-based reconstruction
            self._pattern_based_reconstruction(filtered_results),
            
            # Strategy 4: Simple concatenation by position
            self._simple_spatial_concatenation(filtered_results)
        ]
        
        # Return the best combination based on license plate patterns and length
        for combo in combinations:
            if combo and len(combo) >= 6 and self._matches_license_pattern(combo):
                return combo
        
        # If no pattern match, return the longest valid combination
        valid_combos = [combo for combo in combinations if combo and len(combo) >= 6]
        if valid_combos:
            return max(valid_combos, key=len)
        
        # Fallback to first non-empty combination
        non_empty_combos = [combo for combo in combinations if combo]
        return non_empty_combos[0] if non_empty_combos else ""
    
    def _multiline_spatial_combination(self, ocr_results: List) -> str:
        """
        Combine text fragments that are arranged in multiple lines (typical for truck plates).
        
        Args:
            ocr_results: List of OCR results
            
        Returns:
            Combined text from multi-line arrangement
        """
        if len(ocr_results) < 2:
            return ''.join([text for _, text, _ in ocr_results])
        
        # Group fragments by vertical position (y-coordinate)
        fragments_by_line = {}
        
        for bbox, text, confidence in ocr_results:
            # Get center y-coordinate
            center_y = sum([point[1] for point in bbox]) / len(bbox)
            
            # Group by approximate line (with tolerance for slight variations)
            line_found = False
            tolerance = 30  # pixels
            
            for existing_y in fragments_by_line.keys():
                if abs(center_y - existing_y) < tolerance:
                    fragments_by_line[existing_y].append((bbox, text, confidence))
                    line_found = True
                    break
            
            if not line_found:
                fragments_by_line[center_y] = [(bbox, text, confidence)]
        
        # Sort lines by y-coordinate (top to bottom)
        sorted_lines = sorted(fragments_by_line.items())
        
        # Combine fragments within each line (left to right)
        combined_lines = []
        for y_pos, line_fragments in sorted_lines:
            # Sort fragments in this line by x-coordinate (left to right)
            line_fragments.sort(key=lambda x: min([point[0] for point in x[0]]))
            
            # Combine text from this line
            line_text = ''.join([text for _, text, _ in line_fragments])
            if line_text:
                combined_lines.append(line_text)
        
        # For Indian license plates, typically:
        # Line 1: State code + District code (e.g., "AP39")
        # Line 2: Series + Number (e.g., "U3451")
        if len(combined_lines) == 2:
            # Two-line format
            return combined_lines[0] + combined_lines[1]
        elif len(combined_lines) == 3:
            # Sometimes split into 3 parts: State, District+Series, Number
            return combined_lines[0] + combined_lines[1] + combined_lines[2]
        else:
            # Single line or other format
            return ''.join(combined_lines)
    
    def _horizontal_combination(self, ocr_results: List) -> str:
        """
        Combine text fragments horizontally (left to right).
        
        Args:
            ocr_results: List of OCR results
            
        Returns:
            Horizontally combined text
        """
        # Sort by leftmost x coordinate
        sorted_results = sorted(ocr_results, key=lambda x: min([point[0] for point in x[0]]))
        
        combined_text = ""
        prev_bbox = None
        
        for bbox, text, confidence in sorted_results:
            if prev_bbox is not None:
                # Check for significant horizontal gap
                prev_right = max([point[0] for point in prev_bbox])
                curr_left = min([point[0] for point in bbox])
                
                # If there's a large gap, it might be separate elements
                gap = curr_left - prev_right
                if gap > 100:  # Large gap threshold
                    # Don't add space, but consider if this fragment belongs
                    pass
            
            combined_text += text
            prev_bbox = bbox
        
        return combined_text
    
    def _simple_spatial_concatenation(self, ocr_results: List) -> str:
        """
        Simple concatenation by spatial position.
        
        Args:
            ocr_results: List of OCR results
            
        Returns:
            Spatially concatenated text
        """
        # Sort by position: first by y (top to bottom), then by x (left to right)
        def sort_key(item):
            bbox, text, confidence = item
            center_y = sum([point[1] for point in bbox]) / len(bbox)
            center_x = sum([point[0] for point in bbox]) / len(bbox)
            return (center_y, center_x)
        
        sorted_results = sorted(ocr_results, key=sort_key)
        return ''.join([text for _, text, _ in sorted_results])
    
    def _spatial_text_combination(self, ocr_results: List) -> str:
        """
        Combine text fragments using spatial relationships.
        """
        if not ocr_results:
            return ""
        
        combined_text = ""
        prev_bbox = None
        
        for bbox, text, confidence in ocr_results:
            if prev_bbox is not None:
                # Check for overlap or proximity
                prev_right = prev_bbox[1][0]  # Right edge of previous bbox
                curr_left = bbox[0][0]        # Left edge of current bbox
                
                # If there's significant overlap, merge more carefully
                if curr_left < prev_right:
                    # Handle overlap by taking the higher confidence text
                    overlap_ratio = (prev_right - curr_left) / max(prev_right - prev_bbox[0][0], curr_left - bbox[0][0])
                    if overlap_ratio > 0.3:  # Significant overlap
                        # Take the text with higher confidence
                        continue  # Skip this fragment if it overlaps significantly
            
            combined_text += text
            prev_bbox = bbox
        
        return combined_text
    
    def _pattern_based_reconstruction(self, ocr_results: List) -> str:
        """
        Reconstruct license plate text based on known patterns.
        """
        all_text = ''.join([text for _, text, _ in ocr_results])
        
        # Try to reconstruct common Indian license plate patterns
        # Pattern: 2 letters + 2 digits + 1-2 letters + 4 digits
        
        letters = re.findall(r'[A-Z]+', all_text)
        numbers = re.findall(r'\d+', all_text)
        
        if len(letters) >= 2 and len(numbers) >= 2:
            # Try to construct: LL##L####
            state_code = letters[0][:2] if len(letters[0]) >= 2 else letters[0]
            district_code = numbers[0][:2] if len(numbers[0]) >= 2 else numbers[0]
            series = letters[1][:2] if len(letters[1]) >= 1 else (letters[2][:1] if len(letters) > 2 else "")
            plate_number = numbers[-1][:4] if len(numbers[-1]) >= 4 else numbers[-1]
            
            # Pad if necessary
            if len(state_code) < 2 and len(letters) > 1:
                state_code += letters[1][:2-len(state_code)]
            
            reconstructed = f"{state_code}{district_code}{series}{plate_number}"
            if len(reconstructed) >= 8:
                return reconstructed
        
        return all_text
    
    def _get_combined_bbox(self, ocr_results: List, offset: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Get combined bounding box from OCR results.
        
        Args:
            ocr_results: List of OCR results
            offset: Offset coordinates
            
        Returns:
            Combined bounding box (x1, y1, x2, y2)
        """
        if not ocr_results:
            return (0, 0, 0, 0)
        
        min_x = float('inf')
        min_y = float('inf')
        max_x = 0
        max_y = 0
        
        for bbox, _, _ in ocr_results:
            for point in bbox:
                x, y = point
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        
        # Apply offset for absolute coordinates
        return (
            int(min_x + offset[0]),
            int(min_y + offset[1]),
            int(max_x + offset[0]),
            int(max_y + offset[1])
        )
    
    def _validate_license_plate(self, text: str) -> str:
        """
        Validate and clean license plate text.
        
        Args:
            text: Raw license plate text
            
        Returns:
            Validated license plate text or empty string
        """
        if not text:
            return ""
        
        # Clean the text
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Apply character corrections for common OCR mistakes
        clean_text = self._apply_character_corrections(clean_text)
        
        # Check length
        if len(clean_text) < 6 or len(clean_text) > 12:
            return ""
        
        # Check against patterns
        for pattern in self.plate_patterns:
            if re.match(pattern, clean_text):
                return clean_text
        
        # If no exact pattern match, apply heuristic validation
        if self._heuristic_validation(clean_text):
            return clean_text
        
        return ""
    
    def _apply_character_corrections(self, text: str) -> str:
        """
        Apply common OCR character corrections for license plates.
        
        Args:
            text: Input text with potential OCR errors
            
        Returns:
            Corrected text
        """
        # Common OCR mistakes and their corrections
        corrections = {
            # Number-to-letter corrections (common at start of plates)
            '6': 'G',  # 6 -> G (especially at beginning)
            '0': 'O',  # 0 -> O (in letter positions)
            '1': 'I',  # 1 -> I (in letter positions)
            '5': 'S',  # 5 -> S (in letter positions)
            '8': 'B',  # 8 -> B (in letter positions)
            '3': 'B',  # 3 -> B (sometimes)
            '9': 'P',  # 9 -> P (sometimes at start)
            '4': 'A',  # 4 -> A (sometimes)
            
            # Letter-to-number corrections (for number positions)
            # These will be applied contextually
        }
        
        # Additional specific corrections for common Indian state codes
        state_corrections = {
            'FV': 'AP',  # Common misread of AP (Andhra Pradesh)
            'AP39': 'AP39',  # Keep correct readings
            '6J': 'GJ',   # Gujarat misread
            'TN': 'TN',   # Tamil Nadu
            'KA': 'KA',   # Karnataka
            'MH': 'MH',   # Maharashtra
        }
        
        corrected_text = text
        
        # Apply state code corrections first
        for incorrect, correct in state_corrections.items():
            if corrected_text.startswith(incorrect):
                corrected_text = correct + corrected_text[len(incorrect):]
                break
        
        # Apply character corrections based on position context
        # Indian license plates typically start with 2 letters
        if len(text) >= 2:
            # First two characters should likely be letters
            for i in range(min(2, len(text))):
                char = text[i]
                if char in corrections:
                    # Apply correction for likely letter positions
                    corrected_text = corrected_text[:i] + corrections[char] + corrected_text[i+1:]
        
        # For positions 2-3 (district code), prefer numbers
        if len(text) >= 4:
            for i in range(2, min(4, len(text))):
                char = text[i]
                # Convert letters that look like numbers back to numbers
                letter_to_number = {'O': '0', 'I': '1', 'L': '1', 'S': '5', 'B': '8', 'G': '6'}
                if char in letter_to_number:
                    corrected_text = corrected_text[:i] + letter_to_number[char] + corrected_text[i+1:]
        
        # Special handling for common patterns
        # Pattern: LLNNLNNNN (e.g., AP39U3451)
        if len(corrected_text) >= 9:
            # Check if position 4 (series letter) makes sense
            if corrected_text[4].isdigit():
                # Try to convert to a letter if it looks wrong
                digit_to_letter = {'1': 'I', '3': 'B', '5': 'S', '6': 'G', '0': 'O'}
                if corrected_text[4] in digit_to_letter:
                    corrected_text = corrected_text[:4] + digit_to_letter[corrected_text[4]] + corrected_text[5:]
        
        return corrected_text
    
    def _heuristic_validation(self, text: str) -> bool:
        """
        Apply heuristic validation rules for license plates.
        
        Args:
            text: License plate text
            
        Returns:
            True if text passes heuristic validation
        """
        # Must contain both letters and numbers
        has_letters = bool(re.search(r'[A-Z]', text))
        has_numbers = bool(re.search(r'\d', text))
        
        if not (has_letters and has_numbers):
            return False
        
        # Should not be all letters or all numbers
        if text.isalpha() or text.isdigit():
            return False
        
        # Should have reasonable length
        if len(text) < 6 or len(text) > 12:
            return False
        
        return True
    
    def _matches_license_pattern(self, text: str) -> bool:
        """Check if text matches any license plate pattern."""
        for pattern in self.plate_patterns:
            if re.match(pattern, text):
                return True
        return False
    
    def _calculate_quality_score(self, plate_text: str, confidence: float) -> float:
        """
        Calculate quality score for detection.
        
        Args:
            plate_text: Detected license plate text
            confidence: OCR confidence
            
        Returns:
            Quality score (0-100)
        """
        score = 0
        
        # Base score from confidence
        score += confidence * 40
        
        # Length score
        if 8 <= len(plate_text) <= 10:
            score += 20
        elif 6 <= len(plate_text) <= 12:
            score += 15
        else:
            score += 5
        
        # Pattern matching score
        if self._matches_license_pattern(plate_text):
            score += 30
        elif self._heuristic_validation(plate_text):
            score += 20
        else:
            score += 5
        
        # Character composition score
        letter_count = len(re.findall(r'[A-Z]', plate_text))
        digit_count = len(re.findall(r'\d', plate_text))
        
        if letter_count >= 2 and digit_count >= 4:
            score += 10
        elif letter_count >= 1 and digit_count >= 2:
            score += 5
        
        return min(score, 100)
    
    def _get_vehicle_type(self, class_id: int) -> str:
        """
        Get vehicle type from COCO class ID.
        
        Args:
            class_id: COCO class ID
            
        Returns:
            Vehicle type string
        """
        vehicle_types = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        return vehicle_types.get(class_id, 'vehicle')

    def detect_from_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect license plates from a video frame (numpy array).
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            List of detection results
        """
        try:
            # Detect using YOLO
            results = self.yolo_model(frame, conf=self.confidence_threshold)
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get class and confidence
                        cls = int(box.cls)
                        conf = float(box.conf)
                        
                        # Check if it's a vehicle (car, truck, bus, etc.)
                        vehicle_classes = [2, 3, 5, 7]  # COCO classes for vehicles
                        
                        if cls in vehicle_classes and conf > self.confidence_threshold:
                            # Get bounding box
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            
                            # Extract vehicle region
                            vehicle_region = frame[y1:y2, x1:x2]
                            
                            # Try to find license plate in vehicle region
                            plate_result = self._detect_plate_in_vehicle(vehicle_region, (x1, y1))
                            
                            if plate_result:
                                quality_score = self._calculate_quality_score(
                                    plate_result['plate_text'], 
                                    plate_result['confidence']
                                )
                                
                                detection = {
                                    'plate_text': plate_result['plate_text'],
                                    'confidence': plate_result['confidence'],
                                    'bbox': plate_result['bbox'],
                                    'vehicle_type': self._get_vehicle_type(cls),
                                    'vehicle_confidence': conf,
                                    'quality_score': quality_score
                                }
                                detections.append(detection)
            
            # If no vehicle detected, try direct plate detection on whole frame
            if not detections:
                plate_result = self._detect_plate_in_vehicle(frame, (0, 0))
                if plate_result:
                    quality_score = self._calculate_quality_score(
                        plate_result['plate_text'], 
                        plate_result['confidence']
                    )
                    detection = {
                        'plate_text': plate_result['plate_text'],
                        'confidence': plate_result['confidence'],
                        'bbox': plate_result['bbox'],
                        'vehicle_type': 'unknown',
                        'vehicle_confidence': 0.5,
                        'quality_score': quality_score
                    }
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error during frame detection: {e}")
            return []

# Compatibility class that mimics the original LicensePlateDetector interface
class LicensePlateDetector:
    """
    Compatibility wrapper for the integrated detector.
    Maintains the same interface as the original detector.
    """
    
    def __init__(self, confidence_threshold: float = 0.5, model_path: Optional[str] = None):
        """Initialize with integrated detector."""
        self.detector = IntegratedLicensePlateDetector(
            confidence_threshold=confidence_threshold
        )
        logger.info("License Plate Detector (Integrated) initialized")
    
    def detect(self, image_path: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect license plate and return bounding box.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Bounding box tuple (x1, y1, x2, y2) or None
        """
        result = self.detector.detect(image_path)
        if result:
            return result['bbox']
        return None

# Compatibility class for OCR
class LicensePlateOCR:
    """
    Compatibility wrapper for the integrated detector's OCR.
    Maintains the same interface as the original OCR.
    """
    
    def __init__(self, languages: List[str] = ['en'], use_gpu: bool = True):
        """Initialize with integrated detector."""
        self.detector = IntegratedLicensePlateDetector(
            ocr_languages=languages
        )
        logger.info("License Plate OCR (Integrated) initialized")
    
    def extract_text(self, image_path: str, bbox: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Extract text from license plate.
        
        Args:
            image_path: Path to image file
            bbox: Bounding box (ignored, full detection used)
            
        Returns:
            Extracted license plate text
        """
        result = self.detector.detect(image_path)
        if result:
            return result['plate_text']
        return ""
    
    def extract_text_from_detection(self, frame: np.ndarray, detection: Dict) -> str:
        """
        Extract text from a detection result on a video frame.
        
        Args:
            frame: Video frame as numpy array
            detection: Detection dictionary with bbox and other info
            
        Returns:
            Extracted license plate text
        """
        try:
            if 'bbox' in detection:
                # Extract region from frame using bbox
                x, y, w, h = detection['bbox']
                plate_region = frame[y:y+h, x:x+w]
                
                # Use EasyOCR directly on the extracted region
                ocr_results = self.detector.ocr_reader.readtext(plate_region)
                
                if ocr_results:
                    # Get the text with highest confidence
                    best_result = max(ocr_results, key=lambda x: x[2])
                    text = best_result[1].strip().upper()
                    
                    # Apply basic validation and cleaning
                    text = self.detector._validate_license_plate(text)
                    return text
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting text from detection: {e}")
            return ""
