#!/usr/bin/env python3
"""
Enhanced License Plate Detection System with LLM Integration
Includes proper cropping and LLM-based text recognition for improved accuracy.
"""

import cv2
import numpy as np
import os
import ssl
import time
import base64
import requests
import json
from datetime import datetime
from pathlib import Path
import re
import logging
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass

# Fix SSL certificate issues for EasyOCR model downloads
ssl._create_default_https_context = ssl._create_unverified_context

from ultralytics import YOLO
import easyocr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EnhancedDetectionResult:
    """Enhanced data class for license plate detection result"""
    plate_text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    vehicle_type: str
    vehicle_confidence: float
    quality_score: float
    detection_method: str  # 'ocr', 'llm', or 'hybrid'
    cropped_plate_path: Optional[str] = None

class EnhancedLicensePlateDetector:
    """
    Enhanced license plate detector with LLM integration and improved cropping.
    """
    
    def __init__(self, 
                 yolo_model_path: str = "yolov8n.pt",
                 confidence_threshold: float = 0.25,
                 ocr_languages: List[str] = ['en'],
                 use_llm: bool = True,
                 llm_api_key: Optional[str] = None,
                 save_crops: bool = True):
        """
        Initialize the enhanced detector.
        
        Args:
            yolo_model_path: Path to YOLO model or model name
            confidence_threshold: Minimum confidence for detections
            ocr_languages: Languages for OCR processing
            use_llm: Whether to use LLM for text recognition
            llm_api_key: API key for LLM service (OpenAI)
            save_crops: Whether to save cropped license plate images
        """
        self.confidence_threshold = confidence_threshold
        self.ocr_languages = ocr_languages
        self.use_llm = use_llm
        self.llm_api_key = llm_api_key
        self.save_crops = save_crops
        
        # Create crops directory
        self.crops_dir = Path("license_plate_crops")
        self.crops_dir.mkdir(exist_ok=True)
        
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
            r'^[A-Z]\d{3}[A-Z]{2}\d{3}$',      # Different format
        ]
        
        logger.info("Enhanced License Plate Detector initialized")
    
    def detect(self, image_path: str) -> Optional[Dict]:
        """
        Enhanced detection with proper cropping and LLM integration.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Enhanced detection result dict or None if no plate detected
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
            
            # Step 1: Detect vehicles using YOLO
            vehicles = self._detect_vehicles(image)
            
            if not vehicles:
                logger.info("No vehicles detected, trying full image analysis")
                vehicles = [{'bbox': (0, 0, image.shape[1], image.shape[0]), 'type': 'unknown', 'conf': 0.5}]
            
            best_detection = None
            best_score = 0
            
            # Step 2: For each vehicle, find and crop license plate regions
            for vehicle in vehicles:
                x1, y1, x2, y2 = vehicle['bbox']
                vehicle_region = image[y1:y2, x1:x2]
                
                # Step 3: Detect license plate regions within vehicle
                plate_regions = self._detect_license_plate_regions(vehicle_region)
                
                for plate_region in plate_regions:
                    # Step 4: Crop the license plate
                    cropped_plate = self._crop_license_plate(vehicle_region, plate_region)
                    
                    if cropped_plate is None:
                        continue
                    
                    # Step 5: Save cropped plate if enabled
                    crop_path = None
                    if self.save_crops:
                        crop_path = self._save_cropped_plate(cropped_plate, image_path)
                    
                    # Step 6: Try multiple recognition methods
                    detection_results = []
                    
                    # Method 1: Enhanced OCR with preprocessing
                    ocr_result = self._enhanced_ocr_recognition(cropped_plate)
                    if ocr_result:
                        detection_results.append({**ocr_result, 'method': 'ocr'})
                    
                    # Method 2: LLM-based recognition (if enabled)
                    if self.use_llm and self.llm_api_key:
                        llm_result = self._llm_recognition(cropped_plate)
                        if llm_result:
                            detection_results.append({**llm_result, 'method': 'llm'})
                    
                    # Step 7: Select best result
                    for result in detection_results:
                        quality_score = self._calculate_enhanced_quality_score(
                            result['plate_text'], 
                            result['confidence'],
                            result['method']
                        )
                        
                        if quality_score > best_score:
                            best_score = quality_score
                            
                            # Adjust bbox to absolute coordinates
                            px1, py1, px2, py2 = plate_region
                            abs_bbox = (x1 + px1, y1 + py1, x1 + px2, y1 + py2)
                            
                            best_detection = {
                                'plate_text': result['plate_text'],
                                'confidence': result['confidence'],
                                'bbox': abs_bbox,
                                'vehicle_type': vehicle['type'],
                                'vehicle_confidence': vehicle['conf'],
                                'quality_score': quality_score,
                                'detection_method': result['method'],
                                'cropped_plate_path': crop_path
                            }
            
            return best_detection
            
        except Exception as e:
            logger.error(f"Error during enhanced detection: {e}")
            return None
    
    def _detect_vehicles(self, image: np.ndarray) -> List[Dict]:
        """Detect vehicles in the image using YOLO."""
        vehicles = []
        
        results = self.yolo_model(image, conf=self.confidence_threshold)
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls)
                    conf = float(box.conf)
                    
                    # Vehicle classes in COCO dataset
                    vehicle_classes = {
                        2: 'car',
                        3: 'motorcycle', 
                        5: 'bus',
                        7: 'truck'
                    }
                    
                    if cls in vehicle_classes and conf > self.confidence_threshold:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        vehicles.append({
                            'bbox': (x1, y1, x2, y2),
                            'type': vehicle_classes[cls],
                            'conf': conf
                        })
        
        return vehicles
    
    def _detect_license_plate_regions(self, vehicle_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect potential license plate regions within vehicle image.
        Uses contour detection and aspect ratio filtering.
        """
        regions = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(vehicle_image, cv2.COLOR_BGR2GRAY)
            
            # Apply various edge detection methods
            methods = [
                # Method 1: Sobel edge detection
                cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3),
                # Method 2: Canny edge detection
                cv2.Canny(gray, 50, 150),
                # Method 3: Adaptive threshold
                cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            ]
            
            for edges in methods:
                edges = np.uint8(np.absolute(edges))
                
                # Find contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by aspect ratio and size (typical license plate dimensions)
                    aspect_ratio = w / h if h > 0 else 0
                    area = w * h
                    
                    # License plates typically have aspect ratio between 2:1 and 6:1
                    if (2.0 <= aspect_ratio <= 6.0 and 
                        area > 500 and  # Minimum area
                        w > 60 and h > 15):  # Minimum dimensions
                        
                        # Add some padding
                        padding = 10
                        x1 = max(0, x - padding)
                        y1 = max(0, y - padding)
                        x2 = min(vehicle_image.shape[1], x + w + padding)
                        y2 = min(vehicle_image.shape[0], y + h + padding)
                        
                        regions.append((x1, y1, x2, y2))
            
            # Remove duplicate regions
            regions = self._remove_duplicate_regions(regions)
            
        except Exception as e:
            logger.error(f"Error detecting license plate regions: {e}")
        
        return regions
    
    def _crop_license_plate(self, vehicle_image: np.ndarray, region: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Crop the license plate region from vehicle image."""
        try:
            x1, y1, x2, y2 = region
            cropped = vehicle_image[y1:y2, x1:x2]
            
            # Validate crop
            if cropped.shape[0] < 10 or cropped.shape[1] < 30:
                return None
            
            return cropped
            
        except Exception as e:
            logger.error(f"Error cropping license plate: {e}")
            return None
    
    def _save_cropped_plate(self, cropped_plate: np.ndarray, original_image_path: str) -> str:
        """Save cropped license plate image."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            original_name = Path(original_image_path).stem
            crop_filename = f"crop_{original_name}_{timestamp}.jpg"
            crop_path = self.crops_dir / crop_filename
            
            cv2.imwrite(str(crop_path), cropped_plate)
            logger.info(f"Saved cropped plate: {crop_path}")
            
            return str(crop_path)
            
        except Exception as e:
            logger.error(f"Error saving cropped plate: {e}")
            return None
    
    def _enhanced_ocr_recognition(self, cropped_plate: np.ndarray) -> Optional[Dict]:
        """Enhanced OCR recognition with multiple preprocessing methods."""
        try:
            # Apply multiple preprocessing methods
            preprocessed_images = self._enhanced_preprocessing(cropped_plate)
            
            best_result = None
            best_confidence = 0
            
            for processed_img in preprocessed_images:
                # Use EasyOCR
                results = self.ocr_reader.readtext(processed_img)
                
                for (bbox, text, confidence) in results:
                    cleaned_text = self._clean_plate_text(text)
                    
                    if cleaned_text and len(cleaned_text) >= 6:
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_result = {
                                'plate_text': cleaned_text,
                                'confidence': confidence
                            }
            
            return best_result
            
        except Exception as e:
            logger.error(f"Error in enhanced OCR recognition: {e}")
            return None
    
    def _llm_recognition(self, cropped_plate: np.ndarray) -> Optional[Dict]:
        """Use LLM (OpenAI GPT-4 Vision) for license plate text recognition."""
        try:
            if not self.llm_api_key:
                return None
            
            # Convert image to base64
            _, buffer = cv2.imencode('.jpg', cropped_plate)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare the request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.llm_api_key}"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "This is a cropped image of a license plate. Please extract ONLY the license plate text/number. Return only the alphanumeric characters you see, with no spaces, punctuation, or explanations. If you cannot clearly see the text, return 'UNCLEAR'."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 20
            }
            
            # Make API request
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result['choices'][0]['message']['content'].strip().upper()
                
                if text and text != 'UNCLEAR' and len(text) >= 6:
                    cleaned_text = self._clean_plate_text(text)
                    if cleaned_text:
                        return {
                            'plate_text': cleaned_text,
                            'confidence': 0.9  # High confidence for LLM
                        }
            else:
                logger.error(f"LLM API error: {response.status_code} - {response.text}")
            
        except Exception as e:
            logger.error(f"Error in LLM recognition: {e}")
        
        return None
    
    def _enhanced_preprocessing(self, image: np.ndarray) -> List[np.ndarray]:
        """Enhanced preprocessing methods for better OCR."""
        processed_images = []
        
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Method 1: Original
            processed_images.append(gray)
            
            # Method 2: Gaussian blur + threshold
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(thresh1)
            
            # Method 3: CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            clahe_img = clahe.apply(gray)
            processed_images.append(clahe_img)
            
            # Method 4: Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            processed_images.append(morph)
            
            # Method 5: Adaptive threshold
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            processed_images.append(adaptive)
            
            # Method 6: Upscale for better OCR
            upscaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            processed_images.append(upscaled)
            
        except Exception as e:
            logger.error(f"Error in enhanced preprocessing: {e}")
        
        return processed_images
    
    def _clean_plate_text(self, text: str) -> str:
        """Enhanced text cleaning for license plates."""
        if not text:
            return ""
        
        # Remove unwanted characters
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Common OCR corrections
        corrections = {
            'O': '0',  # Letter O to number 0
            'I': '1',  # Letter I to number 1
            'S': '5',  # Letter S to number 5
            'G': '6',  # Letter G to number 6
            'B': '8',  # Letter B to number 8
            'Z': '2',  # Letter Z to number 2
        }
        
        # Apply corrections based on position context
        result = ""
        for i, char in enumerate(cleaned):
            if char in corrections:
                # Apply smart corrections based on license plate patterns
                if i < 2:  # First two characters are usually letters
                    result += char
                elif i >= len(cleaned) - 4:  # Last four are usually numbers
                    result += corrections.get(char, char)
                else:
                    result += char
            else:
                result += char
        
        return result
    
    def _calculate_enhanced_quality_score(self, plate_text: str, confidence: float, method: str) -> float:
        """Calculate enhanced quality score including method bonus."""
        if not plate_text:
            return 0
        
        base_score = confidence * 100
        
        # Pattern validation bonus
        pattern_bonus = 0
        for pattern in self.plate_patterns:
            if re.match(pattern, plate_text):
                pattern_bonus = 20
                break
        
        # Length bonus
        length_bonus = min(len(plate_text) * 2, 20)
        
        # Method bonus
        method_bonus = 0
        if method == 'llm':
            method_bonus = 15  # LLM gets bonus for better accuracy
        elif method == 'ocr':
            method_bonus = 5
        
        total_score = base_score + pattern_bonus + length_bonus + method_bonus
        return min(total_score, 100)
    
    def _remove_duplicate_regions(self, regions: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Remove duplicate or overlapping regions."""
        if not regions:
            return []
        
        # Sort by area (largest first)
        regions = sorted(regions, key=lambda r: (r[2]-r[0])*(r[3]-r[1]), reverse=True)
        
        unique_regions = []
        for region in regions:
            is_duplicate = False
            for existing in unique_regions:
                if self._regions_overlap(region, existing, threshold=0.5):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_regions.append(region)
        
        return unique_regions
    
    def _regions_overlap(self, region1: Tuple[int, int, int, int], region2: Tuple[int, int, int, int], threshold: float = 0.5) -> bool:
        """Check if two regions overlap significantly."""
        x1_1, y1_1, x2_1, y2_1 = region1
        x1_2, y1_2, x2_2, y2_2 = region2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return False
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        overlap_ratio = intersection_area / min(area1, area2)
        return overlap_ratio > threshold


# Compatibility wrapper for existing API
class LicensePlateDetector:
    """Compatibility wrapper for existing API"""
    
    def __init__(self):
        self.detector = EnhancedLicensePlateDetector(use_llm=False)  # Default without LLM
    
    def detect_license_plate(self, image_path: str) -> Optional[Dict]:
        """Detect license plate - compatibility method"""
        result = self.detector.detect(image_path)
        if result:
            return {
                'plate_number': result['plate_text'],
                'confidence': result['confidence'],
                'bounding_box': result['bbox']
            }
        return None


class LicensePlateOCR:
    """Compatibility wrapper for OCR functionality"""
    
    def __init__(self):
        self.detector = EnhancedLicensePlateDetector(use_llm=False)
    
    def extract_text(self, image_path: str) -> str:
        """Extract text - compatibility method"""
        result = self.detector.detect(image_path)
        return result['plate_text'] if result else ""
