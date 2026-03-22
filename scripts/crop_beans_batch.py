#!/usr/bin/env python3
"""
Simplified Batch Coffee Bean Cropper
Crops multiple beans from images to 224x224 with aspect ratio preservation
Supports HEIC, JPG, PNG, BMP formats
"""

import cv2
import numpy as np
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Try to import HEIC support
try:
    from pillow_heif import register_heif_opener
    from PIL import Image
    register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False
    print("Warning: pillow-heif not installed. HEIC files will be skipped.")
    print("Install with: pip install pillow-heif")


def detect_beans(img, min_area=100, max_area=50000):
    """Detect individual beans in image"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold to create mask (Otsu's method)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_beans = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Simple area filter - works well for iPhone images
        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(contour)
            valid_beans.append((x, y, w, h))
    
    return valid_beans


def crop_to_224(img, x, y, w, h, padding=20):
    """Crop bean region to 224x224 preserving aspect ratio"""
    # Add padding
    x_pad = max(0, x - padding)
    y_pad = max(0, y - padding)
    w_pad = min(img.shape[1] - x_pad, w + 2 * padding)
    h_pad = min(img.shape[0] - y_pad, h + 2 * padding)
    
    # Crop region
    cropped = img[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
    
    # Resize to 224x224 preserving aspect ratio
    h_crop, w_crop = cropped.shape[:2]
    
    if h_crop == 0 or w_crop == 0:
        return None
    
    # Calculate scaling to fit in 224x224
    scale = min(224 / w_crop, 224 / h_crop)
    new_w = int(w_crop * scale)
    new_h = int(h_crop * scale)
    
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create 224x224 canvas with white background
    canvas = np.ones((224, 224, 3), dtype=np.uint8) * 255
    
    # Center the resized image
    y_offset = (224 - new_h) // 2
    x_offset = (224 - new_w) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas


def load_log(log_file):
    """Load processing log"""
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return json.load(f)
    return {"processed_files": [], "total_beans": 0, "last_index": 0}


def save_log(log_file, log_data):
    """Save processing log"""
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def read_image(file_path):
    """Read image file, handling HEIC format"""
    file_path = str(file_path)
    
    # Try HEIC first if supported
    if file_path.lower().endswith('.heic') and HEIC_SUPPORT:
        try:
            pil_img = Image.open(file_path)
            # Convert to RGB (remove alpha if present)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            # Convert PIL to OpenCV format (BGR)
            img_array = np.array(pil_img)
            img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            return img
        except Exception as e:
            print(f"  [ERROR] Failed to read HEIC: {e}")
            return None
    
    # Standard OpenCV read for other formats
    return cv2.imread(file_path)


def process_directory(input_dir, output_dir):
    """Process all images in directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Log file
    log_file = output_path / "processing_log.json"
    log_data = load_log(log_file)
    
    # Get image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.heic'}
    image_files = [f for f in input_path.iterdir() 
                   if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"No images found in {input_dir}")
        return
    
    # Check for HEIC files without support
    heic_files = [f for f in image_files if f.suffix.lower() == '.heic']
    if heic_files and not HEIC_SUPPORT:
        print(f"\nWarning: Found {len(heic_files)} HEIC files but pillow-heif is not installed")
        print("Install with: pip install pillow-heif")
        print("HEIC files will be skipped.\n")
    
    print(f"Found {len(image_files)} images in {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Starting from index: {log_data['last_index']}")
    print("-" * 60)
    
    current_index = log_data['last_index']
    total_beans_processed = 0
    
    for img_file in sorted(image_files):
        img_name = img_file.name
        
        # Skip if already processed
        if img_name in log_data['processed_files']:
            print(f"[SKIP] {img_name} (already processed)")
            continue
        
        # Skip HEIC if no support
        if img_file.suffix.lower() == '.heic' and not HEIC_SUPPORT:
            print(f"[SKIP] {img_name} (HEIC not supported)")
            continue
        
        print(f"\n[PROCESSING] {img_name}")
        
        # Read image
        img = read_image(img_file)
        if img is None:
            print(f"  [ERROR] Failed to read image")
            continue
        
        print(f"  Image size: {img.shape[1]}x{img.shape[0]}")
        
        # Detect beans
        beans = detect_beans(img)
        print(f"  Detected: {len(beans)} beans")
        
        if len(beans) == 0:
            print(f"  [WARNING] No beans detected")
            log_data['processed_files'].append(img_name)
            continue
        
        # Crop each bean
        beans_saved = 0
        for bean_bbox in beans:
            x, y, w, h = bean_bbox
            
            # Crop to 224x224
            bean_img = crop_to_224(img, x, y, w, h)
            
            if bean_img is not None:
                # Save with incremental naming
                output_filename = f"bean_{current_index:06d}.jpg"
                output_filepath = output_path / output_filename
                cv2.imwrite(str(output_filepath), bean_img, 
                           [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                current_index += 1
                beans_saved += 1
        
        print(f"  Saved: {beans_saved} beans (bean_{current_index-beans_saved:06d} to bean_{current_index-1:06d})")
        
        # Update log
        log_data['processed_files'].append(img_name)
        log_data['total_beans'] += beans_saved
        log_data['last_index'] = current_index
        total_beans_processed += beans_saved
        
        # Save log after each image
        save_log(log_file, log_data)
    
    # Count actual images in output directory
    actual_images = len([f for f in output_path.iterdir() 
                        if f.suffix.lower() in {'.jpg', '.jpeg', '.png'}])
    
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Images processed: {len(log_data['processed_files'])}")
    print(f"Total beans cropped: {log_data['total_beans']}")
    print(f"Beans in this run: {total_beans_processed}")
    print(f"Output directory: {output_dir}")
    print(f"Log file: {log_file}")
    print("-" * 60)
    print("ACTUAL IMAGE COUNT IN FOLDER")
    print("-" * 60)
    print(f"Images in folder: {actual_images}")
    print(f"Expected (from log): {log_data['total_beans']}")
    
    if actual_images < log_data['total_beans']:
        removed = log_data['total_beans'] - actual_images
        print(f"Manually removed: {removed} images ({removed/log_data['total_beans']*100:.1f}%)")
        print(f"Remaining: {actual_images} images")
    elif actual_images > log_data['total_beans']:
        extra = actual_images - log_data['total_beans']
        print(f"Extra images found: {extra} (not in log)")
    else:
        print("✓ Count matches log perfectly")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Batch crop coffee beans to 224x224 from multiple images'
    )
    parser.add_argument('input_dir', help='Input directory containing images')
    parser.add_argument('output_dir', help='Output directory for cropped beans')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    process_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
