# ResoScan Installation & Setup Guide

Complete step-by-step guide for setting up the ResoScan software platform.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Python Installation](#python-installation)
3. [Project Setup](#project-setup)
4. [Hardware Setup](#hardware-setup)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 2 GB minimum (4 GB recommended)
- **Disk Space**: 500 MB for installation
- **USB Port**: For ESP32 device connection

### Recommended System

- **CPU**: Intel i5/i7 or equivalent
- **RAM**: 8 GB
- **Python**: 3.9 or 3.10
- **OS**: Windows 10/11 or Ubuntu 20.04 LTS

---

## Python Installation

### Windows

1. **Download Python**
   - Visit https://www.python.org/downloads/
   - Download Python 3.10 installer
   - Run installer

2. **During Installation**
   - ✓ Check "Add Python to PATH"
   - ✓ Check "Install pip"
   - Click "Install Now"

3. **Verify Installation**
   ```bash
   python --version
   pip --version
   ```

### macOS

```bash
# Using Homebrew (recommended)
brew install python@3.10

# Verify
python3 --version
pip3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3-pip python3-venv

# Verify
python3 --version
pip3 --version
```

---

## Project Setup

### 1. Navigate to Project Directory

```bash
cd d:\Study\Hackathons\unisys\ResoScan_Software
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip

```bash
pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**

```
Successfully installed numpy scipy scikit-learn PySerial PyQt5 pyqtgraph ...
```

### 5. Verify Installation

```bash
python -c "
import numpy
import scipy
import sklearn
import serial
import PyQt5
import pyqtgraph
print('✓ All dependencies installed successfully')
"
```

---

## Hardware Setup

### ESP32 Configuration

1. **Install ESP32 Board Manager**
   - Open Arduino IDE
   - Go to Preferences
   - Add URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Go to Board Manager → Search "ESP32" → Install

2. **Install Required Libraries**
   - Sketch → Include Library → Manage Libraries
   - Search and install:
     - Wire (built-in)
     - driver/dac (built-in)
     - driver/adc (built-in)

3. **Upload Firmware**
   - Open `embedded_firmware/resoscan_firmware.ino` in Arduino IDE
   - Select Board: "ESP32 Dev Module"
   - Select Port: Appropriate COM port
   - Click Upload

4. **Monitor Serial Output**
   - Tools → Serial Monitor
   - Set baud rate to 115200
   - Should see startup messages

### Hardware Connections

**ADXL343 Accelerometer (I2C)**

```
ADXL343  →  ESP32
VCC      →  3.3V
GND      →  GND
SDA      →  GPIO 21
SCL      →  GPIO 22
INT      →  (not used in basic config)
```

**Audio Amplifier**

```
Input    →  GPIO 25 (DAC1)
GND      →  GND
VCC      →  5V (from power source)
Output   →  Speaker/Actuator
```

**Force Sensor**

```
Signal   →  GPIO 34 (ADC0)
GND      →  GND
VCC      →  3.3V
```

---

## Running the Application

### Option 1: Demo Mode (No Hardware Required)

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python main.py --mode demo
```

**Output:**

```
╔═══════════════════════════════════════════════════════════╗
║        ResoScan - Non-Invasive Tissue Diagnostics        ║
║          Resonant Modal Spectroscopy Platform            ║
║                   Version 1.0.0 | Unisys 2026            ║
╚═══════════════════════════════════════════════════════════╝

============================================================
DEMO MODE: Simulated ResoScan Operation
============================================================

=== ResoScan Signal Processing Demo ===
...
```

### Option 2: Graphical Interface (GUI)

```bash
python main.py --mode gui
```

**Auto-detect device:**

```bash
python main.py --mode gui
```

**Specify port:**

```bash
# Windows
python main.py --mode gui --device COM3

# Linux
python main.py --mode gui --device /dev/ttyUSB0

# macOS
python main.py --mode gui --device /dev/tty.usbserial-*
```

### Option 3: Command-Line Interface (CLI)

```bash
python main.py --mode cli --device COM3
```

**Interactive menu:**

```
Available commands:
  1. Start CHIRP measurement
  2. Start IMPULSE measurement
  3. Start SINE wave measurement
  4. Get device status
  5. Process buffered data
  6. Exit
```

---

## Running Tests

### Test All Modules

```bash
python -m pytest tests/test_all.py -v
```

### Test Specific Module

```bash
# Signal processing tests
python -m pytest tests/test_all.py::TestSignalProcessor -v

# ML classification tests
python -m pytest tests/test_all.py::TestMLClassifiers -v

# Integration tests
python -m pytest tests/test_all.py::TestIntegration -v
```

### Run Tests with Coverage

```bash
pip install pytest-cov
pytest tests/test_all.py --cov=signal_processing --cov=ml_models --cov-report=html
```

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**

```bash
# Windows: Add Python to PATH
setx PATH "%PATH%;C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python310"

# Verify
python --version
```

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall
pip install -r requirements.txt
```

### Issue: "Device not found / Port error"

**Solution:**

```bash
# List available ports
python -m serial.tools.list_ports

# Try specific port
python main.py --mode gui --device COM3

# On Linux, check permissions
sudo usermod -a -G dialout $USER
```

### Issue: "PyQt5 ImportError"

**Solution:**

```bash
pip install --upgrade PyQt5
# Or for specific platforms
pip install PyQt5==5.15.9
pip install pyqtgraph==0.13.3
```

### Issue: "Serial communication timeout"

**Solution:**

1. Check ESP32 is powered and connected
2. Verify USB cable is working
3. Try different USB port
4. Restart ESP32 (power cycle)
5. Check baud rate is 115200

### Issue: "Permission denied" on Linux/Mac

**Solution:**

```bash
# Make files executable
chmod +x main.py

# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Or run with sudo
sudo python main.py --mode gui --device /dev/ttyUSB0
```

---

## Quick Reference

### Command Summary

```bash
# Setup
python -m venv venv
source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Run
python main.py --mode demo          # Demo mode
python main.py --mode gui           # GUI (auto-detect)
python main.py --mode gui --device COM3  # GUI (specific port)
python main.py --mode cli --device COM3  # CLI

# Test
python -m pytest tests/test_all.py -v

# List ports
python -m serial.tools.list_ports
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Remove Virtual Environment

```bash
# Windows
rmdir /s venv

# Linux/Mac
rm -rf venv
```

---

## Next Steps

1. **Explore Demo Mode**: Run `python main.py --mode demo` to understand the workflow
2. **Review Documentation**: Read `README.md` for API details
3. **Connect Hardware**: Follow hardware setup to connect ESP32
4. **Run GUI**: Launch dashboard with `python main.py --mode gui`
5. **Perform Measurements**: Start your first clinical measurement
6. **Export Data**: Save and analyze results

---

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review README.md for API documentation
3. Check device logs: `python main.py --mode cli --device COM3`
4. Contact development team: ResoScan@MSRIT.edu

---

**Happy diagnosing with ResoScan! 🔬✅**
