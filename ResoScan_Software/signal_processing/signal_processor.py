"""
ResoScan Signal Processing Module
==================================
Handles FFT analysis, feature extraction, and spectral analysis
of tissue resonance data from the ADXL343 accelerometer.

Author: ResoScan Team
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
import json
from dataclasses import dataclass, asdict
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SignalConfig:
    """Configuration for signal processing"""
    sampling_rate: int = 3200          # Hz
    fft_points: int = 1024
    window_type: str = "hann"          # Hanning window
    freq_min: float = 20.0             # Hz
    freq_max: float = 1000.0           # Hz
    prominence_threshold: float = 0.1  # For peak detection


@dataclass
class SpectralFeatures:
    """Extracted spectral features from tissue resonance"""
    resonant_frequency: float          # Hz - Primary resonant peak
    resonant_amplitude: float          # g (acceleration units)
    q_factor: float                    # Quality factor = f_res / bandwidth
    damping_ratio: float               # ζ = 1 / (2 * Q)
    spectral_centroid: float           # Hz - Center of mass of spectrum
    peak_frequencies: List[float]      # Hz - All detected peaks
    peak_amplitudes: List[float]       # g - Amplitudes of peaks
    power_spectral_density: np.ndarray # PSD array
    frequency_axis: np.ndarray         # Frequency axis for PSD
    raw_data: np.ndarray              # Original acceleration data
    timestamp: float                   # Seconds since epoch


class SignalProcessor:
    """
    Core signal processing for ResoScan
    Transforms raw accelerometer data into clinical features
    """
    
    def __init__(self, config: SignalConfig = None):
        """Initialize signal processor"""
        self.config = config or SignalConfig()
        logger.info(f"SignalProcessor initialized: {self.config.sampling_rate} Hz, "
                   f"{self.config.fft_points} FFT points")
    
    def process_raw_signal(self, raw_accel_data: np.ndarray, 
                          timestamp: float = None) -> SpectralFeatures:
        """
        Complete signal processing pipeline:
        1. Windowing (Hanning)
        2. FFT analysis
        3. Peak detection
        4. Feature extraction
        
        Args:
            raw_accel_data: 1D array of acceleration samples (g)
            timestamp: Unix timestamp of measurement
            
        Returns:
            SpectralFeatures object with all extracted features
        """
        if len(raw_accel_data) < self.config.fft_points:
            logger.warning(f"Insufficient data: {len(raw_accel_data)} < {self.config.fft_points}")
            # Pad with zeros
            raw_accel_data = np.pad(raw_accel_data, 
                                   (0, self.config.fft_points - len(raw_accel_data)))
        
        # Trim or select first N points
        raw_accel_data = raw_accel_data[:self.config.fft_points]
        
        # Step 1: Apply window function (Hanning)
        window = signal.get_window(self.config.window_type, len(raw_accel_data))
        windowed_data = raw_accel_data * window
        
        # Step 2: Compute FFT and Power Spectral Density
        fft_result = fft(windowed_data)
        psd = np.abs(fft_result) ** 2 / (self.config.sampling_rate * len(windowed_data))
        
        # One-sided spectrum
        psd_one_sided = 2 * psd[:len(psd)//2]
        freq_axis = fftfreq(len(windowed_data), 1/self.config.sampling_rate)[:len(psd)//2]
        
        # Step 3: Detect peaks in the spectrum
        peaks, properties = signal.find_peaks(
            psd_one_sided,
            prominence=self.config.prominence_threshold,
            distance=5  # Min distance between peaks
        )
        
        if len(peaks) == 0:
            logger.warning("No peaks detected in spectrum")
            peaks = np.array([np.argmax(psd_one_sided)])
        
        # Sort peaks by prominence
        peak_prominences = properties['prominences']
        sorted_idx = np.argsort(peak_prominences)[::-1]  # Descending
        peaks = peaks[sorted_idx]
        
        # Step 4: Extract features
        resonant_idx = peaks[0]
        resonant_freq = freq_axis[resonant_idx]
        resonant_amp = np.sqrt(psd_one_sided[resonant_idx]) * 9.81  # Convert to m/s²
        
        # Q-factor calculation
        q_factor = self._calculate_q_factor(psd_one_sided, freq_axis, resonant_idx)
        
        # Damping ratio
        damping_ratio = 1.0 / (2 * q_factor) if q_factor > 0 else 1.0
        
        # Spectral centroid
        spectral_centroid = np.sum(freq_axis * psd_one_sided) / np.sum(psd_one_sided)
        
        # All peaks
        peak_frequencies = freq_axis[peaks]
        peak_amplitudes = np.sqrt(psd_one_sided[peaks]) * 9.81
        
        features = SpectralFeatures(
            resonant_frequency=float(resonant_freq),
            resonant_amplitude=float(resonant_amp),
            q_factor=float(q_factor),
            damping_ratio=float(damping_ratio),
            spectral_centroid=float(spectral_centroid),
            peak_frequencies=peak_frequencies.tolist(),
            peak_amplitudes=peak_amplitudes.tolist(),
            power_spectral_density=psd_one_sided,
            frequency_axis=freq_axis,
            raw_data=raw_accel_data,
            timestamp=timestamp or 0.0
        )
        
        logger.info(f"Signal processed: f_res={resonant_freq:.1f} Hz, "
                   f"Q={q_factor:.2f}, ζ={damping_ratio:.3f}")
        
        return features
    
    def _calculate_q_factor(self, psd: np.ndarray, freq_axis: np.ndarray, 
                           peak_idx: int, threshold: float = 0.707) -> float:
        """
        Calculate Q-factor using -3dB bandwidth method
        Q = f_resonant / bandwidth
        
        Args:
            psd: Power spectral density array
            freq_axis: Frequency axis array
            peak_idx: Index of resonant peak
            threshold: -3dB point threshold (default 0.707 = -3dB)
            
        Returns:
            Q-factor value
        """
        peak_power = psd[peak_idx]
        half_power = peak_power * (threshold ** 2)
        
        # Find left -3dB point
        left_idx = peak_idx
        while left_idx > 0 and psd[left_idx] > half_power:
            left_idx -= 1
        
        # Find right -3dB point
        right_idx = peak_idx
        while right_idx < len(psd) - 1 and psd[right_idx] > half_power:
            right_idx += 1
        
        bandwidth = freq_axis[right_idx] - freq_axis[left_idx]
        resonant_freq = freq_axis[peak_idx]
        
        if bandwidth > 0:
            return resonant_freq / bandwidth
        return 1.0
    
    def calculate_tissue_stiffness_index(self, healthy_features: SpectralFeatures,
                                       injured_features: SpectralFeatures) -> float:
        """
        Calculate Tibial Stiffness Index (TSI) for fracture healing monitoring
        TSI = (f_injured² / f_healthy²) × 100%
        
        Clinical interpretation:
        - TSI > 80%: Safe for weight-bearing
        - TSI < 50%: Still healing, avoid loading
        
        Args:
            healthy_features: Features from healthy side
            injured_features: Features from injured side
            
        Returns:
            TSI percentage
        """
        f_healthy = healthy_features.resonant_frequency
        f_injured = injured_features.resonant_frequency
        
        if f_healthy > 0:
            tsi = (f_injured ** 2 / f_healthy ** 2) * 100
            logger.info(f"TSI calculated: {tsi:.1f}%")
            return tsi
        return 0.0
    
    def calculate_pneumothorax_index(self, left_features: SpectralFeatures,
                                     right_features: SpectralFeatures) -> float:
        """
        Calculate power ratio for pneumothorax detection
        Ratio = Power_200_400Hz(affected) / Power_200_400Hz(healthy)
        
        Threshold: > 2.0 indicates hyper-resonance (air trapping)
        
        Args:
            left_features: Features from left chest
            right_features: Features from right chest
            
        Returns:
            Power ratio
        """
        # Extract 200-400 Hz band power
        def band_power(features, f_min=200, f_max=400):
            mask = (features.frequency_axis >= f_min) & (features.frequency_axis <= f_max)
            return np.sum(features.power_spectral_density[mask])
        
        power_left = band_power(left_features)
        power_right = band_power(right_features)
        
        if power_right > 0:
            ratio = power_left / power_right
            logger.info(f"Pneumothorax index: {ratio:.2f}")
            return ratio
        return 1.0
    
    def calculate_wave_velocity(self, features_array: List[SpectralFeatures],
                               distance_cm: float) -> float:
        """
        Calculate Lamb wave velocity for bladder compliance monitoring
        velocity = distance / time_delay_between_sensors
        
        Uses spectral peak shift between measurements
        
        Args:
            features_array: List of SpectralFeatures from different sensors
            distance_cm: Distance between sensors in cm
            
        Returns:
            Wave velocity in m/s
        """
        if len(features_array) < 2:
            logger.error("Need at least 2 measurement points")
            return 0.0
        
        # Estimate time delay from phase difference at resonant frequency
        # Simplified: use frequency shift ratio
        freq_ratio = (features_array[1].resonant_frequency / 
                     features_array[0].resonant_frequency)
        
        # Empirical model (simplified)
        time_delay = 0.01 * (1 - freq_ratio)  # seconds
        distance_m = distance_cm / 100.0
        
        if time_delay > 0:
            velocity = distance_m / time_delay
            logger.info(f"Wave velocity: {velocity:.2f} m/s")
            return velocity
        return 0.0
    
    def to_json(self, features: SpectralFeatures) -> str:
        """Serialize features to JSON"""
        data = asdict(features)
        data['power_spectral_density'] = data['power_spectral_density'].tolist()
        data['frequency_axis'] = data['frequency_axis'].tolist()
        data['raw_data'] = data['raw_data'].tolist()
        return json.dumps(data, indent=2)
    
    def from_json(self, json_str: str) -> SpectralFeatures:
        """Deserialize features from JSON"""
        data = json.loads(json_str)
        data['power_spectral_density'] = np.array(data['power_spectral_density'])
        data['frequency_axis'] = np.array(data['frequency_axis'])
        data['raw_data'] = np.array(data['raw_data'])
        return SpectralFeatures(**data)
    
    def generate_synthetic_signal(self, tissue_type="Healthy Bone", duration=1.0, 
                                  sampling_rate=None):
        """
        Generate a realistic synthetic tissue signal for EDUCATIONAL purposes.
        
        This is NOT real tissue data - it's for understanding how the system works.
        
        Args:
            tissue_type: Type of tissue ("Healthy Bone", "Fractured Bone", etc.)
            duration: Signal duration in seconds
            sampling_rate: Samples per second
            
        Returns:
            numpy array: Synthetic accelerometer signal
        """
        sampling_rate = sampling_rate or self.config.sampling_rate
        num_samples = int(duration * sampling_rate)
        time = np.linspace(0, duration, num_samples, endpoint=False)
        
        # Tissue type characteristics
        tissue_profiles = {
            "Healthy Bone": {"freq": 200, "q": 20, "amp": 0.8, "noise": 0.02},
            "Fractured Bone": {"freq": 120, "q": 8, "amp": 0.4, "noise": 0.15},
            "Healing Bone": {"freq": 150, "q": 14, "amp": 0.6, "noise": 0.08},
            "Osteoporotic": {"freq": 120, "q": 10, "amp": 0.5, "noise": 0.12},
            "Dense Bone": {"freq": 260, "q": 24, "amp": 0.9, "noise": 0.01},
            "Soft Tissue": {"freq": 75, "q": 8, "amp": 0.3, "noise": 0.2},
        }
        
        if tissue_type not in tissue_profiles:
            tissue_type = "Healthy Bone"
        
        profile = tissue_profiles[tissue_type]
        frequency = profile["freq"]
        q_factor = profile["q"]
        amplitude = profile["amp"]
        noise_level = profile["noise"]
        
        # Calculate damping from Q-factor
        damping = 1.0 / (2 * q_factor)
        
        # Generate damped sinusoidal signal
        signal = (amplitude * 
                  np.exp(-damping * 2 * np.pi * frequency * time) * 
                  np.sin(2 * np.pi * frequency * time))
        
        # Add realistic noise
        noise = np.random.normal(0, noise_level, num_samples)
        signal = signal + noise
        
        return signal
    
    def analyze(self, signal, sampling_rate=None):
        """
        Analyze an accelerometer signal (synthetic or real).
        
        Simplified interface for quick analysis.
        
        Args:
            signal: numpy array of accelerometer data
            sampling_rate: Samples per second
            
        Returns:
            dict: Analysis results including frequency, Q-factor, quality, etc.
        """
        sampling_rate = sampling_rate or self.config.sampling_rate
        
        # Convert to numpy array if needed
        signal = np.asarray(signal)
        
        # Compute FFT for frequency analysis
        n = len(signal)
        fft_result = fft(signal)
        frequencies = fftfreq(n, 1/sampling_rate)
        
        # Only positive frequencies
        positive_freqs = frequencies[:n//2]
        magnitudes = np.abs(fft_result[:n//2])
        
        # Find dominant frequency
        dominant_idx = np.argmax(magnitudes[1:]) + 1  # Skip DC component
        dominant_frequency = positive_freqs[dominant_idx]
        dominant_magnitude = magnitudes[dominant_idx]
        
        # Calculate SNR estimate
        signal_power = np.mean(signal**2)
        noise_level = np.std(signal)
        snr_db = 10 * np.log10(signal_power / (noise_level**2 + 1e-10))
        
        # Estimate Q-factor from spectral width
        threshold = dominant_magnitude / np.sqrt(2)
        above_threshold = magnitudes > threshold
        
        if np.sum(above_threshold) > 1:
            peak_indices = np.where(above_threshold)[0]
            bandwidth = positive_freqs[peak_indices[-1]] - positive_freqs[peak_indices[0]]
            q_factor = dominant_frequency / (bandwidth + 0.1)
        else:
            q_factor = 10.0
        
        q_factor = np.clip(q_factor, 3, 30)
        
        # Determine signal quality
        if snr_db > 25:
            quality = "EXCELLENT"
        elif snr_db > 15:
            quality = "GOOD"
        elif snr_db > 10:
            quality = "ACCEPTABLE"
        elif snr_db > 5:
            quality = "POOR"
        else:
            quality = "INVALID"
        
        # Analyze stationarity
        segment_size = n // 4
        segment_means = [
            np.mean(signal[i*segment_size:(i+1)*segment_size])
            for i in range(4)
        ]
        stationarity = 1.0 - (np.std(segment_means) / (np.std(signal) + 1e-10))
        stationarity = np.clip(stationarity, 0, 1)
        
        # Estimate tissue type
        freq = dominant_frequency
        if freq < 100:
            tissue_type = "Soft Tissue"
        elif freq < 140:
            tissue_type = "Fractured/Healing Bone"
        elif freq < 200:
            tissue_type = "Osteoporotic Bone"
        else:
            tissue_type = "Healthy/Dense Bone"
        
        # Calculate Tissue Stiffness Index
        tsi = min(100, (freq / 3) + (snr_db * 2) + 20)
        tsi = max(0, tsi)
        
        # Determine status
        if tsi < 40:
            status = "ACUTE"
        elif tsi < 60:
            status = "HEALING"
        elif tsi < 80:
            status = "GOOD PROGRESS"
        else:
            status = "CLEARED"
        
        return {
            'dominant_frequency': dominant_frequency,
            'frequency_hz': dominant_frequency,
            'q_factor': q_factor,
            'snr_db': snr_db,
            'signal_quality': quality,
            'tissue_type': tissue_type,
            'tsi': tsi,
            'status': status,
            'signal_power': signal_power,
            'noise_level': noise_level,
            'stationarity': stationarity,
            'damping': 1.0 / (2 * q_factor),
            'frequencies': positive_freqs,
            'magnitudes': magnitudes,
        }


def demonstrate_signal_processing():
    """Demonstration of signal processing capabilities"""
    logger.info("=== ResoScan Signal Processing Demo ===")
    
    # Generate synthetic tissue resonance signal
    fs = 3200  # Sampling rate
    duration = 1.0  # 1 second
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Simulate damaged bone with lower resonant frequency
    f_res_damaged = 150  # Hz (damaged)
    f_res_healthy = 200  # Hz (healthy)
    
    # Damped oscillation: x(t) = A * exp(-ζ*ω_n*t) * sin(ω_d*t)
    zeta = 0.1  # Damping ratio
    omega_n = 2 * np.pi * f_res_damaged
    omega_d = omega_n * np.sqrt(1 - zeta**2)
    
    damaged_signal = 0.5 * np.exp(-zeta * omega_n * t) * np.sin(omega_d * t)
    
    # Healthy bone
    zeta_healthy = 0.05
    omega_n_healthy = 2 * np.pi * f_res_healthy
    omega_d_healthy = omega_n_healthy * np.sqrt(1 - zeta_healthy**2)
    healthy_signal = 0.8 * np.exp(-zeta_healthy * omega_n_healthy * t) * np.sin(omega_d_healthy * t)
    
    # Process signals
    processor = SignalProcessor()
    
    damaged_features = processor.process_raw_signal(damaged_signal, timestamp=0.0)
    healthy_features = processor.process_raw_signal(healthy_signal, timestamp=1.0)
    
    # Calculate TSI
    tsi = processor.calculate_tissue_stiffness_index(healthy_features, damaged_features)
    
    logger.info(f"\n--- Fracture Healing Example ---")
    logger.info(f"Healthy bone resonant frequency: {healthy_features.resonant_frequency:.1f} Hz")
    logger.info(f"Damaged bone resonant frequency: {damaged_features.resonant_frequency:.1f} Hz")
    logger.info(f"Tibial Stiffness Index (TSI): {tsi:.1f}%")
    logger.info(f"Clinical interpretation: {'✓ SAFE for weight-bearing' if tsi > 80 else '✗ Still healing'}")
    
    logger.info(f"\n--- Feature Comparison ---")
    logger.info(f"Healthy - Q-factor: {healthy_features.q_factor:.2f}, "
               f"Damping: {healthy_features.damping_ratio:.3f}")
    logger.info(f"Damaged - Q-factor: {damaged_features.q_factor:.2f}, "
               f"Damping: {damaged_features.damping_ratio:.3f}")
    
    return damaged_features, healthy_features, tsi


if __name__ == "__main__":
    demonstrate_signal_processing()
