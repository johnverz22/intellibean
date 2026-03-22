# Physical Setup Checklist for Coffee Bean Detection

Print this page and check off each item as you complete it.

---

## 🎯 Goal
Achieve 95%+ detection rate (228-240 beans detected from 240 beans)

---

## ✅ Pre-Capture Checklist

### 1. Background Setup
- [ ] White background material obtained (poster board, cardboard, or paper)
- [ ] Background is MATTE finish (not glossy)
- [ ] Background is CLEAN (no stains, dust, or patterns)
- [ ] Background covers entire camera view area (minimum 40cm × 40cm)
- [ ] Background is FLAT (no wrinkles or curves)

**Test**: Take photo of empty background - should be uniformly white

---

### 2. Lighting Setup
- [ ] Light source positioned above or at 45° angle
- [ ] Light is DIFFUSED (not direct/harsh)
- [ ] NO shadows visible on background
- [ ] NO reflections or glare on background
- [ ] Lighting is EVEN across entire area
- [ ] Brightness level: 500-1000 lux (use phone light meter app)

**Lighting Options** (choose one):
- [ ] LED desk lamp with diffuser (30-40cm above)
- [ ] Window light with white paper diffuser
- [ ] Multiple room lights (all on)
- [ ] Light box or photo tent

**Test**: Take photo of empty background - should have no shadows or bright spots

---

### 3. Camera Setup
- [ ] Camera mounted DIRECTLY ABOVE beans (90° angle)
- [ ] Camera height: 30-50cm above surface
- [ ] Camera is STABLE (tripod, mount, or fixed position)
- [ ] Camera focused on CENTER of bean area
- [ ] Entire bean area fits in frame with small margin
- [ ] Camera settings optimized (see remote_dataset_collector.py)

**Test**: Take test photo - should be sharp and well-framed

---

### 4. Bean Arrangement
- [ ] Beans spaced 5-10mm apart (use ruler to check)
- [ ] NO beans touching each other
- [ ] Beans placed FLAT (not on edge or tilted)
- [ ] Beans in consistent orientation (all curve side up OR all back side up)
- [ ] Grid pattern used (16 columns × 15 rows = 240 beans)
- [ ] Beans evenly distributed across area

**Grid Template** (optional but recommended):
- [ ] Grid template printed or drawn (2.5cm × 2.5cm cells)
- [ ] Transparent sheet placed over grid (for easy cleanup)

**Test**: Count beans manually - should be exactly 240

---

### 5. Environment
- [ ] Room is well-lit
- [ ] No direct sunlight on setup
- [ ] No moving shadows (from people, fans, etc.)
- [ ] Stable surface (no vibrations)
- [ ] Raspberry Pi powered on and connected

---

## 🧪 Testing Procedure

### Phase 1: 10-Bean Test (5 minutes)
- [ ] Arrange 10 beans with proper spacing
- [ ] Capture test image
- [ ] Run detection: `python crop_beans_tunable.py test_10beans.jpg`
- [ ] Result: 9-10 beans detected (90-100%)

**If less than 8 detected, check**:
- [ ] Background white enough?
- [ ] Lighting even?
- [ ] Beans spaced apart?
- [ ] Camera focused?

---

### Phase 2: 50-Bean Test (10 minutes)
- [ ] Arrange 50 beans in grid pattern
- [ ] Capture test image
- [ ] Run detection: `python crop_beans_tunable.py test_50beans.jpg`
- [ ] Result: 48-50 beans detected (96-100%)

**If less than 45 detected, adjust**:
- [ ] Improve lighting
- [ ] Increase bean spacing
- [ ] Try different background
- [ ] Adjust software parameters

---

### Phase 3: Full 240-Bean Test (15 minutes)
- [ ] Arrange all 240 beans in 16×15 grid
- [ ] Double-check spacing and alignment
- [ ] Capture test image
- [ ] Run detection: `python crop_beans_tunable.py test_240beans.jpg`
- [ ] Result: 228-240 beans detected (95-100%)

**If less than 220 detected**:
- [ ] Review all checklist items above
- [ ] Run parameter test: `python test_detection_params.py test_240beans.jpg`
- [ ] Adjust based on recommendations

---

## 📊 Parameter Tuning (if needed)

If physical setup is perfect but detection still low:

### Try These Commands:
```bash
# More sensitive (detect smaller beans)
python crop_beans_tunable.py image.jpg --min-area 150 --max-area 6000

# Less sensitive (reduce false positives)
python crop_beans_tunable.py image.jpg --min-area 300 --max-area 4000

# Adaptive threshold (better for uneven lighting)
python crop_beans_tunable.py image.jpg --threshold adaptive

# Separate touching beans
python crop_beans_tunable.py image.jpg --separate-touching

# Test all combinations
python test_detection_params.py image.jpg
```

---

## 🎯 Success Criteria

### Excellent (Ready for dataset collection)
- ✅ 228-240 beans detected (95-100%)
- ✅ All beans clearly visible in visualization
- ✅ Clean crop boundaries
- ✅ No merged or fragmented beans
- ✅ Consistent detection across entire image

### Good (Minor adjustments needed)
- ✅ 216-240 beans detected (90-100%)
- ⚠ Some beans missed in corners
- ⚠ Occasional merged beans

### Needs Improvement
- ❌ Less than 216 beans detected (<90%)
- ❌ Many beans missed
- ❌ Many false positives
- ❌ Uneven detection across image

---

## 🛒 Recommended Materials

### Essential (Must Have)
- White poster board or cardboard (60cm × 40cm) - $2-5
- Ruler or measuring tape - $1-2

### Recommended (Better Results)
- LED desk lamp with adjustable brightness - $15-25
- White paper for light diffusion - $2-3
- Transparent acrylic sheet (for grid overlay) - $5-10

### Optional (Best Results)
- Light box or photo tent - $30-50
- Camera tripod or adjustable arm - $15-30
- Printed grid template - $1-2
- Light meter app (free on phone)

---

## 📝 Notes Section

Use this space to record your setup details:

**Background material used**: _________________________________

**Light source**: _________________________________

**Camera height**: _________________________________

**Best parameter settings found**:
- min_area: _________
- max_area: _________
- threshold: _________
- Other: _________________________________

**Detection rate achieved**: _________ beans (_______ %)

**Date setup completed**: _________________________________

---

## 🚀 Next Steps After Success

Once you achieve 95%+ detection:

1. **Start dataset collection**
   - Use remote_dataset_collector.py GUI
   - Capture 240 beans per batch
   - Auto-crop with OpenCV

2. **Dataset targets**
   - Good curve: 1,050 images (5 batches)
   - Good back: 450 images (2 batches)
   - Bad curve: 1,050 images (5 batches)
   - Bad back: 450 images (2 batches)
   - **Total: 3,000 images in ~14 batches**

3. **Maintain consistency**
   - Keep same setup for all captures
   - Same lighting, background, spacing
   - Same camera settings
   - Same bean orientation per category

---

**Remember**: Physical setup is MORE important than software tuning!

Priority: Background > Lighting > Spacing > Software Parameters
