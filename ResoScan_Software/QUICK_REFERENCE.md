# ResoScan Dynamic System - Quick Reference Card

## 🚀 What's Dynamic?

| Component           | Static (v1)          | Dynamic (v2)             |
| ------------------- | -------------------- | ------------------------ |
| FFT Window Size     | Fixed 1024           | Adapts 256-2048          |
| Peak Detection      | Fixed prominence 0.1 | Dynamic 1-3× noise floor |
| Noise Filtering     | No filtering         | SNR-tuned Butterworth    |
| Clinical Thresholds | Fixed (TSI >80%)     | Adapts per measurement   |
| Quality Assessment  | None                 | 5-level SNR-based        |
| Window Type         | Hann only            | Hann/Hamming/Tukey       |
| Signal Confidence   | Not reported         | Yes (via quality)        |
| **Result**:         | Basic analysis       | Adaptive diagnostics     |

## 📊 Signal Quality Levels

```
EXCELLENT (SNR > 30 dB)
└─ Perfect conditions, maximum confidence
   └─ Use relaxed thresholds, full sensitivity

GOOD (SNR > 20 dB)
└─ Good conditions, high confidence
   └─ Use standard thresholds

ACCEPTABLE (SNR > 10 dB)
└─ Acceptable conditions, moderate confidence
   └─ Slightly tighter thresholds

POOR (SNR > 0 dB)
└─ Poor conditions, low confidence
   └─ Conservative thresholds, verify measurements

INVALID (SNR ≤ 0 dB)
└─ No valid signal detected
   └─ Repeat measurement
```

## 🔧 How Adaptive Processing Works

### Example: Healthy Bone vs Injured Bone

**Healthy Bone Signal:**

```
Input: Clean resonance at 200 Hz, noise ~0.05
↓
Signal Quality: EXCELLENT (SNR 74 dB)
↓
Processing Adapts:
  • FFT: 1024-point (optimal for this data)
  • Window: Hann (high resolution, stationary)
  • Filter: Order 2, Cutoff 0.2 (light - high SNR)
  • Prominence: 1× noise floor (sensitive)
  • Thresholds: Relaxed (high confidence)
↓
Output: Precise frequency, high confidence diagnosis
```

**Injured Bone Signal:**

```
Input: Weak resonance at 100 Hz, noise ~0.15
↓
Signal Quality: ACCEPTABLE (SNR 12 dB)
↓
Processing Adapts:
  • FFT: 512-point (better for weak signals)
  • Window: Hamming (balanced, some non-stationarity)
  • Filter: Order 3, Cutoff 0.15 (moderate - lower SNR)
  • Prominence: 2× noise floor (reduce false peaks)
  • Thresholds: Conservative (moderate confidence)
↓
Output: Robust frequency estimate, confidence-scaled diagnosis
```

## 🎯 Key Adaptive Formulas

### 1. Signal Quality Assessment

```
SNR (dB) = 10 × log₁₀(signal_power / noise_power)

Quality ← SNR:
  if SNR > 30  → EXCELLENT
  if SNR > 20  → GOOD
  if SNR > 10  → ACCEPTABLE
  if SNR > 0   → POOR
  else         → INVALID
```

### 2. Dynamic FFT Sizing

```
Length ≤ 512   → FFT_SIZE = 256
512 < L ≤ 1024 → FFT_SIZE = 512
1K < L ≤ 2K    → FFT_SIZE = 1024
L > 2048       → FFT_SIZE = 2048

Result: Optimal frequency resolution for each measurement
```

### 3. Stationarity Calculation

```
Divide signal into 4 segments:
  → Calculate mean and variance per segment
  → Compute variance of means across segments

Stationarity = 1 - (variance_of_means / overall_variance)
Range: 0 (non-stationary) to 1 (highly stationary)

Usage:
  > 0.8  → Use Hann window (high resolution)
  0.6-0.8 → Use Hamming window (balanced)
  < 0.6  → Use Tukey window (flexible)
```

### 4. Dynamic Peak Prominence

```
Noise_Floor = median(|signal - median(signal)|)

Prominence_Threshold ← SNR:
  SNR < 10   → 3.0 × Noise_Floor
  10 ≤ SNR < 20 → 2.0 × Noise_Floor
  20 ≤ SNR < 30 → 1.5 × Noise_Floor
  SNR ≥ 30   → 1.0 × Noise_Floor

Result: Fewer false peaks in noisy signals, better detection in clean signals
```

### 5. Dynamic TSI Threshold

```
Base_TSI_Threshold = 80.0%

Quality_Factor ← Signal_Quality:
  EXCELLENT → 0.85 (relax threshold)
  GOOD      → 0.95 (standard)
  ACCEPTABLE → 1.05 (tighten)
  POOR      → 1.20 (conservative)
  INVALID   → N/A

Stationarity_Factor = 0.8 + (0.2 × Stationarity)
Q_Factor_Normalization = (Q_Factor / 10) clamped to [0.8, 1.2]

Dynamic_TSI_Threshold = Base × Quality_Factor × Stationarity × Q_Factor
```

## 📈 Real-Time Adjustment Examples

### Example 1: High Noise Detection

```
Measurement: Noisy environment
↓ SNR drops to 5 dB
↓
System Responds:
  ✓ Quality: POOR (flagged)
  ✓ Filter Order: Increased to 4 (aggressive)
  ✓ Prominence: 3× noise floor (suppress noise peaks)
  ✓ TSI Threshold: +20% (conservative)
  ✓ Confidence: Reduced to 30%
↓
Result: Robust measurement despite noise
```

### Example 2: High Quality Signal

