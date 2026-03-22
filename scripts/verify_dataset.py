#!/usr/bin/env python3
"""
Dataset Verification Tool
Checks dataset structure and quality before training
"""

import os
import argparse
from pathlib import Path
from PIL import Image


def verify_dataset(dataset_dir):
    """Verify dataset structure and contents"""
    
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        print(f"Error: Dataset directory not found: {dataset_dir}")
        return False
    
    print("="*70)
    print("DATASET VERIFICATION")
    print("="*70)
    print(f"Dataset directory: {dataset_dir}")
    print()
    
    # Check structure
    required_dirs = [
        "train/good",
        "train/bad",
        "val/good",
        "val/bad",
        "test/good",
        "test/bad"
    ]
    
    print("-"*70)
    print("DIRECTORY STRUCTURE")
    print("-"*70)
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = dataset_path / dir_name
        exists = dir_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_name}/")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n✗ Error: Missing required directories")
        print("Expected structure:")
        print("  dataset/")
        print("    train/")
        print("      good/")
        print("      bad/")
        print("    val/")
        print("      good/")
        print("      bad/")
        print("    test/")
        print("      good/")
        print("      bad/")
        return False
    
    print()
    
    # Count images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    
    counts = {}
    for dir_name in required_dirs:
        dir_path = dataset_path / dir_name
        images = [f for f in dir_path.iterdir() 
                 if f.suffix.lower() in image_extensions]
        counts[dir_name] = len(images)
    
    print("-"*70)
    print("IMAGE COUNTS")
    print("-"*70)
    print(f"Training:")
    print(f"  Good beans: {counts['train/good']}")
    print(f"  Bad beans: {counts['train/bad']}")
    print(f"  Total: {counts['train/good'] + counts['train/bad']}")
    print()
    print(f"Validation:")
    print(f"  Good beans: {counts['val/good']}")
    print(f"  Bad beans: {counts['val/bad']}")
    print(f"  Total: {counts['val/good'] + counts['val/bad']}")
    print()
    print(f"Test:")
    print(f"  Good beans: {counts['test/good']}")
    print(f"  Bad beans: {counts['test/bad']}")
    print(f"  Total: {counts['test/good'] + counts['test/bad']}")
    print()
    print(f"Grand Total: {sum(counts.values())} images")
    print()
    
    # Check for issues
    issues = []
    warnings = []
    
    # Check minimum counts
    if counts['train/good'] < 100 or counts['train/bad'] < 100:
        issues.append("Training set too small (need 100+ per class)")
    elif counts['train/good'] < 500 or counts['train/bad'] < 500:
        warnings.append("Training set small (500+ per class recommended)")
    
    if counts['val/good'] < 20 or counts['val/bad'] < 20:
        issues.append("Validation set too small (need 20+ per class)")
    elif counts['val/good'] < 100 or counts['val/bad'] < 100:
        warnings.append("Validation set small (100+ per class recommended)")
    
    if counts['test/good'] < 20 or counts['test/bad'] < 20:
        issues.append("Test set too small (need 20+ per class)")
    elif counts['test/good'] < 100 or counts['test/bad'] < 100:
        warnings.append("Test set small (100+ per class recommended)")
    
    # Check class balance
    train_ratio = counts['train/good'] / counts['train/bad'] if counts['train/bad'] > 0 else 0
    val_ratio = counts['val/good'] / counts['val/bad'] if counts['val/bad'] > 0 else 0
    test_ratio = counts['test/good'] / counts['test/bad'] if counts['test/bad'] > 0 else 0
    
    if train_ratio < 0.5 or train_ratio > 2.0:
        warnings.append(f"Training classes imbalanced (ratio: {train_ratio:.2f})")
    
    if val_ratio < 0.5 or val_ratio > 2.0:
        warnings.append(f"Validation classes imbalanced (ratio: {val_ratio:.2f})")
    
    if test_ratio < 0.5 or test_ratio > 2.0:
        warnings.append(f"Test classes imbalanced (ratio: {test_ratio:.2f})")
    
    # Check image sizes
    print("-"*70)
    print("IMAGE VERIFICATION")
    print("-"*70)
    
    sample_sizes = set()
    corrupted = []
    
    for dir_name in required_dirs:
        dir_path = dataset_path / dir_name
        images = [f for f in dir_path.iterdir() 
                 if f.suffix.lower() in image_extensions]
        
        # Check first 5 images from each directory
        for img_file in images[:5]:
            try:
                with Image.open(img_file) as img:
                    sample_sizes.add(img.size)
            except Exception as e:
                corrupted.append(str(img_file))
    
    if corrupted:
        issues.append(f"Found {len(corrupted)} corrupted images")
        print(f"✗ Corrupted images found: {len(corrupted)}")
        for img in corrupted[:5]:
            print(f"    {img}")
        if len(corrupted) > 5:
            print(f"    ... and {len(corrupted)-5} more")
    else:
        print("✓ No corrupted images detected")
    
    print(f"✓ Image sizes found: {sample_sizes}")
    
    if len(sample_sizes) > 1:
        warnings.append("Multiple image sizes detected (should be uniform)")
    
    # Check for 224x224
    if (224, 224) not in sample_sizes:
        warnings.append("Images not 224x224 (recommended for MobileNetV2)")
    
    print()
    
    # Summary
    print("-"*70)
    print("VERIFICATION SUMMARY")
    print("-"*70)
    
    if issues:
        print("✗ ISSUES FOUND:")
        for issue in issues:
            print(f"  • {issue}")
        print()
    
    if warnings:
        print("⚠ WARNINGS:")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    if not issues and not warnings:
        print("✓ Dataset looks good!")
        print()
    
    # Recommendations
    print("-"*70)
    print("RECOMMENDATIONS")
    print("-"*70)
    
    if counts['train/good'] + counts['train/bad'] < 1000:
        print("  • Collect more training data (1000+ images recommended)")
    
    if counts['val/good'] + counts['val/bad'] < 200:
        print("  • Add more validation data (200+ images recommended)")
    
    if train_ratio < 0.8 or train_ratio > 1.2:
        print("  • Balance training classes (aim for 1:1 ratio)")
    
    if (224, 224) not in sample_sizes:
        print("  • Resize images to 224x224 for optimal training")
    
    if not issues and not warnings:
        print("  ✓ Ready for training!")
        print(f"  Run: python scripts/train_mobilenet.py {dataset_dir}/train {dataset_dir}/val")
    
    print()
    print("="*70)
    
    return len(issues) == 0


def main():
    parser = argparse.ArgumentParser(
        description='Verify dataset structure and quality'
    )
    parser.add_argument('dataset_dir', help='Dataset directory to verify')
    
    args = parser.parse_args()
    
    success = verify_dataset(args.dataset_dir)
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
