# ResoScan v2.0 - Complete File Index & Navigation Guide

## 🚀 START HERE

### For Quick Start (5 minutes)

1. **Read:** `QUICK_REFERENCE.md` (2 min)
2. **Run:** `python main_dynamic.py --mode all` (3 min)
3. See dynamic processing in action!

### For Deep Understanding (30 minutes)

1. **Read:** `DYNAMIC_SYSTEM_GUIDE.md` (15 min)
2. **Scan:** `STATUS_REPORT.txt` (5 min)
3. **Review:** Code comments in `signal_processing/dynamic_processor.py` (10 min)

### For Implementation/Integration (1-2 hours)

1. **Study:** `DYNAMIC_SYSTEM_GUIDE.md` - Integration section
2. **Review:** `main_dynamic.py` - See integration patterns
3. **Code:** `signal_processing/dynamic_processor.py` - Understand API
4. **Implement:** In your dashboard or application

---

## 📁 FILE ORGANIZATION

```
ResoScan_Software/
│
├─ ENTRY POINTS (How to Run)
│  ├─ main_dynamic.py                      [350 lines] NEW!
│  │  └─ 4 modes: demo, interactive, fracture, monitoring
│  ├─ main.py                              (original static version)
│  │  └─ 3 modes: demo, gui, cli
│  │
├─ CORE DYNAMIC ENGINE
│  └─ signal_processing/
│     ├─ dynamic_processor.py              [600+ lines] NEW! CORE
│     │  ├─ AdaptiveSignalProcessor class
│     │  ├─ DynamicFeatures dataclass
│     │  ├─ SignalQuality enum (5 levels)
│     │  ├─ 8 adaptive processing methods
│     │  ├─ 2 dynamic clinical calculation methods
│     │  ├─ 1 comprehensive reporting method
│     │  └─ Demo function with 3 test scenarios
│     │
│     ├─ signal_processor.py               (original, for reference)
│     └─ data_acquisition.py               (hardware interface)
│
├─ MACHINE LEARNING
│  └─ ml_models/
│     └─ classifier.py                     (Random Forest & SVM)
│
├─ USER INTERFACE
│  └─ ui_dashboard/
│     └─ dashboard.py                      (PyQt5, ready to integrate)
│
├─ HARDWARE FIRMWARE
│  └─ embedded_firmware/
│     └─ resoscan_firmware.ino             (ESP32 code)
│
├─ CONFIGURATION
│  └─ config.json                          (Device & algorithm settings)
│
├─ TESTING
│  └─ tests/
│     └─ test_all.py                       (16+ unit tests)
│
└─ DOCUMENTATION (This Section)
   ├─ DYNAMIC_SYSTEM_GUIDE.md              [NEW] Technical deep dive
   ├─ QUICK_REFERENCE.md                   [NEW] Quick lookup card
   ├─ DEPLOYMENT_SUMMARY.md                [NEW] Executive summary
   ├─ STATUS_REPORT.txt                    [NEW] Complete status
   ├─ THIS FILE: FILE_INDEX.md             [NEW] Navigation guide
   ├─ README.md                            (Project overview)
   ├─ PROJECT_SUMMARY.md                   (Original requirements)
   ├─ START_HERE.md                        (Setup instructions)
   ├─ INSTALL.md                           (Installation guide)
   └─ INDEX.txt                            (Original file list)
```

---

## 📖 DOCUMENTATION GUIDE

### Quick Reference (2-5 min read)

**File:** `QUICK_REFERENCE.md`

- What's dynamic vs static
- Key adaptive formulas with math
- Real-time adjustment examples
- Configuration options
- Performance tips

**When to read:** For quick understanding

---

### System Guide (15-20 min read)

**File:** `DYNAMIC_SYSTEM_GUIDE.md`

- Complete system architecture
- All 6 adaptive processing steps explained
- DynamicFeatures output detailed
- Integration with existing components
- Performance metrics
- Validation results
- Clinical applications
- Next enhancement steps

**When to read:** For implementation/integration

---

### Status & Results (5-10 min read)

**File:** `STATUS_REPORT.txt`

