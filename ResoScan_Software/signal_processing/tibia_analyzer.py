"""
ResoScan - Tibia Bone Analysis Module
======================================
Specialized module for tibia fracture healing monitoring

Tibia-specific parameters:
- Normal resonant frequency: 180-220 Hz
- Fractured frequency: 80-150 Hz
- Healing frequency: 100-180 Hz
- TSI threshold for weight-bearing: 80%

Author: ResoScan Team
"""

import numpy as np
from .signal_processor import SignalProcessor, SpectralFeatures
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TibiaAnalyzer:
    """Specialized analyzer for tibia bone measurements"""
    
    # Tibia-specific thresholds (from literature)
    NORMAL_FREQ_MIN = 180
    NORMAL_FREQ_MAX = 220
    
    FRACTURED_FREQ_MIN = 80
    FRACTURED_FREQ_MAX = 150
    
    HEALING_FREQ_MIN = 100
    HEALING_FREQ_MAX = 180
    
    # TSI thresholds for weight-bearing decisions
    TSI_SAFE_LOAD = 80.0        # Safe for full weight bearing
    TSI_PARTIAL_LOAD = 60.0     # Partial weight bearing
    TSI_NO_LOAD = 40.0          # No weight bearing
    
    def __init__(self):
        """Initialize tibia analyzer"""
        self.processor = SignalProcessor()
        self.measurement_history = []
    
    def analyze_single_measurement(self, signal: np.ndarray, 
                                   sampling_rate: int = 3200) -> Dict:
        """
        Analyze single tibia measurement
        
        Args:
            signal: Accelerometer signal from tibia
            sampling_rate: Sampling rate in Hz
            
        Returns:
            Dictionary with analysis results
        """
        # Process signal
        features = self.processor.process_raw_signal(signal, timestamp=0.0)
        
        freq = features.resonant_frequency
        q_factor = features.q_factor
        
        # Classify tissue state based on frequency
        if self.NORMAL_FREQ_MIN <= freq <= self.NORMAL_FREQ_MAX:
            tissue_state = "HEALTHY"
            confidence = 0.9
        elif self.HEALING_FREQ_MIN <= freq <= self.HEALING_FREQ_MAX:
            tissue_state = "HEALING"
            confidence = 0.85
        elif self.FRACTURED_FREQ_MIN <= freq <= self.FRACTURED_FREQ_MAX:
            tissue_state = "FRACTURED"
            confidence = 0.8
        else:
            tissue_state = "UNKNOWN"
            confidence = 0.5
        
        result = {
            'frequency_hz': freq,
            'q_factor': q_factor,
            'tissue_state': tissue_state,
            'confidence': confidence,
            'snr_db': self._estimate_snr(features),
            'amplitude': features.resonant_amplitude,
            'damping_ratio': features.damping_ratio,
            'spectral_centroid': features.spectral_centroid,
        }
        
        logger.info(f"Tibia Analysis: {tissue_state} at {freq:.1f} Hz (Q={q_factor:.2f})")
        return result
    
    def calculate_tsi_single_side(self, signal: np.ndarray,
                                   reference_freq: float = 200.0) -> float:
        """
        Calculate TSI for single measurement
        TSI = (measured_freq / reference_freq) × 100%
        (Linear relationship, not squared)
        
        Args:
            signal: Accelerometer signal
            reference_freq: Reference frequency for healthy bone (default 200 Hz)
            
        Returns:
            TSI percentage (0-100%)
        """
        features = self.processor.process_raw_signal(signal)
        measured_freq = features.resonant_frequency
        
        if measured_freq > 0:
            # Linear TSI calculation - frequency ratio times 100
            tsi = (measured_freq / reference_freq) * 100
            tsi = np.clip(tsi, 0, 100)
            return tsi
        return 0.0
    
    def compare_bilateral(self, healthy_signal: np.ndarray,
                         injured_signal: np.ndarray) -> Dict:
        """
        Compare healthy vs injured tibia (bilateral comparison)
        
        Args:
            healthy_signal: Signal from healthy side
            injured_signal: Signal from injured side
            
        Returns:
            Comparison dictionary with TSI and recommendations
        """
        # Process both sides
        healthy_features = self.processor.process_raw_signal(healthy_signal)
        injured_features = self.processor.process_raw_signal(injured_signal)
        
        # Calculate TSI (linear frequency ratio)
        f_healthy = healthy_features.resonant_frequency
        f_injured = injured_features.resonant_frequency
        
        tsi = (f_injured / f_healthy) * 100 if f_healthy > 0 else 0.0
        tsi = np.clip(tsi, 0, 100)
        
        # Determine weight-bearing status
        if tsi >= self.TSI_SAFE_LOAD:
            weight_bearing = "FULL WEIGHT BEARING - Safe to resume normal activity"
        elif tsi >= self.TSI_PARTIAL_LOAD:
            weight_bearing = "PARTIAL WEIGHT BEARING - Supervised activity only"
        elif tsi >= self.TSI_NO_LOAD:
            weight_bearing = "NO WEIGHT BEARING - Avoid loading"
        else:
            weight_bearing = "ACUTE PHASE - Immobilization recommended"
        
        result = {
            'tsi_percentage': tsi,
            'healthy_freq_hz': f_healthy,
            'injured_freq_hz': f_injured,
            'q_factor_healthy': healthy_features.q_factor,
            'q_factor_injured': injured_features.q_factor,
            'weight_bearing_status': weight_bearing,
            'healing_days_estimate': self._estimate_healing_days(tsi),
        }
        
        logger.info(f"Tibia TSI: {tsi:.1f}% | Status: {weight_bearing}")
        return result
    
    def _estimate_healing_days(self, tsi: float) -> int:
        """
        Estimate healing days based on TSI
        Empirical model: ~2-3 TSI points per day
        
        Args:
            tsi: TSI percentage
            
        Returns:
            Estimated days since fracture
        """
        if tsi < 40:
            return 0  # Acute (0-3 days)
        elif tsi < 60:
            return int((tsi - 40) / 2) + 3  # Early healing (3-10 days)
        elif tsi < 80:
            return int((tsi - 60) / 1.5) + 10  # Active healing (10-30 days)
        else:
            return int((tsi - 80) / 1) + 30  # Late healing (30+ days)
    
    def _estimate_snr(self, features: SpectralFeatures) -> float:
        """
        Estimate SNR from features
        
        Args:
            features: Spectral features
            
        Returns:
            Estimated SNR in dB
        """
        psd = features.power_spectral_density
        if len(psd) > 0:
            peak_power = np.max(psd)
            noise_floor = np.median(psd)
            snr = 10 * np.log10(peak_power / (noise_floor + 1e-10))
            return snr
        return 0.0
    
    def track_healing_progression(self, daily_signals: list) -> Dict:
        """
        Track healing progression over multiple days
        
        Args:
            daily_signals: List of signals from consecutive days
            
        Returns:
            Progression report with trends
        """
        tsi_values = []
        frequencies = []
        
        for signal in daily_signals:
            features = self.processor.process_raw_signal(signal)
            freq = features.resonant_frequency
            frequencies.append(freq)
            
            # Use first signal as reference
            if len(frequencies) == 1:
                reference_freq = freq
            
            # Linear TSI calculation (frequency ratio × 100)
            tsi = (freq / reference_freq) * 100
            tsi = np.clip(tsi, 0, 100)
            tsi_values.append(tsi)
        
        # Calculate progression rate
        if len(tsi_values) > 1:
            daily_progress = (tsi_values[-1] - tsi_values[0]) / (len(tsi_values) - 1)
        else:
            daily_progress = 0.0
        
        progression = {
            'tsi_initial': tsi_values[0],
            'tsi_current': tsi_values[-1],
            'tsi_improvement': tsi_values[-1] - tsi_values[0],
            'daily_progress': daily_progress,
            'frequencies': frequencies,
            'measurements_count': len(tsi_values),
            'estimated_weight_bearing': self.TSI_SAFE_LOAD - tsi_values[-1],  # Days to full healing
        }
        
        logger.info(f"Healing Progression: {tsi_values[-1]:.1f}% (improved {daily_progress:.2f}%/day)")
        return progression


