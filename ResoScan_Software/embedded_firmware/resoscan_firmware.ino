/*
 * ResoScan Firmware - ESP32
 * Non-Invasive Tissue Diagnostics via Resonant Modal Spectroscopy
 * 
 * Hardware:
 * - ESP32 (Signal generation + USB communication)
 * - ADXL343 Accelerometer (I2C: GPIO21=SDA, GPIO22=SCL)
 * - Audio Amplifier (DAC output on GPIO25)
 * - Force Sensor (ADC on GPIO34)
 * 
 * Features:
 * - Programmable waveform generation (chirp, impulse, single frequency)
 * - Real-time accelerometer sampling at 3200 Hz
 * - USB serial streaming at 115200 baud
 * - Force feedback for standardized contact
 */

#include <Wire.h>
#include <driver/dac.h>
#include <driver/adc.h>

// ============================================================================
// ADXL343 I2C Configuration
// ============================================================================
#define ADXL343_ADDR 0x53
#define ADXL343_DATAX0 0x32
#define ADXL343_POWER_CTL 0x2D
#define ADXL343_DATA_FORMAT 0x31
#define ADXL343_BW_RATE 0x2C
#define ADXL343_INT_ENABLE 0x2E
#define ADXL343_INT_MAP 0x2F
#define ADXL343_FIFO_CTL 0x38

// ============================================================================
// Pin Definitions
// ============================================================================
#define SDA_PIN 21
#define SCL_PIN 22
#define DAC_PIN GPIO_NUM_25          // DAC1 for speaker excitation
#define FORCE_SENSOR_PIN 34          // ADC0

// ============================================================================
// Waveform Parameters
// ============================================================================
#define SAMPLING_FREQ 3200           // 3200 Hz accelerometer sampling
#define DAC_FREQ 50000               // DAC sampling rate (50 kHz)
#define FREQ_MIN 20                  // Hz
#define FREQ_MAX 1000                // Hz
#define CHIRP_DURATION_MS 500        // 500 ms chirp sweep
#define IMPULSE_WIDTH_MS 20          // 20 ms Gaussian impulse
#define DAC_MAX 255                  // 8-bit DAC

// ============================================================================
// Global Variables
// ============================================================================
volatile bool accel_ready = false;
volatile int accel_samples = 0;
int16_t accel_x, accel_y, accel_z;
uint8_t waveform_type = 0;          // 0=chirp, 1=impulse, 2=sine
uint16_t freq_start = FREQ_MIN;
uint16_t freq_end = FREQ_MAX;
uint16_t freq_current = FREQ_MIN;
float force_value = 0.0;
uint32_t chirp_start_time = 0;
bool chirp_active = false;

// ============================================================================
// Setup Function
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== ResoScan Firmware v1.0 ===");
  Serial.println("Initializing hardware...");
  
  // Initialize I2C for ADXL343
  Wire.begin(SDA_PIN, SCL_PIN, 400000);
  delay(100);
  
  // Initialize ADXL343
  if (!initADXL343()) {
    Serial.println("ERROR: ADXL343 initialization failed!");
    while(1) delay(1000);
  }
  Serial.println("✓ ADXL343 initialized");
  
  // Initialize DAC for audio output
  dac_output_enable(DAC_PIN);
  dac_output_voltage(DAC_PIN, 0);
  Serial.println("✓ DAC initialized");
  
  // Initialize ADC for force sensor
  analogSetAttenuation(ADC_11db);
  Serial.println("✓ Force sensor initialized");
  
  Serial.println("\nReady for operation.");
  Serial.println("Commands: START_CHIRP | START_IMPULSE | START_SINE <freq> | STOP | STATUS");
  Serial.println("=========================================\n");
}

// ============================================================================
// Main Loop
// ============================================================================
void loop() {
  // Read force sensor periodically
  force_value = analogRead(FORCE_SENSOR_PIN) * (3.3 / 4095.0);
  
  // Read accelerometer data
  readADXL343();
  
  // Process serial commands
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    processCommand(cmd);
  }
  
  // Stream accelerometer data if acquisition is active
  if (accel_ready) {
    // Format: ACCEL_DATA <timestamp_ms> <x> <y> <z> <force>
    uint32_t ts = millis();
    Serial.printf("ACCEL_DATA,%lu,%d,%d,%d,%.2f\n", ts, accel_x, accel_y, accel_z, force_value);
    accel_ready = false;
  }
  
  // Manage chirp generation
  if (chirp_active) {
    manageChrpGeneration();
  }
}

// ============================================================================
// ADXL343 Initialization
// ============================================================================
bool initADXL343() {
  // Check device ID
  uint8_t devid = readADXL343Register(0x00);
  if (devid != 0xE5) {
    Serial.printf("ADXL343 ID mismatch: 0x%02X (expected 0xE5)\n", devid);
    return false;
  }
  
  // Set data format: 16-bit, ±16g range
  writeADXL343Register(ADXL343_DATA_FORMAT, 0x0B);
  delay(10);
  
  // Set bandwidth rate: 1600 Hz (0x0F)
  writeADXL343Register(ADXL343_BW_RATE, 0x0F);
  delay(10);
  
  // Enable measurements
  writeADXL343Register(ADXL343_POWER_CTL, 0x08);
  delay(10);
  
  return true;
}

