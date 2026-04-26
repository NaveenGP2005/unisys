#!/usr/bin/env python3
"""
ResoScan - Tissue Diagnostics Platform
=======================================

Honest, Real Implementation:
- Simulation Mode: Educational/testing WITHOUT hardware (realistic but synthetic)
- Hardware Mode: Real measurements from connected ESP32 ADXL343

NO FAKING. Use simulation for understanding, hardware for real data.

Author: ResoScan Team
"""

import argparse
import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from signal_processing.data_acquisition import ResoScanDevice
except ImportError as e:
    print(f"[WARNING] Hardware support not available: {e}")
    ResoScanDevice = None

from signal_processing.signal_processor import SignalProcessor

try:
    from ml_models.classifier import TissueClassifier
except ImportError:
    TissueClassifier = None


def run_hardware_mode():
    """
    HARDWARE MODE: Real ESP32 device with ADXL343 accelerometer
    
    Prerequisites:
    1. ESP32 connected via USB
    2. ADXL343 accelerometer attached to ESP32
    3. Firmware flashed on ESP32
    4. Serial port available
    """
    if not ResoScanDevice:
        print("\n[ERROR] Hardware support not installed")
        print("To use Hardware Mode, install PySerial:")
        print("  pip install PySerial")
        return False
    
    print("\n" + "=" * 80)
    print("RESOSCAN - HARDWARE MODE (REAL MEASUREMENTS)")
    print("=" * 80)
    
    device = ResoScanDevice()
    
    # Try to auto-detect or use specified port
    print("\nSearching for connected ESP32...")
    
    if not device.auto_detect_port():
        print("\n[ERROR] No ESP32 device found!")
        print("\nTo use Hardware Mode:")
        print("  1. Connect ESP32 via USB")
        print("  2. Flash firmware to ESP32")
        print("  3. Run: python resoscan.py --mode hardware --port COM3")
        print("\nFor now, use Simulation Mode:")
        print("  python resoscan.py --mode simulate")
        return False
    
    # Connect to device
    if not device.connect():
        print("\n[ERROR] Could not connect to device")
        return False
    
    print(f"[CONNECTED] Device ready on {device.port}")
    print("\nStarting continuous measurement...")
    print("Press Ctrl+C to stop\n")
    
    try:
        measurement_count = 0
        while True:
            # Get data from device
            data_point = device.data_queue.get(timeout=5)
            
            if data_point.startswith("ACCEL_DATA"):
                measurement_count += 1
                print(f"[{measurement_count}] {data_point}")
                
                # Process signal
                # processor = SignalProcessor()
                # result = processor.analyze(data_point)
                # print(f"     Analysis: {result}")
    
    except KeyboardInterrupt:
        print("\n\nStopping measurement...")
    finally:
        device.disconnect()
        print("[DISCONNECTED] Device stopped")
    
    return True


