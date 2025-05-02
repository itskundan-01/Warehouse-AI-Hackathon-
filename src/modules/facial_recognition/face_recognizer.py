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
from pathlib import Path
import pickle
import time
from datetime import datetime
from scipy.spatial.distance import cosine

# Configure logger
logger = logging.getLogger(__name__)

class FaceRecognizer:
    """Face recognition implementation using ArcFace embeddings."""
    
    RECOGNITION_METHODS = ["arcface", "insightface", "facenet"]
    
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
            method: Recognition method ('arcface', 'insightface', or 'facenet')
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
        
        if self.method not in self.RECOGNITION_METHODS:
            raise ValueError(f"Recognition method must be one of {self.RECOGNITION_METHODS}")
        
        # Default model paths
        if model_path is None:
            # Use models directory relative to project root
            models_dir = Path(__file__).parent.parent.parent.parent / "models" / "facial"
            
            if self.method == "arcface":
                self.model_path = str(models_dir / "arcface_resnet100.onnx")
            elif self.method == "insightface":
                self.model_path = str(models_dir / "insightface.onnx")
            elif self.method == "facenet":
                self.model_path = str(models_dir / "facenet.pb")
        else:
            self.model_path = model_path
            
        # Initialize the selected recognition model
        self._initialize_recognizer()
        
        # Load embeddings database if provided
        if db_path and os.path.exists(db_path):
            self.load_embeddings_db(db_path)
        
        logger.info(f"Face recognizer initialized using {self.method} method")
        
    def _initialize_recognizer(self):
        """Initialize the selected face recognition model."""
        if self.method == "arcface":
            try:
                import onnxruntime
                
                # Check if model file exists
                if not os.path.exists(self.model_path):
                    logger.error(f"ArcFace model file not found at {self.model_path}")
                    raise FileNotFoundError(f"Model file not found: {self.model_path}")
                    
                # Create an ONNX Runtime session
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if self.enable_gpu else ['CPUExecutionProvider']
                self.model = onnxruntime.InferenceSession(self.model_path, providers=providers)
                self.embedding_size = 512
                
            except (ImportError, Exception) as e:
                logger.error(f"Failed to initialize ArcFace: {str(e)}")
                raise RuntimeError(f"Failed to initialize ArcFace: {str(e)}")
                
        elif self.method == "insightface":
            try:
                # Try to use InsightFace if available
                from insightface.app import FaceAnalysis
                self.model = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
                self.model.prepare(ctx_id=-1 if not self.enable_gpu else 0)
                self.embedding_size = 512
                
            except ImportError:
                logger.error("InsightFace package not installed. Please install it or use another method")
                raise ImportError("InsightFace package required but not installed")
                
        elif self.method == "facenet":
            try:
                # FaceNet implementation would go here
                # Typically using TensorFlow
                import tensorflow as tf
                self.model = tf.saved_model.load(self.model_path)
                self.embedding_size = 128  # FaceNet typically uses 128-d embeddings
                
            except ImportError:
                logger.error("TensorFlow not installed. Required for FaceNet")
                raise ImportError("TensorFlow required but not installed")
    
    def get_face_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate embedding for a face image.
        
        Args:
            face_image: Preprocessed face image (should be aligned and sized according to model)
            
        Returns:
            Face embedding as a numpy array
        """
        if face_image is None or face_image.size == 0:
            raise ValueError("Empty face image provided")
            
        if self.method == "arcface":
            return self._get_embedding_arcface(face_image)
        elif self.method == "insightface":
            return self._get_embedding_insightface(face_image)
        elif self.method == "facenet":
            return self._get_embedding_facenet(face_image)
            
    def _get_embedding_arcface(self, face_image: np.ndarray) -> np.ndarray:
        """Generate embedding using ArcFace ONNX model."""
        # Preprocess image
        # ArcFace typically expects BGR input, 112x112, float32 in range [0, 1]
        if face_image.shape[:2] != (112, 112):
            face_image = cv2.resize(face_image, (112, 112))
            
        # Convert to BGR if it's not already
        if len(face_image.shape) == 2:
            # Convert grayscale to BGR
            face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2BGR)
        elif face_image.shape[2] == 4:
            # Convert BGRA to BGR
            face_image = face_image[:, :, :3]
            
        # Normalize and transpose to NCHW format (batch, channels, height, width)
        blob = cv2.dnn.blobFromImage(
            face_image, 
            1.0/255.0,  # scale factor
            (112, 112),  # size
            (0, 0, 0),   # mean
            swapRB=False,  # ArcFace expects BGR
            crop=False
        )
        
        # Run inference
        input_name = self.model.get_inputs()[0].name
        outputs = self.model.run(None, {input_name: blob})
        
        # Get embedding and normalize
        embedding = outputs[0][0]
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
        
    def _get_embedding_insightface(self, face_image: np.ndarray) -> np.ndarray:
        """Generate embedding using InsightFace."""
        # InsightFace expects RGB
        rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # Get face analysis
        faces = self.model.get(rgb_image)
        if len(faces) == 0:
            raise ValueError("No face detected in the image by InsightFace")
            
        # Use the embedding from the first (and hopefully only) face
        embedding = faces[0].embedding
        
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
        
    def _get_embedding_facenet(self, face_image: np.ndarray) -> np.ndarray:
        """Generate embedding using FaceNet."""
        # Preprocess for FaceNet
        # FaceNet typically expects RGB input, 160x160
        if face_image.shape[:2] != (160, 160):
            face_image = cv2.resize(face_image, (160, 160))
            
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # Normalize pixel values to [-1, 1]
        normalized_image = (rgb_image - 127.5) / 128.0
        
        # Add batch dimension
        input_image = np.expand_dims(normalized_image, axis=0).astype(np.float32)
        
        # Run inference using TensorFlow
        embedding = self.model(input_image)[0]
        
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compare two face embeddings and return similarity score.
        
        Args:
            embedding1, embedding2: Face embeddings to compare
            
        Returns:
            Similarity score (higher is more similar, typically 0-1)
        """
        # Using cosine similarity: 1 - cosine distance
        similarity = 1.0 - cosine(embedding1, embedding2)
        return similarity
    
    def find_match(
        self, 
        embedding: np.ndarray,
        return_all_scores: bool = False
    ) -> Union[Dict, Tuple[Dict, Dict]]:
        """
        Find the closest match for a face embedding in the database.
        
        Args:
            embedding: Face embedding to search for
            return_all_scores: Whether to return all similarity scores
            
        Returns:
            If return_all_scores is False:
                Dict with match info: {
                    'id': personnel_id, 
                    'similarity': similarity_score,
                    'is_match': boolean indicating if above threshold
                }
            If return_all_scores is True:
                Tuple of (match_info, all_scores)
                where all_scores is {personnel_id: similarity_score}
        """
        if not self.embeddings_db:
            return {'id': None, 'similarity': 0.0, 'is_match': False}
            
        best_match_id = None
        best_match_score = -1.0
        all_scores = {}
        
        # Compare with all embeddings in database
        for person_id, stored_embedding in self.embeddings_db.items():
            similarity = self.compare_embeddings(embedding, stored_embedding)
            all_scores[person_id] = similarity
            
            if similarity > best_match_score:
                best_match_score = similarity
                best_match_id = person_id
        
        result = {
            'id': best_match_id,
            'similarity': best_match_score,
            'is_match': best_match_score >= self.recognition_threshold
        }
        
        if return_all_scores:
            return result, all_scores
        else:
            return result
            
    def add_to_database(
        self, 
        person_id: str,
        embedding: np.ndarray,
        auto_save: bool = False
    ) -> bool:
        """
        Add a face embedding to the database.
        
        Args:
            person_id: Unique identifier for the person
            embedding: Face embedding to store
            auto_save: Whether to automatically save the updated database
            
        Returns:
            True if added successfully, False otherwise
        """
        if person_id is None or embedding is None:
            return False
        
        # Store the embedding
        self.embeddings_db[person_id] = embedding
        
        # Save if requested
        if auto_save and self.db_path:
            self.save_embeddings_db(self.db_path)
        
        return True
        
    def remove_from_database(
        self, 
        person_id: str,
        auto_save: bool = False
    ) -> bool:
        """
        Remove a person from the embeddings database.
        
        Args:
            person_id: Unique identifier for the person to remove
            auto_save: Whether to automatically save the updated database
            
        Returns:
            True if removed successfully, False if not found
        """
        if person_id in self.embeddings_db:
            del self.embeddings_db[person_id]
            
            # Save if requested
            if auto_save and self.db_path:
                self.save_embeddings_db(self.db_path)
            
            return True
        else:
            return False
        
    def save_embeddings_db(self, path: str) -> bool:
        """
        Save the embeddings database to a file.
        
        Args:
            path: File path to save the database
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                pickle.dump(self.embeddings_db, f)
            self.db_path = path
            logger.info(f"Saved embeddings database with {len(self.embeddings_db)} entries to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save embeddings database: {str(e)}")
            return False
            
    def load_embeddings_db(self, path: str) -> bool:
        """
        Load embeddings database from a file.
        
        Args:
            path: File path to load the database from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(path, 'rb') as f:
                self.embeddings_db = pickle.load(f)
            self.db_path = path
            logger.info(f"Loaded embeddings database with {len(self.embeddings_db)} entries from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load embeddings database: {str(e)}")
            return False
            
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the embeddings database.
        
        Returns:
            Dictionary with stats like count, last modified time, etc.
        """
        stats = {
            'count': len(self.embeddings_db),
            'db_path': self.db_path,
        }
        
        if self.db_path and os.path.exists(self.db_path):
            stats['last_modified'] = datetime.fromtimestamp(
                os.path.getmtime(self.db_path)
            ).strftime('%Y-%m-%d %H:%M:%S')
            stats['size_bytes'] = os.path.getsize(self.db_path)
        
        return stats
        
    def detect_and_recognize(
        self,
        face_image: np.ndarray,
        person_name: Optional[str] = None,
        confidence_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Complete recognition workflow: extract features and find match.
        
        Args:
            face_image: Preprocessed face image
            person_name: If provided, validates if the face belongs to this person
            confidence_threshold: Optional override for recognition threshold
            
        Returns:
            Recognition results
        """
        start_time = time.time()
        
        # Use class threshold if none provided
        if confidence_threshold is None:
            confidence_threshold = self.recognition_threshold
            
        try:
            # Generate embedding
            embedding = self.get_face_embedding(face_image)
            
            # If we're validating a specific person
            if person_name:
                if person_name in self.embeddings_db:
                    stored_embedding = self.embeddings_db[person_name]
                    similarity = self.compare_embeddings(embedding, stored_embedding)
                    
                    result = {
                        'id': person_name,
                        'similarity': float(similarity),
                        'is_match': similarity >= confidence_threshold,
                        'processing_time': time.time() - start_time
                    }
                else:
                    result = {
                        'id': None,
                        'similarity': 0.0,
                        'is_match': False,
                        'error': f"Person {person_name} not found in database",
                        'processing_time': time.time() - start_time
                    }
            else:
                # Find best match
                match_result = self.find_match(embedding)
                match_result['processing_time'] = time.time() - start_time
                result = match_result
            
            return result
        
        except Exception as e:
            logger.error(f"Error in detect_and_recognize: {str(e)}")
            return {
                'id': None,
                'similarity': 0.0,
                'is_match': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
            
    def implement_anti_spoofing(self, face_image: np.ndarray) -> Dict[str, Any]:
        """
        Implement anti-spoofing detection to prevent presentation attacks.
        
        Args:
            face_image: Input face image
            
        Returns:
            Dictionary with anti-spoofing results including:
            - is_real: Boolean indicating if the face is real or a spoof
            - confidence: Confidence score of the detection
            - method: Method(s) used for detection
            - details: Additional details about the analysis
        """
        try:
            # Start time for performance tracking
            start_time = time.time()
            
            # Result dictionary with default values
            result = {
                'is_real': False,
                'confidence': 0.0,
                'method': 'combined',
                'details': {},
                'processing_time': 0.0
            }
            
            # 1. Texture analysis for identifying printed materials
            texture_score = self._analyze_texture_patterns(face_image)
            result['details']['texture_score'] = texture_score
            
            # 2. Eye blink detection for liveness verification
            blink_result = self._detect_eye_blink(face_image)
            result['details']['blink_detection'] = blink_result
            
            # 3. Color variance analysis for screen detection
            color_result = self._analyze_color_variance(face_image)
            result['details']['color_analysis'] = color_result
            
            # 4. Depth analysis (using image cues to simulate depth detection)
            depth_result = self._analyze_depth_cues(face_image)
            result['details']['depth_analysis'] = depth_result
            
            # 5. Reflection analysis for detecting glossy printed materials and screens
            reflection_result = self._detect_reflections(face_image)
            result['details']['reflection_analysis'] = reflection_result
            
            # Calculate weighted confidence score based on all checks
            confidence = (
                texture_score * 0.3 +
                blink_result['score'] * 0.25 +
                color_result['score'] * 0.15 + 
                depth_result['score'] * 0.2 + 
                reflection_result['score'] * 0.1
            )
            
            # Determine if the face is real based on combined confidence
            spoof_threshold = 0.65  # Can be adjusted or made configurable
            is_real = confidence >= spoof_threshold
            
            # Update the result dictionary
            result['is_real'] = is_real
            result['confidence'] = confidence
            result['processing_time'] = time.time() - start_time
            
            logger.debug(f"Anti-spoofing result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in anti-spoofing detection: {str(e)}")
            return {
                'is_real': False,  # Fail closed for security
                'confidence': 0.0,
                'method': 'error',
                'error': str(e),
                'details': {},
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0.0
            }
    
    def _analyze_texture_patterns(self, face_image: np.ndarray) -> float:
        """
        Analyze texture patterns to detect printed materials.
        
        Args:
            face_image: Input face image
            
        Returns:
            Confidence score (0-1) that the image is of a real face
        """
        # Convert to grayscale for texture analysis
        if len(face_image.shape) > 2:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_image.copy()
        
        # Apply Local Binary Pattern (LBP) for texture analysis
        # Simplified version of LBP
        lbp_image = np.zeros_like(gray)
        for i in range(1, gray.shape[0] - 1):
            for j in range(1, gray.shape[1] - 1):
                center = gray[i, j]
                code = 0
                code |= (gray[i-1, j-1] > center) << 0
                code |= (gray[i-1, j] > center) << 1
                code |= (gray[i-1, j+1] > center) << 2
                code |= (gray[i, j+1] > center) << 3
                code |= (gray[i+1, j+1] > center) << 4
                code |= (gray[i+1, j] > center) << 5
                code |= (gray[i+1, j-1] > center) << 6
                code |= (gray[i, j-1] > center) << 7
                lbp_image[i, j] = code
        
        # Calculate LBP histogram
        hist, _ = np.histogram(lbp_image.ravel(), bins=256, range=(0, 256))
        hist = hist.astype('float')
        hist /= (hist.sum() + 1e-7)
        
        # Analyze histogram features
        # Real faces tend to have more varied texture patterns
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        variance = np.var(hist)
        
        # Combine features to determine score
        # Higher entropy and variance usually indicate a real face
        # These thresholds can be fine-tuned
        entropy_score = min(1.0, max(0.0, entropy / 7.5))  # Typical entropy range for real faces
        variance_score = min(1.0, max(0.0, variance * 1000))  # Scale variance to 0-1 range
        
        # Combined score with weights
        score = 0.6 * entropy_score + 0.4 * variance_score
        
        return score
    
    def _detect_eye_blink(self, face_image: np.ndarray) -> Dict[str, Any]:
        """
        Detect eye blinks for liveness verification.
        
        Args:
            face_image: Input face image
            
        Returns:
            Dictionary with blink detection results
        """
        # In a complete implementation, we would analyze multiple frames
        # Since we only have a single image, we'll use eye aspect ratio as a proxy
        try:
            # Convert to grayscale
            if len(face_image.shape) > 2:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image.copy()
            
            # Use OpenCV's Haar cascade to detect eyes
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            if len(eyes) < 2:
                return {'score': 0.4, 'details': 'Unable to detect both eyes'}
            
            # Analyze eye aspect ratio (EAR)
            # Since we can't calculate real EAR without facial landmarks,
            # use a proxy based on eye region intensity and variance
            eye_scores = []
            for (ex, ey, ew, eh) in eyes:
                eye_roi = gray[ey:ey+eh, ex:ex+ew]
                
                # Calculate mean and variance of eye region
                mean_intensity = np.mean(eye_roi)
                variance = np.var(eye_roi)
                
                # Eye openness score based on intensity and variance
                # Open eyes typically have higher variance
                eye_scores.append(min(1.0, variance / 800))
            
            # Average eye openness score
            avg_score = sum(eye_scores) / len(eye_scores)
            
            return {
                'score': avg_score,
                'details': f'Eye regions analyzed: {len(eyes)}'
            }
        
        except Exception as e:
            logger.warning(f"Eye blink detection error: {str(e)}")
            return {'score': 0.5, 'details': f'Analysis error: {str(e)}'}
    
    def _analyze_color_variance(self, face_image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze color variance to detect screens or printouts.
        
        Args:
            face_image: Input face image
            
        Returns:
            Dictionary with color variance analysis results
        """
        try:
            # Ensure we have a color image
            if len(face_image.shape) < 3:
                return {'score': 0.5, 'details': 'Grayscale image provided'}
            
            # Calculate color mean and standard deviation in different channels
            means = []
            stds = []
            
            # Split the image into channels
            channels = cv2.split(face_image)
            for channel in channels:
                means.append(np.mean(channel))
                stds.append(np.std(channel))
            
            # Calculate color ratios
            ratios = []
            for i in range(len(means) - 1):
                for j in range(i + 1, len(means)):
                    if means[j] != 0:
                        ratios.append(means[i] / means[j])
            
            # Real faces tend to have specific color distributions
            # and higher standard deviations in color channels
            avg_std = np.mean(stds)
            
            # Calculate score based on color variance
            # Higher variance usually indicates a real face
            score = min(1.0, avg_std / 50.0)  # Scale to 0-1
            
            # Analyze color ratios for abnormalities
            # Screens often have abnormal color ratios
            ratio_score = 1.0
            for ratio in ratios:
                # Check if ratio is within expected range for human faces
                # Typical R/G ratio is around 1.1-1.3 for most skin tones
                if ratio < 0.7 or ratio > 1.5:
                    ratio_score *= 0.8
            
            # Combined score
            final_score = 0.7 * score + 0.3 * ratio_score
            
            return {
                'score': final_score,
                'details': {
                    'channel_stds': stds,
                    'channel_means': means,
                    'color_ratios': ratios
                }
            }
        
        except Exception as e:
            logger.warning(f"Color variance analysis error: {str(e)}")
            return {'score': 0.5, 'details': f'Analysis error: {str(e)}'}
    
    def _analyze_depth_cues(self, face_image: np.ndarray) -> Dict[str, Any]:
        """
        Analyze depth cues from a single image.
        
        Args:
            face_image: Input face image
            
        Returns:
            Dictionary with depth analysis results
        """
        try:
            # Convert to grayscale
            if len(face_image.shape) > 2:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image.copy()
            
            # Apply Sobel operator to detect edges in X and Y directions
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            
            # Normalize gradient magnitude
            gradient_magnitude = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
            
            # Calculate mean and standard deviation of gradient
            mean_gradient = np.mean(gradient_magnitude)
            std_gradient = np.std(gradient_magnitude)
            
            # Real faces have natural depth transitions and more varied gradients
            # Calculate score based on gradient statistics
            score = min(1.0, max(0.0, (mean_gradient / 40.0) * (std_gradient / 50.0)))
            
            # Check edge distribution
            # Calculate histogram of gradient magnitudes
            hist, _ = np.histogram(gradient_magnitude, bins=50)
            hist = hist.astype('float') / (hist.sum() + 1e-7)
            
            # Calculate entropy of edge distribution
            entropy = -np.sum(hist * np.log2(hist + 1e-7))
            
            # Higher entropy indicates more natural edge distribution
            entropy_score = min(1.0, entropy / 5.0)
            
            # Combine scores
            final_score = 0.6 * score + 0.4 * entropy_score
            
            return {
                'score': final_score,
                'details': {
                    'mean_gradient': float(mean_gradient),
                    'std_gradient': float(std_gradient),
                    'edge_entropy': float(entropy)
                }
            }
        
        except Exception as e:
            logger.warning(f"Depth analysis error: {str(e)}")
            return {'score': 0.5, 'details': f'Analysis error: {str(e)}'}
    
    def _detect_reflections(self, face_image: np.ndarray) -> Dict[str, Any]:
        """
        Detect unnatural reflections that might indicate a screen or glossy printed image.
        
        Args:
            face_image: Input face image
            
        Returns:
            Dictionary with reflection analysis results
        """
        try:
            # Convert to appropriate color space
            hsv = cv2.cvtColor(face_image, cv2.COLOR_BGR2HSV)
            
            # Extract value channel (brightness)
            v_channel = hsv[:,:,2]
            
            # Threshold to find bright spots (potential reflections)
            _, bright_spots = cv2.threshold(v_channel, 220, 255, cv2.THRESH_BINARY)
            
            # Calculate percentage of bright spots
            bright_spot_percentage = np.sum(bright_spots) / (bright_spots.size * 255)
            
            # Calculate distribution of bright spots
            if np.sum(bright_spots) > 0:
                # Get coordinates of bright spots
                y_coords, x_coords = np.where(bright_spots > 0)
                
                if len(x_coords) > 1:
                    # Calculate standard deviation of bright spot positions
                    x_std = np.std(x_coords)
                    y_std = np.std(y_coords)
                    
                    # Calculate spatial distribution score
                    # Well-distributed reflections are more natural
                    distribution_score = min(1.0, (x_std + y_std) / (face_image.shape[0] / 2))
                else:
                    distribution_score = 0.5
            else:
                distribution_score = 0.8  # No bright spots can be good
            
            # Screens and glossy prints often have unnatural reflection patterns
            # Too many bright spots or too concentrated is suspicious
            reflection_score = 0.0
            
            if bright_spot_percentage < 0.01:
                # Very few bright spots - likely real face
                reflection_score = 0.9
            elif bright_spot_percentage > 0.05:
                # Too many bright spots - likely a screen
                reflection_score = 0.2
            else:
                # Moderate number of bright spots - score depends on distribution
                reflection_score = 0.5 + 0.3 * distribution_score
            
            return {
                'score': reflection_score,
                'details': {
                    'bright_spot_percentage': float(bright_spot_percentage),
                    'distribution_score': float(distribution_score) if 'distribution_score' in locals() else 0.0
                }
            }
        
        except Exception as e:
            logger.warning(f"Reflection analysis error: {str(e)}")
            return {'score': 0.5, 'details': f'Analysis error: {str(e)}'}