# Raspberry Pi Bean Sorter - Files Summary

Complete overview of all files created for your Raspberry Pi sorting system.

---

## 📂 File Structure

```
intelli-bean/
│
├── raspberry_pi/                    # Raspberry Pi Python scripts
│   ├── bean_sorter.py              # Main sorting system ⭐
│   ├── test_camera.py              # Camera + model testing
│   └── test_hardware.py            # Hardware component testing
│
├── docs/                            # Documentation
│   ├── RASPBERRY_PI_SETUP.md       # Complete setup guide
│   └── WIRING_DIAGRAM.md           # Visual wiring diagrams
│
├── models/                          # Trained models
│   └── best_model.keras            # Your trained model (89.33% val acc)
│
├── RASPBERRY_PI_QUICK_START.md     # Quick start guide
└── RASPBERRY_PI_FILES_SUMMARY.md   # This file
```

---

## 🎯 Main Files

### 1. `raspberry_pi/bean_sorter.py` ⭐
**Purpose**: Complete bean sorting system with live detection

**Features**:
- Real-time camera detection using trained model
- Servo motor control (gate sorting)
- BTS7960 motor driver control (conveyor belt)
- LED indicators (good/bad beans)
- Live statistics display
- Configurable parameters

**Usage**:
```bash
python3 bean_sorter.py best_model.keras
python3 bean_sorter.py best_model.keras --speed 60 --confidence 0.8
```

**Controls**:
- `s` - Start/stop conveyor
- `q` - Quit and show statistics

**Key Settings**:
```python
SERVO_CLOSED = 2.5          # Gate closed (good beans to side)
SERVO_OPEN = 12.5           # Gate open (bad beans straight)
DETECTION_CONFIDENCE = 0.7  # Minimum confidence threshold
DETECTION_DELAY = 1.5       # Seconds between detections
SERVO_ACTIVATION_DELAY = 0.8  # Bean travel time to gate
CONVEYOR_SPEED = 50         # PWM duty cycle (0-100)
```

---

### 2. `raspberry_pi/test_camera.py`
**Purpose**: Test camera with model predictions

**Features**:
- Live camera feed
- Real-time model predictions
- Confidence scores
- Frame capture and save

**Usage**:
```bash
python3 test_camera.py best_model.keras
```

**Controls**:
- `c` - Capture and show prediction
- `s` - Save current frame
- `q` - Quit

**Output Example**:
```
[Frame 42] Captured!
  Prediction: GOOD
  Confidence: 89.32%
  Raw scores: Bad=0.1068, Good=0.8932
```

---

### 3. `raspberry_pi/test_hardware.py`
**Purpose**: Test individual hardware components

**Features**:
- Servo motor testing (0°, 90°, 180°)
- Motor driver testing (forward/backward)
- LED indicator testing
- Complete system test

**Usage**:
```bash
python3 test_hardware.py all     # Test everything
python3 test_hardware.py servo   # Test servo only
python3 test_hardware.py motor   # Test motor only
python3 test_hardware.py led     # Test LEDs only
```

**What It Tests**:
- Servo: Moves through all positions
- Motor: Forward at 30%, 50%, 70%, then backward
- LEDs: Blinks green, red, then both

---

## 📖 Documentation Files

### 4. `docs/RASPBERRY_PI_SETUP.md`
**Purpose**: Complete setup and configuration guide

**Contents**:
- Hardware requirements list
- Detailed wiring instructions
- Software installation steps
- Testing procedures
- Troubleshooting guide
- Performance optimization
- Auto-start configuration
- Safety notes
- Maintenance schedule

**Sections**:
1. Hardware Requirements
2. Wiring Diagram
3. Pin Layout Reference
4. Software Installation
5. Hardware Testing
6. Camera + Model Testing
7. Running the Sorting System
8. System Logic
9. Troubleshooting
10. Performance Optimization
11. Auto-Start on Boot
12. Safety Notes
13. Maintenance

---

### 5. `docs/WIRING_DIAGRAM.md`
**Purpose**: Visual wiring diagrams and connection tables

**Contents**:
- ASCII art wiring diagrams
- Complete system layout
- Connection summary table
- Physical layout suggestions
- Safety checklist
- Testing order

**Diagrams Include**:
- Raspberry Pi pinout
- Servo motor connections
- BTS7960 motor driver connections
- LED indicator connections
- Camera module connection
- Power supply layout
- Complete system overview

---

### 6. `RASPBERRY_PI_QUICK_START.md`
**Purpose**: Fast setup guide for quick deployment

**Contents**:
- Quick wiring guide
- Essential software setup
- Testing checklist
- Running instructions
- Common adjustments
- Troubleshooting tips

**Perfect For**:
- First-time setup
- Quick reference
- Demonstration setup
- Teaching others

---

## 🔌 GPIO Pin Assignments

| Component | GPIO Pin | Physical Pin | Function |
|-----------|----------|--------------|----------|
| Servo Signal | GPIO 18 | Pin 12 | PWM control |
| Motor RPWM | GPIO 23 | Pin 16 | Forward PWM |
| Motor LPWM | GPIO 24 | Pin 18 | Backward PWM |
| Motor R_EN | GPIO 25 | Pin 22 | Right enable |
| Motor L_EN | GPIO 8 | Pin 24 | Left enable |
| Green LED | GPIO 17 | Pin 11 | Good indicator |
| Red LED | GPIO 27 | Pin 13 | Bad indicator |

---

## ⚙️ System Logic Flow

