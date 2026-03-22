# Detection Optimization Workflow

## Current State → Target State

```
CURRENT STATE (51.7% detection)
┌─────────────────────────────────────┐
│  Brown/Wood Background              │
│  Uneven Lighting (shadows)          │
│  Beans Touching Each Other          │
│  Parameters: min=500, max=10000     │
└─────────────────────────────────────┘
              ↓
    124 beans detected (51.7%)
              ↓
         ❌ NOT READY


TARGET STATE (95%+ detection)
┌─────────────────────────────────────┐
│  WHITE Background (poster board)    │
│  EVEN Lighting (no shadows)         │
│  Beans SPACED 5-10mm apart          │
│  Parameters: min=200, max=5000      │
└─────────────────────────────────────┘
              ↓
    228-240 beans detected (95-100%)
              ↓
         ✅ READY!
```

---

## Step-by-Step Workflow

```
START
  │
  ├─→ 1. READ DOCUMENTATION (5 min)
  │   ├─ IMPROVE_DETECTION.md
  │   └─ docs/QUICK_FIX_GUIDE.md
  │
  ├─→ 2. PHYSICAL SETUP (20 min)
  │   ├─ Get white poster board
  │   ├─ Setup even lighting
  │   └─ Create grid template
  │
  ├─→ 3. TEST WITH 10 BEANS (5 min)
  │   ├─ Arrange 10 beans
  │   ├─ Capture image
  │   ├─ Run: python crop_beans.py image.jpg
  │   └─ Check: 9-10 detected?
  │       ├─ YES → Continue to Step 4
  │       └─ NO → Improve setup, retry
  │
  ├─→ 4. TEST WITH 50 BEANS (10 min)
  │   ├─ Arrange 50 beans in grid
  │   ├─ Capture image
  │   ├─ Run: python crop_beans.py image.jpg
  │   └─ Check: 48-50 detected?
  │       ├─ YES → Continue to Step 5
  │       └─ NO → Adjust setup, retry
  │
  ├─→ 5. TEST WITH 240 BEANS (15 min)
  │   ├─ Arrange all 240 beans
  │   ├─ Capture image
  │   ├─ Run: python crop_beans.py image.jpg
  │   └─ Check: 228-240 detected?
  │       ├─ YES → SUCCESS! Go to Step 7
  │       └─ NO → Continue to Step 6
  │
  ├─→ 6. PARAMETER TUNING (10 min)
  │   ├─ Run: python test_detection_params.py image.jpg
  │   ├─ Review results
  │   ├─ Use best parameters
  │   └─ Retry Step 5
  │
  └─→ 7. START DATASET COLLECTION
      ├─ Run: python remote_dataset_collector.py
      ├─ Capture 240 beans per batch
      ├─ Auto-crop with OpenCV
      └─ Repeat for all categories
```

---

## Decision Tree

```
Is detection rate < 200 beans?
│
├─ YES → Physical Setup Issue
│   │
│   ├─ Is background WHITE?
│   │   ├─ NO → Get white poster board ⭐⭐⭐⭐⭐
│   │   └─ YES → Continue
│   │
│   ├─ Is lighting EVEN (no shadows)?
│   │   ├─ NO → Add/adjust lighting ⭐⭐⭐⭐
│   │   └─ YES → Continue
│   │
│   ├─ Are beans SPACED 5-10mm apart?
│   │   ├─ NO → Increase spacing ⭐⭐⭐⭐
│   │   └─ YES → Continue
│   │
│   └─ Try software tuning:
│       python crop_beans_tunable.py image.jpg --min-area 150
│
└─ NO → Is detection rate > 260 beans?
    │
    ├─ YES → Too Many False Positives
    │   │
    │   ├─ Is background CLEAN (no dust)?
    │   │   ├─ NO → Clean background
    │   │   └─ YES → Continue
    │   │
    │   ├─ Are there SHADOWS?
    │   │   ├─ YES → Improve lighting
    │   │   └─ NO → Continue
    │   │
    │   └─ Try software tuning:
    │       python crop_beans_tunable.py image.jpg --min-area 300
    │
    └─ NO → Detection rate 200-260 beans
        │
        └─ GOOD! Fine-tune to reach 228-240:
            python test_detection_params.py image.jpg
```

