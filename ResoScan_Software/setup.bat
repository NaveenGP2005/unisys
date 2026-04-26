@echo off
REM ResoScan Quick Setup Script for Windows
REM Automates environment setup and dependency installation

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║        ResoScan Quick Setup Script (Windows)              ║
echo ║        Non-Invasive Tissue Diagnostics Platform          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher
    pause
    exit /b 1
)
python --version
echo ✓ Python found

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo ✓ Dependencies installed

REM Verify installation
echo.
echo [5/5] Verifying installation...
python -c "
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

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║              Setup Complete! ✓                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Next steps:
echo   1. Run demo:      python main.py --mode demo
echo   2. Run GUI:       python main.py --mode gui
echo   3. Connect device: python main.py --mode gui --device COM3
echo.
echo For more info, see INSTALL.md and README.md
echo.
pause