- Executive summary
- What's dynamic (8 areas)
- System architecture diagram
- Test results (5 scenarios)
- Performance metrics
- How to use instructions
- Technical specifications
- Improvements summary

**When to read:** For project status overview

---

### Deployment Summary (10 min read)

**File:** `DEPLOYMENT_SUMMARY.md`

- What was done (phases 1-3)
- Demo results (actual test output)
- File summary
- Technical architecture
- How to use (4 modes)
- Learning outcomes
- Next steps

**When to read:** For stakeholder updates

---

### Original Documentation (Reference)

**Files:**

- `README.md` - Project overview
- `PROJECT_SUMMARY.md` - Original requirements
- `START_HERE.md` - Getting started
- `INSTALL.md` - Installation steps
- `INDEX.txt` - Original file listing

**When to read:** For context on what came before

---

## 💻 HOW TO RUN

### Option 1: Comprehensive Demo (Shows Everything)

```bash
cd d:\Study\Hackathons\unisys\ResoScan_Software
python main_dynamic.py --mode all
```

**Output:**

- 3 signal quality scenarios
- Fracture healing progression (Day 0-42)
- Real-time monitoring (20 measurements)
- All statistics and analysis

**Time:** ~2 seconds

---

### Option 2: Quick Demo (3 Scenarios)

```bash
python main_dynamic.py --mode demo
```

**Scenarios:**

1. High-quality clean signal (SNR 74 dB)
2. Noisy signal (SNR 3.4 dB)
3. Different resonance frequency

**Time:** <1 second

---

### Option 3: Interactive Analysis (Explore)

```bash
python main_dynamic.py --mode interactive
```

**Features:**

- 5 tissue type scenarios (healthy, injured, healing, etc.)
- Interactive command menu
- Comparative signal analysis
- Real-time parameter visualization

**Time:** User-controlled

---

### Option 4: Fracture Healing Simulation

```bash
python main_dynamic.py --mode fracture
```

**Simulates:**

- Baseline measurement (healthy bone)
- 5 time points (Day 0, 7, 14, 21, 42)
- Dynamic TSI tracking
- Clinical recommendations

**Time:** ~2 seconds

---

### Option 5: Real-Time Monitoring

```bash
python main_dynamic.py --mode monitoring
```

**Displays:**

- 20 consecutive measurements
- Real-time frequency/Q-factor/SNR tracking
- Quality indicators
- Statistics

**Time:** ~3 seconds (0.1s per measurement)

---

## 🔍 KEY FILES EXPLAINED

### 1. main_dynamic.py

**Purpose:** Entry point with 4 operation modes
**Lines:** 350+
**Key Functions:**

- `print_banner()` - Welcome message
- `run_interactive_demo()` - Interactive mode
- `run_advanced_fracture_monitoring()` - Healing progression
- `run_real_time_monitoring()` - Continuous monitoring
- `main()` - Argument parsing and mode selection

**When to use:** As entry point for all demonstrations

---

### 2. signal_processing/dynamic_processor.py

**Purpose:** CORE adaptive signal processing engine
**Lines:** 600+
**Key Classes:**

- `SignalQuality` (enum) - 5 quality levels
- `DynamicFeatures` (dataclass) - 20+ output parameters
- `AdaptiveSignalProcessor` (class) - Main processing engine

**Key Methods:**

- `process_signal_adaptive()` - 6-step pipeline
- `_assess_signal_quality()` - SNR → 5 levels
- `_adaptive_noise_filter()` - SNR-tuned filtering
- `_calculate_dynamic_fft_size()` - Window sizing
- `_select_optimal_window()` - Window type selection
- `_calculate_dynamic_prominence()` - Peak threshold
- `_calculate_stationarity()` - Signal consistency
- `_calculate_dynamic_thresholds()` - Clinical thresholds
- `calculate_dynamic_tsi()` - TSI with adaptation
- `get_signal_report()` - Comprehensive analysis

**When to use:** For all adaptive signal processing

---

### 3. DYNAMIC_SYSTEM_GUIDE.md

**Purpose:** Technical integration guide
**Sections:**

- System architecture overview
- 6 key dynamic features explained
- DynamicFeatures output specification
- Integration with existing components
- Performance metrics
- Validation results
- Clinical applications
- Enhancement suggestions