```
Measurement: Excellent contact, clean signal
↓ SNR reaches 70 dB
↓
System Responds:
  ✓ Quality: EXCELLENT (flagged)
  ✓ Filter Order: Reduced to 2 (light touch)
  ✓ Prominence: 1× noise floor (maximum sensitivity)
  ✓ TSI Threshold: -15% (sensitive)
  ✓ Confidence: Increased to 100%
↓
Result: Maximum sensitivity to small variations
```

### Example 3: Changing Resonance

```
Measurement: Bone starting to heal
↓ Frequency shifts from 100 Hz → 150 Hz
↓ Q-factor changes from 8 → 12
↓
System Responds:
  ✓ FFT Window: Automatically resized if needed
  ✓ Peak Detection: Adjusted to new frequency
  ✓ Q-Factor Threshold: Updated
  ✓ Dynamic Threshold: Adjusted by new Q-factor ratio
↓
Result: Automatic tracking of healing progression
```

## 🎛️ Configuration (config.json)

Add these for dynamic processor control:

```json
{
  "dynamic_processing": {
    "enabled": true,
    "snr_thresholds": {
      "excellent": 30,
      "good": 20,
      "acceptable": 10,
      "poor": 0
    },
    "adaptive_filtering": {
      "enabled": true,
      "min_order": 2,
      "max_order": 4
    },
    "dynamic_fft": {
      "enabled": true,
      "sizes": [256, 512, 1024, 2048]
    },
    "stationarity_weights": {
      "window_selection": 1.0,
      "threshold_adjustment": 0.3
    },
    "confidence_reporting": true
  }
}
```

## 🔍 Monitoring Outputs

### Per-Measurement Output

```
Measurement #23:
├─ Frequency: 187.5 Hz ±2.1 Hz
├─ Q-Factor: 14.2 (±0.8 from baseline)
├─ Quality: Good
├─ SNR: 22.3 dB
├─ Dynamic TSI Threshold: 76% (adjusted from 80%)
├─ TSI Score: 83% ✓ SAFE FOR LOADING
├─ Confidence: 92%
└─ Processing Time: 4.2 ms
```

### Statistics Over Time

```
Frequency Trend: 185 → 190 → 193 → 195 Hz (healing)
Q-Factor Trend: 10 → 12 → 14 → 15 (improving resonance)
Quality Consistency: 95% (reliable measurements)
Average SNR: 24.6 ± 2.1 dB
Latest Threshold: 74% (adaptive, down from 80%)
```

## 🚀 Running Modes

| Mode            | Command                                     | Best For            |
| --------------- | ------------------------------------------- | ------------------- |
| **Demo**        | `python main_dynamic.py --mode demo`        | Quick validation    |
| **Interactive** | `python main_dynamic.py --mode interactive` | Exploration         |
| **Fracture**    | `python main_dynamic.py --mode fracture`    | Healing tracking    |
| **Monitoring**  | `python main_dynamic.py --mode monitoring`  | Real-time checks    |
| **All**         | `python main_dynamic.py --mode all`         | Complete validation |

## 📱 Integration Checklist

- [ ] Import `AdaptiveSignalProcessor` in dashboard
- [ ] Replace `SignalProcessor()` with `AdaptiveSignalProcessor()`
- [ ] Display `signal_quality` in UI
- [ ] Show `snr_db` in real-time display
- [ ] Display dynamic thresholds in clinical panel
- [ ] Add confidence indicator to results
- [ ] Log `processing_time_ms` for performance monitoring
- [ ] Test with real patient measurements
- [ ] Validate TSI threshold adaptation
- [ ] Document dynamic behavior in clinical protocol

## ⚡ Performance Tips

1. **Fastest Processing:** Use mode='demo' for benchmarking
2. **Best Quality:** Ensure SNR > 20 dB for GOOD quality
3. **For Noisy Environments:** System auto-scales filtering (no tuning needed)
4. **For Real-Time:** Processing is <15ms, allows 60+ Hz measurement rate
5. **For Healing Tracking:** Measure every 2-3 days (sufficient frequency resolution)

## 🔬 Technical Specs

```
Sampling Rate:    3200 Hz
Signal Duration:  1.0 second
Frequency Range:  0-1600 Hz (Nyquist)
FFT Resolution:   0.6 Hz (at 1024 points) → 2.4 Hz (at 256 points)
Dynamic Range:    60 dB (typical)
Latency:          <15 ms per measurement
Throughput:       60+ measurements/second possible
Quality Levels:   5 (EXCELLENT → INVALID)
Confidence Range: 0-100% (derived from SNR)
```

## 💡 Pro Tips

1. **For Best Results:** Ensure good contact pressure (affects SNR)
2. **Signal Quality Check:** If POOR, retry or improve contact
3. **Threshold Interpretation:** Higher threshold = more conservative diagnosis
4. **Trend Analysis:** Watch frequency trend over time (healing indicator)
5. **Confidence Scores:** Only >80% confidence for clinical decisions
6. **Q-Factor:** Increasing Q indicates improving tissue stiffness

## 🎓 Example Workflow

```
1. Place probe on patient tissue
   ↓
2. Start measurement (auto-quality check)
   ↓
3. System reads signal and reports:
   "Quality: Good, SNR: 22.5 dB, Confidence: 88%"
   ↓
4. If Quality < GOOD:
   "Please adjust contact pressure and retry"
   ↓
5. Processing completes:
   "TSI: 85% (threshold 76%) → SAFE FOR LOADING"
   ↓
6. Store result with quality metadata:
   {frequency: 187.5, q_factor: 14.2, tsi: 85, confidence: 88%}
```

---

**Version 2.0 - Full System Dynamics Enabled** ✅
Built for Unisys ResoScan Project | 2026
