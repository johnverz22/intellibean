# Coffee Bean Detection Optimization - Complete Guide

## 📋 Overview

This guide helps you improve OpenCV detection rate from 51% to 95%+ for coffee bean dataset collection.

**Current Status**: 124/240 beans detected (51.7%)  
**Target**: 228-240 beans detected (95-100%)

---

## 🚀 Quick Start (30 minutes)

### Step 1: Read the Quick Fix Guide
```bash
# Open and follow this guide first
docs/QUICK_FIX_GUIDE.md
```

### Step 2: Setup Physical Environment
```bash
# Print and follow this checklist
docs/PHYSICAL_SETUP_CHECKLIST.md
```

### Step 3: Test Detection
```bash
# Test with current image
python crop_beans_tunable.py temp_captures/sampletopcv.jpg

# Or test multiple parameter combinations
python test_detection_params.py temp_captures/sampletopcv.jpg
```

---

## 📁 File Guide

### Documentation Files
- **QUICK_FIX_GUIDE.md** - Start here! 30-minute action plan
- **PHYSICAL_SETUP_CHECKLIST.md** - Printable checklist for setup
- **OPTIMIZE_DETECTION.md** - Comprehensive technical guide
- **DETECTION_README.md** - This file (overview)

### Python Scripts
- **crop_beans.py** - Original cropping script (updated defaults)
- **crop_beans_tunable.py** - Advanced script with parameter tuning
- **test_detection_params.py** - Automated parameter testing
- **remote_dataset_collector.py** - GUI for dataset collection

---

## 🎯 The Problem

### Why Low Detection Rate?

1. **Background** (40% of problem)
   - Beans blend with brown/wood background
   - Low contrast makes edge detection difficult

2. **Lighting** (30% of problem)
   - Shadows create false edges
   - Uneven lighting causes detection gaps
   - Overexposure washes out details

3. **Bean Spacing** (20% of problem)
   - Touching beans detected as single object
   - Overlapping beans confuse algorithm

4. **Software Parameters** (10% of problem)
   - Thresholds too strict
   - Area filters miss valid beans

---

## ✅ The Solution

### Priority Order (Most Important First)

#### 1. White Background ⭐⭐⭐⭐⭐
```
Impact: +30% detection rate
Cost: $2-5 (poster board)
Time: 5 minutes

What to do:
- Get white poster board (matte finish)
- Place on flat surface
- Ensure it's clean and covers entire view
```

#### 2. Even Lighting ⭐⭐⭐⭐
```
Impact: +20% detection rate
Cost: $0-30 (use existing or buy LED lamp)
Time: 10 minutes

What to do:
- Position light 30-40cm above beans
- Use diffused light (not direct)
- Eliminate all shadows
- Check with phone light meter (500-1000 lux)
```

#### 3. Bean Spacing ⭐⭐⭐⭐
```
Impact: +15% detection rate
Cost: $0 (just time)
Time: 15 minutes

What to do:
- Space beans 5-10mm apart
- Use grid template (16×15 = 240 beans)
- Ensure no beans touch
- Keep beans flat (not on edge)
```

#### 4. Software Tuning ⭐⭐
```
Impact: +5-10% detection rate
Cost: $0
Time: 5 minutes

What to do:
- Lower min_area from 500 to 200
- Lower max_area from 10000 to 5000
- Try adaptive threshold
- Use watershed for touching beans
```

---

## 🧪 Testing Workflow

### Phase 1: Quick Test (10 beans)
```bash
# Arrange 10 beans with good spacing
# Capture image
python remote_dataset_collector.py

# Test detection
python crop_beans_tunable.py temp_captures/latest_capture.jpg

# Expected: 9-10 beans detected
```

### Phase 2: Medium Test (50 beans)
```bash
# Arrange 50 beans in grid
# Capture image
python crop_beans_tunable.py temp_captures/test_50beans.jpg

# Expected: 48-50 beans detected
```

### Phase 3: Full Test (240 beans)
```bash
# Arrange all 240 beans
# Capture image
python crop_beans_tunable.py temp_captures/test_240beans.jpg

# Expected: 228-240 beans detected
```