**When to read:** Before implementing integration

---

### 4. QUICK_REFERENCE.md

**Purpose:** Quick lookup reference card
**Sections:**

- Signal quality levels (5-level system)
- How adaptive processing works
- Example scenarios (healthy vs injured)
- Key adaptive formulas with math
- Real-time adjustment examples
- Configuration options
- Monitoring output format
- Technical specifications
- Pro tips
- Example workflow

**When to read:** For quick understanding or lookup

---

### 5. config.json

**Purpose:** Configuration parameters
**Current Settings:** Device, signal processing, clinical thresholds
**Ready For:** Dynamic processor configuration additions
**Next Steps:** Add dynamic processor settings (see DYNAMIC_SYSTEM_GUIDE.md)

---

## 🎯 COMMON TASKS

### Task 1: "Show me dynamic processing in action"

```bash
python main_dynamic.py --mode demo
```

→ Read output, compare with QUICK_REFERENCE.md

---

### Task 2: "Integrate dynamic processor into my code"

1. Read: `DYNAMIC_SYSTEM_GUIDE.md` - Integration section
2. Study: `main_dynamic.py` - See integration patterns
3. Code example:

```python
from signal_processing.dynamic_processor import AdaptiveSignalProcessor

processor = AdaptiveSignalProcessor()
features = processor.process_signal_adaptive(your_signal_data)
print(f"Quality: {features.signal_quality}")
print(f"Frequency: {features.resonant_frequency} Hz")
print(f"Confidence: {features.confidence:.1f}%")
```

---

### Task 3: "Understand what's adaptive"

1. Quick: Read `QUICK_REFERENCE.md` - First 2 sections (5 min)
2. Detailed: Read `DYNAMIC_SYSTEM_GUIDE.md` - Section 2 (10 min)
3. See it: Run `python main_dynamic.py --mode demo` (1 min)

---

### Task 4: "Deploy to production"

1. Read: `STATUS_REPORT.txt` - Specifications section
2. Study: `DYNAMIC_SYSTEM_GUIDE.md` - All sections
3. Review: Code in `dynamic_processor.py`
4. Test: Run all 4 modes to validate
5. Integrate: Follow integration patterns in main_dynamic.py

---

### Task 5: "Understand test results"

1. Read: `STATUS_REPORT.txt` - Test Results section
2. Run: `python main_dynamic.py --mode all`
3. Compare output with expected results in STATUS_REPORT.txt

---

## 📊 DOCUMENTATION COMPARISON

| Task           | Quick Ref  | System Guide | Status     | Deployment |
| -------------- | ---------- | ------------ | ---------- | ---------- |
| Quick Start    | ⭐⭐⭐⭐⭐ | ⭐⭐         | ⭐⭐⭐     | ⭐         |
| Integration    | ⭐⭐       | ⭐⭐⭐⭐⭐   | ⭐⭐       | ⭐⭐⭐     |
| Theory         | ⭐⭐⭐     | ⭐⭐⭐⭐⭐   | ⭐⭐       | ⭐⭐       |
| Formulas       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐       | ⭐         | ⭐         |
| Results        | ⭐⭐       | ⭐⭐         | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   |
| Implementation | ⭐⭐       | ⭐⭐⭐⭐⭐   | ⭐⭐       | ⭐⭐       |
| Examples       | ⭐⭐⭐⭐   | ⭐⭐⭐       | ⭐⭐       | ⭐⭐⭐     |

---

## 🚀 RECOMMENDED READING ORDER

### Path A: "Show Me It Works" (15 min)

1. `QUICK_REFERENCE.md` - What's dynamic (3 min)
2. `python main_dynamic.py --mode demo` - See it work (1 min)
3. `STATUS_REPORT.txt` - Results (5 min)
4. Compare output with test scenarios (5 min)

### Path B: "I Need to Integrate" (1-2 hours)

1. `DYNAMIC_SYSTEM_GUIDE.md` - Architecture (20 min)
2. `signal_processing/dynamic_processor.py` - Study code (30 min)
3. `main_dynamic.py` - Integration patterns (20 min)
4. `QUICK_REFERENCE.md` - Key concepts (10 min)
5. Plan integration in your code (30 min)

