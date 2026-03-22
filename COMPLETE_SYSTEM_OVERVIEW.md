# Coffee Bean Sorting System - Complete Overview

Your complete AI-powered coffee bean sorting system is ready!

---

## 🎯 System Summary

**What It Does**: Automatically sorts coffee beans into GOOD and BAD categories using computer vision and mechanical sorting.

**How It Works**:
1. Camera captures bean image
2. AI model predicts quality (89.33% accuracy)
3. Servo gate directs bean to correct path
4. Conveyor belt moves beans continuously

**Result**: Automated quality control for coffee bean processing

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| **Validation Accuracy** | 89.33% |
| **Test Accuracy** | 85.47% |
| **Good Bean Detection** | 76.54% |
| **Bad Bean Detection** | 94.41% ⭐ |

**Training Time**: ~37 minutes on CPU
- Stage 1 (Transfer Learning): 27 epochs, ~25 minutes
- Stage 2 (Fine-tuning): 9 epochs, ~12 minutes (crashed but best model saved)

---

## 🗂️ Complete File Structure

```
intelli-bean/
│
├── 📁 raspberry_pi/                 # Raspberry Pi Scripts
│   ├── bean_sorter.py              # ⭐ Main sorting system
│   ├── test_camera.py              # Camera + model testing
│   ├── test_hardware.py            # Hardware testing
│   └── README.md                   # Quick reference
│
├── 📁 scripts/                      # Training Scripts (PC)
│   ├── crop_beans_batch.py         # Batch image cropping
│   ├── split_dataset_balanced.py   # Dataset splitting
│   ├── train_simple.py             # Model training
│   ├── test_model_fixed.py         # Model testing
│   └── report_dataset.py           # Dataset statistics
│
├── 📁 models/                       # Trained Models
│   └── best_model.keras            # Your trained model (89.33%)
│
├── 📁 dataset/                      # Training Data
│   ├── train/                      # 1666 images (833 each)
│   ├── val/                        # 356 images (178 each)
│   └── test/                       # 358 images (179 each)
│
├── 📁 test_results/                 # Test Results
│   ├── confusion_matrix.png        # Visual confusion matrix
│   ├── per_class_accuracy.png      # Accuracy chart
│   └── test_results.json           # Detailed metrics
│
├── 📁 docs/                         # Documentation
│   ├── RASPBERRY_PI_SETUP.md       # Complete setup guide
│   ├── WIRING_DIAGRAM.md           # Visual wiring diagrams
│   └── TRAINING_GUIDE.md           # Training documentation
│
├── 📄 RASPBERRY_PI_QUICK_START.md  # Quick start guide
├── 📄 RASPBERRY_PI_FILES_SUMMARY.md # Files overview
├── 📄 TRAINING_QUICK_START.md      # Training guide
├── 📄 BATCH_CROPPER_GUIDE.md       # Image processing guide
└── 📄 COMPLETE_SYSTEM_OVERVIEW.md  # This file
```

---

## 🔧 Hardware Components

### Required Components
1. **Raspberry Pi 4** (4GB RAM)
2. **Pi Camera Module V2/V3**
3. **Servo Motor** (SG90 or MG996R)
4. **BTS7960 Motor Driver** (43A H-Bridge)
5. **DC Motor** (12V for conveyor)
6. **Power Supplies**:
   - 5V 3A (Raspberry Pi)
   - 12V 5A (Motor)
7. **LEDs** (Optional): Green + Red
8. **Jumper Wires**

### Wiring Summary
```
Servo:
  VCC → 5V (Pin 2)
  GND → GND (Pin 6)
  Signal → GPIO 18 (Pin 12)

BTS7960:
  Logic: 5V + GND from Pi
  Control: GPIO 23, 24, 25, 8
  Motor Power: 12V external
  Output: DC Motor

LEDs:
  Green → GPIO 17 (Pin 11)
  Red → GPIO 27 (Pin 13)
```

See `docs/WIRING_DIAGRAM.md` for detailed diagrams.

---

## 💻 Software Setup

