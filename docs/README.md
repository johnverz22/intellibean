# Coffee Bean Sorter - Intelli-Bean

AI-powered coffee bean sorting system using Raspberry Pi 5, Camera Module 3, and servo-controlled gates.

## Project Overview

Automated 2-lane sorting system that classifies coffee beans as GOOD or BAD using computer vision and machine learning.

### Features
- Real-time bean detection and classification
- Servo-controlled sorting gates
- Camera Module 3 integration
- Configurable timing and calibration
- Statistics tracking

## Hardware Requirements

- Raspberry Pi 5 (4GB or 8GB)
- Camera Module 3 (IMX708 NoIR)
- 2x Servo motors (SG90 or MG996R)
- External 5V power supply (2-3A)
- Physical chute/ramp system

## Quick Start

1. **Hardware Setup**
   - Follow `docs/WIRING_GUIDE.md` for connections
   - Build physical chute system (see `docs/SYSTEM_DESIGN.md`)

2. **Software Installation**
   ```bash
   # On Raspberry Pi
   sudo apt update
   sudo apt install python3-rpi.gpio
   pip3 install --break-system-packages RPi.GPIO
   ```

3. **Deploy Code**
   ```bash
   # From your PC
   python scripts/deploy_to_pi.py
   ```

4. **Run System**
   ```bash
   # On Raspberry Pi
   cd ~/coffee-sorter
   python3 src/controller/bean_sorter.py --mode test
   ```

See `docs/QUICK_START.md` for detailed instructions.

## Project Structure

```
intelli-bean/
├── src/
│   ├── controller/          # Raspberry Pi control code
│   │   ├── bean_sorter.py      # Main application
│   │   ├── servo_controller.py # Servo motor control
│   │   └── camera_detector.py  # Camera operations
│   └── ml/                  # Machine learning (future)
├── docs/
│   ├── SYSTEM_DESIGN.md     # Complete system design
│   ├── WIRING_GUIDE.md      # Hardware wiring instructions
│   └── QUICK_START.md       # Quick start guide
├── scripts/                 # Deployment and utility scripts
├── tests/                   # Test files
└── config/
    └── .env                 # Configuration (SSH credentials)

## System Logic

**Sorting Flow:**
```
Bean → Camera Detection → ML Classification → Gate Control → Sorted
                                                    ↓
                                          GOOD: Gate Closed (slides right)
                                          BAD: Gate Opens (falls straight)
```

**GPIO Connections:**
- Servo 1 (Good Gate): GPIO 18 (Pin 12)
- Servo 2 (Bad Gate): GPIO 12 (Pin 32)

## Documentation

- **System Design**: `docs/SYSTEM_DESIGN.md` - Complete system architecture
- **Wiring Guide**: `docs/WIRING_GUIDE.md` - Detailed wiring instructions  
- **Quick Start**: `docs/QUICK_START.md` - Setup and usage guide

## Development

### SSH Connection
```bash
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197
```

### Deploy Updates
```bash
python scripts/deploy_to_pi.py
```

### Test Components
```bash
# Test servos
python3 src/controller/servo_controller.py

# Test camera
python3 src/controller/camera_detector.py

# Test full system
python3 src/controller/bean_sorter.py --mode test
```

## Configuration

Edit `src/controller/servo_controller.py`:
```python
GATE_CLOSED_ANGLE = 0    # Adjust for your servo
GATE_OPEN_ANGLE = 90     # Adjust for your servo
```

Edit `src/controller/bean_sorter.py`:
```python
travel_time = 1.5  # Seconds from camera to gate
```

## Dataset Collection

### Current Status
- **Target**: 3,000 coffee bean images for ML training
- **Categories**: Good/Bad × Curve/Back = 4 categories
- **Collection Method**: Remote GUI + OpenCV auto-cropping

### Quick Start
```bash
# 1. Improve detection rate (IMPORTANT!)
# Read this first: IMPROVE_DETECTION.md
python crop_beans.py temp_captures/sampletopcv.jpg

# 2. Start dataset collection GUI
python remote_dataset_collector.py

# 3. Capture batches of 240 beans
# 4. Auto-crop with OpenCV
```

### Detection Optimization
**Current**: 51.7% detection rate (124/240 beans)  
**Target**: 95%+ detection rate (228-240 beans)

**Quick fixes**:
1. Use WHITE background (poster board)
2. Improve lighting (even, no shadows)
3. Space beans 5-10mm apart

**Documentation**:
- **Start here**: `IMPROVE_DETECTION.md` - Quick action plan
- **Setup guide**: `docs/PHYSICAL_SETUP_CHECKLIST.md` - Printable checklist
- **Technical details**: `docs/OPTIMIZE_DETECTION.md` - Complete guide

**Tools**:
```bash
# Basic cropping (updated defaults)
python crop_beans.py image.jpg

# Advanced tuning
python crop_beans_tunable.py image.jpg --min-area 200 --max-area 5000

# Automated testing
python test_detection_params.py image.jpg
```

See `docs/DATASET_COLLECTION_GUIDE.md` for complete workflow.

## ML Model Integration (Future)

Once dataset is collected:

1. ✅ Collect 3,000 images (in progress)
2. Train classification model
3. Update `classify_bean()` method in `bean_sorter.py`
4. Deploy to Raspberry Pi

## Troubleshooting

See `docs/QUICK_START.md` for common issues and solutions.

## License

MIT License - See LICENSE file for details
