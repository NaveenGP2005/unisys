"""
ResoScan Dynamic Signal Processing Module
==========================================
Fully adaptive signal processing that dynamically adjusts to signal characteristics

Features:
- Adaptive FFT window sizing
- Dynamic peak detection thresholds
- Real-time signal quality assessment
- Adaptive feature extraction
- Dynamic noise filtering
- Signal-dependent clinical thresholds

Author: ResoScan Team
"""

import numpy as np
from scipy import signal, stats
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt, welch
import json
from dataclasses import dataclass, asdict
from typing import Tuple, Dict, List, Optional
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalQuality(Enum):
    """Signal quality levels"""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    ACCEPTABLE = "Acceptable"
    POOR = "Poor"
    INVALID = "Invalid"


@dataclass
class DynamicConfig:
    """Dynamic configuration that adapts based on signal"""
    sampling_rate: int = 3200
    base_fft_points: int = 1024
    window_type: str = "hann"
    freq_min: float = 20.0
    freq_max: float = 1000.0
    noise_threshold: float = 0.1
    adaptive_prominence: bool = True
    dynamic_window_sizing: bool = True
    adaptive_filtering: bool = True


@dataclass
class DynamicFeatures:
    """Dynamically extracted features"""
    # Resonance characteristics
    resonant_frequency: float
    resonant_amplitude: float
    q_factor: float
    damping_ratio: float
    spectral_centroid: float
    
    # Adaptive features
    signal_quality: SignalQuality
    snr_db: float  # Signal-to-noise ratio
    noise_floor: float
    signal_bandwidth: float
    
    # Peak information
    peak_frequencies: List[float]
    peak_amplitudes: List[float]
    num_peaks: int
    peak_sharpness: float
    
    # Spectral characteristics
    power_spectral_density: np.ndarray
    frequency_axis: np.ndarray
    raw_data: np.ndarray
    
    # Dynamic thresholds
    dynamic_threshold_tsi: float
    dynamic_threshold_ratio: float
    dynamic_threshold_velocity: float
    
    # Metadata
    timestamp: float
    processing_time_ms: float
    signal_stationarity: float  # How stable the signal is


