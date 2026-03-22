# OpenCV Setup for Dataset Collection

## Installation Steps

### 1. Install System Packages
```bash
sudo apt update
sudo apt install -y python3-opencv python3-tk python3-pil python3-pil.imagetk
```

### 2. Install Python Packages
```bash
pip3 install --break-system-packages opencv-python pillow numpy
```

### 3. Verify Installation
```bash
python3 -c "import cv2; print(f'OpenCV {cv2.__version__} installed')"
```

## Quick Start

### Run Setup Script
```bash
cd ~/coffee-sorter
chmod +x scripts/setup_dataset_collection.sh
./scripts/setup_dataset_collection.sh
```

### Test Detection
```bash
# Arrange 240 beans on grid, then:
python3 scripts/test_opencv_detection.py
```

This will:
1. Capture test image
2. Process with OpenCV
3. Show detection results
4. Save annotated image to ~/test_results/

### Launch GUI Application
```bash
python3 src/ml/dataset_collector.py
```

## Detection Parameters

### Tuning Detection (if needed)

Edit `src/ml/dataset_collector.py`:

```python
# Line ~180: Adjust these values
min_area = 500   # Minimum bean size (pixels²)
max_area = 5000  # Maximum bean size (pixels²)
```

**If beans not detected:**
- Decrease `min_area` (try 300)
- Increase `max_area` (try 8000)

**If too many false detections:**
- Increase `min_area` (try 800)
- Decrease `max_area` (try 3000)

### Threshold Adjustment

```python
# Line ~175: Adjust threshold method
_, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
# Or use adaptive threshold:
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY_INV, 11, 2)
```

## Workflow

### 1. Physical Setup
- Place white/neutral background
- Arrange 240 beans in 16x15 grid
- Ensure 1-2cm spacing between beans
- Set up consistent lighting

### 2. Test Detection
```bash
python3 scripts/test_opencv_detection.py
```

Review results in `~/test_results/`:
- `detection_result.jpg` - Annotated image with detected beans
- `step1_gray.jpg` - Grayscale conversion
- `step2_blurred.jpg` - After blur
- `step3_thresh.jpg` - After threshold

### 3. Adjust Parameters (if needed)
- Edit detection parameters
- Re-test until ~240 beans detected

### 4. Start Collection
```bash
python3 src/ml/dataset_collector.py
```

### 5. Capture Process
1. Select category (good/bad, curve/back)
2. Arrange beans on grid
3. Click "CAPTURE & PROCESS"
4. System auto-crops and saves individual beans
5. Repeat until target reached

## Troubleshooting

### OpenCV Import Error
```bash
# Try system package
sudo apt install python3-opencv

# Or pip install
pip3 install --break-system-packages opencv-python
```

### Tkinter Not Found
```bash
sudo apt install python3-tk
```

### Camera Not Working
```bash
# Test camera
rpicam-hello --list-cameras

# Check permissions
groups | grep video
```

### Low Detection Rate

**Problem**: Only detecting 100-150 beans instead of 240

**Solutions**:
1. Improve lighting (use diffused LED panel)
2. Increase contrast (darker background or lighter beans)
3. Adjust `min_area` parameter (lower value)
4. Check bean spacing (ensure not touching)

### Too Many Detections

**Problem**: Detecting 300+ objects

**Solutions**:
1. Increase `min_area` to filter noise
2. Clean background (remove dust/artifacts)
3. Adjust morphological operations
4. Use better lighting to reduce shadows

### Poor Crop Quality

**Problem**: Cropped images are blurry or cut off

**Solutions**:
1. Increase camera resolution
2. Improve focus
3. Adjust padding in crop function
4. Better lighting

## Advanced: Custom Detection

For more control, create custom detection script:

```python
import cv2
import numpy as np

def detect_beans(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Your custom processing here
    # ...
    
    return contours

# Use your function
contours = detect_beans('test.jpg')
```

## Performance Tips

1. **Use highest resolution** for capture (4608x2592)
2. **Process at lower resolution** if slow (resize before detection)
3. **Batch processing** - capture multiple grids before processing
4. **GPU acceleration** - OpenCV can use GPU if available

## Dataset Quality Checks

After each capture session:

```bash
# Count images
ls ~/coffee_dataset/good_beans/curve/ | wc -l

# Check image sizes
du -sh ~/coffee_dataset/good_beans/curve/

# View random samples
eog ~/coffee_dataset/good_beans/curve/good_curve_*.jpg
```

## Backup Dataset

Regularly backup your dataset:

```bash
# Compress dataset
tar -czf coffee_dataset_backup_$(date +%Y%m%d).tar.gz ~/coffee_dataset/

# Copy to PC
scp coffee_dataset_backup_*.tar.gz user@pc:/backup/
```
