# Coffee Bean Sorter - Quick Start Guide

## Setup Steps

### 1. Hardware Assembly (30-60 minutes)

1. **Build the chute system**
   - Create angled ramp (30-45°)
   - Single feed lane at top
   - Split into 2 lanes at bottom
   - Mount camera above detection point
   - Install servo gates at split point

2. **Wire the electronics**
   - Follow `WIRING_GUIDE.md`
   - Connect servos to GPIO 18 and GPIO 12
   - Use external 5V power supply
   - Double-check all connections

3. **Test hardware**
   ```bash
   python3 src/controller/servo_controller.py
   ```

### 2. Software Setup (10 minutes)

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-rpi.gpio python3-pip
   pip3 install --break-system-packages RPi.GPIO
   ```

2. **Clone/copy project files to Pi**
   ```bash
   # From your PC
   scp -i ~/.ssh/id_ed25519_rpi -r src/ beans@192.168.100.197:~/coffee-sorter/
   ```

3. **Test camera**
   ```bash
   cd ~/coffee-sorter
   python3 src/controller/camera_detector.py
   ```

### 3. Calibration (15 minutes)

1. **Calibrate servo angles**
   ```bash
   python3 src/controller/bean_sorter.py --mode calibrate-servo
   ```
   
   Find angles where:
   - Gate fully closed (blocks bean path)
   - Gate fully open (allows bean through)
   
   Update values in `servo_controller.py`:
   ```python
   GATE_CLOSED_ANGLE = 0    # Your closed angle
   GATE_OPEN_ANGLE = 90     # Your open angle
   ```

2. **Calibrate timing**
   ```bash
   python3 src/controller/bean_sorter.py --mode calibrate-timing
   ```
   
   Measure how long bean takes to travel from camera to gate.
   
   Run sorter with measured time:
   ```bash
   python3 src/controller/bean_sorter.py --travel-time 1.5
   ```

### 4. Test Run (5 minutes)

1. **Test mode (simulated beans)**
   ```bash
   python3 src/controller/bean_sorter.py --mode test --beans 10
   ```

2. **Manual mode (real beans)**
   ```bash
   python3 src/controller/bean_sorter.py --mode continuous
   ```
   
   Press Enter when bean enters detection zone.

### 5. Train ML Model (Later)

Currently using random classification for testing.

To add real ML:
1. Collect dataset of good/bad beans
2. Train classification model
3. Update `classify_bean()` in `bean_sorter.py`

## Usage Commands

### Basic Operation
```bash
# Test mode (10 simulated beans)
python3 src/controller/bean_sorter.py --mode test --beans 10

# Continuous mode (manual trigger)
python3 src/controller/bean_sorter.py --mode continuous

# With custom travel time
python3 src/controller/bean_sorter.py --travel-time 2.0
```

### Calibration
```bash
# Calibrate servo angles
python3 src/controller/bean_sorter.py --mode calibrate-servo

# Calibrate timing
python3 src/controller/bean_sorter.py --mode calibrate-timing
```

### Testing Components
```bash
# Test servos only
python3 src/controller/servo_controller.py

# Test camera only
python3 src/controller/camera_detector.py
```

## Troubleshooting

### Servo doesn't move
- Check wiring (signal to correct GPIO pin)
- Verify external power supply connected
- Run calibration mode to test

### Gate timing is off
- Re-run timing calibration
- Adjust `travel_time` parameter
- Check bean velocity is consistent

### Camera not capturing
- Check camera connection
- Run: `rpicam-hello --list-cameras`
- Verify camera enabled in config

### Beans not sorting correctly
- Check gate angles (closed should block, open should allow)
- Verify timing delay is correct
- Test with slower bean feed rate

## System Logic Summary

```
1. Bean enters detection zone
   ↓
2. Camera captures image
   ↓
3. ML model classifies: GOOD or BAD
   ↓
4. Wait for bean to travel to gate
   ↓
5. Actuate gate:
   - GOOD: Gate stays CLOSED → bean slides to good lane
   - BAD: Gate OPENS briefly → bean falls to bad lane
   ↓
6. Gate closes, ready for next bean
```

## Next Steps

1. ✅ Hardware assembly
2. ✅ Software installation
3. ✅ Calibration
4. ✅ Test run
5. ⏳ Collect bean dataset
6. ⏳ Train ML model
7. ⏳ Integrate ML model
8. ⏳ Production run

## Support

For issues or questions:
- Check `SYSTEM_DESIGN.md` for detailed explanations
- Check `WIRING_GUIDE.md` for connection help
- Review code comments in source files