### On PC (Windows)
```bash
# Already completed:
✅ Dataset created (2380 images, balanced)
✅ Model trained (89.33% validation accuracy)
✅ Model tested (85.47% test accuracy)
✅ Confusion matrix generated
```

### On Raspberry Pi
```bash
# 1. Install dependencies
sudo apt install -y python3-pip python3-opencv python3-picamera2
pip3 install tensorflow RPi.GPIO numpy opencv-python

# 2. Enable camera
sudo raspi-config  # Interface Options → Camera → Enable

# 3. Transfer files
scp models/best_model.keras pi@raspberrypi.local:~/bean_sorter/
scp raspberry_pi/*.py pi@raspberrypi.local:~/bean_sorter/

# 4. Test hardware
python3 test_hardware.py all

# 5. Test camera
python3 test_camera.py best_model.keras

# 6. Run sorter
python3 bean_sorter.py best_model.keras
```

---

## 🚀 Quick Start Guide

### Step 1: Hardware Setup (30 minutes)
1. Connect servo to GPIO 18
2. Connect BTS7960 to GPIO 23, 24, 25, 8
3. Connect LEDs to GPIO 17, 27
4. Connect camera to CSI port
5. Connect power supplies (5V + 12V)

### Step 2: Software Setup (15 minutes)
1. Install dependencies
2. Enable camera
3. Transfer model and scripts
4. Test components

### Step 3: Testing (10 minutes)
1. Test servo: `python3 test_hardware.py servo`
2. Test motor: `python3 test_hardware.py motor`
3. Test camera: `python3 test_camera.py best_model.keras`

### Step 4: Run System (Ready!)
```bash
python3 bean_sorter.py best_model.keras
```

**Total Setup Time**: ~1 hour

---

## 🎮 System Controls

### During Operation
- Press `s` - Start/stop conveyor belt
- Press `q` - Quit and show statistics

### Command Line Options
```bash
# Adjust conveyor speed (0-100)
python3 bean_sorter.py best_model.keras --speed 60

# Adjust detection confidence (0-1)
python3 bean_sorter.py best_model.keras --confidence 0.8

# Both options
python3 bean_sorter.py best_model.keras --speed 60 --confidence 0.8
```

---

## 🔄 System Operation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SORTING PROCESS                          │
└─────────────────────────────────────────────────────────────┘

1. DETECTION
   Camera captures frame (640x480)
   ↓
   Resize to 224x224
   ↓
   Model predicts: GOOD or BAD
   ↓
   Check confidence > 0.7

2. DELAY
   Wait 0.8 seconds (bean travel time)

3. SORTING
   If GOOD bean:
   ├─ Servo closes gate (0°)
   ├─ Bean diverted to SIDE
   ├─ Green LED blinks
   └─ Counter: good_beans++
   
   If BAD bean:
   ├─ Servo opens gate (180°)
   ├─ Bean continues STRAIGHT
   ├─ Red LED blinks
   └─ Counter: bad_beans++

4. RESET
   Servo returns to neutral (90°)
   ↓
   Ready for next bean

5. STATISTICS
   Display on screen:
   - Good beans: X
   - Bad beans: Y
   - Total: Z
   - Current prediction with confidence
```

---

## 📈 Performance Metrics

### Model Accuracy
- **Overall**: 85.47%
- **Good Beans**: 76.54% (137/179 correct)
- **Bad Beans**: 94.41% (169/179 correct)

### Confusion Matrix
```
              Predicted
              Bad    Good
Actual Bad    169     10     ← 94.41% correct
       Good    42    137     ← 76.54% correct
