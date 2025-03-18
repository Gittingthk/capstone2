"""
Cell Analysis Module
Handles cell image capture and analysis using AI models
"""

import cv2
import numpy as np
import tensorflow as tf
import logging
from typing import Dict, Any, Tuple
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class CellAnalyzer:
    def __init__(self, 
                 model_path: str = 'models/cell_analysis_model.h5',
                 camera_index: int = 0,
                 image_size: Tuple[int, int] = (640, 480)):
        """Initialize the cell analyzer"""
        self.image_size = image_size
        self.camera_index = camera_index
        
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(camera_index)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, image_size[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, image_size[1])
            
            # Load AI model
            self.model = self._load_model(model_path)
            
            logger.info("Cell analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cell analyzer: {str(e)}")
            raise
            
    def _load_model(self, model_path: str) -> tf.keras.Model:
        """Load the TensorFlow model for cell analysis"""
        try:
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found at {model_path}")
                # Create a simple model for testing
                return self._create_test_model()
                
            return tf.keras.models.load_model(model_path)
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return self._create_test_model()
            
    def _create_test_model(self) -> tf.keras.Model:
        """Create a simple test model for development"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(64, 64, 3)),
            tf.keras.layers.Conv2D(32, 3, activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(64, 3, activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(2, activation='sigmoid')
        ])
        model.compile(optimizer='adam',
                     loss='binary_crossentropy',
                     metrics=['accuracy'])
        return model
        
    def capture_image(self) -> np.ndarray:
        """Capture an image from the camera"""
        try:
            ret, frame = self.camera.read()
            if not ret:
                raise Exception("Failed to capture image")
                
            # Save image with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"images/cell_image_{timestamp}.jpg"
            os.makedirs("images", exist_ok=True)
            cv2.imwrite(filename, frame)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing image: {str(e)}")
            raise
            
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the image for model input"""
        try:
            # Resize image
            processed = cv2.resize(image, (64, 64))
            
            # Normalize pixel values
            processed = processed.astype(np.float32) / 255.0
            
            # Add batch dimension
            processed = np.expand_dims(processed, axis=0)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
            
    def analyze_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze the cell image and return results"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Run inference
            predictions = self.model.predict(processed_image)
            
            # Extract results
            confluence = self._calculate_confluence(image)
            contamination_score = predictions[0][1]  # Assuming binary classification
            
            results = {
                'confluence': confluence,
                'contamination_detected': contamination_score > 0.5,
                'contamination_probability': float(contamination_score),
                'timestamp': datetime.now().isoformat()
            }
            
            # Log results
            logger.info(f"Analysis results: {results}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise
            
    def _calculate_confluence(self, image: np.ndarray) -> float:
        """Calculate cell confluence percentage"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to segment cells
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Calculate confluence as percentage of white pixels
            confluence = (np.sum(binary > 0) / binary.size) * 100
            
            return confluence
            
        except Exception as e:
            logger.error(f"Error calculating confluence: {str(e)}")
            return 0.0
            
    def close(self):
        """Release resources"""
        try:
            if self.camera is not None:
                self.camera.release()
            logger.info("Cell analyzer resources released")
        except Exception as e:
            logger.error(f"Error closing cell analyzer: {str(e)}")
            
    def __del__(self):
        """Destructor to ensure resources are released"""
        self.close() 