class AdaptiveSignalProcessor:
    """
    Adaptive signal processing that dynamically adjusts parameters
    based on real-time signal characteristics
    """
    
    def __init__(self, config: DynamicConfig = None):
        """Initialize adaptive processor"""
        self.config = config or DynamicConfig()
        self.signal_history = []
        self.max_history = 10
        logger.info("Adaptive Signal Processor initialized")
    
    def process_signal_adaptive(self, raw_accel_data: np.ndarray, 
                               timestamp: float = None) -> DynamicFeatures:
        """
        Adaptive signal processing pipeline:
        1. Signal quality assessment
        2. Adaptive noise filtering
        3. Dynamic FFT window sizing
        4. Adaptive peak detection
        5. Dynamic feature extraction
        6. Signal-based threshold computation
        
        Args:
            raw_accel_data: Accelerometer samples
            timestamp: Measurement timestamp
            
        Returns:
            DynamicFeatures with adaptive characteristics
        """
        import time
        start_time = time.time()
        
        # Ensure data is numpy array
        raw_accel_data = np.asarray(raw_accel_data, dtype=np.float32)
        
        # Step 1: Assess signal quality
        signal_quality, snr_db = self._assess_signal_quality(raw_accel_data)
        logger.info(f"Signal Quality: {signal_quality.value} (SNR: {snr_db:.2f} dB)")
        
        # Step 2: Adaptive noise filtering
        filtered_data = self._adaptive_noise_filter(raw_accel_data, snr_db)
        
        # Step 3: Determine dynamic FFT parameters
        fft_size = self._calculate_dynamic_fft_size(filtered_data)
        window_type = self._select_optimal_window(filtered_data)
        
        # Pad or trim data
        if len(filtered_data) < fft_size:
            filtered_data = np.pad(filtered_data, (0, fft_size - len(filtered_data)))
        else:
            filtered_data = filtered_data[:fft_size]
        
        # Step 4: Compute FFT with dynamic parameters
        window = signal.get_window(window_type, len(filtered_data))
        windowed_data = filtered_data * window
        
        fft_result = fft(windowed_data)
        psd = np.abs(fft_result) ** 2 / (self.config.sampling_rate * len(windowed_data))
        psd_one_sided = 2 * psd[:len(psd)//2]
        freq_axis = fftfreq(len(windowed_data), 1/self.config.sampling_rate)[:len(psd)//2]
        
        # Step 5: Adaptive peak detection
        noise_floor = np.median(psd_one_sided)
        dynamic_prominence = self._calculate_dynamic_prominence(psd_one_sided, noise_floor, snr_db)
        
        peaks, properties = signal.find_peaks(
            psd_one_sided,
            prominence=dynamic_prominence,
            distance=max(1, int(5 * len(psd_one_sided) / 1000))
        )
        
        if len(peaks) == 0:
            peaks = np.array([np.argmax(psd_one_sided)])
        
        # Sort by prominence
        peak_prominences = properties.get('prominences', np.ones(len(peaks)))
        sorted_idx = np.argsort(peak_prominences)[::-1]
        peaks = peaks[sorted_idx]
        
        # Step 6: Extract dynamic features
        resonant_idx = peaks[0]
        resonant_freq = freq_axis[resonant_idx]
        resonant_amp = np.sqrt(psd_one_sided[resonant_idx]) * 9.81
        
        # Adaptive Q-factor calculation
        q_factor = self._calculate_adaptive_q_factor(psd_one_sided, freq_axis, resonant_idx)
        damping_ratio = 1.0 / (2 * q_factor) if q_factor > 0 else 1.0
        
        # Spectral centroid
        spectral_centroid = np.sum(freq_axis * psd_one_sided) / np.sum(psd_one_sided)
        
        # Peak sharpness (higher Q = sharper peaks)
        peak_sharpness = q_factor / (1 + q_factor)
        
        # Signal bandwidth
        signal_bandwidth = np.sqrt(np.sum((freq_axis - spectral_centroid)**2 * psd_one_sided) / np.sum(psd_one_sided))
        
        # Signal stationarity (consistency over time)
        stationarity = self._calculate_stationarity(raw_accel_data)
        
        # Dynamic thresholds based on signal characteristics
        dynamic_thresholds = self._calculate_dynamic_thresholds(
            resonant_freq, q_factor, damping_ratio, snr_db, stationarity
        )
        
        # All peaks
        peak_frequencies = freq_axis[peaks[:min(10, len(peaks))]].tolist()
        peak_amplitudes = (np.sqrt(psd_one_sided[peaks[:min(10, len(peaks))]]) * 9.81).tolist()
        
        processing_time = (time.time() - start_time) * 1000
        
        features = DynamicFeatures(
            resonant_frequency=float(resonant_freq),
            resonant_amplitude=float(resonant_amp),
            q_factor=float(q_factor),
            damping_ratio=float(damping_ratio),
            spectral_centroid=float(spectral_centroid),
            signal_quality=signal_quality,
            snr_db=float(snr_db),
            noise_floor=float(noise_floor),
            signal_bandwidth=float(signal_bandwidth),
            peak_frequencies=peak_frequencies,
            peak_amplitudes=peak_amplitudes,
            num_peaks=len(peaks),
            peak_sharpness=float(peak_sharpness),
            power_spectral_density=psd_one_sided,
            frequency_axis=freq_axis,
            raw_data=raw_accel_data,
            dynamic_threshold_tsi=dynamic_thresholds['tsi'],
            dynamic_threshold_ratio=dynamic_thresholds['ratio'],
            dynamic_threshold_velocity=dynamic_thresholds['velocity'],
            timestamp=timestamp or 0.0,
            processing_time_ms=processing_time,
            signal_stationarity=float(stationarity)
        )
        
        # Store in history
        self.signal_history.append(features)
        if len(self.signal_history) > self.max_history:
            self.signal_history.pop(0)
        
        logger.info(f"Adaptive processing complete: f_res={resonant_freq:.1f}Hz, "
                   f"Q={q_factor:.2f}, SNR={snr_db:.1f}dB, Quality={signal_quality.value}")
        
        return features
    
    def _assess_signal_quality(self, data: np.ndarray) -> Tuple[SignalQuality, float]:
        """
        Assess signal quality based on multiple metrics
        Returns: (quality_level, snr_dB)
        """
        # Calculate signal-to-noise ratio
        signal_power = np.mean(data ** 2)
        noise_power = np.median(np.abs(data - np.median(data)))
        
        # Calculate SNR in dB
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / (noise_power ** 2 + 1e-10))
        else:
            snr_db = 40  # Assume good signal if noise is near zero
        
        # Assess quality based on SNR
        if snr_db > 30:
            quality = SignalQuality.EXCELLENT
        elif snr_db > 20:
            quality = SignalQuality.GOOD
        elif snr_db > 10:
            quality = SignalQuality.ACCEPTABLE
        elif snr_db > 0:
            quality = SignalQuality.POOR
        else:
            quality = SignalQuality.INVALID
        
        return quality, snr_db
    
    def _adaptive_noise_filter(self, data: np.ndarray, snr_db: float) -> np.ndarray:
        """
        Apply adaptive filtering based on signal quality
        """
        if not self.config.adaptive_filtering:
            return data
        
        # Design filter based on SNR
        if snr_db < 15:
            # Poor signal - use aggressive filtering
            order = 4
            cutoff = 0.1
        elif snr_db < 25:
            # Acceptable signal - moderate filtering
            order = 3
            cutoff = 0.15
        else:
            # Good signal - light filtering
            order = 2
            cutoff = 0.2
        
        try:
            # Design and apply Butterworth filter
            b, a = butter(order, cutoff, btype='high')
            filtered_data = filtfilt(b, a, data)
            return filtered_data
        except:
            return data
    
    def _calculate_dynamic_fft_size(self, data: np.ndarray) -> int:
        """
        Calculate optimal FFT size based on data characteristics
        """
        if not self.config.dynamic_window_sizing:
            return self.config.base_fft_points
        
        data_length = len(data)
        
        # Use next power of 2 for efficiency
        if data_length >= 2048:
            fft_size = 2048
        elif data_length >= 1024:
            fft_size = 1024
        elif data_length >= 512:
            fft_size = 512
        else:
            fft_size = 256
        
        return fft_size
    
    def _select_optimal_window(self, data: np.ndarray) -> str:
        """
        Select window type based on signal characteristics
        """
        # Analyze signal stationarity
        stationarity = self._calculate_stationarity(data)
        
        if stationarity > 0.8:
            # Stationary signal - use high-resolution window
            return 'hann'
        elif stationarity > 0.6:
            # Semi-stationary - balanced window
            return 'hamming'
        else:
            # Non-stationary - use flexible window
            return 'tukey'
    
    def _calculate_dynamic_prominence(self, psd: np.ndarray, noise_floor: float, 
                                      snr_db: float) -> float:
        """
        Calculate dynamic peak prominence threshold
        """
        if not self.config.adaptive_prominence:
            return 0.1
        
        # Adjust prominence based on signal quality
        if snr_db < 10:
            return noise_floor * 3
        elif snr_db < 20:
            return noise_floor * 2
        elif snr_db < 30:
            return noise_floor * 1.5
        else:
            return noise_floor * 1.0
    
    def _calculate_adaptive_q_factor(self, psd: np.ndarray, freq_axis: np.ndarray, 
                                     peak_idx: int, threshold: float = 0.707) -> float:
        """
        Calculate Q-factor using adaptive threshold
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
            q_factor = resonant_freq / bandwidth
        else:
            q_factor = 1.0
        
        # Clamp Q-factor to reasonable range
        q_factor = np.clip(q_factor, 0.1, 100.0)
        return q_factor
    
    def _calculate_stationarity(self, data: np.ndarray) -> float:
        """
        Calculate signal stationarity (0 to 1)
        """
        if len(data) < 100:
            return 0.5
        
        # Divide into segments
        n_segments = 4
        segment_length = len(data) // n_segments
        
        means = []
        variances = []
        
        for i in range(n_segments):
            segment = data[i*segment_length:(i+1)*segment_length]
            means.append(np.mean(segment))
            variances.append(np.var(segment))
        
        # Calculate consistency
        mean_consistency = 1.0 - (np.std(means) / (np.mean(np.abs(data)) + 1e-10))
        var_consistency = 1.0 - (np.std(variances) / (np.mean(variances) + 1e-10))
        
        stationarity = np.clip((mean_consistency + var_consistency) / 2, 0, 1)
        return stationarity
    
    def _calculate_dynamic_thresholds(self, f_res: float, q_factor: float, 
                                      damping: float, snr_db: float, 
                                      stationarity: float) -> Dict[str, float]:
        """
        Calculate dynamic clinical thresholds based on signal characteristics
        """
        # Base thresholds
        tsi_base = 0.80
        ratio_base = 2.0
        velocity_base = 4.0
        
        # Adjust based on signal quality
        quality_factor = snr_db / 30.0  # Normalize SNR
        quality_factor = np.clip(quality_factor, 0.5, 1.5)
        
        # Adjust based on signal stationarity
        stationarity_factor = 1.0 - (0.2 * (1 - stationarity))
        
        # Adjust based on Q-factor (sharpness of resonance)
        q_factor_adj = 1.0 + (0.1 * np.log10(max(q_factor, 1)))
        
        return {
            'tsi': tsi_base * stationarity_factor,
            'ratio': ratio_base * quality_factor * q_factor_adj,
            'velocity': velocity_base * (1.0 / quality_factor)
        }
    
    def calculate_dynamic_tsi(self, healthy_features: DynamicFeatures,
                             injured_features: DynamicFeatures) -> Dict:
        """
        Calculate TSI with dynamic thresholds
        """
        f_healthy = healthy_features.resonant_frequency
        f_injured = injured_features.resonant_frequency
        
        if f_healthy > 0:
            tsi = (f_injured ** 2 / f_healthy ** 2) * 100
        else:
            tsi = 0
        
        # Use dynamic threshold
        threshold = injured_features.dynamic_threshold_tsi * 100
        
        # Clinical interpretation
        if tsi > threshold:
            status = "✓ SAFE FOR WEIGHT-BEARING"
            confidence = min(100, (tsi / threshold) * 100)
        elif tsi > threshold * 0.6:
            status = "⚠ PARTIAL HEALING - MONITORED LOADING"
            confidence = (tsi / threshold) * 100
        else:
            status = "✗ ACTIVE HEALING - AVOID LOADING"
            confidence = (tsi / threshold) * 100
        
        return {
            'tsi': tsi,
            'dynamic_threshold': threshold,
            'status': status,
            'confidence': confidence,
            'healthy_freq': f_healthy,
            'injured_freq': f_injured,
            'signal_quality': injured_features.signal_quality.value,
            'snr_db': injured_features.snr_db
        }
    
    def calculate_dynamic_pneumothorax_index(self, left_features: DynamicFeatures,
                                            right_features: DynamicFeatures) -> Dict:
        """
        Calculate pneumothorax detection with dynamic thresholds
        """
        def band_power(features, f_min=200, f_max=400):
            mask = (features.frequency_axis >= f_min) & (features.frequency_axis <= f_max)
            return np.sum(features.power_spectral_density[mask])
        
        power_left = band_power(left_features)
        power_right = band_power(right_features)
        
        if power_right > 0:
            ratio = power_left / power_right
        else:
            ratio = 1.0
        
        # Use dynamic threshold
        threshold = left_features.dynamic_threshold_ratio
        
        # Clinical interpretation
        if ratio > threshold:
            status = "⚠ PNEUMOTHORAX LIKELY - HYPER-RESONANCE DETECTED"
            confidence = min(100, (ratio / threshold) * 100)
        elif ratio > threshold * 0.7:
            status = "⚠ POSSIBLE PNEUMOTHORAX - FURTHER INVESTIGATION NEEDED"
            confidence = (ratio / threshold) * 100
        else:
            status = "✓ NORMAL - NO PNEUMOTHORAX"
            confidence = 100 - abs(ratio - 1) * 20
        
        return {
            'power_ratio': ratio,
            'dynamic_threshold': threshold,
            'status': status,
            'confidence': np.clip(confidence, 0, 100),
            'left_power': power_left,
            'right_power': power_right,
            'signal_quality_left': left_features.signal_quality.value,
            'signal_quality_right': right_features.signal_quality.value
        }
    
    def get_signal_report(self, features: DynamicFeatures) -> str:
        """Generate comprehensive signal quality report"""
        report = f"""
╔═══════════════════════════════════════════════════════════╗
║              DYNAMIC SIGNAL ANALYSIS REPORT               ║
╚═══════════════════════════════════════════════════════════╝

📊 SIGNAL QUALITY
─────────────────────────────────────────────────────────────
Quality Level:           {features.signal_quality.value}
Signal-to-Noise Ratio:   {features.snr_db:.2f} dB
Noise Floor:             {features.noise_floor:.6f}
Stationarity:            {features.signal_stationarity:.1%}

🎯 RESONANCE CHARACTERISTICS
─────────────────────────────────────────────────────────────
Resonant Frequency:      {features.resonant_frequency:.1f} Hz
Resonant Amplitude:      {features.resonant_amplitude:.3f} g
Q-Factor:                {features.q_factor:.2f}
Damping Ratio:           {features.damping_ratio:.4f}
Peak Sharpness:          {features.peak_sharpness:.3f}

📈 SPECTRAL INFORMATION
─────────────────────────────────────────────────────────────
Spectral Centroid:       {features.spectral_centroid:.1f} Hz
Signal Bandwidth:        {features.signal_bandwidth:.1f} Hz
Number of Peaks:         {features.num_peaks}
Top Peak Frequencies:    {', '.join([f'{f:.1f}' for f in features.peak_frequencies[:3]])} Hz

🔧 DYNAMIC THRESHOLDS
─────────────────────────────────────────────────────────────
TSI Threshold:           {features.dynamic_threshold_tsi:.1%}
Power Ratio Threshold:   {features.dynamic_threshold_ratio:.2f}
Velocity Threshold:      {features.dynamic_threshold_velocity:.2f} m/s

⏱️ PROCESSING
─────────────────────────────────────────────────────────────
Processing Time:         {features.processing_time_ms:.2f} ms
Timestamp:               {features.timestamp:.2f}s
        """
        return report


def demo_dynamic_processing():
    """Demonstrate adaptive signal processing"""
    logger.info("=== ResoScan Dynamic Signal Processing Demo ===\n")
    
    processor = AdaptiveSignalProcessor()
    
    # Generate test signals with varying quality
    fs = 3200
    duration = 1.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Signal 1: High quality (clean)
    logger.info("Generating HIGH QUALITY signal...")
    f_res = 200
    zeta = 0.05
    omega_n = 2 * np.pi * f_res
    omega_d = omega_n * np.sqrt(1 - zeta**2)
    signal_high_quality = 0.8 * np.exp(-zeta * omega_n * t) * np.sin(omega_d * t)
    
    features_high = processor.process_signal_adaptive(signal_high_quality, 0.0)
    print(processor.get_signal_report(features_high))
    
    # Signal 2: Noisy (poor quality)
    logger.info("\nGenerating NOISY signal...")
    noise = np.random.normal(0, 0.3, len(signal_high_quality))
    signal_noisy = signal_high_quality + noise
    
    features_noisy = processor.process_signal_adaptive(signal_noisy, 1.0)
    print(processor.get_signal_report(features_noisy))
    
    # Signal 3: Different resonance frequency (different tissue)
    logger.info("\nGenerating DIFFERENT RESONANCE signal...")
    f_res_damaged = 120
    omega_n_damaged = 2 * np.pi * f_res_damaged
    omega_d_damaged = omega_n_damaged * np.sqrt(1 - 0.15**2)
    signal_damaged = 0.5 * np.exp(-0.15 * omega_n_damaged * t) * np.sin(omega_d_damaged * t)
    
    features_damaged = processor.process_signal_adaptive(signal_damaged, 2.0)
    print(processor.get_signal_report(features_damaged))
    
    # Dynamic TSI Calculation
    logger.info("\n" + "="*60)
    logger.info("DYNAMIC TSI CALCULATION")
    logger.info("="*60)
    tsi_result = processor.calculate_dynamic_tsi(features_high, features_damaged)
    print(f"\nTSI Result: {tsi_result['tsi']:.1f}%")
    print(f"Dynamic Threshold: {tsi_result['dynamic_threshold']:.1f}%")
    print(f"Status: {tsi_result['status']}")
    print(f"Confidence: {tsi_result['confidence']:.1f}%")


if __name__ == "__main__":
    demo_dynamic_processing()
