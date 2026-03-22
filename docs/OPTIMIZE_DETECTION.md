# Optimizing Coffee Bean Detection - Complete Guide

## Current Issue
Detection rate: 51.7% (124 beans detected out of 240 target)

## Solution: Physical Setup + Software Tuning

---

## PART 1: Physical Setup (Most Important!)

### 1. Background Setup ⭐ CRITICAL
**Problem**: Beans blend with background, hard to detect edges

**Solution**:
- ✅ **Use WHITE paper/cardboard** as background (not wood/table)
- ✅ **Matte finish** (not glossy - causes reflections)
- ✅ **Clean surface** (no dust, stains, or patterns)
- ✅ **Large enough** to cover entire camera view

**DIY Setup**:
```
┌─────────────────────────────┐
│  White poster board         │
│  (60cm x 40cm minimum)      │
│                             │
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○    │ ← Coffee beans
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○    │
│  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○    │
└─────────────────────────────┘
```

### 2. Lighting Setup ⭐ CRITICAL
**Problem**: Shadows, uneven lighting, overexposure

**Solution A: Diffused LED Panel (Best)**
```
        ┌─────────────┐
        │  LED Panel  │
        │  (Diffused) │
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │   Camera    │
        └──────┬──────┘
               ↓
        ═══════════════  ← Beans on white surface
```

**Solution B: Two Side Lights (Good)**
```
    LED ←─────────────→ LED
     ↘                 ↙
        ┌─────────────┐
        │   Camera    │
        └──────┬──────┘
               ↓
        ═══════════════  ← Beans
```

**Solution C: Natural Light + Diffuser (OK)**
```
    Window
       ↓
    [White sheet/paper] ← Diffuser
       ↓
    ═══════════════  ← Beans
```

**Lighting Checklist**:
- [ ] No direct sunlight (too harsh)
- [ ] No shadows from beans
- [ ] Even brightness across entire surface
- [ ] No reflections/glare
- [ ] Brightness: 500-1000 lux (use phone light meter app)

### 3. Bean Arrangement ⭐ IMPORTANT
**Problem**: Beans touching = detected as one object

**Solution**:
- ✅ **Minimum 5mm spacing** between beans
- ✅ **Grid template** (print or draw lines)
- ✅ **Consistent orientation** (all curve side up)
- ✅ **Flat placement** (no beans on edge)

**Grid Template** (16x15 = 240 beans):
```
Print this grid on paper, place under transparent sheet:

┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤
... (15 rows total)

Each cell: 2.5cm x 2.5cm
Total grid: 40cm x 37.5cm
```

### 4. Camera Setup
**Problem**: Blurry, wrong angle, wrong distance

**Solution**:
- ✅ **Mount camera directly above** (90° angle)
- ✅ **Height**: 30-50cm above beans
- ✅ **Stable mount** (tripod or fixed position)
- ✅ **Focus on center** of grid
- ✅ **Frame entire grid** with small margin

**Camera Position**:
```
        Camera
          │
          │ 30-50cm
          │
          ↓
    ═══════════════
    Grid with beans
```

---

## PART 2: Software Optimization

### 1. Adjust Detection Parameters

Edit `crop_beans.py` line 48-49:

**Current (Too Strict)**:
```python
min_area = 500   # Too high - missing small beans
max_area = 10000 # Too high - missing medium beans
```

**Recommended (Better)**:
```python
min_area = 200   # Lower to catch smaller beans
max_area = 5000  # Lower to avoid grouping
```

**For Your Specific Beans** (measure one bean):
```python
# Measure one bean in pixels (width × height)
# Example: 50px × 80px = 4000px²
bean_area = 4000
min_area = bean_area * 0.5  # 50% smaller
max_area = bean_area * 2.0  # 200% larger
```

### 2. Improve Threshold Method

**Current**: Otsu's method (automatic)
**Problem**: May not work well with your lighting

**Try Adaptive Threshold**:
```python
# Replace line 38 in crop_beans.py:
# OLD:
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# NEW:
thresh = cv2.adaptiveThreshold(blurred, 255, 
                               cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 11, 2)
```

### 3. Adjust Morphological Operations

**If beans are merging**:
```python
# Increase opening to separate beans
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
```

**If beans are fragmenting**:
```python
# Increase closing to fill gaps
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
```

### 4. Use Color-Based Detection (Advanced)

