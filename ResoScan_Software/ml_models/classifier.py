"""
ResoScan Machine Learning Classification Module
================================================
Trains and deploys ML models for tissue diagnosis

Models:
- Random Forest: Tissue state classification (Normal/Abnormal)
- SVM: Material stiffness prediction
- Neural Network: Multi-condition classification

Author: ResoScan Team
"""

import numpy as np
import json
import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import logging

# ML Libraries
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of ML classification"""
    prediction: str                    # 'Normal' or 'Abnormal'
    confidence: float                  # 0.0 to 1.0
    probability_normal: float
    probability_abnormal: float
    feature_importance: Dict[str, float]
    timestamp: float


class FeatureExtractor:
    """Extract ML-ready features from spectral data"""
    
    @staticmethod
    def extract_features(spectral_features) -> np.ndarray:
        """
        Extract comprehensive feature vector from spectral features
        
        Features (17-dimensional):
        0. Resonant frequency (Hz)
        1. Resonant amplitude (g)
        2. Q-factor
        3. Damping ratio
        4. Spectral centroid (Hz)
        5. Peak count
        6. Bandwidth (Hz)
        7. Peak-to-noise ratio
        8-16. Top 3 peak frequencies and amplitudes (9 values)
        
        Args:
            spectral_features: SpectralFeatures object
            
        Returns:
            Feature vector as numpy array
        """
        features = []
        
        # Basic spectral features
        features.append(spectral_features.resonant_frequency)
        features.append(spectral_features.resonant_amplitude)
        features.append(spectral_features.q_factor)
        features.append(spectral_features.damping_ratio)
        features.append(spectral_features.spectral_centroid)
        
        # Peak analysis
        num_peaks = len(spectral_features.peak_frequencies)
        features.append(num_peaks)
        
        # Bandwidth from first peak
        if len(spectral_features.peak_frequencies) > 0:
            peak_freq = spectral_features.peak_frequencies[0]
            # Approximate bandwidth
            if spectral_features.q_factor > 0:
                bandwidth = peak_freq / spectral_features.q_factor
            else:
                bandwidth = 1.0
            features.append(bandwidth)
        else:
            features.append(0.0)
        
        # Peak-to-noise ratio
        psd = spectral_features.power_spectral_density
        if len(psd) > 0:
            peak_power = np.max(psd)
            noise_floor = np.median(psd)
            pnr = peak_power / (noise_floor + 1e-10)
            features.append(pnr)
        else:
            features.append(0.0)
        
        # Top 3 peaks (frequencies and amplitudes)
        for i in range(3):
            if i < len(spectral_features.peak_frequencies):
                features.append(spectral_features.peak_frequencies[i])
            else:
                features.append(0.0)
        
        for i in range(3):
            if i < len(spectral_features.peak_amplitudes):
                features.append(spectral_features.peak_amplitudes[i])
            else:
                features.append(0.0)
        
        return np.array(features, dtype=np.float32)
    
    @staticmethod
    def extract_batch_features(spectral_features_list: List) -> np.ndarray:
        """Extract features from multiple measurements"""
        features_list = []
        for sf in spectral_features_list:
            features_list.append(FeatureExtractor.extract_features(sf))
        return np.vstack(features_list)


class DiagnosticModel:
    """
    Base diagnostic model class
    Implements training, prediction, and model persistence
    """
    
    def __init__(self, model_name: str = "ResoScan_Model"):
        self.model_name = model_name
        self.classifier = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'resonant_frequency', 'resonant_amplitude', 'q_factor', 'damping_ratio',
            'spectral_centroid', 'num_peaks', 'bandwidth', 'peak_to_noise_ratio',
            'peak1_freq', 'peak2_freq', 'peak3_freq',
            'peak1_amp', 'peak2_amp', 'peak3_amp'
        ]
        self.is_trained = False
        self.training_accuracy = 0.0
        self.test_accuracy = 0.0
    
    def save_model(self, filepath: str):
        """Save trained model to disk"""
        if not self.is_trained:
            logger.warning("Model not trained yet")
            return False
        
        try:
            model_data = {
                'classifier': self.classifier,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'training_accuracy': self.training_accuracy,
                'test_accuracy': self.test_accuracy
            }
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model from disk"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.classifier = model_data['classifier']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.training_accuracy = model_data['training_accuracy']
            self.test_accuracy = model_data['test_accuracy']
            self.is_trained = True
            
            logger.info(f"Model loaded from {filepath}")
            logger.info(f"Training accuracy: {self.training_accuracy:.2%}")
            logger.info(f"Test accuracy: {self.test_accuracy:.2%}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class FractureHealingClassifier(DiagnosticModel):
    """
    Classification model for fracture healing monitoring
    Predicts: Healing / Healed / Partially-Healed
    """
    
    def __init__(self):
        super().__init__("FractureHealing_RFC")
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.classes = ['Healing', 'Partially-Healed', 'Healed']
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_test: np.ndarray = None, y_test: np.ndarray = None):
        """Train fracture healing classifier"""
        try:
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            # Train classifier
            self.classifier.fit(X_train_scaled, y_train)
            self.training_accuracy = self.classifier.score(X_train_scaled, y_train)
            
            if X_test is not None and y_test is not None:
                X_test_scaled = self.scaler.transform(X_test)
                self.test_accuracy = self.classifier.score(X_test_scaled, y_test)
                logger.info(f"Test accuracy: {self.test_accuracy:.2%}")
                logger.info(f"\nClassification Report:\n{classification_report(y_test, self.classifier.predict(X_test_scaled))}")
            
            self.is_trained = True
            logger.info(f"Training accuracy: {self.training_accuracy:.2%}")
            logger.info(f"Model trained: {self.model_name}")
            
            return True
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def predict(self, features: np.ndarray) -> ClassificationResult:
        """Predict fracture healing state"""
        if not self.is_trained:
            logger.error("Model not trained")
            return None
        
        try:
            # Ensure 2D input
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            features_scaled = self.scaler.transform(features)
            
            # Get prediction and probabilities
            prediction_idx = self.classifier.predict(features_scaled)[0]
            prediction_label = self.classes[prediction_idx]
            
            probabilities = self.classifier.predict_proba(features_scaled)[0]
            confidence = float(np.max(probabilities))
            
            # Feature importance
            feature_importance = {
                name: float(importance)
                for name, importance in zip(self.feature_names[:len(self.classifier.feature_importances_)],
                                            self.classifier.feature_importances_)
            }
            
            result = ClassificationResult(
                prediction=prediction_label,
                confidence=confidence,
                probability_normal=float(probabilities[2]),  # 'Healed'
                probability_abnormal=float(probabilities[0]),  # 'Healing'
                feature_importance=feature_importance,
                timestamp=0.0
            )
            
            logger.info(f"Prediction: {prediction_label} ({confidence:.1%} confidence)")
            return result
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None


class TissueAbnormalityDetector(DiagnosticModel):
    """
    Binary classifier for tissue abnormality detection
    Predicts: Normal / Abnormal
    Uses SVM with RBF kernel
    """
    
    def __init__(self):
        super().__init__("TissueAbnormality_SVM")
        self.classifier = SVC(
            kernel='rbf',
            gamma='scale',
            probability=True,
            random_state=42
        )
        self.classes = ['Normal', 'Abnormal']
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_test: np.ndarray = None, y_test: np.ndarray = None):
        """Train abnormality detector"""
        try:
            X_train_scaled = self.scaler.fit_transform(X_train)
            
            self.classifier.fit(X_train_scaled, y_train)
            self.training_accuracy = self.classifier.score(X_train_scaled, y_train)
            
            if X_test is not None and y_test is not None:
                X_test_scaled = self.scaler.transform(X_test)
                self.test_accuracy = self.classifier.score(X_test_scaled, y_test)
                logger.info(f"Test accuracy: {self.test_accuracy:.2%}")
            
            self.is_trained = True
            logger.info(f"Training accuracy: {self.training_accuracy:.2%}")
            return True
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return False
    
    def predict(self, features: np.ndarray) -> ClassificationResult:
        """Predict tissue normality"""
        if not self.is_trained:
            logger.error("Model not trained")
            return None
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            features_scaled = self.scaler.transform(features)
            
            prediction_idx = self.classifier.predict(features_scaled)[0]
            prediction_label = self.classes[prediction_idx]
            
            probabilities = self.classifier.predict_proba(features_scaled)[0]
            confidence = float(np.max(probabilities))
            
            result = ClassificationResult(
                prediction=prediction_label,
                confidence=confidence,
                probability_normal=float(probabilities[0]),
                probability_abnormal=float(probabilities[1]),
                feature_importance={},
                timestamp=0.0
            )
            
            logger.info(f"Prediction: {prediction_label} ({confidence:.1%} confidence)")
            return result
        
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None


def generate_synthetic_training_data(n_samples: int = 200) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training data for demonstration
    In production, use real clinical data
    """
    logger.info(f"Generating {n_samples} synthetic training samples...")
    
    X = []
    y = []
    
    # Class 0: Normal tissue
    for _ in range(n_samples // 2):
        features = np.array([
            np.random.normal(200, 30),     # resonant_frequency (Hz)
            np.random.normal(0.8, 0.1),    # resonant_amplitude (g)
            np.random.normal(15, 3),       # q_factor
            np.random.normal(0.035, 0.01), # damping_ratio
            np.random.normal(250, 50),     # spectral_centroid (Hz)
            np.random.poisson(8),          # num_peaks
            np.random.normal(15, 5),       # bandwidth
            np.random.normal(20, 5),       # peak_to_noise_ratio
            np.random.normal(200, 30),     # peak1_freq
            np.random.normal(450, 50),     # peak2_freq
            np.random.normal(700, 100),    # peak3_freq
            np.random.normal(0.7, 0.15),   # peak1_amp
            np.random.normal(0.4, 0.1),    # peak2_amp
            np.random.normal(0.2, 0.05),   # peak3_amp
        ])
        X.append(features)
        y.append(0)  # Normal
    
    # Class 1: Abnormal tissue
    for _ in range(n_samples // 2):
        features = np.array([
            np.random.normal(120, 40),     # resonant_frequency (Hz) - lower
            np.random.normal(0.5, 0.2),    # resonant_amplitude (g) - lower
            np.random.normal(8, 3),        # q_factor - lower
            np.random.normal(0.08, 0.02),  # damping_ratio - higher
            np.random.normal(180, 60),     # spectral_centroid (Hz) - lower
            np.random.poisson(5),          # num_peaks - fewer
            np.random.normal(25, 8),       # bandwidth - wider
            np.random.normal(8, 3),        # peak_to_noise_ratio - lower
            np.random.normal(120, 40),     # peak1_freq
            np.random.normal(300, 70),     # peak2_freq
            np.random.normal(550, 120),    # peak3_freq
            np.random.normal(0.4, 0.2),    # peak1_amp
            np.random.normal(0.2, 0.1),    # peak2_amp
            np.random.normal(0.1, 0.05),   # peak3_amp
        ])
        X.append(features)
        y.append(1)  # Abnormal
    
    return np.array(X), np.array(y)


def demo_ml_classification():
    """Demonstration of ML classification capabilities"""
    logger.info("=== ResoScan ML Classification Demo ===\n")
    
    # Generate synthetic data
    X, y = generate_synthetic_training_data(500)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train fracture healing classifier
    logger.info("--- Training Fracture Healing Classifier ---")
    healing_model = FractureHealingClassifier()
    
    # Convert binary labels to multiclass for demonstration
    y_train_multiclass = np.random.randint(0, 3, len(y_train))
    y_test_multiclass = np.random.randint(0, 3, len(y_test))
    
    healing_model.train(X_train, y_train_multiclass, X_test, y_test_multiclass)
    
    # Save model
    model_path = "fracture_healing_model.pkl"
    healing_model.save_model(model_path)
    
    # Predict on test sample
    logger.info("\n--- Predicting on New Sample ---")
    test_sample = X_test[0:1]
    result = healing_model.predict(test_sample)
    logger.info(f"Prediction: {result.prediction}")
    logger.info(f"Confidence: {result.confidence:.1%}")
    
    # Train abnormality detector
    logger.info("\n--- Training Tissue Abnormality Detector ---")
    abnormality_model = TissueAbnormalityDetector()
    abnormality_model.train(X_train, y_train, X_test, y_test)
    
    # Predict
    result_abnormal = abnormality_model.predict(test_sample)
    logger.info(f"Prediction: {result_abnormal.prediction}")
    logger.info(f"Confidence: {result_abnormal.confidence:.1%}")
    
    logger.info("\n✓ ML Demo Complete")


if __name__ == "__main__":
    demo_ml_classification()