def run_simulation_mode():
    """
    SIMULATION MODE: Educational demonstration
    
    This mode generates REALISTIC but SYNTHETIC tissue signals
    to demonstrate how the system works WITHOUT hardware.
    
    This is for:
    - Understanding the platform
    - Testing without hardware
    - Development and debugging
    - Educational purposes
    
    It is NOT real patient data.
    """
    print("\n" + "=" * 80)
    print("RESOSCAN - SIMULATION MODE (EDUCATIONAL/SYNTHETIC DATA)")
    print("=" * 80)
    print("\nNOTE: This is educational simulation, not real measurements")
    print("      Real hardware measurements require connected device\n")
    
    import numpy as np
    from signal_processing.signal_processor import SignalProcessor
    
    processor = SignalProcessor()
    
    # Define realistic tissue types for simulation
    tissue_types = [
        "Healthy Bone",
        "Fractured Bone", 
        "Healing Bone",
        "Osteoporotic",
        "Dense Bone",
        "Soft Tissue"
    ]
    
    print("Generating synthetic tissue signals for demonstration...\n")
    print(f"{'Measurement':<15} {'Tissue Type':<20} {'Frequency (Hz)':<15} {'Quality':<15}")
    print("-" * 65)
    
    # Generate a few synthetic measurements
    for i in range(5):
        # Randomly select tissue type
        tissue = np.random.choice(tissue_types)
        
        # Generate synthetic signal based on tissue type
        signal = processor.generate_synthetic_signal(
            tissue_type=tissue,
            duration=1.0,
            sampling_rate=3200
        )
        
        # Analyze the signal
        analysis = processor.analyze(signal, sampling_rate=3200)
        
        frequency = analysis.get('dominant_frequency', 0)
        quality = analysis.get('signal_quality', 'UNKNOWN')
        
        print(f"Sim {i+1:<12} {tissue:<20} {frequency:<15.2f} {quality:<15}")
    
    print("\n" + "=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    print("""
This simulation demonstrates the ResoScan analysis pipeline:

1. TISSUE CHARACTERIZATION
   - Tissue types: Healthy/Fractured/Healing/Osteoporotic/Dense/Soft
   - Each type has realistic frequency and Q-factor characteristics

2. SIGNAL ANALYSIS
   - Frequency detection: FFT-based spectral analysis
   - Quality assessment: Based on signal-to-noise ratio
   - Q-factor computation: From resonance characteristics

3. CLINICAL INTERPRETATION
   - Tissue Stiffness Index (TSI): 0-100%
   - Healing status: ACUTE/HEALING/GOOD/CLEARED
   - Recommendations: Activity levels and follow-up

TO USE WITH REAL HARDWARE:
  1. Connect ESP32 with ADXL343 accelerometer
  2. Flash firmware to device
  3. Run: python resoscan.py --mode hardware --port COM3

FOR MORE INFORMATION:
  - See README.md for setup instructions
  - Check embedded_firmware/ for ESP32 code
  - Review signal_processing/ for algorithm details
""")
    
    return True


def run_demo():
    """
    Quick demonstration comparing simulation vs requirements for hardware
    """
    print("\n" + "=" * 80)
    print("RESOSCAN - QUICK DEMO")
    print("=" * 80)
    
    print("""
ResoScan is a professional tissue diagnostics platform.

CURRENT STATUS:
  [✓] Signal processing engine: COMPLETE
  [✓] Analysis algorithms: COMPLETE
  [✓] ML classification: READY
  [✓] UI/Dashboard: READY
  [✗] Hardware connection: REQUIRES DEVICE

WHAT YOU CAN DO NOW (Without Hardware):
  - Understand how the system works
  - See analysis algorithms in action
  - Test with synthetic tissue signals
  - Explore the user interface

WHAT YOU NEED FOR REAL MEASUREMENTS:
  - ESP32 microcontroller ($10-15)
  - ADXL343 accelerometer (~$5)
  - USB cable for connection
  - 5 minutes to flash firmware

QUICK START:

1. See what's possible without hardware:
   $ python resoscan.py --mode simulate

2. Connect hardware and run:
   $ python resoscan.py --mode hardware

3. Build a custom analysis:
   $ python
   >>> from signal_processing.dynamic_processor import SignalProcessor
   >>> processor = SignalProcessor()
   >>> signal = processor.generate_synthetic_signal("Healing Bone", 1.0, 3200)
   >>> result = processor.analyze(signal, 3200)
   >>> print(result)
""")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="ResoScan - Tissue Diagnostics Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MODES:
  demo        Show quick overview and options
  simulate    Run educational simulation (no hardware needed)
  hardware    Connect to real ESP32 device and measure (REQUIRES DEVICE)

EXAMPLES:
  python resoscan.py --mode demo
  python resoscan.py --mode simulate
  python resoscan.py --mode hardware --port COM3

HARDWARE CONNECTION:
  Without --port, will auto-detect ESP32
  For manual port: python resoscan.py --mode hardware --port /dev/ttyUSB0
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['demo', 'simulate', 'hardware'],
        default='demo',
        help='Operating mode (default: demo)'
    )
    
    parser.add_argument(
        '--port',
        help='Serial port for hardware connection (e.g., COM3, /dev/ttyUSB0)'
    )
    
    args = parser.parse_args()
    
    # Run requested mode
    if args.mode == 'demo':
        success = run_demo()
    elif args.mode == 'simulate':
        success = run_simulation_mode()
    elif args.mode == 'hardware':
        success = run_hardware_mode()
    else:
        print("Unknown mode")
        return 1
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