```
1. Camera captures frame (640x480)
   ↓
2. Resize to 224x224 for model
   ↓
3. Model predicts: GOOD or BAD
   ↓
4. Check confidence > threshold (0.7)
   ↓
5. Wait for bean travel time (0.8s)
   ↓
6. Control servo:
   - GOOD: Close gate (0°) → Bean to SIDE
   - BAD: Open gate (180°) → Bean STRAIGHT
   ↓
7. Blink LED indicator
   ↓
8. Return servo to neutral (90°)
   ↓
9. Update statistics
   ↓
10. Repeat
```

---

## 🎛️ Configurable Parameters

### In `bean_sorter.py`:

**GPIO Pins**:
```python
SERVO_PIN = 18
MOTOR_RPWM = 23
MOTOR_LPWM = 24
MOTOR_R_EN = 25
MOTOR_L_EN = 8
LED_GOOD = 17
LED_BAD = 27
```

**Servo Positions**:
```python
SERVO_CLOSED = 2.5   # 0° - Good beans to side
SERVO_OPEN = 12.5    # 180° - Bad beans straight
SERVO_NEUTRAL = 7.5  # 90° - Waiting position
```

**Detection Settings**:
```python
DETECTION_CONFIDENCE = 0.7  # Minimum confidence (0-1)
DETECTION_DELAY = 1.5       # Seconds between detections
SERVO_ACTIVATION_DELAY = 0.8  # Bean travel time
```

**Motor Settings**:
```python
CONVEYOR_SPEED = 50  # PWM duty cycle (0-100)
```

---

## 📊 Model Performance

Your trained model (`best_model.keras`):

| Metric | Value |
|--------|-------|
| Validation Accuracy | 89.33% |
| Test Accuracy | 85.47% |
| Good Bean Detection | 76.54% |
| Bad Bean Detection | 94.41% |

**Confusion Matrix**:
```
              Predicted
              Bad    Good
Actual Bad    169     10
       Good    42    137
```

**Interpretation**:
- Excellent at detecting bad beans (94.41%)
- Good at detecting good beans (76.54%)
- 42 good beans misclassified as bad (conservative sorting)
- Only 10 bad beans missed (safe for quality)

---

## 🚀 Quick Start Checklist

- [ ] 1. Wire all components (see `WIRING_DIAGRAM.md`)
- [ ] 2. Install software dependencies
- [ ] 3. Enable camera in raspi-config
- [ ] 4. Transfer model and scripts to Pi
- [ ] 5. Test camera: `python3 test_camera.py best_model.keras`
- [ ] 6. Test servo: `python3 test_hardware.py servo`
- [ ] 7. Test motor: `python3 test_hardware.py motor`
- [ ] 8. Test LEDs: `python3 test_hardware.py led`
- [ ] 9. Run sorter: `python3 bean_sorter.py best_model.keras`
- [ ] 10. Calibrate timing and positions

---

## 🔧 Common Adjustments

### Servo Not Reaching Positions
Edit in `bean_sorter.py`:
```python
SERVO_CLOSED = 2.0  # Try 2.0-3.0 for 0°
SERVO_OPEN = 13.0   # Try 12.0-13.0 for 180°
```

### Bean Misses Gate
Edit in `bean_sorter.py`:
```python
SERVO_ACTIVATION_DELAY = 1.0  # Increase if bean too slow
SERVO_ACTIVATION_DELAY = 0.6  # Decrease if bean too fast
```

### Too Many False Detections
```bash
# Increase confidence threshold
python3 bean_sorter.py best_model.keras --confidence 0.8
```

### Conveyor Too Fast/Slow
```bash
# Adjust speed (0-100)
python3 bean_sorter.py best_model.keras --speed 40
```

---

## 📦 Files to Transfer to Raspberry Pi

**Required**:
1. `raspberry_pi/bean_sorter.py`
2. `raspberry_pi/test_camera.py`
3. `raspberry_pi/test_hardware.py`
4. `models/best_model.keras`

**Optional (for reference)**:
5. `docs/RASPBERRY_PI_SETUP.md`
6. `docs/WIRING_DIAGRAM.md`
7. `RASPBERRY_PI_QUICK_START.md`

**Transfer Command** (from Windows):
```bash
scp models/best_model.keras pi@raspberrypi.local:~/bean_sorter/
scp raspberry_pi/*.py pi@raspberrypi.local:~/bean_sorter/
```

---

## 🎓 Learning Resources

**Understanding the Code**:
- `bean_sorter.py` - Main system with comments
- `test_camera.py` - Simple camera + model example
- `test_hardware.py` - GPIO control examples

**Hardware Guides**:
- `RASPBERRY_PI_SETUP.md` - Complete hardware setup
- `WIRING_DIAGRAM.md` - Visual connection guide

**Quick Reference**:
- `RASPBERRY_PI_QUICK_START.md` - Fast setup guide

---

## 🆘 Troubleshooting Quick Reference

| Problem | Solution | File Reference |
|---------|----------|----------------|
| Camera not working | Enable in raspi-config | RASPBERRY_PI_SETUP.md |
| Servo jitters | Check 5V power | RASPBERRY_PI_SETUP.md |
| Motor doesn't run | Check 12V power, enable pins | test_hardware.py |
| Low accuracy | Adjust confidence, lighting | bean_sorter.py |
| GPIO errors | Run GPIO.cleanup() | test_hardware.py |
| Wrong servo positions | Adjust duty cycle values | bean_sorter.py |
| Bean timing off | Adjust SERVO_ACTIVATION_DELAY | bean_sorter.py |

---

## 📞 Support

For detailed help, see:
1. `RASPBERRY_PI_QUICK_START.md` - Quick fixes
2. `docs/RASPBERRY_PI_SETUP.md` - Detailed troubleshooting
3. `docs/WIRING_DIAGRAM.md` - Connection verification

---

**All Files Ready!** Your complete Raspberry Pi bean sorting system is documented and ready to deploy. 🚀☕
