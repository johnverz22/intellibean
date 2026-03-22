# Coffee Bean Sorter - Quick Start Guide

Get your Raspberry Pi bean sorting system running in minutes!

---

## 📦 What You Need

### Hardware
- Raspberry Pi 4 (4GB RAM)
- Pi Camera Module V2/V3
- Servo Motor (SG90 or MG996R)
- BTS7960 Motor Driver
- DC Motor (12V)
- Power supplies (5V 3A + 12V 5A)
- Jumper wires

### Software
- Raspberry Pi OS (Bullseye or later)
- Python 3.9+
- Your trained model: `best_model.keras`

---

## 🔌 Quick Wiring

### Servo Motor (Gate)
```
Servo          Raspberry Pi
-----          ------------
VCC (Red)   →  5V (Pin 2)
GND (Brown) →  GND (Pin 6)
Signal      →  GPIO 18 (Pin 12)
```

### BTS7960 Motor Driver (Conveyor)
```
BTS7960        Raspberry Pi
-------        ------------
VCC (Logic) →  5V (Pin 2)
GND (Logic) →  GND (Pin 14)
RPWM        →  GPIO 23 (Pin 16)
LPWM        →  GPIO 24 (Pin 18)
R_EN        →  GPIO 25 (Pin 22)
L_EN        →  GPIO 8 (Pin 24)

Motor Power →  12V External Supply
B+/B-       →  DC Motor
```

**⚠️ IMPORTANT**: Use separate power supplies for Pi (5V) and motor (12V)!

See `docs/WIRING_DIAGRAM.md` for detailed diagrams.

---

## 💻 Software Setup

### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3-pip python3-opencv python3-picamera2

# Install Python libraries
pip3 install tensorflow RPi.GPIO numpy opencv-python
```

### 2. Enable Camera
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
sudo reboot
```

### 3. Transfer Files
Copy these files to your Raspberry Pi:
```
~/bean_sorter/
├── best_model.keras          # Your trained model
├── bean_sorter.py            # Main sorting system
├── test_camera.py            # Camera test
└── test_hardware.py          # Hardware test
```

---

## 🧪 Testing (Do This First!)

### Test 1: Camera
```bash
cd ~/bean_sorter
python3 test_camera.py best_model.keras
```
- Press `c` to capture and predict
- Press `q` to quit

### Test 2: Servo
```bash
python3 test_hardware.py servo
```
Watch servo move: 0° → 90° → 180° → 90°

### Test 3: Motor
```bash
python3 test_hardware.py motor
```
Motor should run forward, then backward

### Test 4: All Hardware
```bash
python3 test_hardware.py all
```

---

## 🚀 Run the Sorter

### Start Sorting
```bash
python3 bean_sorter.py best_model.keras
```

### Controls
- Press `s` to START/STOP conveyor
- Press `q` to QUIT

### What Happens
1. Camera detects bean
2. Model predicts quality
3. After 0.8 seconds (bean travel time):
   - **GOOD bean**: Gate CLOSES → Bean goes to SIDE
   - **BAD bean**: Gate OPENS → Bean goes STRAIGHT
4. Statistics shown on screen

---

## ⚙️ Adjusting Settings

### Change Conveyor Speed
```bash
python3 bean_sorter.py best_model.keras --speed 60
# Speed: 0-100 (default: 50)
```

### Change Detection Confidence
```bash
python3 bean_sorter.py best_model.keras --confidence 0.8
# Confidence: 0-1 (default: 0.7)
```

### Edit Timing in Code
Open `bean_sorter.py` and adjust:
```python
DETECTION_DELAY = 1.5       # Time between detections
SERVO_ACTIVATION_DELAY = 0.8  # Bean travel time to gate
```

---

## 🎯 Servo Position Logic

```
Position    Angle    Gate State    Bean Path
--------    -----    ----------    ---------
CLOSED      0°       Blocked       → SIDE (Good beans)
NEUTRAL     90°      Waiting       -
OPEN        180°     Open          → STRAIGHT (Bad beans)
```

To adjust positions, edit in `bean_sorter.py`:
```python
SERVO_CLOSED = 2.5   # 0° - Try 2.0 to 3.0
SERVO_OPEN = 12.5    # 180° - Try 12.0 to 13.0
```

---

## 📊 Understanding Output

### On Screen Display
```
┌─────────────────────────────┐
│ GOOD BEAN (89.3%)           │  ← Current detection
│                             │
│ [Detection Zone]            │  ← Yellow box
│                             │
│ Good: 45                    │  ← Statistics
│ Bad: 12                     │
│ Total: 57                   │
└─────────────────────────────┘
```

### Console Output
```
→ GOOD BEAN: Gate CLOSED (to side)
→ BAD BEAN: Gate OPEN (straight)
```

---

## 🔧 Troubleshooting

### Camera Not Working
```bash
# Test camera
libcamera-hello

# If fails, enable camera:
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Servo Jitters
- Check 5V power supply (needs stable voltage)
- Verify GPIO 18 connection
- Try external 5V power for servo

### Motor Doesn't Run
- Check 12V power supply
- Verify enable pins (R_EN, L_EN)
- Test with: `python3 test_hardware.py motor`

### Low Detection Accuracy
- Improve lighting
- Adjust confidence: `--confidence 0.6`
- Clean camera lens

### GPIO Errors
```bash
# Clean up GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"
```

---

## 📁 File Structure

```
~/bean_sorter/
├── best_model.keras          # Trained model (89.33% accuracy)
├── bean_sorter.py            # Main sorting system
├── test_camera.py            # Test camera + model
├── test_hardware.py          # Test servo + motor
└── docs/
    ├── RASPBERRY_PI_SETUP.md # Detailed setup guide
    └── WIRING_DIAGRAM.md     # Visual wiring guide
```

---

## 🎓 Next Steps

1. ✅ Complete hardware testing
2. ✅ Run camera test with model
3. ✅ Calibrate servo positions
4. ✅ Adjust bean travel timing
5. ✅ Test with real beans
6. ✅ Fine-tune detection confidence
7. ✅ Optimize conveyor speed

---

## 📚 Full Documentation

- **Detailed Setup**: `docs/RASPBERRY_PI_SETUP.md`
- **Wiring Diagrams**: `docs/WIRING_DIAGRAM.md`
- **Training Guide**: `TRAINING_QUICK_START.md`

---

## 🆘 Need Help?

1. Check troubleshooting section above
2. Review `docs/RASPBERRY_PI_SETUP.md`
3. Test components individually
4. Verify all connections

---

**Ready to Sort!** Your coffee bean sorting system is operational. ☕🚀

**Statistics from your model:**
- Validation Accuracy: 89.33%
- Test Accuracy: 85.47%
- Good Bean Detection: 76.54%
- Bad Bean Detection: 94.41%
