"""
Face detection module for WarehouseVision AI.

This module uses a deep learning-based face detection model to identify and
extract faces from camera frames. It provides functionality for:
- Detecting faces in images/video frames
- Extracting facial regions with bounding boxes
- Basic pre-processing of detected faces
- Low-light enhancement for improved detection
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import os
import sys
import importlib.util

# Configure logger
logger = logging.getLogger(__name__)

# Fix for MTCNN import issues
def import_mtcnn():
    """Import MTCNN safely with proper error handling."""
    try:
        # First try normal import
        from mtcnn import MTCNN
        return MTCNN
    except ImportError as e:
        # If that fails, try to find the package in site-packages
        mtcnn_spec = importlib.util.find_spec('mtcnn')
        if mtcnn_spec:
            logger.info(f"Found MTCNN at {mtcnn_spec.origin}")
            # Try again with full path
            try:
                mtcnn_path = os.path.dirname(mtcnn_spec.origin)
                if mtcnn_path not in sys.path:
                    sys.path.append(mtcnn_path)
                from mtcnn import MTCNN
                return MTCNN
            except ImportError as e2:
                logger.error(f"Failed to import MTCNN after finding spec: {e2}")
                return None
        else:
            logger.error(f"MTCNN package not found: {e}")
            return None

class FaceDetector:
    """Face detection implementation using OpenCV's DNN module with MTCNN or RetinaFace models."""
    
    DETECTION_METHODS = ["mtcnn", "retinaface", "opencv-dnn"]
    
    def __init__(
        self,
        method: str = "opencv-dnn",
        model_path: Optional[str] = None,
        min_confidence: float = 0.7,
        enable_gpu: bool = False
    ):
        """
        Initialize face detector with specified model.
        
        Args:
            method: Detection method ('mtcnn', 'retinaface', or 'opencv-dnn')
            model_path: Path to model weights (if None, uses default)
            min_confidence: Minimum confidence threshold for detections
            enable_gpu: Whether to use GPU acceleration if available
        """
        self.method = method.lower()
        self.min_confidence = min_confidence
        self.enable_gpu = enable_gpu
        self.model = None
        self.model_path = None
        self.config_path = None
        
        if self.method not in self.DETECTION_METHODS:
            logger.warning(f"Detection method {self.method} not in {self.DETECTION_METHODS}, falling back to opencv-dnn")
            self.method = "opencv-dnn"
        
        # Default model paths
        if model_path is None:
            # Use models directory relative to project root
            models_dir = Path(__file__).parent.parent.parent.parent / "models" / "facial"
            os.makedirs(models_dir, exist_ok=True)
            
            if self.method == "opencv-dnn":
                self.model_path = str(models_dir / "opencv_face_detector.caffemodel")
                self.config_path = str(models_dir / "opencv_face_detector.prototxt")
                
                # Check if OpenCV DNN model files exist
                if not os.path.exists(self.model_path) or not os.path.exists(self.config_path):
                    # Try using a pre-downloaded ArcFace model instead if available
                    arcface_path = models_dir / "arcface_resnet100.onnx"
                    if os.path.exists(arcface_path) and os.path.getsize(arcface_path) > 1000000:
                        logger.info(f"Found ArcFace model at {arcface_path}, using MTCNN detection instead")
                        self.method = "mtcnn"
                        self.model_path = str(models_dir)
                    
            elif self.method == "retinaface":
                self.model_path = str(models_dir / "retinaface.onnx")
            elif self.method == "mtcnn":
                self.model_path = str(models_dir)  # MTCNN uses multiple models in a directory
        else:
            self.model_path = model_path
            
        # Initialize the selected detection model
        self._initialize_detector()
        logger.info(f"Face detector initialized using {self.method} method")
        
    def _initialize_detector(self):
        """Initialize the selected face detection model."""
        if self.method == "opencv-dnn":
            if not Path(self.model_path).exists() or not Path(self.config_path).exists():
                logger.warning(f"Model files not found. Using default OpenCV face detector")
                self.model = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                self.method = "haar"  # Fallback to Haar cascades
            else:
                try:
                    self.model = cv2.dnn.readNet(self.model_path, self.config_path)
                    
                    # Configure GPU if enabled - safely handle backend selection
                    if self.enable_gpu:
                        try:
                            # Try using CUDA backend first
                            self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                            self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                            logger.info("CUDA backend enabled for face detection")
                        except Exception as e1:
                            logger.warning(f"CUDA backend failed: {str(e1)}")
                            try:
                                # Try OpenVINO as a fallback
                                self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                                self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                                logger.info("Using CPU backend for face detection")
                            except Exception as e2:
                                logger.warning(f"OpenCV backend failed: {str(e2)}")
                                # If all else fails, don't set a specific backend
                                logger.info("Using default backend for face detection")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenCV DNN model: {str(e)}")
                    logger.warning("Falling back to Haar cascade face detector")
                    self.model = cv2.CascadeClassifier(
                        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                    )
                    self.method = "haar"  # Fallback to Haar cascades
                
        elif self.method == "retinaface":
            try:
                import onnxruntime
                # Create an ONNX Runtime session to run the RetinaFace model
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.enable_gpu else ['CPUExecutionProvider']
                self.model = onnxruntime.InferenceSession(self.model_path, providers=providers)
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize RetinaFace: {str(e)}")
                # Try MTCNN
                MTCNN = import_mtcnn()
                if MTCNN:
                    try:
                        # Initialize MTCNN without parameters that might not be supported
                        self.model = MTCNN()
                        self.method = "mtcnn"
                        logger.info("Switched to MTCNN for face detection")
                    except Exception as e:
                        logger.error(f"Failed to initialize MTCNN: {str(e)}")
                        # Fallback to OpenCV Haar cascades
                        self.model = cv2.CascadeClassifier(
                            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                        )
                        self.method = "haar"
                else:
                    # Fallback to OpenCV Haar cascades
                    logger.error("MTCNN package not installed. Falling back to Haar cascades")
                    self.model = cv2.CascadeClassifier(
                        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                    )
                    self.method = "haar"
                
        elif self.method == "mtcnn":
            MTCNN = import_mtcnn()
            if MTCNN:
                try:
                    # Initialize MTCNN without parameters that might not be supported
                    self.model = MTCNN()
                    logger.info("MTCNN detector initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize MTCNN: {str(e)}")
                    # Fallback to OpenCV Haar cascades
                    self.model = cv2.CascadeClassifier(
                        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                    )
                    self.method = "haar"
            else:
                logger.error("MTCNN package not installed. Falling back to Haar cascades")
                # Fallback to OpenCV Haar cascades
                self.model = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                self.method = "haar"

    def detect_faces(self, image: np.ndarray):
        """
        Detect faces in an input image.
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detected faces with their bounding boxes and confidence scores
        """
        if image is None or image.size == 0:
            logger.warning("Empty image provided to face detector")
            return []
            
        # Create a copy to avoid modifying the original
        img = image.copy()
        
        # Convert to RGB for certain models
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        faces = []
        
        try:
            # Detect faces using the appropriate method
            if self.method == "mtcnn":
                # MTCNN already returns detections with keypoints
                detections = self.model.detect_faces(rgb_img)
                
                for detection in detections:
                    confidence = detection['confidence']
                    if confidence < self.min_confidence:  # Filter by confidence
                        continue
                        
                    # MTCNN returns [x, y, width, height]
                    box = detection['box']
                    faces.append({
                        'bbox': box,  # [x, y, width, height]
                        'confidence': confidence
                    })
                    
            elif self.method == "haar":
                # Convert to grayscale for Haar cascade
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                detections = self.model.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                for (x, y, w, h) in detections:
                    faces.append({
                        'bbox': [x, y, w, h],  # [x, y, width, height]
                        'confidence': 0.9  # Haar doesn't provide confidence, use default
                    })
                    
            elif self.method == "opencv-dnn":
                # Prepare image for DNN
                blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), [104, 117, 123], False, False)
                self.model.setInput(blob)
                
                # Run forward pass
                detections = self.model.forward()
                
                height, width = img.shape[:2]
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    
                    if confidence < self.min_confidence:
                        continue
                        
                    # Compute the coordinates of the bounding box
                    x1 = int(detections[0, 0, i, 3] * width)
                    y1 = int(detections[0, 0, i, 4] * height)
                    x2 = int(detections[0, 0, i, 5] * width)
                    y2 = int(detections[0, 0, i, 6] * height)
                    
                    # Convert to [x, y, width, height] format
                    bbox = [x1, y1, x2-x1, y2-y1]
                    
                    faces.append({
                        'bbox': bbox,
                        'confidence': float(confidence)
                    })
            
            return faces
            
        except Exception as e:
            logger.error(f"Error during face detection: {str(e)}")
            return []
        
    def detect_faces_in_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces in a video frame.
        
        Args:
            frame: OpenCV frame/image as numpy array
            
        Returns:
            List of face detection dictionaries with bbox, confidence, etc.
        """
        try:
            if self.method == "mtcnn" and self.model is not None:
                return self._detect_with_mtcnn_frame(frame)
            else:
                return self._detect_with_opencv_frame(frame)
                
        except Exception as e:
            logger.error(f"Error detecting faces in frame: {str(e)}")
            return []
    
    def _detect_with_mtcnn_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces using MTCNN on a video frame.
        
        Args:
            frame: OpenCV frame as numpy array
            
        Returns:
            List of face detection dictionaries
        """
        try:
            # Convert BGR to RGB for MTCNN
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            detections = self.model.detect_faces(rgb_frame)
            
            faces = []
            for detection in detections:
                if detection['confidence'] >= self.min_confidence:
                    bbox = detection['box']
                    # Convert to [x1, y1, x2, y2] format
                    x1, y1, w, h = bbox
                    x2, y2 = x1 + w, y1 + h
                    
                    face_data = {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": detection['confidence'],
                        "keypoints": detection.get('keypoints', {}),
                        "method": "mtcnn"
                    }
                    faces.append(face_data)
            
            logger.debug(f"MTCNN detected {len(faces)} faces in frame")
            return faces
            
        except Exception as e:
            logger.error(f"Error in MTCNN frame detection: {str(e)}")
            return []
    
    def _detect_with_opencv_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces using OpenCV DNN on a video frame.
        
        Args:
            frame: OpenCV frame as numpy array
            
        Returns:
            List of face detection dictionaries
        """
        try:
            if self.model is not None:
                return self._detect_with_dnn_frame(frame)
            else:
                return self._detect_with_cascade_frame(frame)
                
        except Exception as e:
            logger.error(f"Error in OpenCV frame detection: {str(e)}")
            return []
    
    def _detect_with_dnn_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces using DNN model on a video frame.
        """
        height, width = frame.shape[:2]
        
        # Create blob from frame
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
        
        # Set input to the network
        self.model.setInput(blob)
        
        # Run inference
        detections = self.model.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence >= self.min_confidence:
                # Get bounding box coordinates
                x1 = int(detections[0, 0, i, 3] * width)
                y1 = int(detections[0, 0, i, 4] * height)
                x2 = int(detections[0, 0, i, 5] * width)
                y2 = int(detections[0, 0, i, 6] * height)
                
                # Ensure coordinates are within frame bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)
                
                # Check if bounding box is valid
                if x2 > x1 and y2 > y1:
                    face_data = {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": float(confidence),
                        "method": "opencv-dnn"
                    }
                    faces.append(face_data)
        
        logger.debug(f"DNN detected {len(faces)} faces in frame")
        return faces
    
    def _detect_with_cascade_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces using Haar cascade on a video frame.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast for better detection
        gray = cv2.equalizeHist(gray)
        
        # Detect faces
        face_rects = self.model.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        faces = []
        for (x, y, w, h) in face_rects:
            # Convert to [x1, y1, x2, y2] format
            x1, y1, x2, y2 = x, y, x + w, y + h
            
            # Calculate confidence based on face size (larger faces = higher confidence)
            face_area = w * h
            confidence = min(face_area / 10000, 0.95)  # Normalize and cap at 0.95
            
            if confidence >= self.min_confidence:
                face_data = {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": confidence,
                    "method": "opencv-cascade"
                }
                faces.append(face_data)
        
        logger.debug(f"Cascade detected {len(faces)} faces in frame")
        return faces