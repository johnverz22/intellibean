#!/usr/bin/env python3
"""
Coffee Bean Cropper with Fixed Size Output
Crops beans and resizes to consistent dimensions for ML training
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path

def crop_beans_fixed_size(image_path, output_dir, target_size=224, 
                          min_area=100, max_area=50000, 
                          padding=10, maintain_aspect=True):
    """
    Crop beans and resize to fixed dimensions
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save cropped beans
        target_size: Target size (width and height) in pixels
        min_area: Minimum contour area
        max_area: Maximum contour area
        padding: Padding around bean in pixels
        maintain_aspect: If True, pad to square; if False, stretch
    
    Returns:
        Number of beans cropped
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return 0
    
    print(f"Processing: {image_path}")
    print(f"Image size: {img.shape[1]}x{img.shape[0]} pixels")
    print(f"Target size: {target_size}x{target_size} pixels")
    print(f"Maintain aspect ratio: {maintain_aspect}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"Found {len(contours)} contours")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename
    base_name = Path(image_path).stem
    
    # Process each contour
    bean_count = 0
    valid_beans = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area
        if min_area < area < max_area:
            valid_beans.append(contour)
    
    print(f"Valid beans: {len(valid_beans)}")
    
    # Crop and resize beans
    for i, contour in enumerate(valid_beans):
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add padding
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(img.shape[1] - x, w + 2 * padding)
        h = min(img.shape[0] - y, h + 2 * padding)
        
        # Crop bean
        bean_img = img[y:y+h, x:x+w]
        
        # Resize to fixed size
        if maintain_aspect:
            # Maintain aspect ratio by padding
            resized_bean = resize_with_padding(bean_img, target_size)
        else:
            # Stretch to fit
            resized_bean = cv2.resize(bean_img, (target_size, target_size))
        
        # Save
        bean_count += 1
        output_path = os.path.join(output_dir, f"{base_name}_bean{bean_count:03d}.jpg")
        cv2.imwrite(output_path, resized_bean)
    
    print(f"✓ Cropped and resized {bean_count} beans to {target_size}x{target_size}")
    
    # Create visualization
    vis_img = img.copy()
    for contour in valid_beans:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    vis_path = os.path.join(output_dir, f"{base_name}_detection.jpg")
    cv2.imwrite(vis_path, vis_img)
    print(f"✓ Visualization saved: {vis_path}")
    
    return bean_count


def resize_with_padding(img, target_size):
    """
    Resize image to target size while maintaining aspect ratio
    Adds padding to make it square
    """
    h, w = img.shape[:2]
    
    # Calculate scaling factor
    scale = target_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Resize
    resized = cv2.resize(img, (new_w, new_h))
    
    # Create square canvas with padding
    canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
    canvas.fill(255)  # White background
    
    # Calculate position to center the image
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    
    # Place resized image on canvas
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas


def main():
    parser = argparse.ArgumentParser(description='Crop beans with fixed size output')
    parser.add_argument('image', help='Input image path')
    parser.add_argument('--output', '-o', default='./cropped_beans_fixed', 
                       help='Output directory')
    parser.add_argument('--size', '-s', type=int, default=224,
                       help='Target size (width and height) in pixels (default: 224)')
    parser.add_argument('--min-area', type=int, default=100,
                       help='Minimum bean area (default: 100)')
    parser.add_argument('--max-area', type=int, default=50000,
                       help='Maximum bean area (default: 50000)')
    parser.add_argument('--padding', type=int, default=10,
                       help='Padding around bean (default: 10)')
    parser.add_argument('--stretch', action='store_true',
                       help='Stretch to fit instead of padding (not recommended)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Coffee Bean Cropper - Fixed Size Output")
    print("="*70)
    print(f"\nParameters:")
    print(f"  Target size: {args.size}x{args.size} pixels")
    print(f"  Min area: {args.min_area}")
    print(f"  Max area: {args.max_area}")
    print(f"  Padding: {args.padding}")
    print(f"  Maintain aspect: {not args.stretch}")
    print("="*70)
    print()
    
    # Process image
    bean_count = crop_beans_fixed_size(
        args.image,
        args.output,
        target_size=args.size,
        min_area=args.min_area,
        max_area=args.max_area,
        padding=args.padding,
        maintain_aspect=not args.stretch
    )
    
    print()
    print("="*70)
    print(f"✓ Complete! {bean_count} beans saved to {args.output}")
    print("="*70)
    
    # Show size recommendations
    print("\nRecommended sizes for ML:")
    print("  224x224 - Best for transfer learning (MobileNet, ResNet)")
    print("  128x128 - Good balance of speed and quality")
    print("  96x96   - Faster training, smaller model")
    print("  64x64   - Very fast, may lose detail")


if __name__ == "__main__":
    main()