---

## Tool Selection Guide

```
Which tool should I use?

┌─────────────────────────────────────────────────────────┐
│ I want to test current setup quickly                    │
│ → python crop_beans.py image.jpg                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ I want to adjust parameters manually                    │
│ → python crop_beans_tunable.py image.jpg \              │
│      --min-area 200 --max-area 5000                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ I want to find best parameters automatically            │
│ → python test_detection_params.py image.jpg             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ I want to capture images from Raspberry Pi              │
│ → python remote_dataset_collector.py                    │
└─────────────────────────────────────────────────────────┘
```

---

## Parameter Impact Visualization

```
min_area (Minimum Bean Size)
─────────────────────────────────────────────────────
100        200        300        400        500
 │          │          │          │          │
 ├──────────┼──────────┼──────────┼──────────┤
 │          │          │          │          │
More       RECOMMENDED  Balanced   Less      Too
Sensitive  (Default)              Sensitive  Strict
│          │          │          │          │
Detects    Good       Filters    Misses     Misses
small      balance    noise      small      many
beans                            beans      beans
│          │          │          │          │
More       Fewer      Fewer      Fewer      Fewer
noise      false      false      false      false
           positives  positives  positives  positives


max_area (Maximum Bean Size)
─────────────────────────────────────────────────────
3000       4000       5000       6000       10000
 │          │          │          │          │
 ├──────────┼──────────┼──────────┼──────────┤
 │          │          │          │          │
Too        Balanced   RECOMMENDED More       Too
Strict                (Default)   Lenient    Lenient
│          │          │          │          │
Misses     Good       Good       Allows     Allows
large      balance    balance    merged     many
beans                            beans      merged
│          │          │          │          │
Fewer      Fewer      Fewer      More       Many
merged     merged     merged     merged     merged
beans      beans      beans      beans      beans
```

---

## Physical Setup Impact

```
BACKGROUND IMPACT (+30% detection)
─────────────────────────────────────────────────────
Brown/Wood          Gray/Cream          White
Background          Background          Background
│                   │                   │
Low Contrast        Medium Contrast     High Contrast
│                   │                   │
Weak Edges          OK Edges            Clear Edges
│                   │                   │
~50% detection      ~70% detection      ~80% detection
❌ NOT READY        ⚠️ NEEDS WORK       ✅ GOOD


LIGHTING IMPACT (+20% detection)
─────────────────────────────────────────────────────
Uneven              Single Light        Even Diffused
Lighting            Source              Lighting
│                   │                   │
Shadows             Some Shadows        No Shadows
│                   │                   │
Variable            Mostly              Consistent
Threshold           Consistent          Threshold
│                   │                   │
~60% detection      ~75% detection      ~90% detection
❌ NOT READY        ⚠️ NEEDS WORK       ✅ GOOD


SPACING IMPACT (+15% detection)
─────────────────────────────────────────────────────
Beans               Beans               Beans
Touching            2-4mm Apart         5-10mm Apart
│                   │                   │
Merged              Some Merged         Separate
Detection           Detection           Detection
│                   │                   │
Single              Occasional          Individual
Objects             Merging             Objects
│                   │                   │
~70% detection      ~85% detection      ~95% detection
❌ NOT READY        ⚠️ NEEDS WORK       ✅ EXCELLENT
```

---

## Success Progression

