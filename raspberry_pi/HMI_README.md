# Touchscreen HMI - Coffee Bean Sorter

Farmer-friendly touchscreen interface for the coffee bean sorting system.

---

## 🎯 Two Versions Available

### 1. Full Version (Raspberry Pi)
**File**: `bean_sorter_hmi.py`

**Features**:
- Real hardware control (servo, motor, camera)
- Live bean detection with AI model
- Touchscreen interface
- Automatic sorting

**Run**:
```bash
python3 bean_sorter_hmi.py best_model.keras
```

### 2. Demo Version (PC Testing)
**File**: `bean_sorter_hmi_demo.py`

**Features**:
- No hardware required
- Simulated bean detection
- Test interface on PC
- All UI features working

**Run**:
```bash
# Windows
py -3.12 bean_sorter_hmi_demo.py

# Linux/Mac
python3 bean_sorter_hmi_demo.py
```

---

## 🖥️ Interface Overview

```
┌─────────────────────────────────────────┐
│     ☕ COFFEE BEAN SORTER ☕            │
│                                         │
│        ● READY TO START                 │
│                                         │
│  ┌──────────┐      ┌──────────┐       │
│  │  GOOD    │      │   BAD    │       │
│  │  BEANS   │      │  BEANS   │       │
│  │    42    │      │    18    │       │
│  └──────────┘      └──────────┘       │
│                                         │
│      ┌──────────────────┐              │
│      │ TOTAL BEANS      │              │
│      │ SORTED           │              │
│      │      60          │              │
│      └──────────────────┘              │
│                                         │
│  [▶ START]    [■ STOP & SUMMARY]       │
└─────────────────────────────────────────┘
```

---

## 🎮 How to Use

### Simple 3-Step Process

**1. START**
- Tap "▶ START SORTING"
- Conveyor starts automatically
- Counters update in real-time

**2. MONITOR**
- Watch counters increase
- Green = Good beans
- Red = Bad beans
- Blue = Total

**3. STOP**
- Tap "■ STOP & SUMMARY"
- View results
- Tap "NEW SESSION" to reset

---

## 📊 Features

### Real-Time Counters
- **GOOD BEANS** (Green) - Quality beans count
- **BAD BEANS** (Red) - Defective beans count
- **TOTAL BEANS** (Blue) - Total processed

### Status Indicators
- **● READY TO START** (Orange) - System ready
- **● SORTING IN PROGRESS** (Green) - Active sorting
- **● PROCESS COMPLETED** (Orange) - Session ended

### Summary Window
Shows after stopping:
- Good beans count and percentage
- Bad beans count and percentage
- Total beans sorted
- Session duration
- Options: NEW SESSION or CLOSE

### Automatic Features
- ✅ Conveyor starts/stops automatically
- ✅ Counters update in real-time
- ✅ Summary appears automatically
- ✅ Counters reset on new session

---

## 🔧 Installation

### On Raspberry Pi
```bash
# Install dependencies
sudo apt install -y python3-tk
pip3 install tensorflow RPi.GPIO numpy opencv-python

# Run HMI
python3 bean_sorter_hmi.py best_model.keras
```

### On PC (Demo)
```bash
# No special installation needed
# Just run the demo
python3 bean_sorter_hmi_demo.py
```

---

## ⚙️ Configuration

### Adjust Detection Speed
```python
DETECTION_DELAY = 1.5  # Seconds between detections
```

### Adjust Conveyor Speed
```python
CONVEYOR_SPEED = 50  # PWM duty cycle (0-100)
```

### Change Button Sizes
```python
self.button_font = tkfont.Font(family='Arial', size=28, weight='bold')
```

---

## 🎓 Farmer Training

### 5-Minute Training
1. Show the three counters
2. Tap START button
3. Watch counters increase
4. Tap STOP button
5. View summary
6. Tap NEW SESSION

**That's it!** No technical knowledge needed.

---

## 🐛 Troubleshooting

### Touchscreen Not Responding
```bash
sudo apt install -y xinput-calibrator
xinput_calibrator
```

### Buttons Too Small
Edit font sizes in the script

### Can't Exit
Press `Alt+F4` or tap small Exit button (bottom right)

---

## 📚 Documentation

- **Full Guide**: `docs/TOUCHSCREEN_HMI_GUIDE.md`
- **Setup Guide**: `docs/RASPBERRY_PI_SETUP.md`
- **Wiring**: `docs/WIRING_DIAGRAM.md`

---

## 🎯 Comparison: HMI vs Command Line

| Feature | HMI Version | Command Line Version |
|---------|-------------|---------------------|
| Interface | Touchscreen | Keyboard |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Counters | Large, visible | Terminal text |
| Summary | Automatic popup | Manual check |
| Reset | One button | Manual |
| Farmer-Friendly | Yes | No |
| Technical Skills | None | Basic |

---

## 💡 When to Use Each Version

### Use HMI Version When:
- ✅ Farmers will operate the system
- ✅ Touchscreen is available
- ✅ Easy operation is priority
- ✅ Visual feedback is important
- ✅ No technical training available

### Use Command Line Version When:
- ✅ Technical operator
- ✅ Remote SSH access
- ✅ Debugging needed
- ✅ No display available
- ✅ Headless operation

---

## 🚀 Quick Start

### Test on PC First
```bash
# Run demo to see interface
python3 bean_sorter_hmi_demo.py

# Test all features:
# 1. Click START
# 2. Watch counters increase
# 3. Click STOP
# 4. View summary
# 5. Click NEW SESSION
```

### Deploy to Raspberry Pi
```bash
# Transfer files
scp bean_sorter_hmi.py pi@raspberrypi.local:~/bean_sorter/
scp best_model.keras pi@raspberrypi.local:~/bean_sorter/

# Run on Pi
ssh pi@raspberrypi.local
cd ~/bean_sorter
python3 bean_sorter_hmi.py best_model.keras
```

---

**Ready to Use!** The touchscreen HMI makes coffee bean sorting accessible to everyone. ☕🚀
