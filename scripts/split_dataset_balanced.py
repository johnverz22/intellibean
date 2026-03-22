#!/usr/bin/env python3
"""
Balanced Dataset Splitter
Splits cropped images into train/val/test with equal class sizes
Uses the minimum count between classes to ensure balance
"""

import os
import shutil
import argparse
import random
from pathlib import Path


def split_dataset_balanced(good_dir, bad_dir, output_dir, train_ratio=0.7, val_ratio=0.15, seed=42):
    """Split dataset into balanced train, validation, and test sets"""
    
    random.seed(seed)
    
    test_ratio = 1.0 - train_ratio - val_ratio
    
    if test_ratio < 0:
        print("Error: train_ratio + val_ratio must be <= 1.0")
        return
    
    good_path = Path(good_dir)
    bad_path = Path(bad_dir)
    output_path = Path(output_dir)
    
    # Verify input directories
    if not good_path.exists():
        print(f"Error: Good beans directory not found: {good_dir}")
        return
    
    if not bad_path.exists():
        print(f"Error: Bad beans directory not found: {bad_dir}")
        return
    
    print("="*70)
    print("Balanced Dataset Splitter")
    print("="*70)
    print(f"Good beans source: {good_dir}")
    print(f"Bad beans source: {bad_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Split ratio: {train_ratio:.0%} train, {val_ratio:.0%} val, {test_ratio:.0%} test")
    print(f"Random seed: {seed}")
    print("-"*70)
    
    # Get image files
    image_extensions = {'.jpg', '.jpeg', '.png'}
    
    good_images = [f for f in good_path.iterdir() 
                   if f.suffix.lower() in image_extensions]
    bad_images = [f for f in bad_path.iterdir() 
                  if f.suffix.lower() in image_extensions]
    
    print(f"\nFound images:")
    print(f"  Good beans: {len(good_images)}")
    print(f"  Bad beans: {len(bad_images)}")
    
    if len(good_images) == 0 or len(bad_images) == 0:
        print("\nError: Need images in both directories")
        return
    
    # Balance classes - use minimum count
    min_count = min(len(good_images), len(bad_images))
    
    print(f"\nBalancing classes:")
    print(f"  Using {min_count} images per class (balanced)")
    
    if len(good_images) > min_count:
        print(f"  Excluding {len(good_images) - min_count} good bean images")
    if len(bad_images) > min_count:
        print(f"  Excluding {len(bad_images) - min_count} bad bean images")
    
    # Shuffle and select
    random.shuffle(good_images)
    random.shuffle(bad_images)
    
    good_images = good_images[:min_count]
    bad_images = bad_images[:min_count]
    
    # Create output structure
    train_good = output_path / "train" / "good"
    train_bad = output_path / "train" / "bad"
    val_good = output_path / "val" / "good"
    val_bad = output_path / "val" / "bad"
    test_good = output_path / "test" / "good"
    test_bad = output_path / "test" / "bad"
    
    for dir_path in [train_good, train_bad, val_good, val_bad, test_good, test_bad]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Calculate split points
    train_end = int(min_count * train_ratio)
    val_end = int(min_count * (train_ratio + val_ratio))
    
    # Split good beans
    good_train = good_images[:train_end]
    good_val = good_images[train_end:val_end]
    good_test = good_images[val_end:]
    
    # Split bad beans
    bad_train = bad_images[:train_end]
    bad_val = bad_images[train_end:val_end]
    bad_test = bad_images[val_end:]
    
    print(f"\nBalanced split breakdown:")
    print(f"  Train: {len(good_train)} good + {len(bad_train)} bad = {len(good_train) + len(bad_train)} total")
    print(f"  Val:   {len(good_val)} good + {len(bad_val)} bad = {len(good_val) + len(bad_val)} total")
    print(f"  Test:  {len(good_test)} good + {len(bad_test)} bad = {len(good_test) + len(bad_test)} total")
    print(f"  Total: {min_count * 2} images ({min_count} per class)")
    
    # Copy files
    print(f"\nCopying files...")
    
    # Copy good train
    for img in good_train:
        shutil.copy2(img, train_good / img.name)
    print(f"  ✓ Copied {len(good_train)} good beans to train/")
    
    # Copy good val
    for img in good_val:
        shutil.copy2(img, val_good / img.name)
    print(f"  ✓ Copied {len(good_val)} good beans to val/")
    
    # Copy good test
    for img in good_test:
        shutil.copy2(img, test_good / img.name)
    print(f"  ✓ Copied {len(good_test)} good beans to test/")
    
    # Copy bad train
    for img in bad_train:
        shutil.copy2(img, train_bad / img.name)
    print(f"  ✓ Copied {len(bad_train)} bad beans to train/")
    
    # Copy bad val
    for img in bad_val:
        shutil.copy2(img, val_bad / img.name)
    print(f"  ✓ Copied {len(bad_val)} bad beans to val/")
    
    # Copy bad test
    for img in bad_test:
        shutil.copy2(img, test_bad / img.name)
    print(f"  ✓ Copied {len(bad_test)} bad beans to test/")
    
    print("\n" + "="*70)
    print("BALANCED SPLIT COMPLETE")
    print("="*70)
    print(f"Dataset ready at: {output_dir}")
    print(f"\nDirectory structure:")
    print(f"  {output_dir}/train/good/ ({len(good_train)} images)")
    print(f"  {output_dir}/train/bad/ ({len(bad_train)} images)")
    print(f"  {output_dir}/val/good/ ({len(good_val)} images)")
    print(f"  {output_dir}/val/bad/ ({len(bad_val)} images)")
    print(f"  {output_dir}/test/good/ ({len(good_test)} images)")
    print(f"  {output_dir}/test/bad/ ({len(bad_test)} images)")
    print(f"\nClass balance: Perfect 1:1 ratio ({min_count} per class)")
    print("\nNext steps:")
    print(f"  1. Verify: python scripts/verify_dataset.py {output_dir}")
    print(f"  2. Train: python scripts/train_mobilenet.py {output_dir}/train {output_dir}/val")
    print(f"  3. Test: python scripts/test_model.py {output_dir}/test ./models/best_model.h5")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description='Split cropped beans into balanced train/val/test datasets'
    )
    parser.add_argument('good_dir', help='Directory with good bean images')
    parser.add_argument('bad_dir', help='Directory with bad bean images')
    parser.add_argument('output_dir', help='Output directory for split dataset')
    parser.add_argument('--train', type=float, default=0.7, 
                       help='Train split ratio (default: 0.7 = 70%%)')
    parser.add_argument('--val', type=float, default=0.15,
                       help='Validation split ratio (default: 0.15 = 15%%)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility (default: 42)')
    
    args = parser.parse_args()
    
    test_ratio = 1.0 - args.train - args.val
    
    if test_ratio < 0:
        print("Error: --train + --val must be <= 1.0")
        return
    
    if test_ratio < 0.1:
        print(f"Warning: Test set will be very small ({test_ratio:.0%})")
        print("Recommended: --train 0.7 --val 0.15 (leaves 15% for test)")
    
    split_dataset_balanced(args.good_dir, args.bad_dir, args.output_dir, 
                          args.train, args.val, args.seed)


if __name__ == "__main__":
    main()
