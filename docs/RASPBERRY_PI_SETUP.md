# Raspberry Pi Bean Sorting System - Setup Guide

Complete guide for setting up the coffee bean sorting system on Raspberry Pi.

---

## Hardware Requirements

### Components
1. **Raspberry Pi 4** (4GB RAM recommended)
2. **Raspberry Pi Camera Module V2** or **Pi Camera V3**
3. **Servo Motor** (SG90 or MG996R)
4. **BTS7960 Motor Driver** (43A H-Bridge for conveyor belt)
5. **DC Motor** (12V for conveyor belt)
6. **Power Supply**:
   - 5V 3A for Raspberry Pi
   - 12V 5A for motor driver and DC motor
7. **LEDs** (Optional):
   - Green LED (good beans indicator)
   - Red LED (bad beans indicator)
   - 2x 220Ω resistors
8. **Jumper Wires** (Male-to-Female)
9. **Breadboard** (Optional, for testing)

---

## Wiring Diagram

### Servo Motor (Gate Control)
```
Servo Motor          Raspberry Pi
-----------          ------------
VCC (Red)      →     5V (Pin 2 or 4)
GND (Brown)    →     GND (Pin 6)
Signal (Orange)→     GPIO 18 (Pin 12)
```

### BTS7960 Motor Driver (Conveyor Belt)
```
BTS7960              Raspberry Pi          DC Motor
-------              ------------          --------
VCC                → 5V (Pin 2)
GND                → GND (Pin 14)
RPWM (Right PWM)   → GPIO 23 (Pin 16)
LPWM (Left PWM)    → GPIO 24 (Pin 18)
R_EN (Right Enable)→ GPIO 25 (Pin 22)
L_EN (Left Enable) → GPIO 8 (Pin 24)

B+                 → Motor (+)
B-                 → Motor (-)
VCC (Motor Power)  → 12V Power Supply (+)
GND (Motor Power)  → 12V Power Supply (-)
```

**IMPORTANT**: BTS7960 has TWO power inputs:
- **Logic Power (VCC/GND)**: Connect to Raspberry Pi 5V
- **Motor Power (VCC/GND)**: Connect to 12V external power supply

### LED Indicators (Optional)
```
Component            Raspberry Pi
---------            ------------
Green LED (+)  →     GPIO 17 (Pin 11) → 220Ω resistor → LED → GND
Red LED (+)    →     GPIO 27 (Pin 13) → 220Ω resistor → LED → GND
```

### Camera Module
```
Camera Ribbon Cable → Camera CSI Port (between HDMI and USB ports)
```

---

## Pin Layout Reference

```
Raspberry Pi GPIO Pinout (BCM numbering):

     3V3  (1) (2)  5V      ← Servo VCC
   GPIO2  (3) (4)  5V      ← BTS7960 Logic VCC
   GPIO3  (5) (6)  GND     ← Servo GND
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18  ← Servo Signal
  GPIO27 (13) (14) GND     ← BTS7960 GND
  GPIO22 (15) (16) GPIO23  ← BTS7960 RPWM
     3V3 (17) (18) GPIO24  ← BTS7960 LPWM
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25  ← BTS7960 R_EN
  GPIO11 (23) (24) GPIO8   ← BTS7960 L_EN
     GND (25) (26) GPIO7
```

---

## Software Installation

### 1. Update Raspberry Pi OS
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python Dependencies
```bash
# Install system packages
sudo apt install -y python3-pip python3-opencv python3-picamera2

# Install Python packages
pip3 install tensorflow
pip3 install RPi.GPIO
pip3 install numpy
pip3 install opencv-python
```

### 3. Enable Camera
```bash
# For Raspberry Pi OS Bullseye or later
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Reboot
sudo reboot
```

### 4. Test Camera
```bash
# Test camera capture
libcamera-hello
```

### 5. Transfer Files to Raspberry Pi

From your Windows PC:
```bash
# Copy model file
scp models/best_model.keras pi@raspberrypi.local:~/bean_sorter/

# Copy Python scripts
scp raspberry_pi/*.py pi@raspberrypi.local:~/bean_sorter/
```

Or use FileZilla/WinSCP for GUI file transfer.

---

## Hardware Testing

### Test 1: Servo Motor
```bash
cd ~/bean_sorter
python3 test_hardware.py servo
```

**Expected behavior**:
- Servo moves to 0° (closed position)
- Servo moves to 90° (neutral)
- Servo moves to 180° (open position)
- Servo returns to 90°

### Test 2: Motor Driver (Conveyor)
```bash
python3 test_hardware.py motor
```

**Expected behavior**:
- Motor runs forward at 30%, 50%, 70% speed
- Motor stops
- Motor runs backward at 30% speed
- Motor stops

### Test 3: LED Indicators
```bash
python3 test_hardware.py led
```

**Expected behavior**:
- Green LED blinks
- Red LED blinks
- Both LEDs blink together

### Test 4: All Hardware
```bash
python3 test_hardware.py all
```

---

## Camera + Model Testing

### Test Camera with Model
```bash
python3 test_camera.py best_model.keras
```

