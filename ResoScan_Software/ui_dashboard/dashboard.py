"""
ResoScan GUI Dashboard - PyQt5
===============================
Real-time visualization and diagnostic interface

Features:
- Live spectrogram and FFT display
- Tissue stiffness index calculation
- Clinical indicators and thresholds
- Multi-measurement management
- Data export functionality

Author: ResoScan Team
"""

import sys
import numpy as np
from datetime import datetime
from pathlib import Path
import json
import threading
import time

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
        QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
        QFileDialog, QGroupBox, QFormLayout, QProgressBar, QStatusBar
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
    from PyQt5.QtGui import QColor, QFont, QIcon
    from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
    from PyQt5.QtCore import QDateTime
except ImportError as e:
    print(f"PyQt5 not installed: {e}")
    print("Install with: pip install PyQt5 PyQtGraph")
    sys.exit(1)

try:
    import pyqtgraph as pg
except ImportError:
    print("PyQtGraph not installed. Install with: pip install pyqtgraph")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MeasurementWorker(QThread):
    """Background worker thread for measurements"""
    
    progress = pyqtSignal(int)
    measurement_complete = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, device, measurement_type: str, duration_ms: int = 2000):
        super().__init__()
        self.device = device
        self.measurement_type = measurement_type
        self.duration_ms = duration_ms
    
    def run(self):
        try:
            if self.measurement_type == "chirp":
                self.device.start_chirp_measurement()
            elif self.measurement_type == "impulse":
                self.device.start_impulse_measurement()
            elif self.measurement_type == "sine":
                self.device.start_sine_measurement(100, self.duration_ms)
            
            # Wait for measurement
            time.sleep(self.duration_ms / 1000.0 + 0.5)
            
            # Get data
            ax, ay, az, ts = self.device.get_buffered_data(3200)
            
            self.measurement_complete.emit({
                'type': self.measurement_type,
                'x': ax.tolist(),
                'y': ay.tolist(),
                'z': az.tolist(),
                'timestamps': ts.tolist()
            })
        
        except Exception as e:
            self.error_signal.emit(str(e))


