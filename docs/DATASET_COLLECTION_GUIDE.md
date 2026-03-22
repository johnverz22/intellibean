# Coffee Bean Dataset Collection Guide

## Overview
Collect 3000 coffee bean images for ML training using automated capture and cropping.

## Dataset Structure

### Target Dataset
- **Total Images**: 3,000 beans
- **Good Beans**: 1,500 images
  - Curve side: 1,050 images
  - Back side: 450 images
- **Bad Beans**: 1,500 images
  - Curve side: 1,050 images
  - Back side: 450 images

### Capture Strategy
- **Batch Size**: 240 beans per capture
- **Total Batches**: ~13 batches (3000 ÷ 240)
- **Method**: Grid layout, single camera capture, OpenCV auto-crop

## Folder Structure
```
dataset/
├── good_beans/
│   ├── curve/
│   │   ├── good_curve_0001.jpg
│   │   ├── good_curve_0002.jpg
│   │   └── ... (1050 images)
│   └── back/
│       ├── good_back_0001.jpg
│       ├── good_back_0002.jpg
│       └── ... (450 images)
└── bad_beans/
    ├── curve/
    │   ├── bad_curve_0001.jpg
    │   ├── bad_curve_0002.jpg
    │   └── ... (1050 images)
    └── back/
        ├── bad_back_0001.jpg
        ├── bad_back_0002.jpg
        └── ... (450 images)
```

## Physical Setup

### Grid Layout for 240 Beans
```
Recommended: 16x15 grid = 240 beans

┌─────────────────────────────────┐
│  Camera (mounted above)         │
└─────────────────────────────────┘
                ↓
┌─────────────────────────────────┐
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  │ ← 16 beans
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  │
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  │
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  │
│  ... (15 rows total)            │
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○  │
└─────────────────────────────────┘
```

### Setup Requirements
1. **Flat surface** with white/neutral background
2. **Consistent lighting** (LED panel or natural light)
3. **Camera mount** (tripod or fixed position)
4. **Grid template** (printed or marked surface)
5. **Bean spacing**: 1-2cm between beans

## Workflow

### Step 1: Setup Environment
```bash
# Install dependencies
sudo apt update
sudo apt install python3-opencv python3-tk
pip3 install --break-system-packages opencv-python pillow
```

### Step 2: Prepare Beans
1. Sort beans into good/bad piles
2. Separate curve side and back side
3. Place 240 beans on grid (all same type/side)

### Step 3: Capture Image
1. Run GUI application
2. Click "Capture" button
3. Select category (good/bad, curve/back)
4. System auto-crops and saves individual beans

### Step 4: Repeat
- Continue until target dataset reached
- Track progress in GUI

## Capture Sessions

### Session Planning
```
Session 1: Good Beans - Curve Side
  - Batch 1: 240 beans
  - Batch 2: 240 beans
  - Batch 3: 240 beans
  - Batch 4: 240 beans
  - Batch 5: 90 beans
  Total: 1,050 images

Session 2: Good Beans - Back Side
  - Batch 1: 240 beans
  - Batch 2: 210 beans
  Total: 450 images

Session 3: Bad Beans - Curve Side
  - Batch 1-5: Same as Session 1
  Total: 1,050 images

Session 4: Bad Beans - Back Side
  - Batch 1-2: Same as Session 2
  Total: 450 images
```

## Quality Control

### Before Capture
- [ ] All beans properly positioned
- [ ] No overlapping beans
- [ ] Consistent lighting
- [ ] Camera focused
- [ ] Background clean

### After Capture
- [ ] Review cropped images
- [ ] Delete poor quality images
- [ ] Re-capture if needed
- [ ] Verify count matches expected

## Tips for Best Results

1. **Lighting**
   - Use diffused light to avoid shadows
   - Consistent brightness across grid
   - Avoid reflections on beans

2. **Bean Placement**
   - Ensure beans don't touch
   - Orient all beans same direction
   - Keep beans flat on surface

3. **Camera Settings**
   - Use highest resolution (4608x2592)
   - Fixed focus (not auto-focus)
   - Consistent white balance

4. **Processing**
   - Adjust detection threshold if needed
   - Verify all beans detected
   - Manual review of cropped images

## Troubleshooting

### Not All Beans Detected
- Increase contrast between beans and background
- Adjust OpenCV threshold parameters
- Ensure beans are separated

### Poor Crop Quality
- Check camera focus
- Improve lighting
- Increase image resolution

### Overlapping Detections
- Increase bean spacing
- Adjust contour detection parameters
- Use morphological operations

## Progress Tracking

Use the GUI to track:
- Images captured per category
- Total dataset progress
- Remaining images needed
- Session statistics
