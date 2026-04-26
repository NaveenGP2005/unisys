"""
ResoScan Data Acquisition Module
=================================
Handles serial communication with ESP32 and real-time data streaming

Author: ResoScan Team
"""

import serial
import threading
import queue
import numpy as np
from datetime import datetime
import logging
from typing import Callable, Optional, List
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAcquisitionBuffer:
    """Ring buffer for accelerometer data"""
    
    def __init__(self, buffer_size: int = 3200):
        """
        Args:
            buffer_size: Number of samples to store (default 1 second at 3200 Hz)
        """
        self.buffer_size = buffer_size
        self.buffer_x = np.zeros(buffer_size, dtype=np.float32)
        self.buffer_y = np.zeros(buffer_size, dtype=np.float32)
        self.buffer_z = np.zeros(buffer_size, dtype=np.float32)
        self.timestamps = np.zeros(buffer_size, dtype=np.uint32)
        self.write_idx = 0
        self.is_full = False
    
    def add_sample(self, ax: float, ay: float, az: float, timestamp: int):
        """Add accelerometer sample to buffer"""
        self.buffer_x[self.write_idx] = ax
        self.buffer_y[self.write_idx] = ay
        self.buffer_z[self.write_idx] = az
        self.timestamps[self.write_idx] = timestamp
        
        self.write_idx = (self.write_idx + 1) % self.buffer_size
        if self.write_idx == 0:
            self.is_full = True
    
    def get_window(self, num_samples: int) -> tuple:
        """Extract last N samples in chronological order"""
        if num_samples > self.buffer_size:
            num_samples = self.buffer_size
        
        if not self.is_full:
            # Buffer not full yet
            start_idx = max(0, self.write_idx - num_samples)
            return (
                self.buffer_x[start_idx:self.write_idx],
                self.buffer_y[start_idx:self.write_idx],
                self.buffer_z[start_idx:self.write_idx],
                self.timestamps[start_idx:self.write_idx]
            )
        else:
            # Buffer is full, wrap around
            if num_samples >= self.buffer_size:
                return (self.buffer_x, self.buffer_y, self.buffer_z, self.timestamps)
            
            start_idx = (self.write_idx - num_samples) % self.buffer_size
            if start_idx + num_samples <= self.buffer_size:
                return (
                    self.buffer_x[start_idx:start_idx + num_samples],
                    self.buffer_y[start_idx:start_idx + num_samples],
                    self.buffer_z[start_idx:start_idx + num_samples],
                    self.timestamps[start_idx:start_idx + num_samples]
                )
            else:
                # Wrap around case
                part1_len = self.buffer_size - start_idx
                return (
                    np.concatenate([self.buffer_x[start_idx:], self.buffer_x[:self.write_idx]]),
                    np.concatenate([self.buffer_y[start_idx:], self.buffer_y[:self.write_idx]]),
                    np.concatenate([self.buffer_z[start_idx:], self.buffer_z[:self.write_idx]]),
                    np.concatenate([self.timestamps[start_idx:], self.timestamps[:self.write_idx]])
                )
    
    def get_all(self) -> tuple:
        """Get all buffered data"""
        return self.get_window(self.buffer_size)
    
    def clear(self):
        """Clear buffer"""
        self.buffer_x.fill(0)
        self.buffer_y.fill(0)
        self.buffer_z.fill(0)
        self.timestamps.fill(0)
        self.write_idx = 0
        self.is_full = False