class ResoScanDashboard(QMainWindow):
    """
    Main dashboard for ResoScan diagnostics
    """
    
    def __init__(self, device=None):
        super().__init__()
        self.device = device
        self.current_features = None
        self.measurements_history = []
        self.measurement_worker = None
        
        self.setWindowTitle("ResoScan - Non-Invasive Tissue Diagnostics")
        self.setGeometry(100, 100, 1600, 1000)
        
        self.init_ui()
        self.setup_timers()
        
        logger.info("Dashboard initialized")
    
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # Left side: Controls
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.create_connection_panel())
        left_layout.addWidget(self.create_measurement_panel())
        left_layout.addWidget(self.create_diagnostic_panel())
        left_layout.addStretch()
        
        # Right side: Visualization
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.create_visualization_tabs())
        
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
    
    def create_connection_panel(self) -> QGroupBox:
        """Connection and device status panel"""
        group = QGroupBox("Device Connection")
        layout = QFormLayout()
        
        # Port selection
        self.port_combo = QComboBox()
        self.port_combo.addItems(['COM3', 'COM4', '/dev/ttyUSB0', '/dev/ttyUSB1'])
        layout.addRow("Serial Port:", self.port_combo)
        
        # Connect button
        self.connect_btn = QPushButton("Connect Device")
        self.connect_btn.clicked.connect(self.on_connect_clicked)
        layout.addRow(self.connect_btn)
        
        # Status label
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addRow("Status:", self.status_label)
        
        # Device info
        self.samples_label = QLabel("0 samples")
        layout.addRow("Samples:", self.samples_label)
        
        group.setLayout(layout)
        return group
    
    def create_measurement_panel(self) -> QGroupBox:
        """Measurement control panel"""
        group = QGroupBox("Measurement Control")
        layout = QFormLayout()
        
        # Measurement type
        self.measurement_type = QComboBox()
        self.measurement_type.addItems(['Chirp (20-1000 Hz)', 'Impulse', 'Sine Wave'])
        layout.addRow("Measurement Type:", self.measurement_type)
        
        # Duration
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(500, 5000)
        self.duration_spinbox.setValue(2000)
        self.duration_spinbox.setSuffix(" ms")
        layout.addRow("Duration:", self.duration_spinbox)
        
        # Start button
        self.start_measure_btn = QPushButton("Start Measurement")
        self.start_measure_btn.clicked.connect(self.on_start_measurement)
        self.start_measure_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        layout.addRow(self.start_measure_btn)
        
        # Progress
        self.measure_progress = QProgressBar()
        layout.addRow(self.measure_progress)
        
        group.setLayout(layout)
        return group
    
    def create_diagnostic_panel(self) -> QGroupBox:
        """Clinical diagnostic panel"""
        group = QGroupBox("Clinical Diagnostics")
        layout = QFormLayout()
        
        # Application selection
        self.application_combo = QComboBox()
        self.application_combo.addItems([
            'Fracture Healing',
            'Pneumothorax Detection',
            'Bladder Compliance'
        ])
        self.application_combo.currentTextChanged.connect(self.on_application_changed)
        layout.addRow("Application:", self.application_combo)
        
        # Clinical threshold
        self.threshold_label = QLabel("TSI > 80% for safe weight-bearing")
        layout.addRow("Threshold:", self.threshold_label)
        
        # Result display
        self.result_label = QLabel("No measurement yet")
        self.result_label.setStyleSheet("font-size: 14px; color: #1976D2;")
        layout.addRow("Result:", self.result_label)
        
        # Confidence
        self.confidence_progress = QProgressBar()
        self.confidence_progress.setValue(0)
        layout.addRow("Confidence:", self.confidence_progress)
        
        # Export button
        self.export_btn = QPushButton("Export Measurement")
        self.export_btn.clicked.connect(self.on_export_data)
        layout.addRow(self.export_btn)
        
        group.setLayout(layout)
        return group
    
    def create_visualization_tabs(self) -> QTabWidget:
        """Create visualization tabs"""
        tabs = QTabWidget()
        
        # Tab 1: FFT/Spectrogram
        self.fft_plot = pg.PlotWidget(title="Power Spectral Density")
        self.fft_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.fft_plot.setLabel('left', 'Power Spectral Density', units='g²/Hz')
        self.fft_plot.showGrid(x=True, y=True)
        tabs.addTab(self.fft_plot, "FFT / Spectrogram")
        
        # Tab 2: Time domain
        self.time_plot = pg.PlotWidget(title="Acceleration Data")
        self.time_plot.setLabel('bottom', 'Time', units='s')
        self.time_plot.setLabel('left', 'Acceleration', units='g')
        self.time_plot.showGrid(x=True, y=True)
        tabs.addTab(self.time_plot, "Time Domain")
        
        # Tab 3: Measurement history
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            'Timestamp', 'Type', 'f_res (Hz)', 'Q-factor', 'TSI (%)', 'Status'
        ])
        self.history_table.setRowCount(20)
        tabs.addTab(self.history_table, "Measurement History")
        
        # Tab 4: Statistics
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-family: monospace; white-space: pre;")
        tabs.addTab(self.stats_label, "Statistics")
        
        return tabs
    
    def on_connect_clicked(self):
        """Handle device connection"""
        if self.device is None:
            QMessageBox.warning(self, "Error", "No device instance provided")
            return
        
        try:
            port = self.port_combo.currentText()
            if self.device.connect(port):
                self.connect_btn.setText("Disconnect Device")
                self.status_label.setText("Connected")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.statusBar.showMessage(f"Connected to {port}")
            else:
                QMessageBox.critical(self, "Error", "Failed to connect to device")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def on_start_measurement(self):
        """Start a measurement"""
        if not self.device or not self.device.is_connected:
            QMessageBox.warning(self, "Error", "Device not connected")
            return
        
        measurement_idx = self.measurement_type.currentIndex()
        measurement_types = ["chirp", "impulse", "sine"]
        
        self.start_measure_btn.setEnabled(False)
        self.measure_progress.setValue(0)
        
        self.measurement_worker = MeasurementWorker(
            self.device,
            measurement_types[measurement_idx],
            self.duration_spinbox.value()
        )
        self.measurement_worker.measurement_complete.connect(self.on_measurement_complete)
        self.measurement_worker.error_signal.connect(self.on_measurement_error)
        self.measurement_worker.start()
        
        self.statusBar.showMessage("Measurement in progress...")
    
    def on_measurement_complete(self, data: dict):
        """Process completed measurement"""
        try:
            # Simulate signal processing
            from signal_processing.signal_processor import SignalProcessor
            
            processor = SignalProcessor()
            ax = np.array(data['x'])
            
            features = processor.process_raw_signal(ax, timestamp=time.time())
            
            # Plot FFT
            self.fft_plot.clear()
            self.fft_plot.plot(features.frequency_axis, features.power_spectral_density,
                             pen=pg.mkPen(color='#1976D2', width=2))
            
            # Plot time domain
            self.time_plot.clear()
            self.time_plot.plot(ax, pen=pg.mkPen(color='#FF6F00', width=1))
            
            # Update diagnostic result
            self.result_label.setText(
                f"f_res = {features.resonant_frequency:.1f} Hz | "
                f"Q = {features.q_factor:.2f} | "
                f"ζ = {features.damping_ratio:.3f}"
            )
            self.confidence_progress.setValue(int(np.mean(np.abs(features.peak_amplitudes)) * 100))
            
            # Add to history
            self.measurements_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': data['type'],
                'features': features
            })
            
            # Update table
            row = len(self.measurements_history) - 1
            if row < self.history_table.rowCount():
                self.history_table.setItem(row, 0, QTableWidgetItem(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                self.history_table.setItem(row, 1, QTableWidgetItem(data['type'].upper()))
                self.history_table.setItem(row, 2, QTableWidgetItem(
                    f"{features.resonant_frequency:.1f}"
                ))
                self.history_table.setItem(row, 3, QTableWidgetItem(
                    f"{features.q_factor:.2f}"
                ))
            
            self.statusBar.showMessage("Measurement complete")
            self.start_measure_btn.setEnabled(True)
        
        except Exception as e:
            logger.error(f"Error processing measurement: {e}")
            self.on_measurement_error(str(e))
    
    def on_measurement_error(self, error: str):
        """Handle measurement error"""
        QMessageBox.critical(self, "Measurement Error", error)
        self.start_measure_btn.setEnabled(True)
        self.statusBar.showMessage("Error during measurement")
    
    def on_application_changed(self, app_name: str):
        """Update diagnostic thresholds based on application"""
        thresholds = {
            'Fracture Healing': 'TSI > 80% for safe weight-bearing',
            'Pneumothorax Detection': 'Power Ratio > 2.0 indicates pneumothorax',
            'Bladder Compliance': 'Wave velocity > 4 m/s indicates elevated pressure'
        }
        self.threshold_label.setText(thresholds.get(app_name, ""))
    
    def on_export_data(self):
        """Export current measurement data"""
        if not self.measurements_history:
            QMessageBox.warning(self, "Warning", "No measurements to export")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Measurement",
            "",
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if filepath:
            try:
                # Simplified export
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'measurements_count': len(self.measurements_history),
                    'latest_measurement': {
                        'type': self.measurements_history[-1]['type'],
                        'timestamp': self.measurements_history[-1]['timestamp']
                    }
                }
                
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                QMessageBox.information(self, "Success", f"Data exported to {filepath}")
                self.statusBar.showMessage(f"Exported to {filepath}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {e}")
    
    def setup_timers(self):
        """Setup periodic update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(500)  # Update every 500ms
    
    def update_display(self):
        """Update display elements"""
        if self.device and self.device.is_connected:
            self.samples_label.setText(f"{self.device.samples_received} samples")
            stats = self.device.get_statistics()
            self.stats_label.setText(
                f"Connected: {stats['is_connected']}\n"
                f"Samples: {stats['samples_received']}\n"
                f"Errors: {stats['errors_count']}\n"
                f"Buffer: {stats['buffer_usage']:.1f}%"
            )


def run_dashboard(device=None):
    """Launch the dashboard"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    dashboard = ResoScanDashboard(device)
    dashboard.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Run without device (demo mode)
    run_dashboard()
