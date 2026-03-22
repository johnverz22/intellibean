# Quick Fix Guide - Improve Detection from 51% to 95%+

## Current Status
- **Detection Rate**: 51.7% (124/240 beans)
- **Problem**: Low contrast, poor lighting, beans too close together

## Quick Action Plan (30 minutes)

### Step 1: Physical Setup (15 minutes) ⭐ MOST IMPORTANT

#### A. Background
```
✅ DO THIS NOW:
1. Get white paper/cardboard (poster board is best)
2. Place on flat surface
3. Make sure it's CLEAN (no stains, dust)
4. Cover entire camera view area
```

#### B. Lighting
```
✅ CHOOSE ONE:

Option 1 - LED Desk Lamp (Best if you have one):
   - Position 30-40cm above beans
   - Use diffused/soft light (not direct)
   - Angle slightly to avoid shadows

Option 2 - Window Light (Good):
   - Place setup near window
   - Use indirect sunlight (not direct sun)
   - Add white paper as diffuser if too bright

Option 3 - Room Light (OK):
   - Turn on all room lights
   - Add desk lamp if available
   - Avoid shadows on beans
```

#### C. Bean Arrangement
```
✅ CRITICAL:
1. Space beans 5-10mm apart (use ruler)
2. Don't let beans touch each other
3. Place beans flat (not on edge)
4. Arrange in grid pattern (16 columns × 15 rows)
```

**Quick Grid Template**:
```
Print this or draw on paper:
- 16 columns × 15 rows = 240 beans
- Each cell: 2.5cm × 2.5cm
- Total area: 40cm × 37.5cm
```

### Step 2: Test with 10 Beans (5 minutes)

```bash
# Arrange 10 beans with good spacing
# Capture test image
python remote_dataset_collector.py

# Test detection
python crop_beans.py temp_captures/[latest_capture].jpg
```

**Expected Result**: 9-10 beans detected (90-100%)

If less than 8 detected:
- Check background (is it white?)
- Check lighting (any shadows?)
- Check spacing (beans touching?)

### Step 3: Adjust Software Parameters (5 minutes)

If physical setup is good but detection still low, adjust parameters:

```bash
# Run with adjusted parameters
python crop_beans_tunable.py temp_captures/sampletopcv.jpg --min-area 200 --max-area 5000
```

Try different values:
- **min_area**: 150, 200, 250, 300
- **max_area**: 4000, 5000, 6000

### Step 4: Full Test with 240 Beans (5 minutes)

Once 10-bean test works:
1. Arrange all 240 beans in grid
2. Capture image
3. Run detection
4. Should get 230-240 beans (95-100%)

---

## Troubleshooting Quick Reference

### Problem: Still detecting <200 beans

**Check in this order**:
1. ❓ Is background WHITE? (not brown/wood)
2. ❓ Are beans SPACED apart? (5mm minimum)
3. ❓ Is lighting EVEN? (no shadows)
4. ❓ Is camera FOCUSED? (not blurry)

**Quick fixes**:
- Add more light
- Increase bean spacing
- Use whiter background
- Lower min_area to 200

### Problem: Detecting >260 beans (false positives)

**Quick fixes**:
- Clean background (remove dust)
- Reduce shadows
- Increase min_area to 400
- Better lighting

### Problem: Beans merged together

**Quick fixes**:
- Increase spacing between beans
- Use `--separate-touching` flag
- Adjust morphological operations

---

## Shopping List (Optional but Recommended)

### Minimal ($5-10)
- White poster board (60cm × 40cm)
- Ruler for spacing

### Better ($20-30)
- White poster board
- LED desk lamp (diffused)
- Transparent sheet for grid

### Best ($50+)
- Light box or photo tent
- LED panel light
- Camera tripod
- Printed grid template

---

## Expected Timeline

| Setup Quality | Time | Detection Rate |
|--------------|------|----------------|
| Quick (paper + room light) | 15 min | 80-90% |
| Good (poster + desk lamp) | 30 min | 90-95% |
| Best (light box + grid) | 1 hour | 95-100% |

---

## Next Steps After Good Detection

Once you achieve 95%+ detection:

1. **Capture dataset batches**:
   - 240 beans per capture
   - Auto-crop with OpenCV
   - Save to organized folders

2. **Dataset targets**:
   - Good curve: 1,050 images
   - Good back: 450 images
   - Bad curve: 1,050 images
   - Bad back: 450 images
   - **Total: 3,000 images**

3. **Batches needed**:
   - ~5 captures for good curve
   - ~2 captures for good back
   - ~5 captures for bad curve
   - ~2 captures for bad back
   - **Total: ~14 captures**

---

## Key Takeaway

**Physical setup matters MORE than software tuning!**

Priority order:
1. White background (most important)
2. Even lighting (very important)
3. Bean spacing (very important)
4. Software parameters (fine-tuning)

Start with physical setup, then adjust software if needed.