// ============================================================================
// Read ADXL343 Data (6 bytes: 2 per axis)
// ============================================================================
void readADXL343() {
  Wire.beginTransmission(ADXL343_ADDR);
  Wire.write(ADXL343_DATAX0);
  Wire.endTransmission(false);
  
  Wire.requestFrom(ADXL343_ADDR, (uint8_t)6);
  if (Wire.available() >= 6) {
    uint8_t xl = Wire.read();
    uint8_t xh = Wire.read();
    uint8_t yl = Wire.read();
    uint8_t yh = Wire.read();
    uint8_t zl = Wire.read();
    uint8_t zh = Wire.read();
    
    accel_x = (int16_t)(xh << 8 | xl);
    accel_y = (int16_t)(yh << 8 | yl);
    accel_z = (int16_t)(zh << 8 | zl);
    
    accel_ready = true;
    accel_samples++;
  }
}

// ============================================================================
// I2C Helper Functions
// ============================================================================
uint8_t readADXL343Register(uint8_t reg) {
  Wire.beginTransmission(ADXL343_ADDR);
  Wire.write(reg);
  Wire.endTransmission(false);
  Wire.requestFrom(ADXL343_ADDR, (uint8_t)1);
  if (Wire.available()) return Wire.read();
  return 0xFF;
}

void writeADXL343Register(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(ADXL343_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission(true);
}

// ============================================================================
// Waveform Generation
// ============================================================================
void generateChirp() {
  /*
   * Logarithmic chirp from FREQ_MIN to FREQ_MAX
   * Duration: CHIRP_DURATION_MS
   */
  chirp_start_time = millis();
  chirp_active = true;
  Serial.printf("Starting chirp: %d Hz -> %d Hz over %d ms\n", 
                FREQ_MIN, FREQ_MAX, CHIRP_DURATION_MS);
}

void manageChrpGeneration() {
  uint32_t elapsed = millis() - chirp_start_time;
  
  if (elapsed >= CHIRP_DURATION_MS) {
    dac_output_voltage(DAC_PIN, 0);
    chirp_active = false;
    Serial.println("Chirp complete.");
    return;
  }
  
  // Logarithmic frequency sweep: f(t) = f_min * (f_max/f_min)^(t/T)
  float progress = (float)elapsed / CHIRP_DURATION_MS;
  freq_current = FREQ_MIN * pow((float)FREQ_MAX / FREQ_MIN, progress);
  
  // Generate sine wave sample
  static uint32_t phase = 0;
  float sample = 127.5 + 127.5 * sin(2 * M_PI * phase / (DAC_FREQ / freq_current));
  dac_output_voltage(DAC_PIN, (uint8_t)sample);
  
  phase++;
  if (phase >= DAC_FREQ) phase = 0;
}

void generateImpulse() {
  /*
   * Gaussian impulse centered at time 0
   */
  Serial.println("Starting Gaussian impulse...");
  uint32_t start_time = millis();
  
  while (millis() - start_time < IMPULSE_WIDTH_MS) {
    uint32_t elapsed = millis() - start_time;
    float t = (float)elapsed / IMPULSE_WIDTH_MS - 0.5;  // -0.5 to 0.5
    float gaussian = 127.5 + 127.5 * exp(-20 * t * t);
    dac_output_voltage(DAC_PIN, (uint8_t)gaussian);
    delayMicroseconds(20);  // ~50 kHz DAC update rate
  }
  
  dac_output_voltage(DAC_PIN, 0);
  Serial.println("Impulse complete.");
}

void generateSine(uint16_t freq, uint16_t duration_ms) {
  /*
   * Pure sine wave at specified frequency
   */
  Serial.printf("Starting sine: %d Hz for %d ms\n", freq, duration_ms);
  uint32_t start_time = millis();
  uint32_t phase = 0;
  
  while (millis() - start_time < duration_ms) {
    float sample = 127.5 + 127.5 * sin(2 * M_PI * phase / (DAC_FREQ / freq));
    dac_output_voltage(DAC_PIN, (uint8_t)sample);
    phase++;
    if (phase >= DAC_FREQ) phase = 0;
    delayMicroseconds(20);
  }
  
  dac_output_voltage(DAC_PIN, 0);
  Serial.println("Sine complete.");
}

// ============================================================================
// Serial Command Processing
// ============================================================================
void processCommand(String cmd) {
  if (cmd == "START_CHIRP") {
    generateChirp();
  }
  else if (cmd == "START_IMPULSE") {
    generateImpulse();
  }
  else if (cmd.startsWith("START_SINE")) {
    int space_idx = cmd.indexOf(' ');
    if (space_idx != -1) {
      String freq_str = cmd.substring(space_idx + 1);
      uint16_t freq = freq_str.toInt();
      if (freq >= FREQ_MIN && freq <= FREQ_MAX) {
        generateSine(freq, 2000);  // 2 second duration
      } else {
        Serial.printf("ERROR: Frequency out of range [%d, %d]\n", FREQ_MIN, FREQ_MAX);
      }
    }
  }
  else if (cmd == "STOP") {
    dac_output_voltage(DAC_PIN, 0);
    chirp_active = false;
    Serial.println("Stopped.");
  }
  else if (cmd == "STATUS") {
    Serial.printf("=== Status ===\n");
    Serial.printf("Accel samples: %d\n", accel_samples);
    Serial.printf("Force: %.2f V\n", force_value);
    Serial.printf("Chirp active: %s\n", chirp_active ? "YES" : "NO");
    Serial.printf("Accel ready: %s\n", accel_ready ? "YES" : "NO");
  }
  else {
    Serial.println("Unknown command. Try: START_CHIRP | START_IMPULSE | START_SINE <freq> | STOP | STATUS");
  }
}