class ResoScanDevice:
    """
    Main interface for ResoScan hardware communication
    Manages serial connection, data streaming, and command execution
    """
    
    def __init__(self, port: str = None, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize device connection
        
        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Serial communication speed
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_connected = False
        
        self.data_buffer = DataAcquisitionBuffer(buffer_size=3200)
        self.data_queue = queue.Queue(maxsize=1000)
        self.read_thread = None
        self.stop_reading = False
        
        # Callbacks
        self.on_data_received: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Statistics
        self.samples_received = 0
        self.errors_count = 0
        self.connection_time = None
    
    def auto_detect_port(self) -> Optional[str]:
        """Auto-detect ESP32 serial port"""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                if 'CH340' in port.description or 'USB' in port.description or 'ESP32' in port.description:
                    logger.info(f"Found ESP32 on port: {port.device}")
                    return port.device
        except Exception as e:
            logger.error(f"Error detecting port: {e}")
        
        return None
    
    def connect(self, port: str = None) -> bool:
        """
        Establish serial connection to device
        
        Args:
            port: Serial port (auto-detected if None)
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_connected:
            logger.warning("Already connected")
            return True
        
        try_port = port or self.port or self.auto_detect_port()
        
        if not try_port:
            logger.error("No serial port specified and auto-detection failed")
            return False
        
        try:
            self.serial_conn = serial.Serial(
                port=try_port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for ESP32 to reset
            
            self.is_connected = True
            self.connection_time = datetime.now()
            logger.info(f"Connected to {try_port} at {self.baudrate} baud")
            
            # Start read thread
            self.stop_reading = False
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            return True
        
        except serial.SerialException as e:
            logger.error(f"Failed to connect: {e}")
            if self.on_error:
                self.on_error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if not self.is_connected:
            return
        
        self.stop_reading = True
        if self.read_thread:
            self.read_thread.join(timeout=2)
        
        if self.serial_conn:
            self.serial_conn.close()
        
        self.is_connected = False
        logger.info("Disconnected")
    
    def _read_loop(self):
        """Background thread for reading serial data"""
        logger.info("Data read thread started")
        
        while not self.stop_reading and self.is_connected:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if line.startswith("ACCEL_DATA,"):
                        self._parse_accel_data(line)
                    elif line.startswith("ERROR"):
                        logger.error(f"Device error: {line}")
                        self.errors_count += 1
                        if self.on_error:
                            self.on_error(line)
                    else:
                        # Status or info message
                        logger.debug(f"Device: {line}")
                    
                    # Queue for UI
                    self.data_queue.put(line, block=False)
                
                else:
                    time.sleep(0.001)  # Small delay to prevent CPU spinning
            
            except queue.Full:
                logger.warning("Data queue full, dropping oldest message")
            except Exception as e:
                logger.error(f"Read error: {e}")
                self.errors_count += 1
                if self.on_error:
                    self.on_error(f"Read error: {e}")
                time.sleep(0.1)
        
        logger.info("Data read thread stopped")
    
    def _parse_accel_data(self, line: str):
        """Parse accelerometer data line"""
        try:
            # Format: ACCEL_DATA,<timestamp>,<x>,<y>,<z>,<force>
            parts = line.split(',')
            if len(parts) != 6:
                return
            
            timestamp = int(parts[1])
            ax = float(parts[2])
            ay = float(parts[3])
            az = float(parts[4])
            force = float(parts[5])
            
            # Convert raw counts to g (assuming ±16g range on ADXL343)
            ax_g = ax / 2048.0
            ay_g = ay / 2048.0
            az_g = az / 2048.0
            
            self.data_buffer.add_sample(ax_g, ay_g, az_g, timestamp)
            self.samples_received += 1
            
            if self.on_data_received:
                self.on_data_received({
                    'timestamp': timestamp,
                    'ax': ax_g,
                    'ay': ay_g,
                    'az': az_g,
                    'force': force
                })
        
        except Exception as e:
            logger.error(f"Parse error: {e}")
    
    def send_command(self, cmd: str) -> bool:
        """
        Send command to device
        
        Args:
            cmd: Command string (e.g., 'START_CHIRP', 'START_IMPULSE', 'START_SINE 100')
            
        Returns:
            True if sent successfully
        """
        if not self.is_connected:
            logger.error("Not connected")
            return False
        
        try:
            self.serial_conn.write((cmd + '\n').encode('utf-8'))
            logger.info(f"Command sent: {cmd}")
            return True
        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False
    
    def start_chirp_measurement(self) -> bool:
        """Start chirp frequency sweep (20-1000 Hz over 500ms)"""
        return self.send_command("START_CHIRP")
    
    def start_impulse_measurement(self) -> bool:
        """Start Gaussian impulse measurement"""
        return self.send_command("START_IMPULSE")
    
    def start_sine_measurement(self, frequency: int, duration_ms: int = 2000) -> bool:
        """Start pure sine wave measurement at specified frequency"""
        return self.send_command(f"START_SINE {frequency}")
    
    def stop_measurement(self) -> bool:
        """Stop any ongoing measurement"""
        return self.send_command("STOP")
    
    def get_status(self) -> bool:
        """Request device status"""
        return self.send_command("STATUS")
    
    def get_buffered_data(self, num_samples: int = 3200) -> tuple:
        """
        Get buffered accelerometer data
        
        Args:
            num_samples: Number of samples to retrieve (default 1 second)
            
        Returns:
            Tuple of (ax, ay, az, timestamps) as numpy arrays
        """
        return self.data_buffer.get_window(num_samples)
    
    def clear_buffer(self):
        """Clear data buffer"""
        self.data_buffer.clear()
    
    def get_statistics(self) -> dict:
        """Get connection statistics"""
        return {
            'is_connected': self.is_connected,
            'port': self.port,
            'samples_received': self.samples_received,
            'errors_count': self.errors_count,
            'connection_time': self.connection_time.isoformat() if self.connection_time else None,
            'buffer_usage': self.data_buffer.write_idx / self.data_buffer.buffer_size * 100
        }


def demo_data_acquisition():
    """Demonstration of data acquisition"""
    logger.info("=== ResoScan Data Acquisition Demo ===\n")
    
    # Create device instance
    device = ResoScanDevice()
    
    def on_data(data):
        if device.samples_received % 100 == 0:
            logger.info(f"Received {device.samples_received} samples - "
                       f"ax={data['ax']:.3f}g, force={data['force']:.2f}V")
    
    def on_error(error):
        logger.error(f"Error: {error}")
    
    device.on_data_received = on_data
    device.on_error = on_error
    
    # Attempt connection
    logger.info("Attempting to auto-detect and connect...")
    if device.connect():
        logger.info("✓ Connected successfully\n")
        
        # Wait a moment
        time.sleep(1)
        
        # Request status
        device.get_status()
        time.sleep(0.5)
        
        # Start a chirp measurement
        logger.info("Starting chirp measurement...")
        device.start_chirp_measurement()
        
        # Let it run for a few seconds
        time.sleep(4)
        
        # Get buffered data
        ax, ay, az, ts = device.get_buffered_data(1024)
        logger.info(f"\nBuffered data: {len(ax)} samples")
        logger.info(f"Acceleration range X: [{np.min(ax):.3f}, {np.max(ax):.3f}] g")
        logger.info(f"Acceleration range Y: [{np.min(ay):.3f}, {np.max(ay):.3f}] g")
        logger.info(f"Acceleration range Z: [{np.min(az):.3f}, {np.max(az):.3f}] g")
        
        # Get statistics
        stats = device.get_statistics()
        logger.info(f"\nStatistics: {stats}")
        
        # Disconnect
        device.disconnect()
        logger.info("\n✓ Demo complete")
    else:
        logger.info("Could not connect to device. Make sure ESP32 is connected and port is available.")


if __name__ == "__main__":
    demo_data_acquisition()
