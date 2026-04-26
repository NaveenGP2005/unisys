"""
ResoScan Unit Tests
===================
Comprehensive test suite for all software modules

Author: ResoScan Team
"""

import unittest
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from signal_processing.signal_processor import SignalProcessor, SignalConfig, SpectralFeatures
from ml_models.classifier import (
    FeatureExtractor, FractureHealingClassifier,
    TissueAbnormalityDetector, generate_synthetic_training_data
)


class TestSignalProcessor(unittest.TestCase):
    """Test signal processing module"""
    
    def setUp(self):
        self.processor = SignalProcessor()
        self.fs = 3200
        self.duration = 1.0
        self.t = np.linspace(0, self.duration, int(self.fs * self.duration), endpoint=False)
    
    def test_initialization(self):
        """Test signal processor initialization"""
        self.assertIsNotNone(self.processor)
        self.assertEqual(self.processor.config.sampling_rate, 3200)
        self.assertEqual(self.processor.config.fft_points, 1024)
    
    def test_generate_test_signal(self):
        """Generate and verify test signal"""
        f_res = 150
        zeta = 0.1
        omega_n = 2 * np.pi * f_res
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        
        signal = 0.5 * np.exp(-zeta * omega_n * self.t) * np.sin(omega_d * self.t)
        
        self.assertEqual(len(signal), len(self.t))
        self.assertGreater(np.max(signal), 0)
        self.assertLess(np.min(signal), 0)
    
    def test_process_raw_signal(self):
        """Test signal processing pipeline"""
        f_res = 150
        zeta = 0.1
        omega_n = 2 * np.pi * f_res
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        
        signal = 0.5 * np.exp(-zeta * omega_n * self.t) * np.sin(omega_d * self.t)
        
        features = self.processor.process_raw_signal(signal)
        
        self.assertIsInstance(features, SpectralFeatures)
        self.assertGreater(features.resonant_frequency, 0)
        self.assertGreater(features.q_factor, 0)
        self.assertGreater(features.damping_ratio, 0)
    
    def test_resonant_frequency_detection(self):
        """Test resonant frequency is correctly detected"""
        expected_freq = 200
        zeta = 0.05
        omega_n = 2 * np.pi * expected_freq
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        
        signal = 0.5 * np.exp(-zeta * omega_n * self.t) * np.sin(omega_d * self.t)
        
        features = self.processor.process_raw_signal(signal)
        
        # Allow 5% error margin
        error_percent = abs(features.resonant_frequency - expected_freq) / expected_freq * 100
        self.assertLess(error_percent, 5, f"Frequency detection error: {error_percent:.1f}%")
    
    def test_tissue_stiffness_index(self):
        """Test TSI calculation for fracture healing"""
        f_healthy = 200
        f_injured = 150
        
        # Create healthy signal
        zeta = 0.05
        omega_n = 2 * np.pi * f_healthy
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        healthy_signal = 0.8 * np.exp(-zeta * omega_n * self.t) * np.sin(omega_d * self.t)
        
        # Create injured signal
        zeta_inj = 0.1
        omega_n_inj = 2 * np.pi * f_injured
        omega_d_inj = omega_n_inj * np.sqrt(1 - zeta_inj**2)
        injured_signal = 0.5 * np.exp(-zeta_inj * omega_n_inj * self.t) * np.sin(omega_d_inj * self.t)
        
        healthy_features = self.processor.process_raw_signal(healthy_signal)
        injured_features = self.processor.process_raw_signal(injured_signal)
        
        tsi = self.processor.calculate_tissue_stiffness_index(healthy_features, injured_features)
        
        # TSI should be between 0 and 100
        self.assertGreater(tsi, 0)
        self.assertLess(tsi, 100)
        
        # TSI should be less than 100% (injured < healthy)
        self.assertLess(tsi, 100)
        
        # Clinical interpretation
        if tsi > 80:
            status = "Safe for weight-bearing"
        elif tsi > 50:
            status = "Partial healing"
        else:
            status = "Active healing"
        
        self.assertIn(status, ["Safe for weight-bearing", "Partial healing", "Active healing"])
    
    def test_pneumothorax_index(self):
        """Test pneumothorax detection index"""
        # Healthy lung
        healthy_signal = 0.5 * np.sin(2 * np.pi * 300 * self.t)
        
        # Affected lung (hyper-resonant)
        affected_signal = 0.8 * np.sin(2 * np.pi * 300 * self.t)
        
        healthy_features = self.processor.process_raw_signal(healthy_signal)
        affected_features = self.processor.process_raw_signal(affected_signal)
        
        power_ratio = self.processor.calculate_pneumotharax_index(affected_features, healthy_features)
        
        self.assertGreater(power_ratio, 0)
    
    def test_feature_extraction(self):
        """Test spectral feature extraction"""
        f_res = 150
        signal = 0.5 * np.sin(2 * np.pi * f_res * self.t)
        
        features = self.processor.process_raw_signal(signal)
        
        # Verify all features are present
        self.assertGreater(features.resonant_frequency, 0)
        self.assertGreater(features.q_factor, 0)
        self.assertGreater(features.spectral_centroid, 0)
        self.assertGreater(len(features.peak_frequencies), 0)
        self.assertEqual(len(features.peak_frequencies), len(features.peak_amplitudes))