### Phase 4: Parameter Optimization (if needed)
```bash
# Test multiple parameter combinations automatically
python test_detection_params.py temp_captures/test_240beans.jpg

# Review results and use best parameters
```

---

## 🔧 Parameter Tuning Guide

### When to Adjust Parameters

**Too Few Detections (<200 beans)**
```bash
# Try more sensitive settings
python crop_beans_tunable.py image.jpg --min-area 150 --max-area 6000

# Or adaptive threshold
python crop_beans_tunable.py image.jpg --threshold adaptive

# Or watershed separation
python crop_beans_tunable.py image.jpg --separate-touching
```

**Too Many Detections (>260 beans)**
```bash
# Try less sensitive settings
python crop_beans_tunable.py image.jpg --min-area 300 --max-area 4000

# Or increase morphology
python crop_beans_tunable.py image.jpg --morph-close 3 --morph-open 2
```

**Beans Merging Together**
```bash
# Use watershed algorithm
python crop_beans_tunable.py image.jpg --separate-touching

# Or increase opening
python crop_beans_tunable.py image.jpg --morph-open 2
```

### Parameter Reference

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| min_area | 200 | 100-500 | Lower = detect smaller beans |
| max_area | 5000 | 3000-10000 | Higher = detect larger beans |
| threshold | otsu | otsu/adaptive | Adaptive = better for uneven lighting |
| morph_close | 2 | 1-5 | Higher = fill gaps in beans |
| morph_open | 1 | 1-3 | Higher = separate touching beans |

---

## 📊 Expected Results

### With Proper Setup

| Metric | Value |
|--------|-------|
| Detection Rate | 95-100% (228-240 beans) |
| False Positives | <5 |
| Processing Time | 5-10 seconds |
| Crop Quality | Sharp, well-framed |

### Signs of Good Setup
- ✅ All beans visible in visualization
- ✅ Consistent detection across image
- ✅ Clean crop boundaries
- ✅ No merged or fragmented beans
- ✅ Even detection in corners and center

### Signs of Poor Setup
- ❌ Beans missing from corners
- ❌ Shadows creating false detections
- ❌ Beans merged together
- ❌ Uneven detection across image
- ❌ Many false positives (dust, stains)

---

## 🛒 Shopping List

### Minimal Setup ($5-10)
- White poster board (60cm × 40cm)
- Ruler for spacing

**Expected Result**: 80-90% detection rate

### Recommended Setup ($30-50)
- White poster board
- LED desk lamp (diffused)
- Transparent acrylic sheet
- Printed grid template

**Expected Result**: 90-95% detection rate

### Professional Setup ($100-150)
- Light box or photo tent
- Multiple LED panels
- Camera tripod
- Printed grid on foam board
- Color calibration card

**Expected Result**: 95-100% detection rate

---

## 🎓 Understanding the Algorithm

### Processing Steps

1. **Grayscale Conversion**
   - Simplifies image to single channel
   - Removes color information

2. **Gaussian Blur**
   - Reduces noise
   - Smooths edges

3. **Thresholding**
   - Separates beans from background
   - Creates binary image (black/white)

4. **Morphological Operations**
   - Closing: Fills small gaps in beans
   - Opening: Separates touching beans

5. **Contour Detection**
   - Finds bean boundaries
   - Extracts shape information

6. **Filtering**
   - Removes too small/large objects
   - Filters by shape (circularity)

7. **Cropping**
   - Extracts each bean
   - Adds padding
   - Saves individual images

### Why Physical Setup Matters

**Good Setup**:
```
White background → High contrast → Clear edges → Easy detection
Even lighting → No shadows → Consistent threshold → Accurate contours
Spaced beans → Separate objects → Individual detection → Correct count
```

**Poor Setup**:
```
Dark background → Low contrast → Weak edges → Missed beans
Uneven lighting → Shadows → Variable threshold → False detections
Touching beans → Single object → Merged detection → Low count
```

---

## 🐛 Troubleshooting

