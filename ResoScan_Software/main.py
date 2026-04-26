"""
ResoScan Main Application
==========================
Complete end-to-end diagnostic platform

Author: ResoScan Team
Version: 1.0.0
"""

import sys
import argparse
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print ResoScan banner"""
    banner = r"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        ResoScan - Non-Invasive Tissue Diagnostics        ║
    ║          Resonant Modal Spectroscopy Platform            ║
    ║                                                           ║
    ║              Version 1.0.0 | Unisys 2026                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_demo_mode():
    """Run complete demonstration without hardware"""
    print("\n" + "="*60)
    print("DEMO MODE: Simulated ResoScan Operation")
    print("="*60 + "\n")
    
    try:
        from signal_processing.signal_processor import SignalProcessor, demonstrate_signal_processing
        from ml_models.classifier import demo_ml_classification, FeatureExtractor
        import numpy as np
        
        # 1. Signal Processing Demo
        logger.info("Starting signal processing demonstration...")
        print("\n" + "-"*60)
        print("1. SIGNAL PROCESSING DEMO")
        print("-"*60)
        damaged_features, healthy_features, tsi = demonstrate_signal_processing()
        
        # 2. ML Classification Demo
        logger.info("Starting ML classification demonstration...")
        print("\n" + "-"*60)
        print("2. MACHINE LEARNING CLASSIFICATION DEMO")
        print("-"*60)
        demo_ml_classification()
        
        # 3. Complete Workflow Demo
        logger.info("Starting complete diagnostic workflow...")
        print("\n" + "-"*60)
        print("3. COMPLETE DIAGNOSTIC WORKFLOW")
        print("-"*60)
        
        # Simulate a fracture healing monitoring scenario
        print("\n[SCENARIO] Monitoring fracture healing at day 7 post-injury\n")
        
        fs = 3200
        duration = 1.0
        t = np.linspace(0, duration, int(fs * duration), endpoint=False)
        
        # Day 0 (baseline injured bone)
        f_res_day0 = 100
        zeta_day0 = 0.15
        omega_n_day0 = 2 * np.pi * f_res_day0
        omega_d_day0 = omega_n_day0 * np.sqrt(1 - zeta_day0**2)
        signal_day0 = 0.3 * np.exp(-zeta_day0 * omega_n_day0 * t) * np.sin(omega_d_day0 * t)
        
        # Day 7 (partial healing)
        f_res_day7 = 160
        zeta_day7 = 0.08
        omega_n_day7 = 2 * np.pi * f_res_day7
        omega_d_day7 = omega_n_day7 * np.sqrt(1 - zeta_day7**2)
        signal_day7 = 0.6 * np.exp(-zeta_day7 * omega_n_day7 * t) * np.sin(omega_d_day7 * t)
        
        # Day 42 (healed)
        f_res_day42 = 200
        zeta_day42 = 0.05
        omega_n_day42 = 2 * np.pi * f_res_day42
        omega_d_day42 = omega_n_day42 * np.sqrt(1 - zeta_day42**2)
        signal_day42 = 0.8 * np.exp(-zeta_day42 * omega_n_day42 * t) * np.sin(omega_d_day42 * t)
        
        processor = SignalProcessor()
        
        features_day0 = processor.process_raw_signal(signal_day0, timestamp=0.0)
        features_day7 = processor.process_raw_signal(signal_day7, timestamp=1.0)
        features_day42 = processor.process_raw_signal(signal_day42, timestamp=2.0)
        
        # Calculate TSI progression
        tsi_day7 = processor.calculate_tissue_stiffness_index(features_day42, features_day7)
        tsi_day0 = processor.calculate_tissue_stiffness_index(features_day42, features_day0)
        
        print(f"{'Day':<10} {'f_res (Hz)':<15} {'Q-factor':<15} {'TSI (%)':<15} {'Status':<20}")
        print("-" * 75)
        print(f"{'0':<10} {features_day0.resonant_frequency:<15.1f} {features_day0.q_factor:<15.2f} {tsi_day0:<15.1f} {'Severely Injured':<20}")
        print(f"{'7':<10} {features_day7.resonant_frequency:<15.1f} {features_day7.q_factor:<15.2f} {tsi_day7:<15.1f} {'Healing':<20}")
        print(f"{'42':<10} {features_day42.resonant_frequency:<15.1f} {features_day42.q_factor:<15.2f} {'100.0':<15} {'Healed':<20}")
        
        print("\nClinical Interpretation:")
        print(f"  • Day 0:  TSI = {tsi_day0:.1f}% → IMMOBILIZE (no weight-bearing)")
        print(f"  • Day 7:  TSI = {tsi_day7:.1f}% → MONITOR (partial weight-bearing may be safe)")
        print(f"  • Day 42: TSI = 100.0% → CLEAR FOR ACTIVITY (full weight-bearing safe)\n")
        
        # 4. Feature Extraction for ML
        print("\n" + "-"*60)
        print("4. FEATURE EXTRACTION FOR ML MODELS")
        print("-"*60)
        
        features_ml = FeatureExtractor.extract_features(features_day7)
        print(f"\nExtracted ML feature vector (17D):")
        print(f"  • f_resonant = {features_ml[0]:.1f} Hz")
        print(f"  • amplitude = {features_ml[1]:.3f} g")
        print(f"  • Q-factor = {features_ml[2]:.2f}")
        print(f"  • damping = {features_ml[3]:.4f}")
        print(f"  • spectral_centroid = {features_ml[4]:.1f} Hz")
        print(f"  ... (12 more features for ML classification)\n")
        
        # 5. Pneumothorax detection demo
        print("\n" + "-"*60)
        print("5. PNEUMOTHORAX DETECTION EXAMPLE")
        print("-"*60)
        
        # Simulate healthy lungs
        healthy_lung = 0.5 * np.exp(-0.05 * 2 * np.pi * 300 * t) * np.sin(2 * np.pi * 300 * t)
        features_healthy = processor.process_raw_signal(healthy_lung)
        
        # Simulate pneumothorax (hyper-resonant)
        pneumo_lung = 0.7 * np.exp(-0.03 * 2 * np.pi * 300 * t) * np.sin(2 * np.pi * 300 * t)
        features_pneumo = processor.process_raw_signal(pneumo_lung)
        
        power_ratio = processor.calculate_pneumothorax_index(features_pneumo, features_healthy)
        
        print(f"\nChest percussion analysis:")
        print(f"  Left side (affected):  {features_pneumo.resonant_amplitude:.3f} g (hyper-resonant)")
        print(f"  Right side (healthy):  {features_healthy.resonant_amplitude:.3f} g")
        print(f"  Power ratio:           {power_ratio:.2f}")
        print(f"  Clinical finding:      {'✓ PNEUMOTHORAX DETECTED' if power_ratio > 2.0 else '✗ Normal'}\n")
        
        # 6. Export capabilities
        print("\n" + "-"*60)
        print("6. DATA EXPORT CAPABILITIES")
        print("-"*60)
        
        json_export = processor.to_json(features_day7)
        print(f"\nMeasurement exported as JSON:")
        print(f"  • Spectral features: resonant_frequency, Q-factor, damping")
        print(f"  • Peak analysis: frequencies and amplitudes")
        print(f"  • Raw acceleration data: 1024 time-domain samples")
        print(f"  • Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("  1. Connect ESP32 device via USB")
        print("  2. Run: python main.py --device COM3 --gui")
        print("  3. Start real-time measurements from dashboard\n")
        
        return True
    
    except Exception as e:
        logger.error(f"Demo mode error: {e}", exc_info=True)
        return False


def run_cli_mode(port: str = None):
    """Run command-line interface for manual operations"""
    print("\n" + "="*60)
    print("COMMAND-LINE INTERFACE MODE")
    print("="*60 + "\n")
    
    try:
        from signal_processing.data_acquisition import ResoScanDevice
        from signal_processing.signal_processor import SignalProcessor
        import numpy as np
        
        device = ResoScanDevice()
        processor = SignalProcessor()
        
        print("Attempting to connect to device...")
        if not device.connect(port):
            logger.error("Failed to connect to device")
            return False
        
        logger.info("✓ Connected successfully\n")
        
        while True:
            print("\nAvailable commands:")
            print("  1. Start CHIRP measurement")
            print("  2. Start IMPULSE measurement")
            print("  3. Start SINE wave measurement")
            print("  4. Get device status")
            print("  5. Process buffered data")
            print("  6. Exit")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                device.start_chirp_measurement()
                time.sleep(2)
            elif choice == '2':
                device.start_impulse_measurement()
                time.sleep(1)
            elif choice == '3':
                freq = int(input("Enter frequency (20-1000 Hz): "))
                device.start_sine_measurement(freq)
                time.sleep(2)
            elif choice == '4':
                device.get_status()
                time.sleep(0.5)
                stats = device.get_statistics()
                print(f"\nDevice Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
            elif choice == '5':
                ax, ay, az, ts = device.get_buffered_data(3200)
                if len(ax) > 0:
                    features = processor.process_raw_signal(ax)
                    print(f"\nSignal Analysis:")
                    print(f"  Resonant frequency: {features.resonant_frequency:.1f} Hz")
                    print(f"  Q-factor: {features.q_factor:.2f}")
                    print(f"  Damping ratio: {features.damping_ratio:.3f}")
                    print(f"  Peak frequencies: {features.peak_frequencies[:3]}")
            elif choice == '6':
                break
        
        device.disconnect()
        logger.info("✓ Disconnected")
        return True
    
    except Exception as e:
        logger.error(f"CLI mode error: {e}", exc_info=True)
        return False


def run_gui_mode(port: str = None):
    """Run graphical user interface"""
    print("\n" + "="*60)
    print("GRAPHICAL USER INTERFACE MODE")
    print("="*60 + "\n")
    
    try:
        from signal_processing.data_acquisition import ResoScanDevice
        from ui_dashboard.dashboard import run_dashboard
        
        device = ResoScanDevice()
        
        print("Initializing dashboard...")
        run_dashboard(device)
        
        return True
    
    except Exception as e:
        logger.error(f"GUI mode error: {e}", exc_info=True)
        return False


def main():
    """Main entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='ResoScan - Non-Invasive Tissue Diagnostics Platform'
    )
    parser.add_argument(
        '--mode',
        choices=['demo', 'cli', 'gui'],
        default='demo',
        help='Operation mode (default: demo)'
    )
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        help='Serial port for device (e.g., COM3, /dev/ttyUSB0)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'demo':
            success = run_demo_mode()
        elif args.mode == 'cli':
            success = run_cli_mode(args.device)
        elif args.mode == 'gui':
            success = run_gui_mode(args.device)
        else:
            success = False
        
        if not success:
            logger.error("Operation failed")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