class TestFeatureExtractor(unittest.TestCase):
    """Test ML feature extraction"""
    
    def setUp(self):
        self.processor = SignalProcessor()
        self.t = np.linspace(0, 1, 3200, endpoint=False)
    
    def test_feature_vector_dimensions(self):
        """Test feature vector is 17-dimensional"""
        signal = 0.5 * np.sin(2 * np.pi * 150 * self.t)
        features = self.processor.process_raw_signal(signal)
        
        feature_vector = FeatureExtractor.extract_features(features)
        
        self.assertEqual(len(feature_vector), 17)
    
    def test_feature_extraction_consistency(self):
        """Test feature extraction is consistent"""
        signal = 0.5 * np.sin(2 * np.pi * 150 * self.t)
        features = self.processor.process_raw_signal(signal)
        
        vector1 = FeatureExtractor.extract_features(features)
        vector2 = FeatureExtractor.extract_features(features)
        
        np.testing.assert_array_almost_equal(vector1, vector2)
    
    def test_batch_feature_extraction(self):
        """Test batch feature extraction"""
        signals = []
        for _ in range(5):
            signal = 0.5 * np.sin(2 * np.pi * 150 * self.t)
            features = self.processor.process_raw_signal(signal)
            signals.append(features)
        
        batch_features = FeatureExtractor.extract_batch_features(signals)
        
        self.assertEqual(batch_features.shape[0], 5)
        self.assertEqual(batch_features.shape[1], 17)


class TestMLClassifiers(unittest.TestCase):
    """Test ML classification models"""
    
    def setUp(self):
        self.X, self.y = generate_synthetic_training_data(200)
    
    def test_synthetic_data_generation(self):
        """Test synthetic data generation"""
        self.assertEqual(self.X.shape[0], 200)
        self.assertEqual(self.X.shape[1], 14)  # 14 feature dimensions
        self.assertEqual(len(self.y), 200)
        self.assertEqual(len(np.unique(self.y)), 2)  # Binary classification
    
    def test_tissue_abnormality_detector_training(self):
        """Test tissue abnormality detector training"""
        model = TissueAbnormalityDetector()
        
        self.assertFalse(model.is_trained)
        
        # Split data
        split = int(0.8 * len(self.X))
        X_train, X_test = self.X[:split], self.X[split:]
        y_train, y_test = self.y[:split], self.y[split:]
        
        # Train
        model.train(X_train, y_train, X_test, y_test)
        
        self.assertTrue(model.is_trained)
        self.assertGreater(model.training_accuracy, 0.6)
    
    def test_tissue_abnormality_detector_prediction(self):
        """Test tissue abnormality detector prediction"""
        model = TissueAbnormalityDetector()
        
        # Train
        split = int(0.8 * len(self.X))
        X_train, y_train = self.X[:split], self.y[:split]
        model.train(X_train, y_train)
        
        # Predict
        result = model.predict(self.X[0:1])
        
        self.assertIsNotNone(result)
        self.assertIn(result.prediction, ['Normal', 'Abnormal'])
        self.assertGreater(result.confidence, 0)
        self.assertLess(result.confidence, 1)
        self.assertGreater(result.probability_normal, 0)
        self.assertGreater(result.probability_abnormal, 0)
    
    def test_fracture_healing_classifier(self):
        """Test fracture healing classifier"""
        model = FractureHealingClassifier()
        
        # Generate multiclass labels
        y_multiclass = np.random.randint(0, 3, len(self.y))
        
        # Split data
        split = int(0.8 * len(self.X))
        X_train, y_train = self.X[:split], y_multiclass[:split]
        
        # Train
        model.train(X_train, y_train)
        
        self.assertTrue(model.is_trained)
        
        # Predict
        result = model.predict(self.X[0:1])
        
        self.assertIsNotNone(result)
        self.assertIn(result.prediction, ['Healing', 'Partially-Healed', 'Healed'])


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_complete_workflow(self):
        """Test complete diagnostic workflow"""
        # 1. Generate signal
        fs = 3200
        duration = 1.0
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        
        f_res = 150
        zeta = 0.1
        omega_n = 2 * np.pi * f_res
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        signal = 0.5 * np.exp(-zeta * omega_n * t) * np.sin(omega_d * t)
        
        # 2. Process signal
        processor = SignalProcessor()
        features = processor.process_raw_signal(signal)
        
        # 3. Extract ML features
        ml_features = FeatureExtractor.extract_features(features)
        
        # 4. Train and predict with ML model
        X_train, y_train = generate_synthetic_training_data(200)
        model = TissueAbnormalityDetector()
        model.train(X_train[:int(0.8*len(X_train))], y_train[:int(0.8*len(y_train))])
        
        result = model.predict(ml_features.reshape(1, -1))
        
        # Verify complete workflow
        self.assertIsNotNone(features)
        self.assertIsNotNone(ml_features)
        self.assertIsNotNone(result)
        self.assertIn(result.prediction, ['Normal', 'Abnormal'])


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSignalProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestMLClassifiers))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