If beans are brown and background is white:
```python
# Convert to HSV color space
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Define brown color range
lower_brown = np.array([10, 50, 50])
upper_brown = np.array([30, 255, 200])

# Create mask
mask = cv2.inRange(hsv, lower_brown, upper_brown)
```

---

## PART 3: Testing & Iteration

### Step-by-Step Optimization Process

**1. Start with Physical Setup**
```bash
# Test with 10 beans first
python crop_beans.py test_10beans.jpg
```

Expected: 10/10 detected (100%)

**2. Scale to 50 beans**
```bash
python crop_beans.py test_50beans.jpg
```

Expected: 48-50/50 detected (96-100%)

**3. Full 240 beans**
```bash
python crop_beans.py test_240beans.jpg
```

Expected: 230-240/240 detected (96-100%)

### Troubleshooting Guide

**Problem: Too Few Detections (<200)**

Check:
1. Background contrast (white background?)
2. Lighting (even, no shadows?)
3. Bean spacing (5mm minimum?)
4. min_area too high? (try 200)

**Problem: Too Many Detections (>260)**

Check:
1. Background clean? (no dust/stains)
2. Shadows creating false detections?
3. min_area too low? (try 400)
4. Increase morphological opening

**Problem: Beans Merged Together**

Check:
1. Beans touching? (increase spacing)
2. Increase morphological opening
3. Use watershed algorithm (advanced)

**Problem: Beans Fragmented**

Check:
1. Increase morphological closing
2. Adjust threshold value
3. Better lighting

---

## PART 4: Recommended Shopping List

### Essential Items
1. **White Poster Board** (60cm x 40cm) - $2-5
   - Matte finish, thick cardboard
   
2. **LED Panel Light** (Diffused, 5000K-6500K) - $15-30
   - Adjustable brightness
   - Diffused (not direct LED)
   
3. **Camera Tripod** or **Adjustable Arm** - $10-20
   - Stable mounting
   - Adjustable height

### Optional Items
4. **Grid Template** (Printed) - $1
   - 16x15 grid, 2.5cm cells
   
5. **Transparent Acrylic Sheet** - $5-10
   - Place over grid template
   - Easy to clean

6. **Light Meter App** (Free)
   - Measure lighting consistency
   - Target: 500-1000 lux

---

## PART 5: Quick Setup Guide

### Minimal Setup (Budget: $5)
1. White poster board as background
2. Natural window light + white paper diffuser
3. Camera on stack of books
4. Hand-drawn grid with ruler

### Recommended Setup (Budget: $50)
1. White poster board
2. LED panel light (diffused)
3. Camera tripod
4. Printed grid template
5. Transparent acrylic sheet

### Professional Setup (Budget: $150)
1. Light box or photo tent
2. Multiple LED panels
3. Professional camera mount
4. Printed grid on foam board
5. Color calibration card

---

## PART 6: Expected Results

### With Proper Setup
- **Detection Rate**: 95-100% (228-240 beans)
- **False Positives**: <5
- **Processing Time**: 5-10 seconds
- **Crop Quality**: Sharp, well-framed

### Signs of Good Setup
✅ All beans clearly visible in visualization
✅ Consistent detection across entire image
✅ Clean crop boundaries
✅ No merged or fragmented beans

### Signs of Poor Setup
❌ Beans missing from corners
❌ Shadows creating false detections
❌ Beans merged together
❌ Uneven detection across image

---

## PART 7: Advanced Techniques

### 1. Watershed Algorithm (Separate Touching Beans)
```python
# Add after morphological operations
dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
_, sure_fg = cv2.threshold(dist_transform, 0.5*dist_transform.max(), 255, 0)
```

### 2. Machine Learning Detection (YOLO/Faster R-CNN)
- Train custom object detector
- Better for complex scenarios
- Requires labeled dataset

### 3. Multi-Scale Detection
- Process image at different resolutions
- Combine results
- Better for varying bean sizes

---

## Summary Checklist

Before capturing dataset:
- [ ] White matte background
- [ ] Even, diffused lighting (no shadows)
- [ ] Beans spaced 5mm apart
- [ ] Camera mounted directly above
- [ ] Grid template in place
- [ ] Test with 10 beans first
- [ ] Adjust parameters if needed
- [ ] Achieve >95% detection rate

**Most Important**: Physical setup (background + lighting) matters more than software tuning!
