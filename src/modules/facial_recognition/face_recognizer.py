"""
Face recognition module for WarehouseVision AI.

This module implements facial recognition using deep learning embeddings,
specifically ArcFace for feature extraction and matching. It includes:
- Face embedding generation using ArcFace or similar models
- Efficient matching against a database of known embeddings
- Confidence scoring for recognition results
- Privacy-preserving techniques
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Union, Any
import os
import sys
from pathlib import Path
import pickle
import time
from datetime import datetime
from scipy.spatial.distance import cosine
import subprocess
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

class FaceRecognizer:
    """Face recognition implementation using ArcFace embeddings."""
    
    RECOGNITION_METHODS = ["arcface", "insightface", "facenet", "opencv"]
    
    def __init__(
        self,
        method: str = "arcface",
        model_path: Optional[str] = None,
        recognition_threshold: float = 0.6,
        enable_gpu: bool = False,
        db_path: Optional[str] = None
    ):
        """
        Initialize face recognition with specified model.
        
        Args:
            method: Recognition method ('arcface', 'insightface', 'facenet', or 'opencv')
            model_path: Path to model weights (if None, uses default)
            recognition_threshold: Threshold for recognition confidence
            enable_gpu: Whether to use GPU acceleration if available
            db_path: Path to stored embeddings database (if any)
        """
        self.method = method.lower()
        self.recognition_threshold = recognition_threshold
        self.enable_gpu = enable_gpu
        self.model = None
        self.model_path = None
        self.embedding_size = 512  # Default for ArcFace
        self.db_path = db_path
        
        self.embeddings_db = {}  # Dictionary of {id: embedding}
        self.opencv_face_detector = None  # OpenCV backup detector
        
        if self.method not in self.RECOGNITION_METHODS:
            logger.warning(f"Recognition method {self.method} not in {self.RECOGNITION_METHODS}, falling back to opencv")
            self.method = "opencv"
        
        # Default model paths
        if model_path is None:
            # Use models directory relative to project root
            models_dir = Path(__file__).parent.parent.parent.parent / "models" / "facial"
            os.makedirs(models_dir, exist_ok=True)
            
            if self.method == "arcface":
                self.model_path = str(models_dir / "arcface_resnet100.onnx")
            elif self.method == "insightface":
                self.model_path = str(models_dir / "insightface.onnx")
            elif self.method == "facenet":
                self.model_path = str(models_dir / "facenet.pb")
        else:
            self.model_path = model_path
            
        # Initialize the selected recognition model
        try:
            self._initialize_recognizer()
        except Exception as e:
            logger.warning(f"Failed to initialize {self.method} recognizer: {e}. Falling back to OpenCV detector.")
            self.method = "opencv"
            self._initialize_opencv_detector()
        
        # Load embeddings database if provided
        if db_path and os.path.exists(db_path):
            self.load_embeddings_db(db_path)
        
        logger.info(f"Face recognizer initialized using {self.method} method")
        
    def _initialize_opencv_detector(self):
        """Initialize OpenCV's built-in face detector as fallback."""
        logger.info("Initializing OpenCV face detector as fallback")
        # Initialize OpenCV's face detection
        self.opencv_face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # OpenCV detector doesn't provide embeddings, so we'll use a dummy size
        self.embedding_size = 128
        
    def _initialize_recognizer(self):
        """Initialize the selected face recognition model."""
        # Define paths
        models_dir = Path(self.model_path).parent if self.model_path else None
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "download_arcface.py"

        # Handle missing model file generically
        def handle_missing_model(method_name):
            logger.error(f"{method_name} model file not found at {self.model_path}")
            
            # Check if download script exists
            if os.path.exists(script_path):
                try:
                    logger.info(f"Attempting to download the missing {method_name} model file...")
                    subprocess.run([sys.executable, str(script_path)], check=True)
                    logger.info("Model download script execution completed.")
                    
                    # Check if download was successful
                    if not os.path.exists(self.model_path):
                        raise FileNotFoundError(f"Model file still not found after download attempt: {self.model_path}")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to download the {method_name} model file: {e}")
                    instructions = (
                        f"\nTo manually download the model:\n"
                        f"1. Run: python {script_path}\n"
                        f"2. Ensure the file is saved to: {models_dir}\n"
                    )
                    logger.info(instructions)
                    raise FileNotFoundError(f"Model file not found and download failed: {self.model_path}. {instructions}")
            else:
                instructions = (
                    f"\nThe model download script was not found at {script_path}. To resolve this issue:\n"
                    f"1. Ensure the scripts directory exists in the project root\n"
                    f"2. Create the download_arcface.py script if missing\n"
                    f"3. Manually download the {method_name} model to: {models_dir}\n"
                )
                logger.error(instructions)
                raise FileNotFoundError(f"Model file not found: {self.model_path}. Download script not found. {instructions}")
            
            return False

        if self.method == "opencv":
            self._initialize_opencv_detector()
            return

        if self.method == "arcface":
            try:
                import onnxruntime
                
                # Check if model file exists
                if not os.path.exists(self.model_path):
                    handle_missing_model("ArcFace")
                    
                # Create an ONNX Runtime session
                logger.info(f"Loading ArcFace model from {self.model_path}")
                try:
                    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.enable_gpu else ['CPUExecutionProvider']
                    self.model = onnxruntime.InferenceSession(self.model_path, providers=providers)
                    # Try to get input details to validate the model format
                    input_details = self.model.get_inputs()
                    logger.info(f"Model loaded successfully. Input shape: {input_details[0].shape}")
                    self.embedding_size = 512
                except Exception as model_error:
                    # The model might have a different format than expected
                    logger.error(f"Error loading model in standard format: {str(model_error)}")
                    logger.info("Attempting to use the model with InsightFace...")
                    self.method = "insightface"
                    
                    # Try using InsightFace directly with the downloaded model
                    try:
                        from insightface.app import FaceAnalysis
                        self.model = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
                        self.model.prepare(ctx_id=-1 if not self.enable_gpu else 0)
                        logger.info("Successfully switched to InsightFace model")
                    except ImportError:
                        logger.error("InsightFace package not installed. Falling back to OpenCV")
                        self.method = "opencv"
                        self._initialize_opencv_detector()
                    
            except ImportError:
                logger.error("ONNX Runtime not installed. Required for ArcFace")
                raise ImportError("ONNX Runtime required but not installed. Install it with 'pip install onnxruntime'")
            except Exception as e:
                logger.error(f"Failed to initialize ArcFace: {str(e)}")
                raise RuntimeError(f"Failed to initialize ArcFace: {str(e)}")
                
        elif self.method == "insightface":
            try:
                # Try to use InsightFace if available
                from insightface.app import FaceAnalysis
                
                # Check if model file exists
                if self.model_path and not os.path.exists(self.model_path):
                    handle_missing_model("InsightFace")
                    
                self.model = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
                self.model.prepare(ctx_id=-1 if not self.enable_gpu else 0)
                self.embedding_size = 512
                
            except ImportError:
                logger.error("InsightFace package not installed. Please install it with 'pip install insightface'")
                raise ImportError("InsightFace package required but not installed. Install it with 'pip install insightface'")
            except Exception as e:
                logger.error(f"Failed to initialize InsightFace: {str(e)}")
                raise RuntimeError(f"Failed to initialize InsightFace: {str(e)}")
                
        elif self.method == "facenet":
            try:
                # FaceNet implementation would go here
                # Typically using TensorFlow
                import tensorflow as tf
                
                # Check if model file exists
                if not os.path.exists(self.model_path):
                    handle_missing_model("FaceNet")
                    
                self.model = tf.saved_model.load(self.model_path)
                self.embedding_size = 128  # FaceNet typically uses 128-d embeddings
                
            except ImportError:
                logger.error("TensorFlow not installed. Required for FaceNet")
                raise ImportError("TensorFlow required but not installed. Install it with 'pip install tensorflow'")
            except Exception as e:
                logger.error(f"Failed to initialize FaceNet: {str(e)}")
                raise RuntimeError(f"Failed to initialize FaceNet: {str(e)}")
                
    def generate_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate embedding for a face image.
        
        Args:
            face_image: Extracted and aligned face image
            
        Returns:
            Face embedding vector
        """
        try:
            # Check if image is appropriate for embedding generation
            if face_image is None or face_image.size == 0:
                raise ValueError("Invalid face image")
                
            # Normalize input image based on method
            if self.method == "arcface":
                # ArcFace preprocessing
                if face_image.shape != (112, 112, 3):
                    face_image = cv2.resize(face_image, (112, 112))
                # Convert to RGB if grayscale
                if len(face_image.shape) == 2:
                    face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
                # Normalize to range [0, 1] and convert to BCHW
                img = face_image.astype(np.float32) / 255.0
                img = (img - 0.5) / 0.5  # Normalize to [-1, 1]
                img = img.transpose(2, 0, 1)  # HWC to CHW
                img = np.expand_dims(img, axis=0)  # Add batch dimension
                
                # Run inference
                try:
                    input_name = self.model.get_inputs()[0].name
                    outputs = self.model.run(None, {input_name: img})
                    embedding = outputs[0][0]
                except Exception as inference_error:
                    logger.error(f"Error during inference: {str(inference_error)}")
                    # Fallback to OpenCV embedding if model inference fails
                    return self._generate_opencv_embedding(face_image)
                
            elif self.method == "insightface":
                # InsightFace preprocessing and embedding generation
                faces = self.model.get(face_image)
                if len(faces) == 0:
                    raise ValueError("No face detected by InsightFace")
                embedding = faces[0].embedding
                
            elif self.method == "facenet":
                # FaceNet preprocessing
                if face_image.shape[:2] != (160, 160):
                    face_image = cv2.resize(face_image, (160, 160))
                # Convert to RGB if grayscale
                if len(face_image.shape) == 2:
                    face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
                # Normalize
                img = face_image.astype(np.float32)
                std = np.std(img)
                mean = np.mean(img)
                img = (img - mean) / std if std > 0 else img - mean
                img = np.expand_dims(img, axis=0)
                
                # Run inference
                embedding = self.model(img)
                embedding = embedding.numpy()[0]
                
            elif self.method == "opencv":
                # OpenCV fallback - use local binary patterns histogram as a simple embedding
                embedding = self._generate_opencv_embedding(face_image)
                
            else:
                raise ValueError(f"Unsupported method: {self.method}")
                
            # Normalize embedding to unit length
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return empty embedding in case of error
            return np.zeros(self.embedding_size, dtype=np.float32)
    
    def _generate_opencv_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate a simple embedding using OpenCV's LBP histograms.
        This is a fallback when deep learning models are unavailable.
        
        Args:
            face_image: Aligned face image
            
        Returns:
            Simple face descriptor based on LBP histogram
        """
        # Resize for consistency
        face = cv2.resize(face_image, (64, 64))
        
        # Convert to grayscale if needed
        if len(face.shape) > 2:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Apply LBP
        radius = 1
        n_points = 8 * radius
        lbp = self._local_binary_pattern(face, n_points, radius, method="uniform")
        
        # Compute histogram
        n_bins = n_points + 2  # uniform pattern produces n_points+2 values
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins))
        
        # Normalize histogram
        hist = hist.astype("float")
        hist /= (hist.sum() + 1e-6)
        
        # If embedding_size is larger than histogram, pad with zeros
        if len(hist) < self.embedding_size:
            embedding = np.zeros(self.embedding_size, dtype=np.float32)
            embedding[:len(hist)] = hist
        else:
            # If histogram is too large, truncate
            embedding = hist[:self.embedding_size].astype(np.float32)
            
        return embedding
    
    def _local_binary_pattern(self, image, n_points, radius, method="uniform"):
        """
        Compute local binary pattern for an image.
        A simplified version for OpenCV fallback.
        
        Args:
            image: Input grayscale image
            n_points: Number of points
            radius: Radius of circle
            method: LBP method
            
        Returns:
            LBP image
        """
        # Get dimensions
        height, width = image.shape
        
        # Initialize output LBP image
        lbp = np.zeros((height, width), dtype=np.uint8)
        
        # Loop through the image
        for y in range(radius, height - radius):
            for x in range(radius, width - radius):
                # Get center pixel value
                center = image[y, x]
                binary_code = 0
                
                # Sample points around the center
                for i in range(n_points):
                    # Calculate sample point coordinates
                    theta = 2 * np.pi * i / n_points
                    x_i = x + radius * np.cos(theta)
                    y_i = y + radius * np.sin(theta)
                    
                    # Bilinear interpolation
                    x1, y1 = int(x_i), int(y_i)
                    x2, y2 = min(x1 + 1, width - 1), min(y1 + 1, height - 1)
                    dx, dy = x_i - x1, y_i - y1
                    
                    # Get interpolated value
                    value = (1 - dx) * (1 - dy) * image[y1, x1] + \
                            dx * (1 - dy) * image[y1, x2] + \
                            (1 - dx) * dy * image[y2, x1] + \
                            dx * dy * image[y2, x2]
                    
                    # Update binary code
                    if value >= center:
                        binary_code |= (1 << i)
                
                # Assign LBP value to the pixel
                lbp[y, x] = binary_code
                
        return lbp
    
    def recognize_face(self, embedding: np.ndarray, min_confidence: float = None) -> Tuple[Optional[str], float]:
        """
        Recognize a face by comparing its embedding with stored embeddings.
        
        Args:
            embedding: Face embedding to compare
            min_confidence: Override default recognition confidence threshold
            
        Returns:
            Tuple of (identity, confidence)
        """
        if not self.embeddings_db:
            return None, 0.0
            
        if min_confidence is None:
            min_confidence = self.recognition_threshold
            
        # Calculate cosine similarity with all stored embeddings
        best_match = None
        best_score = -1.0
        
        for identity, stored_embedding in self.embeddings_db.items():
            # Skip if stored embedding is not valid
            if stored_embedding is None or len(stored_embedding) == 0:
                continue
                
            # Normalize the stored embedding if not already normalized
            norm = np.linalg.norm(stored_embedding)
            if norm > 0:
                stored_embedding = stored_embedding / norm
                
            # Calculate cosine similarity (dot product of normalized vectors)
            similarity = np.dot(embedding, stored_embedding)
            
            # Update best match
            if similarity > best_score:
                best_score = similarity
                best_match = identity
                
        # Return best match if above threshold
        if best_score >= min_confidence:
            return best_match, best_score
        else:
            return None, best_score
    
    def detect_faces(self, image: np.ndarray, min_face_size: int = 30) -> List[Dict[str, Any]]:
        """
        Detect faces in an input image.
        
        Args:
            image: Input image (BGR format)
            min_face_size: Minimum face size to detect (in pixels)
            
        Returns:
            List of detected faces with their bounding boxes and landmarks
        """
        if image is None or image.size == 0:
            logger.warning("Empty image provided to face detector")
            return []
            
        # Create a copy to avoid modifying the original
        img = image.copy()
        
        # Convert to RGB if needed for certain models
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        faces = []
        
        try:
            if self.method == "arcface":
                # Use MTCNN or another face detector compatible with ArcFace
                MTCNN = import_mtcnn()
                if MTCNN:
                    detector = MTCNN()
                    detections = detector.detect_faces(rgb_img)
                    
                    for detection in detections:
                        confidence = detection['confidence']
                        if confidence < 0.9:  # Filter by confidence
                            continue
                            
                        x, y, w, h = detection['box']
                        box = [x, y, x+w, y+h]
                        
                        # Extract landmarks
                        landmarks = detection['keypoints']
                        face_landmarks = {
                            'left_eye': landmarks['left_eye'],
                            'right_eye': landmarks['right_eye'],
                            'nose': landmarks['nose'],
                            'mouth_left': landmarks['mouth_left'],
                            'mouth_right': landmarks['mouth_right']
                        }
                        
                        faces.append({
                            'bbox': box,
                            'confidence': confidence,
                            'landmarks': face_landmarks,
                            'aligned_face': self._align_face(img, box, face_landmarks)
                        })
                else:
                    logger.warning("MTCNN not installed, falling back to OpenCV face detector")
                    # Fall back to OpenCV cascade
                    faces = self._detect_faces_opencv(img, min_face_size)
                    
            elif self.method == "insightface":
                # Use InsightFace's own face detector
                face_results = self.model.get(rgb_img)
                
                for face in face_results:
                    bbox = face.bbox.astype(np.int32)
                    box = [bbox[0], bbox[1], bbox[2], bbox[3]]
                    
                    # Extract landmarks
                    face_landmarks = {}
                    landmarks = face.landmark.astype(np.int32)
                    if landmarks.shape[0] >= 5:  # Basic 5-point landmarks
                        face_landmarks['left_eye'] = (landmarks[0][0], landmarks[0][1])
                        face_landmarks['right_eye'] = (landmarks[1][0], landmarks[1][1])
                        face_landmarks['nose'] = (landmarks[2][0], landmarks[2][1])
                        face_landmarks['mouth_left'] = (landmarks[3][0], landmarks[3][1])
                        face_landmarks['mouth_right'] = (landmarks[4][0], landmarks[4][1])
                    
                    faces.append({
                        'bbox': box,
                        'confidence': face.det_score,
                        'landmarks': face_landmarks,
                        'aligned_face': face.embedding is not None,  # InsightFace already aligned the face
                        'embedding': face.embedding  # InsightFace provides embedding directly
                    })
                    
            elif self.method == "facenet":
                # Similar to ArcFace case, use MTCNN which is compatible with FaceNet
                MTCNN = import_mtcnn()
                if MTCNN:
                    detector = MTCNN()
                    detections = detector.detect_faces(rgb_img)
                    
                    for detection in detections:
                        confidence = detection['confidence']
                        if confidence < 0.9:
                            continue
                            
                        x, y, w, h = detection['box']
                        box = [x, y, x+w, y+h]
                        
                        # Extract landmarks
                        landmarks = detection['keypoints']
                        face_landmarks = {
                            'left_eye': landmarks['left_eye'],
                            'right_eye': landmarks['right_eye'],
                            'nose': landmarks['nose'],
                            'mouth_left': landmarks['mouth_left'],
                            'mouth_right': landmarks['mouth_right']
                        }
                        
                        faces.append({
                            'bbox': box,
                            'confidence': confidence,
                            'landmarks': face_landmarks,
                            'aligned_face': self._align_face(img, box, face_landmarks)
                        })
                else:
                    logger.warning("MTCNN not installed, falling back to OpenCV face detector")
                    # Fall back to OpenCV cascade
                    faces = self._detect_faces_opencv(img, min_face_size)
                    
            elif self.method == "opencv":
                # Use OpenCV's built-in face detector
                faces = self._detect_faces_opencv(img, min_face_size)
                
            else:
                logger.error(f"Unsupported method for face detection: {self.method}")
                return []
                
            return faces
            
        except Exception as e:
            logger.error(f"Error during face detection: {str(e)}")
            # Fallback to OpenCV detector in case of errors
            logger.info("Falling back to OpenCV face detector")
            return self._detect_faces_opencv(img, min_face_size)
            
    def _detect_faces_opencv(self, image: np.ndarray, min_face_size: int = 30) -> List[Dict[str, Any]]:
        """
        Detect faces using OpenCV's cascade classifier.
        
        Args:
            image: Input image (BGR format)
            min_face_size: Minimum face size to detect
            
        Returns:
            List of detected faces with their bounding boxes
        """
        if self.opencv_face_detector is None:
            self._initialize_opencv_detector()
            
        # Convert to grayscale for cascade classifier
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces_rect = self.opencv_face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(min_face_size, min_face_size)
        )
        
        faces = []
        for (x, y, w, h) in faces_rect:
            # Create bounding box
            box = [x, y, x+w, y+h]
            
            # Expand box to improve face alignment
            expanded_box = self._expand_face_box(box, image.shape[1], image.shape[0])
            
            # Estimate facial landmarks using relative positions
            # This is a very rough approximation
            face_width = expanded_box[2] - expanded_box[0]
            face_height = expanded_box[3] - expanded_box[1]
            
            # Estimate eye positions based on typical facial proportions
            left_eye_x = int(expanded_box[0] + 0.3 * face_width)
            right_eye_x = int(expanded_box[0] + 0.7 * face_width)
            eye_y = int(expanded_box[1] + 0.4 * face_height)
            
            # Estimate other facial landmarks
            nose_x = int(expanded_box[0] + 0.5 * face_width)
            nose_y = int(expanded_box[1] + 0.5 * face_height)
            
            mouth_left_x = int(expanded_box[0] + 0.35 * face_width)
            mouth_right_x = int(expanded_box[0] + 0.65 * face_width)
            mouth_y = int(expanded_box[1] + 0.7 * face_height)
            
            landmarks = {
                'left_eye': (left_eye_x, eye_y),
                'right_eye': (right_eye_x, eye_y),
                'nose': (nose_x, nose_y),
                'mouth_left': (mouth_left_x, mouth_y),
                'mouth_right': (mouth_right_x, mouth_y)
            }
            
            # Extract and align face using estimated landmarks
            aligned_face = self._align_face(image, expanded_box, landmarks)
            
            faces.append({
                'bbox': expanded_box,
                'confidence': 0.9,  # Arbitrary confidence for OpenCV detector
                'landmarks': landmarks,
                'aligned_face': aligned_face
            })
            
        return faces
        
    def _expand_face_box(self, box: List[int], img_width: int, img_height: int, expansion_factor: float = 0.2) -> List[int]:
        """
        Expand the face bounding box to include more context.
        
        Args:
            box: Original bounding box [x1, y1, x2, y2]
            img_width: Width of the image
            img_height: Height of the image
            expansion_factor: How much to expand the box by
            
        Returns:
            Expanded bounding box
        """
        width = box[2] - box[0]
        height = box[3] - box[1]
        
        # Calculate expanded coordinates
        x1 = max(0, box[0] - int(width * expansion_factor))
        y1 = max(0, box[1] - int(height * expansion_factor))
        x2 = min(img_width, box[2] + int(width * expansion_factor))
        y2 = min(img_height, box[3] + int(height * expansion_factor))
        
        return [x1, y1, x2, y2]
        
    def _align_face(self, image: np.ndarray, box: List[int], landmarks: Dict[str, Tuple[int, int]]) -> np.ndarray:
        """
        Align a face based on eye positions.
        
        Args:
            image: Input image
            box: Face bounding box
            landmarks: Facial landmarks including eye positions
            
        Returns:
            Aligned face image
        """
        # If we don't have proper landmarks, just crop the face
        if not landmarks or 'left_eye' not in landmarks or 'right_eye' not in landmarks:
            return image[box[1]:box[3], box[0]:box[2]]
            
        # Get eye centers
        left_eye = landmarks['left_eye']
        right_eye = landmarks['right_eye']
        
        # Calculate angle and scale for alignment
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        
        if dx == 0:  # Avoid division by zero
            angle = 0
        else:
            angle = np.degrees(np.arctan2(dy, dx))
            
        # Determine desired eye position based on method
        desired_eye_x = 0.35  # Percentage of image width
        if self.method == "arcface":
            desired_size = (112, 112)
        elif self.method == "facenet": 
            desired_size = (160, 160)
        else:
            desired_size = (96, 96)  # Default size
            
        # Calculate scale from eye distance
        eye_distance = np.sqrt((dx ** 2) + (dy ** 2))
        desired_eye_distance = desired_size[0] * (desired_eye_x * 2)  # Left and right eye positions
        scale = desired_eye_distance / eye_distance if eye_distance > 0 else 1.0
        
        # Calculate eye midpoint
        eye_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
        
        # Get the rotation matrix
        M = cv2.getRotationMatrix2D(eye_center, angle, scale)
        
        # Update the translation part of the matrix
        tX = desired_size[0] * 0.5
        tY = desired_size[1] * desired_eye_x
        M[0, 2] += (tX - eye_center[0])
        M[1, 2] += (tY - eye_center[1])
        
        # Apply the affine transformation
        aligned_face = cv2.warpAffine(image, M, desired_size, flags=cv2.INTER_CUBIC)
        
        return aligned_face