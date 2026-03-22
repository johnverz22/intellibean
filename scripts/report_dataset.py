#!/usr/bin/env python3
"""
Dataset Report Tool
Shows actual image counts vs logged counts
Useful after manually removing bad crops
"""

import os
import json
import argparse
from pathlib import Path


def generate_report(directory):
    """Generate report for a cropped dataset directory"""
    
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Error: Directory not found: {directory}")
        return
    
    # Load log file
    log_file = dir_path / "processing_log.json"
    
    if not log_file.exists():
        print(f"Error: No processing log found in {directory}")
        print("This directory was not processed by crop_beans_batch.py")
        return
    
    with open(log_file, 'r') as f:
        log_data = json.load(f)
    
    # Count actual images
    image_extensions = {'.jpg', '.jpeg', '.png'}
    actual_images = [f for f in dir_path.iterdir() 
                     if f.suffix.lower() in image_extensions]
    actual_count = len(actual_images)
    
    # Get file size info
    total_size = sum(f.stat().st_size for f in actual_images)
    avg_size = total_size / actual_count if actual_count > 0 else 0
    
    # Print report
    print("=" * 70)
    print("DATASET REPORT")
    print("=" * 70)
    print(f"Directory: {directory}")
    print(f"Log file: {log_file}")
    print()
    
    print("-" * 70)
    print("PROCESSING HISTORY")
    print("-" * 70)
    print(f"Source images processed: {len(log_data['processed_files'])}")
    print(f"Total beans cropped: {log_data['total_beans']}")
    print(f"Last index used: {log_data['last_index']}")
    print()
    
    print("-" * 70)
    print("CURRENT STATE")
    print("-" * 70)
    print(f"Images in folder: {actual_count}")
    print(f"Expected (from log): {log_data['total_beans']}")
    print()
    
    # Compare counts
    if actual_count < log_data['total_beans']:
        removed = log_data['total_beans'] - actual_count
        removal_rate = (removed / log_data['total_beans']) * 100
        print(f"Status: {removed} images manually removed ({removal_rate:.1f}%)")
        print(f"Remaining: {actual_count} images ({100-removal_rate:.1f}%)")
        print()
        print("Quality Control:")
        if removal_rate < 5:
            print("  ✓ Excellent - Very few bad crops (<5%)")
        elif removal_rate < 10:
            print("  ✓ Good - Acceptable removal rate (<10%)")
        elif removal_rate < 20:
            print("  ⚠ Fair - Consider improving detection (10-20%)")
        else:
            print("  ⚠ High removal rate (>20%) - Check detection settings")
    elif actual_count > log_data['total_beans']:
        extra = actual_count - log_data['total_beans']
        print(f"Status: {extra} extra images found (not in log)")
        print("  ⚠ Warning: Images added manually or log is outdated")
    else:
        print("Status: ✓ Count matches log perfectly")
        print("  No manual removals detected")
    
    print()
    print("-" * 70)
    print("FILE STATISTICS")
    print("-" * 70)
    print(f"Total size: {total_size / (1024*1024):.2f} MB")
    print(f"Average file size: {avg_size / 1024:.2f} KB")
    print(f"Smallest file: {min(f.stat().st_size for f in actual_images) / 1024:.2f} KB")
    print(f"Largest file: {max(f.stat().st_size for f in actual_images) / 1024:.2f} KB")
    print()
    
    print("-" * 70)
    print("SOURCE IMAGES")
    print("-" * 70)
    for i, source_file in enumerate(log_data['processed_files'], 1):
        print(f"  {i}. {source_file}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Dataset ready: {actual_count} images")
    
    if actual_count >= 500:
        print("✓ Sufficient for training (500+ images recommended)")
    elif actual_count >= 200:
        print("⚠ Minimal dataset (200-500 images) - more data recommended")
    else:
        print("✗ Insufficient data (<200 images) - collect more images")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='Generate report for cropped bean dataset'
    )
    parser.add_argument('directory', help='Directory containing cropped beans')
    
    args = parser.parse_args()
    generate_report(args.directory)


if __name__ == "__main__":
    main()
