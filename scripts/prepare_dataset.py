#!/usr/bin/env python3
"""
Prepare fresh dataset for training.
- Merges cropped_images/bad + cropped_images/bad/curve into one bad pool
- Balances good vs bad (uses min count of both)
- Splits 70% train / 15% val / 15% test
- Wipes and rebuilds dataset/ folder cleanly
"""

import os
import shutil
import random
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE          = Path(__file__).resolve().parent.parent
GOOD_DIR      = BASE / "cropped_images" / "good"
GOOD_CURVE    = BASE / "cropped_images" / "good" / "curve"
BAD_DIR       = BASE / "cropped_images" / "bad"
BAD_CURVE     = BASE / "cropped_images" / "bad" / "curve"
DATASET_OUT   = BASE / "dataset"

TRAIN_RATIO   = 0.70
VAL_RATIO     = 0.15
# test = remaining 15%
CAP_PER_CLASS = 1500   # target dataset size per class

SEED = 42
random.seed(SEED)

# ── Collect images ─────────────────────────────────────────────────────────────
exts = {'.jpg', '.jpeg', '.png'}

# Good: root + curve subfolder
good_root_imgs  = sorted([f for f in GOOD_DIR.iterdir()
                           if f.suffix.lower() in exts and f.is_file()])
good_curve_imgs = sorted([f for f in GOOD_CURVE.iterdir()
                           if f.suffix.lower() in exts and f.is_file()])
good_imgs = good_root_imgs + good_curve_imgs

# Bad: root + curve subfolder
bad_root_imgs  = sorted([f for f in BAD_DIR.iterdir()
                          if f.suffix.lower() in exts and f.is_file()])
bad_curve_imgs = sorted([f for f in BAD_CURVE.iterdir()
                          if f.suffix.lower() in exts and f.is_file()])
bad_imgs = bad_root_imgs + bad_curve_imgs

print(f"Good pool (root):  {len(good_root_imgs)}")
print(f"Good pool (curve): {len(good_curve_imgs)}")
print(f"Good pool TOTAL:   {len(good_imgs)}")
print(f"Bad pool (root):   {len(bad_root_imgs)}")
print(f"Bad pool (curve):  {len(bad_curve_imgs)}")
print(f"Bad pool TOTAL:    {len(bad_imgs)}")

# ── Balance ────────────────────────────────────────────────────────────────────
cap = min(len(good_imgs), len(bad_imgs), CAP_PER_CLASS)
print(f"\nCapping at {cap} per class (target={CAP_PER_CLASS})")

random.shuffle(good_imgs)
random.shuffle(bad_imgs)

good_imgs = good_imgs[:cap]
bad_imgs  = bad_imgs[:cap]

# ── Split ──────────────────────────────────────────────────────────────────────
train_end = int(cap * TRAIN_RATIO)
val_end   = int(cap * (TRAIN_RATIO + VAL_RATIO))

splits = {
    "train": {"good": good_imgs[:train_end],   "bad": bad_imgs[:train_end]},
    "val":   {"good": good_imgs[train_end:val_end], "bad": bad_imgs[train_end:val_end]},
    "test":  {"good": good_imgs[val_end:],      "bad": bad_imgs[val_end:]},
}

print(f"\nSplit breakdown:")
for split, classes in splits.items():
    g = len(classes['good'])
    b = len(classes['bad'])
    print(f"  {split:5s}: {g} good + {b} bad = {g+b} total")

# ── Wipe old dataset and rebuild ───────────────────────────────────────────────
if DATASET_OUT.exists():
    print(f"\nRemoving old dataset at {DATASET_OUT} ...")
    shutil.rmtree(DATASET_OUT)

print("Building new dataset...")
for split, classes in splits.items():
    for cls, files in classes.items():
        dest = DATASET_OUT / split / cls
        dest.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(f, dest / f.name)
        print(f"  {split}/{cls}: {len(files)} images copied")

print("\n✓ Dataset ready at:", DATASET_OUT)
print(f"  Total images: {cap * 2} ({cap} per class)")
print(f"  Good: {len(good_imgs)} available, using {cap}")
print(f"  Bad:  {len(bad_imgs)} available, using {cap}")
print("\nNext step — run training:")
print("  py -3.12 scripts/train_mobilenet.py")
