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

# Configure logger
logger = logging.getLogger(__name__)

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
        
        if self.method not in self.DETECTION_METHODS:
            raise ValueError(f"Detection method must be one of {self.DETECTION_METHODS}")
        
        # Default model paths
        if model_path is None:
            # Use models directory relative to project root
            models_dir = Path(__file__).parent.parent.parent.parent / "models" / "facial"
            
            if self.method == "opencv-dnn":
                self.model_path = str(models_dir / "opencv_face_detector.caffemodel")
                self.config_path = str(models_dir / "opencv_face_detector.prototxt")
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
                # Fallback to OpenCV DNN
                self.method = "opencv-dnn"
                self._initialize_detector()
                
        elif self.method == "mtcnn":
            try:
                from mtcnn import MTCNN
                self.model = MTCNN(min_face_size=20, scale_factor=0.709)
            except ImportError:
                logger.error("MTCNN package not installed. Falling back to OpenCV DNN")
                # Fallback to OpenCV DNN
                self.method = "opencv-dnn"
                self._initialize_detector()
                
    def detect_faces(
        self, 
        image: np.ndarray, 
        enhance_low_light: bool = False
    ) -> List[Dict[str, Union[float, List[int]]]]:
        """
        Detect faces in an image.
        
        Args:
            image: Input image as numpy array (BGR format)
            enhance_low_light: Whether to enhance low-light images
            
        Returns:
            List of face detections, each with:
                - 'bbox': [x, y, width, height]
                - 'confidence': Detection confidence score
                - 'landmarks': Facial landmarks if available
        """
        if image is None or image.size == 0:
            logger.warning("Empty image provided to face detector")
            return []
        
        # Enhance low-light images if requested
        if enhance_low_light:
            image = self._enhance_low_light(image)
            
        # Process based on detection method
        if self.method == "mtcnn":
            return self._detect_with_mtcnn(image)
        elif self.method == "retinaface":
            return self._detect_with_retinaface(image)
        else:  # opencv-dnn or fallback haar
            return self._detect_with_opencv(image)
            
    def _detect_with_opencv(self, image: np.ndarray) -> List[Dict[str, Union[float, List[int]]]]:
        """Detect faces using OpenCV DNN or Haar cascade."""
        results = []
        height, width = image.shape[:2]
        
        if self.method == "haar":
            # Convert to grayscale for Haar cascade
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.model.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                results.append({
                    'bbox': [x, y, w, h],
                    'confidence': 1.0,  # No confidence score for Haar
                    'landmarks': None
                })
        else:
            # Prepare input blob for DNN
            blob = cv2.dnn.blobFromImage(
                image, 1.0, (300, 300), [104, 117, 123], False, False
            )
            
            self.model.setInput(blob)
            detections = self.model.forward()
            
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > self.min_confidence:
                    # Get coordinates and convert to integers
                    x1 = int(detections[0, 0, i, 3] * width)
                    y1 = int(detections[0, 0, i, 4] * height)
                    x2 = int(detections[0, 0, i, 5] * width)
                    y2 = int(detections[0, 0, i, 6] * height)
                    
                    # Ensure coordinates are within image boundaries
                    x1 = max(0, min(x1, width - 1))
                    y1 = max(0, min(y1, height - 1))
                    x2 = max(0, min(x2, width - 1))
                    y2 = max(0, min(y2, height - 1))
                    
                    results.append({
                        'bbox': [x1, y1, x2 - x1, y2 - y1],
                        'confidence': float(confidence),
                        'landmarks': None
                    })
                    
        return results
        
    def _detect_with_mtcnn(self, image: np.ndarray) -> List[Dict[str, Union[float, List[int]]]]:
        """Detect faces using MTCNN."""
        # MTCNN requires RGB format
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detections = self.model.detect_faces(rgb_image)
        
        results = []
        for detection in detections:
            if detection['confidence'] >= self.min_confidence:
                x, y, w, h = detection['box']
                results.append({
                    'bbox': [x, y, w, h],
                    'confidence': float(detection['confidence']),
                    'landmarks': detection['keypoints']
                })
                
        return results
        
    def _detect_with_retinaface(self, image: np.ndarray) -> List[Dict[str, Union[float, List[int]]]]:
        """Detect faces using RetinaFace ONNX model."""
        # Preprocess image for RetinaFace
        height, width = image.shape[:2]
        input_size = (640, 640)  # Standard size for RetinaFace
        
        # Resize and create blob
        img_resized = cv2.resize(image, input_size)
        img_tensor = img_resized.transpose(2, 0, 1).astype(np.float32)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        img_tensor = (img_tensor - 127.5) / 128.0
        
        # Get outputs
        input_name = self.model.get_inputs()[0].name
        outputs = self.model.run(None, {input_name: img_tensor})
        
        # Process outputs (boxes, scores, landmarks)
        boxes = outputs[0][0]
        scores = outputs[1][0]
        
        # Scale back to original image
        scale_x = width / input_size[0]
        scale_y = height / input_size[1]
        
        results = []
        for i, score in enumerate(scores):
            if score >= self.min_confidence:
                box = boxes[i]
                x1 = int(box[0] * input_size[0] * scale_x)
                y1 = int(box[1] * input_size[1] * scale_y)
                x2 = int(box[2] * input_size[0] * scale_x)
                y2 = int(box[3] * input_size[1] * scale_y)
                
                # Ensure coordinates are within image boundaries
                x1 = max(0, min(x1, width - 1))
                y1 = max(0, min(y1, height - 1))
                x2 = max(0, min(x2, width - 1))
                y2 = max(0, min(y2, height - 1))
                
                results.append({
                    'bbox': [x1, y1, x2 - x1, y2 - y1],
                    'confidence': float(score),
                    'landmarks': None  # We could extract landmarks if needed
                })
                
        return results
        
    def _enhance_low_light(self, image: np.ndarray) -> np.ndarray:
        """Enhance low-light images for better face detection."""
        # Simple CLAHE (Contrast Limited Adaptive Histogram Equalization) enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced_lab = cv2.merge((l, a, b))
        enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_image
        
    def extract_face(
        self, 
        image: np.ndarray, 
        bbox: List[int], 
        margin: float = 0.2,
        target_size: Tuple[int, int] = (112, 112)
    ) -> np.ndarray:
        """
        Extract and preprocess a face region from an image.
        
        Args:
            image: Input image
            bbox: Bounding box [x, y, width, height]
            margin: Percentage to expand the bounding box
            target_size: Size to resize the extracted face
            
        Returns:
            Preprocessed face image
        """
        x, y, w, h = bbox
        
        # Add margin
        margin_x = int(w * margin)
        margin_y = int(h * margin)
        
        # Calculate coordinates with margin
        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(image.shape[1], x + w + margin_x)
        y2 = min(image.shape[0], y + h + margin_y)
        
        # Extract face region
        face = image[y1:y2, x1:x2]
        
        # Resize to target size if needed
        if target_size:
            face = cv2.resize(face, target_size)
            
        return face
        
    def detect_and_extract_faces(
        self,
        image: np.ndarray,
        enhance_low_light: bool = False,
        target_size: Tuple[int, int] = (112, 112)
    ) -> List[Dict]:
        """
        Detect faces and extract the face regions.
        
        Args:
            image: Input image
            enhance_low_light: Whether to enhance low-light images
            target_size: Size to resize extracted faces
            
        Returns:
            List of dictionaries with face detections and extracted face images
        """
        detections = self.detect_faces(image, enhance_low_light)
        results = []
        
        for detection in detections:
            bbox = detection['bbox']
            face_img = self.extract_face(image, bbox, target_size=target_size)
            
            results.append({
                'detection': detection,
                'face_image': face_img
            })
            
        return results