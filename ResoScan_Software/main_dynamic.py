"""
ResoScan Dynamic Main Application
==================================
End-to-end platform with fully adaptive signal processing

Modes:
- demo: Simulation with synthetic signals
- live: Real-time hardware measurements
- interactive: Interactive real-time analysis

Author: ResoScan Team
Version: 2.0 (Dynamic)
"""

import sys
import argparse
import logging
import numpy as np
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print ResoScan banner"""
    banner = """
    ===============================================================
                                                                   
       ResoScan - Dynamic Adaptive Tissue Diagnostics             
       Resonant Modal Spectroscopy Platform v2.0                  
                                                                   
       Fully adaptive signal processing based on                  
       real-time signal characteristics                           
                                                                   
                  Version 2.0 | Unisys 2026                       
                                                                   
    ===============================================================
    """
    print(banner)


def run_interactive_demo():
    """Interactive demo with multiple scenarios"""
    print("\n" + "="*70)
    print("INTERACTIVE DYNAMIC PROCESSING DEMO")
    print("="*70 + "\n")
    
    from signal_processing.dynamic_processor import AdaptiveSignalProcessor, SignalQuality
    
    processor = AdaptiveSignalProcessor()
    fs = 3200
    duration = 1.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    scenarios = {
        '1': {
            'name': 'Healthy Bone (High Quality)',
            'description': 'Clean signal from healthy bone tissue',
            'f_res': 200,
            'zeta': 0.05,
            'amplitude': 0.8,
            'noise': 0.05
        },
        '2': {
            'name': 'Injured Bone (Lower Frequency)',
            'description': 'Signal from fractured/injured bone',
            'f_res': 120,
            'zeta': 0.15,
            'amplitude': 0.5,
            'noise': 0.1
        },
        '3': {
            'name': 'Healing Bone (Intermediate)',
            'description': 'Signal from bone in healing process',
            'f_res': 160,
            'zeta': 0.08,
            'amplitude': 0.65,
            'noise': 0.08
        },
        '4': {
            'name': 'Poor SNR Signal',
            'description': 'Signal with high noise (poor conditions)',
            'f_res': 180,
            'zeta': 0.06,
            'amplitude': 0.4,
            'noise': 0.35
        },
        '5': {
            'name': 'Pneumothorax Resonance',
            'description': 'Hyper-resonant lung (pneumothorax)',
            'f_res': 300,
            'zeta': 0.03,
            'amplitude': 0.9,
            'noise': 0.05
        }
    }
    
    print("Available Scenarios:")
    print("-" * 70)
    for key, scenario in scenarios.items():
        print(f"{key}. {scenario['name']}")
        print(f"   {scenario['description']}\n")
    
    print("Commands:")
    print("  Enter scenario number (1-5) to analyze")
    print("  'compare' to compare scenarios")
    print("  'quit' to exit\n")
    
    analyzed_signals = {}
    
    while True:
        user_input = input(">>> Enter command: ").strip().lower()
        
        if user_input == 'quit':
            break
        
        elif user_input == 'compare':
            if len(analyzed_signals) < 2:
                print("⚠ Need at least 2 analyzed signals to compare\n")
                continue
            
            print("\n" + "="*70)
            print("COMPARATIVE ANALYSIS")
            print("="*70)
            
            signal_names = list(analyzed_signals.keys())
            for i, name1 in enumerate(signal_names):
                for name2 in signal_names[i+1:]:
                    features1 = analyzed_signals[name1]
                    features2 = analyzed_signals[name2]
                    
                    print(f"\nComparing: {name1} vs {name2}")
                    print("-" * 70)
                    print(f"Frequency difference:  {abs(features1.resonant_frequency - features2.resonant_frequency):.1f} Hz")
                    print(f"Q-factor difference:   {abs(features1.q_factor - features2.q_factor):.2f}")
                    print(f"SNR difference:        {abs(features1.snr_db - features2.snr_db):.2f} dB")
                    print(f"Damping difference:    {abs(features1.damping_ratio - features2.damping_ratio):.4f}")
                    
                    # TSI calculation
                    tsi_result = processor.calculate_dynamic_tsi(features2, features1)
                    print(f"\nTSI Analysis ({name2} vs {name1}):")
                    print(f"  TSI: {tsi_result['tsi']:.1f}%")
                    print(f"  Status: {tsi_result['status']}")
                    print(f"  Confidence: {tsi_result['confidence']:.1f}%")
            
            print()
        
        elif user_input in scenarios:
            scenario = scenarios[user_input]
            print(f"\n▶ Processing: {scenario['name']}")
            print(f"  {scenario['description']}\n")
            
            # Generate signal
            omega_n = 2 * np.pi * scenario['f_res']
            omega_d = omega_n * np.sqrt(1 - scenario['zeta']**2)
            base_signal = scenario['amplitude'] * np.exp(-scenario['zeta'] * omega_n * t) * np.sin(omega_d * t)
            noise = np.random.normal(0, scenario['noise'], len(t))
            signal_data = base_signal + noise
            
            # Process
            features = processor.process_signal_adaptive(signal_data, time.time())
            print(processor.get_signal_report(features))
            
            analyzed_signals[scenario['name']] = features
        
        else:
            print("❌ Invalid command\n")


def run_advanced_fracture_monitoring():
    """Advanced fracture monitoring with multiple measurements"""
    print("\n" + "="*70)
    print("ADVANCED FRACTURE HEALING MONITORING")
    print("="*70 + "\n")
    
    from signal_processing.dynamic_processor import AdaptiveSignalProcessor
    
    processor = AdaptiveSignalProcessor()
    fs = 3200
    duration = 1.0
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # Simulate healing progression (Day 0, 7, 14, 21, 42)
    healing_progression = [
        {'day': 0, 'f_res': 100, 'zeta': 0.18, 'amplitude': 0.3, 'label': 'Day 0: Acute Fracture'},
        {'day': 7, 'f_res': 130, 'zeta': 0.12, 'amplitude': 0.5, 'label': 'Day 7: Early Healing'},
        {'day': 14, 'f_res': 160, 'zeta': 0.08, 'amplitude': 0.65, 'label': 'Day 14: Mid Healing'},
        {'day': 21, 'f_res': 180, 'zeta': 0.06, 'amplitude': 0.75, 'label': 'Day 21: Late Healing'},
        {'day': 42, 'f_res': 200, 'zeta': 0.04, 'amplitude': 0.85, 'label': 'Day 42: Healed'},
    ]
    
    # Get baseline (healthy bone)
    omega_n_healthy = 2 * np.pi * 200
    omega_d_healthy = omega_n_healthy * np.sqrt(1 - 0.04**2)
    healthy_signal = 0.85 * np.exp(-0.04 * omega_n_healthy * t) * np.sin(omega_d_healthy * t)
    healthy_signal += np.random.normal(0, 0.05, len(t))
    
    logger.info("Acquiring baseline measurement (healthy bone)...")
    baseline_features = processor.process_signal_adaptive(healthy_signal, 0.0)
    print(f"\n✓ Baseline established: f_res = {baseline_features.resonant_frequency:.1f} Hz")
    
    # Monitor healing progression
    print("\n" + "="*70)
    print("MONITORING FRACTURE HEALING PROGRESSION")
    print("="*70 + "\n")
    
    tsi_history = []
    
    for measurement in healing_progression:
        logger.info(f"Processing {measurement['label']}...")
        
        omega_n = 2 * np.pi * measurement['f_res']
        omega_d = omega_n * np.sqrt(1 - measurement['zeta']**2)
        signal_data = measurement['amplitude'] * np.exp(-measurement['zeta'] * omega_n * t) * np.sin(omega_d * t)
        signal_data += np.random.normal(0, 0.08, len(t))
        
        features = processor.process_signal_adaptive(signal_data, measurement['day'])
        
        # Calculate TSI
        tsi_result = processor.calculate_dynamic_tsi(baseline_features, features)
        tsi_history.append(tsi_result)
        
        print(f"\n{measurement['label']}")
        print("-" * 70)
        print(f"Resonant Frequency:    {features.resonant_frequency:.1f} Hz")
        print(f"Q-Factor:              {features.q_factor:.2f}")
        print(f"Signal Quality:        {features.signal_quality.value}")
        print(f"SNR:                   {features.snr_db:.2f} dB")
        print(f"\nTSI Score:             {tsi_result['tsi']:.1f}%")
        print(f"Dynamic Threshold:     {tsi_result['dynamic_threshold']:.1f}%")
        print(f"Status:                {tsi_result['status']}")
        print(f"Confidence:            {tsi_result['confidence']:.1f}%")
    
    # Plot progression
    print("\n" + "="*70)
    print("HEALING PROGRESSION SUMMARY")
    print("="*70 + "\n")
    
    print("Timeline of Tissue Stiffness Index (TSI):")
    print("-" * 70)
    for i, tsi in enumerate(tsi_history):
        day = healing_progression[i]['day']
        tsi_pct = tsi['tsi']
        threshold = tsi['dynamic_threshold']
        
        # Visual bar
        bar_length = int(tsi_pct / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        
        print(f"Day {day:2d}: [{bar}] {tsi_pct:5.1f}% (threshold: {threshold:.1f}%)")
    
    print("\n" + "="*70)
    print("CLINICAL RECOMMENDATIONS")
    print("="*70 + "\n")
    
    final_tsi = tsi_history[-1]['tsi']
    final_threshold = tsi_history[-1]['dynamic_threshold']
    
    if final_tsi > final_threshold:
        print("✓ CLEARED FOR WEIGHT-BEARING ACTIVITIES")
        print(f"  TSI reached {final_tsi:.1f}% (above threshold of {final_threshold:.1f}%)")
    elif final_tsi > final_threshold * 0.7:
        print("⚠ PARTIAL ACTIVITY - MONITORED LOADING RECOMMENDED")
        print(f"  TSI is {final_tsi:.1f}% (approaching threshold of {final_threshold:.1f}%)")
    else:
        print("✗ CONTINUE IMMOBILIZATION")
        print(f"  TSI is {final_tsi:.1f}% (below threshold of {final_threshold:.1f}%)")
    
    print()


def run_real_time_monitoring():
    """Continuous real-time monitoring simulation"""
    print("\n" + "="*70)
    print("REAL-TIME CONTINUOUS MONITORING")
    print("="*70 + "\n")
    
    from signal_processing.dynamic_processor import AdaptiveSignalProcessor
    
    processor = AdaptiveSignalProcessor()
    fs = 3200
    
    print("Starting continuous monitoring (20 measurements, 5 samples each)...\n")
    print("Measurement │ Frequency │ Q-Factor │ Quality │ SNR  │ Status")
    print("-" * 70)
    
    measurements = []
    
    for i in range(20):
        # Generate varying signal (simulating time-varying tissue properties)
        duration = 0.05  # 50ms chunks
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        
        # Slowly changing frequency (simulating healing or fatigue)
        base_freq = 150 + i * 1.5  # Gradually increasing
        zeta = 0.10 - i * 0.001
        
        omega_n = 2 * np.pi * base_freq
        omega_d = omega_n * np.sqrt(1 - max(0.001, zeta)**2)
        signal_data = 0.6 * np.exp(-max(0.001, zeta) * omega_n * t) * np.sin(omega_d * t)
        signal_data += np.random.normal(0, 0.08, len(t))
        
        # Process
        features = processor.process_signal_adaptive(signal_data, i * 0.05)
        measurements.append(features)
        
        # Determine status
        if features.signal_quality.value == "Excellent":
            status = "✓ Excellent"
        elif features.signal_quality.value == "Good":
            status = "✓ Good"
        elif features.signal_quality.value == "Acceptable":
            status = "⚠ Acceptable"
        else:
            status = "✗ Poor"
        
        print(f"      {i+1:2d}      │ {features.resonant_frequency:7.1f} Hz │  {features.q_factor:5.2f}   │ "
              f"{features.signal_quality.value:7s} │ {features.snr_db:5.1f} │ {status}")
        
        time.sleep(0.1)  # Simulate measurement delay
    
    print("\n" + "="*70)
    print("MONITORING STATISTICS")
    print("="*70 + "\n")
    
    frequencies = [m.resonant_frequency for m in measurements]
    q_factors = [m.q_factor for m in measurements]
    snrs = [m.snr_db for m in measurements]
    
    print(f"Resonant Frequency:    {np.mean(frequencies):.1f} ± {np.std(frequencies):.1f} Hz")
    print(f"Q-Factor:              {np.mean(q_factors):.2f} ± {np.std(q_factors):.2f}")
    print(f"Signal-to-Noise Ratio: {np.mean(snrs):.1f} ± {np.std(snrs):.1f} dB")
    print(f"Measurement Drift:     {frequencies[-1] - frequencies[0]:.1f} Hz over 20 measurements")
    print(f"Consistency:           {(1 - np.std(frequencies) / np.mean(frequencies)):.1%}")
    
    print()


def main():
    """Main application"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='ResoScan Dynamic Adaptive Tissue Diagnostics Platform'
    )
    parser.add_argument(
        '--mode',
        choices=['demo', 'interactive', 'monitoring', 'fracture', 'all'],
        default='interactive',
        help='Operation mode'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'demo':
            from signal_processing.dynamic_processor import demo_dynamic_processing
            demo_dynamic_processing()
        
        elif args.mode == 'interactive':
            run_interactive_demo()
        
        elif args.mode == 'monitoring':
            run_real_time_monitoring()
        
        elif args.mode == 'fracture':
            run_advanced_fracture_monitoring()
        
        elif args.mode == 'all':
            print("\n🚀 Running comprehensive ResoScan demo suite...\n")
            
            from signal_processing.dynamic_processor import demo_dynamic_processing
            demo_dynamic_processing()
            
            run_advanced_fracture_monitoring()
            run_real_time_monitoring()
        
        logger.info("✅ ResoScan application completed successfully")
    
    except KeyboardInterrupt:
        print("\n\n⚠ Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
