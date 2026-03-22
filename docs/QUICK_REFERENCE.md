# Quick Reference Card - Detection Optimization

## 🎯 Goal
Improve detection from 51.7% (124 beans) to 95%+ (228-240 beans)

---

## 📖 Documentation (Read First)

| File | Purpose | Time |
|------|---------|------|
| **IMPROVE_DETECTION.md** | Start here! | 5 min |
| **docs/QUICK_FIX_GUIDE.md** | 30-min action plan | 10 min |
| **docs/PHYSICAL_SETUP_CHECKLIST.md** | Printable checklist | 5 min |

---

## ⚡ Quick Commands

```bash
# Test current setup
python crop_beans.py temp_captures/sampletopcv.jpg

# Tune parameters
python crop_beans_tunable.py image.jpg --min-area 200 --max-area 5000

# Find best parameters automatically
python test_detection_params.py image.jpg

# Start dataset collection
python remote_dataset_collector.py
```

---

## 🔧 The 3 Most Important Fixes

### 1. WHITE BACKGROUND ⭐⭐⭐⭐⭐
```
Impact: +30% detection
Cost: $2-5
Time: 5 minutes
Action: Get white poster board (matte finish)
```

### 2. EVEN LIGHTING ⭐⭐⭐⭐
```
Impact: +20% detection
Cost: $0-30
Time: 10 minutes
Action: Use diffused light, eliminate shadows
```

### 3. BEAN SPACING ⭐⭐⭐⭐
```
Impact: +15% detection
Cost: $0
Time: 15 minutes
Action: Space beans 5-10mm apart, use grid
```

---

## 🧪 Testing Workflow

```bash
# 1. Test with 10 beans (5 min)
python crop_beans.py test_10beans.jpg
# Expected: 9-10 detected

# 2. Test with 50 beans (10 min)
python crop_beans.py test_50beans.jpg
# Expected: 48-50 detected

# 3. Test with 240 beans (15 min)
python crop_beans.py test_240beans.jpg
# Expected: 228-240 detected

# 4. Optimize if needed (10 min)
python test_detection_params.py test_240beans.jpg
```

---

## 🐛 Troubleshooting

### Too Few Detections (<200)
```bash
# Check: White background? Even lighting? Beans spaced?
# Try: Lower thresholds
python crop_beans_tunable.py image.jpg --min-area 150
```

### Too Many Detections (>260)
```bash
# Check: Clean background? No shadows?
# Try: Higher thresholds
python crop_beans_tunable.py image.jpg --min-area 300
```

### Beans Merged
```bash
# Check: Beans touching?
# Try: Watershed separation
python crop_beans_tunable.py image.jpg --separate-touching
```

---

## 📊 Parameter Reference

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| min_area | 200 | 100-500 | Lower = detect smaller |
| max_area | 5000 | 3000-10000 | Higher = detect larger |
| threshold | otsu | otsu/adaptive | Adaptive = uneven light |
| morph_close | 2 | 1-5 | Higher = fill gaps |
| morph_open | 1 | 1-3 | Higher = separate |

---

## ✅ Success Checklist

- [ ] White background in place
- [ ] Even lighting (no shadows)
- [ ] Beans spaced 5-10mm apart
- [ ] Camera focused and stable
- [ ] Test 10 beans: 9-10 detected
- [ ] Test 50 beans: 48-50 detected
- [ ] Test 240 beans: 228-240 detected
- [ ] Detection rate: 95-100%
- [ ] Setup is repeatable

---

## 🛒 Shopping List

### Minimal ($5)
- White poster board
- Ruler

### Recommended ($30)
- White poster board
- LED desk lamp
- Transparent sheet
- Grid template

---

## 📈 Expected Results

| Setup | Time | Detection |
|-------|------|-----------|
| Current | 0 min | 51.7% ❌ |
| + Background | 5 min | ~75% ⚠️ |
| + Lighting | 15 min | ~85% ⚠️ |
| + Spacing | 30 min | ~90% ✅ |
| + Tuning | 45 min | ~95% ✅ |

---

## 🚀 Next Steps

1. Read `IMPROVE_DETECTION.md`
2. Setup white background + lighting
3. Test with `crop_beans.py`
4. Iterate until 95%+ detection
5. Start dataset collection

---

## 📞 Need Help?

- Quick fix: `docs/QUICK_FIX_GUIDE.md`
- Setup help: `docs/PHYSICAL_SETUP_CHECKLIST.md`
- Technical: `docs/OPTIMIZE_DETECTION.md`
- Overview: `docs/DETECTION_README.md`

---

**Remember**: Physical setup (background + lighting + spacing) = 90% of solution!