# Example usage for tibia-specific analysis
if __name__ == "__main__":
    import numpy as np
    
    print("="*80)
    print("RESOSCAN - TIBIA BONE ANALYSIS")
    print("="*80)
    
    analyzer = TibiaAnalyzer()
    
    # Create synthetic healthy tibia signal (200 Hz resonance)
    fs = 3200
    duration = 1.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Healthy tibia: High amplitude at 200 Hz, lower damping
    freq_healthy = 200
    amplitude_healthy = 0.8
    damping_healthy = 0.02  # Low damping (high Q)
    healthy_signal = amplitude_healthy * np.exp(-damping_healthy * 2 * np.pi * freq_healthy * t) * np.sin(2 * np.pi * freq_healthy * t)
    healthy_signal += 0.005 * np.random.randn(len(t))  # Low noise
    
    # Fractured tibia: Lower amplitude at 120 Hz, higher damping
    freq_fractured = 120
    amplitude_fractured = 0.4
    damping_fractured = 0.08  # Higher damping (lower Q)
    fractured_signal = amplitude_fractured * np.exp(-damping_fractured * 2 * np.pi * freq_fractured * t) * np.sin(2 * np.pi * freq_fractured * t)
    fractured_signal += 0.01 * np.random.randn(len(t))  # Low noise
    
    # Analyze
    print("\n[1] Single Side Analysis")
    print("-" * 80)
    result = analyzer.analyze_single_measurement(healthy_signal)
    print(f"Healthy Tibia: {result['tissue_state']} at {result['frequency_hz']:.1f} Hz")
    
    result = analyzer.analyze_single_measurement(fractured_signal)
    print(f"Fractured Tibia: {result['tissue_state']} at {result['frequency_hz']:.1f} Hz")
    
    print("\n[2] Bilateral Comparison")
    print("-" * 80)
    comparison = analyzer.compare_bilateral(healthy_signal, fractured_signal)
    print(f"TSI: {comparison['tsi_percentage']:.1f}%")
    print(f"Status: {comparison['weight_bearing_status']}")
    print(f"Estimated days since fracture: {comparison['healing_days_estimate']}")
    
    print("\n[3] Healing Progression Tracking")
    print("-" * 80)
    # Simulate 7 days of healing (frequency increases from 120 to 200 Hz)
    daily_signals = []
    for day in range(7):
        freq_day = 120 + day * 12  # Frequency increases with healing
        sig = 0.4 * np.exp(-0.08 * 2 * np.pi * freq_day * t) * np.sin(2 * np.pi * freq_day * t)
        sig += 0.01 * np.random.randn(len(t))  # Low noise
        daily_signals.append(sig)
    
    progression = analyzer.track_healing_progression(daily_signals)
    print(f"Initial TSI: {progression['tsi_initial']:.1f}%")
    print(f"Current TSI: {progression['tsi_current']:.1f}%")
    print(f"Improvement: {progression['tsi_improvement']:.1f}%")
    print(f"Daily progress: {progression['daily_progress']:.2f}%/day")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)