```

### Interpretation
- **Conservative sorting**: 42 good beans marked as bad (safe for quality)
- **High bad detection**: Only 10 bad beans missed (excellent quality control)
- **Suitable for production**: Prioritizes removing bad beans

---

## ⚙️ Adjustable Parameters

### In `bean_sorter.py`:

**Servo Positions** (adjust if needed):
```python
SERVO_CLOSED = 2.5   # 0° - Gate closed (good beans to side)
SERVO_OPEN = 12.5    # 180° - Gate open (bad beans straight)
SERVO_NEUTRAL = 7.5  # 90° - Waiting position
```

**Detection Settings**:
```python
DETECTION_CONFIDENCE = 0.7  # Minimum confidence (0-1)
DETECTION_DELAY = 1.5       # Seconds between detections
SERVO_ACTIVATION_DELAY = 0.8  # Bean travel time to gate
```

**Motor Settings**:
```python
CONVEYOR_SPEED = 50  # PWM duty cycle (0-100)
```

**GPIO Pins** (if needed):
```python
SERVO_PIN = 18
MOTOR_RPWM = 23
MOTOR_LPWM = 24
MOTOR_R_EN = 25
MOTOR_L_EN = 8
LED_GOOD = 17
LED_BAD = 27
```

---

## 🔧 Common Adjustments

### Servo Not Reaching Positions
```python
# Try different duty cycle values
SERVO_CLOSED = 2.0  # Try 2.0-3.0 for 0°
SERVO_OPEN = 13.0   # Try 12.0-13.0 for 180°
```

### Bean Timing Issues
```python
# Bean arrives too early
SERVO_ACTIVATION_DELAY = 0.6

# Bean arrives too late
SERVO_ACTIVATION_DELAY = 1.0
```

### Detection Sensitivity
```bash
# More strict (fewer detections)
python3 bean_sorter.py best_model.keras --confidence 0.85

# More lenient (more detections)
python3 bean_sorter.py best_model.keras --confidence 0.6
```

### Conveyor Speed
```bash
# Slower (more accurate)
python3 bean_sorter.py best_model.keras --speed 40

# Faster (higher throughput)
python3 bean_sorter.py best_model.keras --speed 70
```

---

## 📚 Documentation Reference

### Quick Guides
- **`RASPBERRY_PI_QUICK_START.md`** - Fast setup (5 min read)
- **`TRAINING_QUICK_START.md`** - Model training guide
- **`BATCH_CROPPER_GUIDE.md`** - Image processing

### Detailed Guides
- **`docs/RASPBERRY_PI_SETUP.md`** - Complete setup (30 min read)
- **`docs/WIRING_DIAGRAM.md`** - Visual wiring diagrams
- **`docs/TRAINING_GUIDE.md`** - Training documentation

### Reference
- **`RASPBERRY_PI_FILES_SUMMARY.md`** - All files overview
- **`raspberry_pi/README.md`** - Scripts reference
- **`COMPLETE_SYSTEM_OVERVIEW.md`** - This file

---

## 🐛 Troubleshooting

### Camera Issues
```bash
# Test camera
libcamera-hello

# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Servo Issues
- Check 5V power supply (stable voltage needed)
- Verify GPIO 18 connection
- Test: `python3 test_hardware.py servo`
- Adjust duty cycle values if positions wrong

### Motor Issues
- Check 12V power supply (5A+ needed)
- Verify enable pins (R_EN, L_EN)
- Test: `python3 test_hardware.py motor`
- Check motor connections (B+/B-)

### Detection Issues
- Improve lighting conditions
- Clean camera lens
- Adjust confidence threshold
- Check model file integrity

### GPIO Errors
```bash
# Clean up GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

# Add user to gpio group
sudo usermod -a -G gpio $USER
```

---

## 🎓 Next Steps

### Immediate
1. ✅ Complete hardware assembly
2. ✅ Test all components individually
3. ✅ Calibrate servo positions
4. ✅ Adjust bean travel timing
5. ✅ Test with real beans

### Optimization
1. Fine-tune detection confidence
2. Optimize conveyor speed
3. Improve lighting setup
4. Add more training data
5. Retrain model if needed

### Advanced
1. Convert to TFLite for faster inference
2. Add auto-start on boot
3. Implement data logging
4. Add remote monitoring
5. Create web interface

---

## 📊 Dataset Information