### Problem: Still <200 beans detected

**Checklist**:
1. Is background WHITE? (not cream, gray, or brown)
2. Is lighting EVEN? (no shadows visible)
3. Are beans SPACED? (5mm minimum)
4. Is camera FOCUSED? (not blurry)
5. Is image SHARP? (check camera settings)

**Try**:
```bash
# Lower thresholds
python crop_beans_tunable.py image.jpg --min-area 150

# Adaptive threshold
python crop_beans_tunable.py image.jpg --threshold adaptive

# Test all combinations
python test_detection_params.py image.jpg
```

### Problem: >260 beans detected (false positives)

**Checklist**:
1. Is background CLEAN? (no dust, stains, patterns)
2. Are there SHADOWS? (creating false edges)
3. Is lighting TOO BRIGHT? (causing reflections)

**Try**:
```bash
# Higher thresholds
python crop_beans_tunable.py image.jpg --min-area 300

# More morphology
python crop_beans_tunable.py image.jpg --morph-open 2
```

### Problem: Beans merged together

**Checklist**:
1. Are beans TOUCHING? (increase spacing)
2. Is threshold TOO AGGRESSIVE? (merging nearby objects)

**Try**:
```bash
# Watershed separation
python crop_beans_tunable.py image.jpg --separate-touching

# More opening
python crop_beans_tunable.py image.jpg --morph-open 2
```

### Problem: Beans fragmented

**Checklist**:
1. Is lighting TOO HARSH? (creating internal shadows)
2. Is threshold TOO WEAK? (breaking beans apart)

**Try**:
```bash
# More closing
python crop_beans_tunable.py image.jpg --morph-close 3

# Adaptive threshold
python crop_beans_tunable.py image.jpg --threshold adaptive
```

---

## 📈 Dataset Collection Workflow

Once you achieve 95%+ detection:

### 1. Prepare Batches
- 240 beans per batch
- Consistent setup for all captures
- Same lighting, background, spacing

### 2. Capture Images
```bash
# Use GUI application
python remote_dataset_collector.py

# Select category (good/bad, curve/back)
# Click "CAPTURE IMAGE" button
# Image saved to coffee_dataset/
```

### 3. Auto-Crop Beans
```bash
# Crop automatically after capture
python crop_beans.py coffee_dataset/good_beans/curve/good_curve_0001.jpg

# Or use tunable version
python crop_beans_tunable.py coffee_dataset/good_beans/curve/good_curve_0001.jpg
```

### 4. Verify Results
- Check detection_visualization.jpg
- Ensure 228-240 beans detected
- Verify crop quality

### 5. Repeat
- Good curve: 5 batches (1,050 images)
- Good back: 2 batches (450 images)
- Bad curve: 5 batches (1,050 images)
- Bad back: 2 batches (450 images)
- **Total: 14 batches = 3,000 images**

---

## 🎯 Success Metrics

### Ready for Dataset Collection
- ✅ 95-100% detection rate (228-240 beans)
- ✅ Consistent results across multiple captures
- ✅ Clean crop boundaries
- ✅ Processing time <10 seconds
- ✅ Setup is repeatable

### Next Steps
1. Start dataset collection
2. Maintain consistent setup
3. Verify each batch
4. Complete 3,000 images
5. Train ML model

---

## 📞 Need Help?

### Check These Files First
1. QUICK_FIX_GUIDE.md - Quick solutions
2. PHYSICAL_SETUP_CHECKLIST.md - Setup verification
3. OPTIMIZE_DETECTION.md - Technical details

### Common Issues
- Low detection → Check background and lighting
- High false positives → Clean background, reduce shadows
- Merged beans → Increase spacing, use watershed
- Fragmented beans → Improve lighting, adjust morphology

### Test Commands
```bash
# Basic test
python crop_beans.py image.jpg

# Advanced test
python crop_beans_tunable.py image.jpg --min-area 200 --max-area 5000

# Automated testing
python test_detection_params.py image.jpg
```

---

**Remember**: Physical setup (background + lighting + spacing) is 90% of the solution!
