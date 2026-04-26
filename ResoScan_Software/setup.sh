#!/bin/bash
# ResoScan Quick Setup Script
# Automates environment setup and dependency installation

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        ResoScan Quick Setup Script                       ║"
echo "║        Non-Invasive Tissue Diagnostics Platform          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi
python3 --version
echo "✓ Python found"

# Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Verify installation
echo ""
echo "[5/5] Verifying installation..."
python3 -c "
import sys
import numpy
import scipy
import sklearn
import serial
print('✓ numpy:       ', numpy.__version__)
print('✓ scipy:       ', scipy.__version__)
print('✓ scikit-learn:', sklearn.__version__)
print('✓ PySerial:    ', serial.VERSION)
try:
    import PyQt5
    print('✓ PyQt5:       OK')
except:
    print('⚠ PyQt5:       Install optional GUI components')
"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              Setup Complete! ✓                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Run demo:      python main.py --mode demo"
echo "  2. Run GUI:       python main.py --mode gui"
echo "  3. Connect device: python main.py --mode gui --device COM3"
echo ""
echo "For more info, see INSTALL.md and README.md"
