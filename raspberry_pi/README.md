# Raspberry Pi Scripts - Coffee Bean Sorter

Python scripts for running the coffee bean sorting system on Raspberry Pi.

---

## Files in This Directory

### 1. `bean_sorter.py` ⭐ MAIN SYSTEM
Complete bean sorting system with camera detection and hardware control.

**Run**:
```bash
python3 bean_sorter.py /path/to/best_model.keras
```

**Options**:
```bash
--speed 60          # Conveyor speed (0-100, default: 50)
--confidence 0.8    # Detection threshold (0-1, default: 0.7)
```

**Controls**:
- `s` - Start/stop conveyor
- `q` - Quit

---

### 2. `test_camera.py` - Camera Testing
Test camera with model predictions in real-time.

**Run**:
```bash
python3 test_camera.py /path/to/best_model.keras
```

**Controls**:
- `c` - Capture and predict
- `s` - Save frame
- `q` - Quit

---

### 3. `test_hardware.py` - Hardware Testing
Test servo, motor, and LEDs independently.

**Run**:
```bash
python3 test_hardware.py all     # Test everything
python3 test_hardware.py servo   # Servo only
python3 test_hardware.py motor   # Motor only
python3 test_hardware.py led     # LEDs only
```

---

## Quick Setup

### 1. Install Dependencies
```bash
sudo apt install -y python3-pip python3-opencv python3-picamera2
pip3 install tensorflow RPi.GPIO numpy opencv-python
```

### 2. Enable Camera
```bash
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### 3. Test Hardware
```bash
python3 test_hardware.py all
```

### 4. Test Camera
```bash
python3 test_camera.py best_model.keras
```

### 5. Run Sorter
```bash
python3 bean_sorter.py best_model.keras
```

---

## GPIO Pins Used

| Component | GPIO | Pin | Function |
|-----------|------|-----|----------|
| Servo | 18 | 12 | Gate control |
| Motor RPWM | 23 | 16 | Forward |
| Motor LPWM | 24 | 18 | Backward |
| Motor R_EN | 25 | 22 | Enable |
| Motor L_EN | 8 | 24 | Enable |
| Green LED | 17 | 11 | Good indicator |
| Red LED | 27 | 13 | Bad indicator |

---

## System Logic

```
Camera → Model → Prediction → Wait → Servo Control
                                      ├─ GOOD: Gate CLOSED (to side)
                                      └─ BAD: Gate OPEN (straight)
```

---

## Documentation

- **Quick Start**: `../RASPBERRY_PI_QUICK_START.md`
- **Full Setup**: `../docs/RASPBERRY_PI_SETUP.md`
- **Wiring**: `../docs/WIRING_DIAGRAM.md`
- **Summary**: `../RASPBERRY_PI_FILES_SUMMARY.md`

---

## Troubleshooting

**Camera not working**:
```bash
libcamera-hello  # Test camera
sudo raspi-config  # Enable if needed
```

**GPIO errors**:
```bash
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"
```

**Test individual components**:
```bash
python3 test_hardware.py servo
python3 test_hardware.py motor
```

---

**Ready to Sort!** 🚀☕