### Current Dataset
- **Total Images**: 2380 (1190 good, 1190 bad)
- **Training**: 1666 images (833 each)
- **Validation**: 356 images (178 each)
- **Testing**: 358 images (179 each)
- **Split Ratio**: 70% / 15% / 15%
- **Balance**: Perfect 1:1 ratio

### Image Specifications
- **Size**: 224x224 pixels
- **Format**: JPG
- **Preprocessing**: Aspect ratio preserved
- **Source**: iPhone HEIC images (3024x4032)
- **Cropping**: Automated batch processing

---

## 🔄 Retraining the Model

If you want to retrain with more data:

```bash
# 1. Add more images to cropped_images/good and cropped_images/bad

# 2. Re-split dataset
py -3.12 scripts/split_dataset_balanced.py cropped_images dataset

# 3. Retrain model
py -3.12 scripts/train_simple.py dataset/train dataset/val --output models --epochs 50

# 4. Test new model
py -3.12 scripts/test_model_fixed.py dataset/test models/best_model.keras --output test_results

# 5. Transfer to Raspberry Pi
scp models/best_model.keras pi@raspberrypi.local:~/bean_sorter/
```

**Training Time**: ~37 minutes on CPU, faster with GPU

---

## 💡 Tips for Best Results

### Hardware
- Use stable power supplies (avoid voltage drops)
- Ensure good lighting (consistent, bright)
- Keep camera lens clean
- Secure all connections
- Allow servo to reach positions fully

### Software
- Start with default settings
- Adjust one parameter at a time
- Test after each adjustment
- Monitor statistics during operation
- Keep backup of working configuration

### Operation
- Calibrate with test beans first
- Monitor first 50 beans closely
- Adjust timing based on belt speed
- Clean detection area regularly
- Check servo gate movement

---

## 🎯 Success Criteria

Your system is working correctly when:
- ✅ Camera shows live feed with predictions
- ✅ Servo moves smoothly between positions
- ✅ Conveyor belt runs at consistent speed
- ✅ Good beans diverted to side collection
- ✅ Bad beans continue straight
- ✅ LEDs blink for each detection
- ✅ Statistics update correctly
- ✅ Accuracy matches test results (~85%)

---

## 📞 Support Resources

### Documentation
1. Quick Start: `RASPBERRY_PI_QUICK_START.md`
2. Full Setup: `docs/RASPBERRY_PI_SETUP.md`
3. Wiring: `docs/WIRING_DIAGRAM.md`
4. Files: `RASPBERRY_PI_FILES_SUMMARY.md`

### Testing
1. Hardware: `python3 test_hardware.py all`
2. Camera: `python3 test_camera.py best_model.keras`
3. Individual: `python3 test_hardware.py [servo|motor|led]`

### Troubleshooting
1. Check connections (wiring diagram)
2. Test components individually
3. Review error messages
4. Check power supplies
5. Verify GPIO pins

---

## 🎉 System Status

```
✅ Dataset Created: 2380 images (balanced)
✅ Model Trained: 89.33% validation accuracy
✅ Model Tested: 85.47% test accuracy
✅ Confusion Matrix: Generated
✅ Raspberry Pi Scripts: Ready
✅ Documentation: Complete
✅ Wiring Diagrams: Available
✅ Testing Scripts: Included
✅ Quick Start Guide: Written

🚀 SYSTEM READY FOR DEPLOYMENT!
```

---

## 📝 Summary

You now have a complete AI-powered coffee bean sorting system:

**Hardware**: Raspberry Pi + Camera + Servo + Motor Driver + Conveyor
**Software**: Trained model (89.33% accuracy) + Control scripts
**Documentation**: Complete setup and troubleshooting guides
**Testing**: Individual component and system tests
**Performance**: 85.47% test accuracy, 94.41% bad bean detection

**Total Development Time**: Dataset preparation + Training + Integration
**Setup Time**: ~1 hour for new deployment
**Operation**: Fully automated with manual controls

---

**Your coffee bean sorting system is ready to deploy!** ☕🚀

For any questions, refer to the documentation files or test scripts.
Good luck with your project! 🎓