**Controls**:
- Press `c` to capture and show prediction
- Press `s` to save current frame
- Press `q` to quit

**Expected output**:
```
Loading model...
✓ Model loaded
  Input shape: (None, 224, 224, 3)
  Output shape: (None, 2)

Initializing camera...
✓ Camera ready

LIVE DETECTION TEST
Press 'q' to quit
Press 'c' to capture and predict
```

---

## Running the Sorting System

### Start the Bean Sorter
```bash
python3 bean_sorter.py best_model.keras
```

### Command Line Options
```bash
# Custom conveyor speed (0-100)
python3 bean_sorter.py best_model.keras --speed 60

# Custom confidence threshold (0-1)
python3 bean_sorter.py best_model.keras --confidence 0.8

# Both options
python3 bean_sorter.py best_model.keras --speed 60 --confidence 0.8
```

### Controls During Operation
- Press `s` to start/stop conveyor belt
- Press `q` to quit and show statistics

---

## System Logic

### Sorting Flow
```
1. Camera captures frame
2. Model predicts bean quality
3. If confidence > threshold:
   - Wait for bean to reach servo (0.8 seconds)
   - If GOOD bean:
     * Close gate (servo to 0°)
     * Bean diverted to side collection
     * Green LED blinks
   - If BAD bean:
     * Open gate (servo to 180°)
     * Bean continues straight
     * Red LED blinks
4. Servo returns to neutral (90°)
5. Repeat
```

### Servo Positions
- **0° (CLOSED)**: Gate blocks path → Good beans go to SIDE
- **90° (NEUTRAL)**: Default waiting position
- **180° (OPEN)**: Gate allows passage → Bad beans go STRAIGHT

---

## Troubleshooting

### Camera Issues

**Problem**: Camera not detected
```bash
# Check camera connection
libcamera-hello

# If error, check cable connection and enable camera:
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

**Problem**: "Failed to create camera"
```bash
# Update picamera2
pip3 install --upgrade picamera2
```

### Servo Issues

**Problem**: Servo jitters or doesn't move
- Check power supply (servo needs stable 5V)
- Verify GPIO 18 connection
- Test with hardware test script

**Problem**: Servo moves but positions are wrong
- Adjust duty cycle values in `bean_sorter.py`:
```python
SERVO_CLOSED = 2.5   # Try 2.0 to 3.0
SERVO_OPEN = 12.5    # Try 12.0 to 13.0
```

### Motor Driver Issues

**Problem**: Motor doesn't run
- Check 12V power supply connection
- Verify enable pins are HIGH
- Test with hardware test script
- Check motor connections (B+/B-)

**Problem**: Motor runs but weak
- Increase PWM duty cycle (speed parameter)
- Check 12V power supply amperage (needs 5A+)
- Verify motor driver can handle motor current

### Model Issues

**Problem**: Low accuracy
- Adjust confidence threshold: `--confidence 0.6`
- Improve lighting conditions
- Retrain model with more data

**Problem**: Model too slow
- Reduce detection frequency (increase `DETECTION_DELAY`)
- Use TFLite model (faster inference)

### GPIO Issues

**Problem**: "GPIO already in use"
```bash
# Clean up GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"
```

**Problem**: Permission denied
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Logout and login again
```

---

## Performance Optimization

### 1. Use TFLite Model (Faster)
Convert your model to TFLite format on PC:
```python
import tensorflow as tf

model = tf.keras.models.load_model('best_model.keras')
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

### 2. Adjust Detection Parameters
In `bean_sorter.py`:
```python
DETECTION_DELAY = 1.0  # Faster detection (was 1.5)
SERVO_ACTIVATION_DELAY = 0.6  # Faster sorting (was 0.8)
```

### 3. Reduce Camera Resolution
```python
config = camera.create_preview_configuration(
    main={"size": (320, 240), "format": "RGB888"}  # Lower resolution
)
```

---

## Auto-Start on Boot (Optional)

Create systemd service:
```bash
sudo nano /etc/systemd/system/bean-sorter.service
```

Add:
```ini
[Unit]
Description=Coffee Bean Sorting System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/bean_sorter
ExecStart=/usr/bin/python3 /home/pi/bean_sorter/bean_sorter.py /home/pi/bean_sorter/best_model.keras
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable bean-sorter.service
sudo systemctl start bean-sorter.service
```

---

## Safety Notes

1. **Power Supply**: Use separate power supplies for Raspberry Pi (5V) and motor (12V)
2. **Motor Driver**: BTS7960 can get hot - ensure adequate cooling
3. **Servo**: Don't force servo manually when powered
4. **Wiring**: Double-check all connections before powering on
5. **Emergency Stop**: Keep power switch accessible

---

## Maintenance

### Daily
- Clean camera lens
- Check belt tension
- Verify servo gate movement

### Weekly
- Clean detection area
- Check all wire connections
- Test emergency stop

### Monthly
- Backup model and scripts
- Update system packages
- Check motor driver temperature

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review hardware connections
3. Test components individually
4. Check system logs: `journalctl -u bean-sorter.service`

---

**System Ready!** Your coffee bean sorting machine is now operational. 🚀☕