### Path C: "Complete Deep Dive" (3-4 hours)

1. All documentation files in order
2. Review all code in signal_processing/dynamic_processor.py
3. Run all 4 modes of main_dynamic.py
4. Study test scenarios in STATUS_REPORT.txt
5. Plan production deployment

---

## 🔗 CROSS-REFERENCES

| Document                | Links To                      |
| ----------------------- | ----------------------------- |
| QUICK_REFERENCE.md      | - Configuration (config.json) |
|                         | - Technical Specs             |
|                         | - Pro Tips                    |
| DYNAMIC_SYSTEM_GUIDE.md | - dynamic_processor.py        |
|                         | - data_acquisition.py         |
|                         | - classifier.py               |
|                         | - dashboard.py                |
| STATUS_REPORT.txt       | - Test Results                |
|                         | - File Index                  |
|                         | - Next Steps                  |
| main_dynamic.py         | - dynamic_processor.py        |
|                         | - All 4 demo modes            |

---

## ⚡ QUICK LINKS

### To Run Demo

```bash
python main_dynamic.py --mode all
```

### To View Quick Reference

```bash
notepad QUICK_REFERENCE.md
# or
cat QUICK_REFERENCE.md
```

### To Read System Guide

```bash
notepad DYNAMIC_SYSTEM_GUIDE.md
```

### To Check Status

```bash
cat STATUS_REPORT.txt
```

### To Study Core Code

```bash
notepad signal_processing/dynamic_processor.py
```

---

## 📝 FILE VERSION CONTROL

| File                    | Version | Date       | Status      |
| ----------------------- | ------- | ---------- | ----------- |
| main_dynamic.py         | 1.0     | 2026-04-26 | ✅ Complete |
| dynamic_processor.py    | 1.0     | 2026-04-26 | ✅ Complete |
| QUICK_REFERENCE.md      | 1.0     | 2026-04-26 | ✅ Complete |
| DYNAMIC_SYSTEM_GUIDE.md | 1.0     | 2026-04-26 | ✅ Complete |
| DEPLOYMENT_SUMMARY.md   | 1.0     | 2026-04-26 | ✅ Complete |
| STATUS_REPORT.txt       | 1.0     | 2026-04-26 | ✅ Complete |
| FILE_INDEX.md           | 1.0     | 2026-04-26 | ✅ Complete |

---

## 🎓 KEY CONCEPTS

**5 Signal Quality Levels**

- EXCELLENT: SNR > 30 dB
- GOOD: SNR > 20 dB
- ACCEPTABLE: SNR > 10 dB
- POOR: SNR > 0 dB
- INVALID: SNR ≤ 0 dB

**6-Step Adaptive Pipeline**

1. Signal Quality Assessment
2. Adaptive Noise Filtering
3. Dynamic FFT Sizing
4. Optimal Window Selection
5. Adaptive Peak Detection
6. Dynamic Threshold Computation

**20+ Dynamic Parameters**

- Signal quality, SNR, noise floor
- Stationarity, Q-factor, damping
- Spectral properties
- Dynamic thresholds
- Confidence scores

---

## ✨ WHAT'S NEW IN v2.0

- ✅ 600+ lines of adaptive signal processing
- ✅ 5-level signal quality assessment
- ✅ Dynamic FFT sizing (256-2048)
- ✅ SNR-tuned filtering and peak detection
- ✅ Stationarity analysis
- ✅ Adaptive clinical thresholds
- ✅ Confidence scoring
- ✅ Real-time parameter adjustment
- ✅ 4 demonstration modes
- ✅ Comprehensive documentation

---

## 🎯 PROJECT STATUS

**Phase 1: Requirements Analysis** ✅ Complete
**Phase 2: Platform Development** ✅ Complete
**Phase 3: Dynamic Enhancement** ✅ Complete
**Phase 4: Integration** 🔄 Next
**Phase 5: Clinical Validation** ⏳ Planned

---

**Last Updated:** 2026-04-26
**Version:** 2.0 - Dynamic Adaptive Platform
**Status:** Ready for Production