```
PHASE 1: Current Setup (0 min)
┌────────────────────────────────────┐
│ Brown background                   │
│ Uneven lighting                    │
│ Beans touching                     │
│ Default parameters                 │
└────────────────────────────────────┘
         ↓
   124 beans (51.7%)
         ↓
    ❌ NOT READY


PHASE 2: White Background (5 min)
┌────────────────────────────────────┐
│ ✅ White poster board              │
│ Uneven lighting                    │
│ Beans touching                     │
│ Default parameters                 │
└────────────────────────────────────┘
         ↓
   ~180 beans (75%)
         ↓
    ⚠️ BETTER


PHASE 3: + Even Lighting (15 min)
┌────────────────────────────────────┐
│ ✅ White poster board              │
│ ✅ Even lighting (no shadows)      │
│ Beans touching                     │
│ Default parameters                 │
└────────────────────────────────────┘
         ↓
   ~204 beans (85%)
         ↓
    ⚠️ GOOD


PHASE 4: + Bean Spacing (30 min)
┌────────────────────────────────────┐
│ ✅ White poster board              │
│ ✅ Even lighting (no shadows)      │
│ ✅ Beans spaced 5-10mm             │
│ Default parameters                 │
└────────────────────────────────────┘
         ↓
   ~216 beans (90%)
         ↓
    ✅ READY (but can improve)


PHASE 5: + Parameter Tuning (45 min)
┌────────────────────────────────────┐
│ ✅ White poster board              │
│ ✅ Even lighting (no shadows)      │
│ ✅ Beans spaced 5-10mm             │
│ ✅ Optimized parameters            │
└────────────────────────────────────┘
         ↓
   ~228 beans (95%)
         ↓
    ✅ EXCELLENT!


PHASE 6: + Full Optimization (60 min)
┌────────────────────────────────────┐
│ ✅ White poster board              │
│ ✅ Professional lighting           │
│ ✅ Grid template                   │
│ ✅ Optimized parameters            │
└────────────────────────────────────┘
         ↓
   ~235 beans (98%)
         ↓
    ✅ PERFECT!
```

---

## Dataset Collection Flow

```
PREPARATION
    │
    ├─→ Achieve 95%+ detection rate
    │   (228-240 beans detected)
    │
    └─→ Setup is consistent and repeatable
        │
        ↓
COLLECTION LOOP (14 batches)
    │
    ├─→ Arrange 240 beans in grid
    │   (Same setup every time)
    │
    ├─→ Capture image
    │   python remote_dataset_collector.py
    │
    ├─→ Auto-crop beans
    │   python crop_beans.py image.jpg
    │
    ├─→ Verify results
    │   Check: 228-240 beans detected?
    │   ├─ YES → Save batch, continue
    │   └─ NO → Adjust setup, retry
    │
    └─→ Repeat for all categories:
        ├─ Good curve: 5 batches (1,050 images)
        ├─ Good back: 2 batches (450 images)
        ├─ Bad curve: 5 batches (1,050 images)
        └─ Bad back: 2 batches (450 images)
        │
        ↓
COMPLETION
    │
    └─→ Total: 3,000 images
        Ready for ML training!
```

---

## Quick Reference

```
┌─────────────────────────────────────────────────────────┐
│ MOST IMPORTANT THINGS                                   │
├─────────────────────────────────────────────────────────┤
│ 1. WHITE BACKGROUND ⭐⭐⭐⭐⭐ (+30% detection)          │
│ 2. EVEN LIGHTING ⭐⭐⭐⭐ (+20% detection)               │
│ 3. BEAN SPACING ⭐⭐⭐⭐ (+15% detection)                │
│ 4. SOFTWARE TUNING ⭐⭐ (+5-10% detection)              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ QUICK COMMANDS                                          │
├─────────────────────────────────────────────────────────┤
│ Test current setup:                                     │
│   python crop_beans.py image.jpg                        │
│                                                         │
│ Tune parameters:                                        │
│   python crop_beans_tunable.py image.jpg \              │
│       --min-area 200 --max-area 5000                    │
│                                                         │
│ Find best parameters:                                   │
│   python test_detection_params.py image.jpg             │
│                                                         │
│ Start collection:                                       │
│   python remote_dataset_collector.py                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SUCCESS CRITERIA                                        │
├─────────────────────────────────────────────────────────┤
│ ✅ 228-240 beans detected (95-100%)                     │
│ ✅ Consistent across multiple captures                  │
│ ✅ Clean crop boundaries                                │
│ ✅ No merged or fragmented beans                        │
│ ✅ Processing time <10 seconds                          │
│ ✅ Setup is repeatable                                  │
└─────────────────────────────────────────────────────────┘
```

---

**Remember**: Physical setup is 90% of the solution!

Start with background → lighting → spacing → then tune software.
