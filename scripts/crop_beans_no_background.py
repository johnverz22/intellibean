#!/usr/bin/env python3
"""
Coffee Bean Cropper with Background Removal
Crops beans, removes background, and resizes to consistent dimensions
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path

def remove_background(img, mask):
    """
    Remove background using mask
    Returns image with white background
    """
    # Create white background
    result = np.ones_like(img) * 255
    
    # Apply mask
    result[mask > 0] = img[mask > 0]
    
    return result


def crop_beans_no_background(image_path, output_dir, target_size=224, 
                             min_area=100, max_area=50000, 
                             padding=10, background_color='white'):
    """
    Crop beans with background removal
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save cropped beans
        target_size: Target size (width and height) in pixels
        min_area: Minimum contour area
        max_area: Maximum contour area
        padding: Padding around bean in pixels
        background_color: 'white' or 'transparent'
    
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
    print(f"Background: {background_color}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold to create mask
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
    
    # Crop and process beans
    for i, contour in enumerate(valid_beans):
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add padding
        x_pad = max(0, x - padding)
        y_pad = max(0, y - padding)
        w_pad = min(img.shape[1] - x_pad, w + 2 * padding)
        h_pad = min(img.shape[0] - y_pad, h + 2 * padding)
        
        # Crop bean and mask
        bean_img = img[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad].copy()
        bean_mask = thresh[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad].copy()
        
        # Remove background
        bean_no_bg = remove_background(bean_img, bean_mask)
        
        # Resize to fixed size with padding
        resized_bean = resize_with_padding(bean_no_bg, target_size, background_color)
        
        # Save
        bean_count += 1
        output_path = os.path.join(output_dir, f"{base_name}_bean{bean_count:03d}.jpg")
        cv2.imwrite(output_path, resized_bean)
    
    print(f"✓ Cropped {bean_count} beans (background removed) to {target_size}x{target_size}")
    
    # Create visualization
    vis_img = img.copy()
    for contour in valid_beans:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(vis_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    vis_path = os.path.join(output_dir, f"{base_name}_detection.jpg")
    cv2.imwrite(vis_path, vis_img)
    print(f"✓ Visualization saved: {vis_path}")
    
    return bean_count


def resize_with_padding(img, target_size, background_color='white'):
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
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create square canvas
    if background_color == 'white':
        canvas = np.ones((target_size, target_size, 3), dtype=np.uint8) * 255
    else:  # black or other
        canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
    
    # Calculate position to center the image
    x_offset = (target_size - new_w) // 2
    y_offset = (target_size - new_h) // 2
    
    # Place resized image on canvas
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    return canvas


def main():
    parser = argparse.ArgumentParser(description='Crop beans with background removal')
    parser.add_argument('image', help='Input image path')
    parser.add_argument('--output', '-o', default='./cropped_beans_no_bg', 
                       help='Output directory')
    parser.add_argument('--size', '-s', type=int, default=224,
                       help='Target size (width and height) in pixels (default: 224)')
    parser.add_argument('--min-area', type=int, default=100,
                       help='Minimum bean area (default: 100)')
    parser.add_argument('--max-area', type=int, default=50000,
                       help='Maximum bean area (default: 50000)')
    parser.add_argument('--padding', type=int, default=10,
                       help='Padding around bean (default: 10)')
    parser.add_argument('--bg-color', choices=['white', 'black'], default='white',
                       help='Background color (default: white)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("Coffee Bean Cropper - Background Removal")
    print("="*70)
    print(f"\nParameters:")
    print(f"  Target size: {args.size}x{args.size} pixels")
    print(f"  Min area: {args.min_area}")
    print(f"  Max area: {args.max_area}")
    print(f"  Padding: {args.padding}")
    print(f"  Background: {args.bg_color}")
    print("="*70)
    print()
    
    # Process image
    bean_count = crop_beans_no_background(
        args.image,
        args.output,
        target_size=args.size,
        min_area=args.min_area,
        max_area=args.max_area,
        padding=args.padding,
        background_color=args.bg_color
    )
    
    print()
    print("="*70)
    print(f"✓ Complete! {bean_count} beans saved to {args.output}")
    print("="*70)
    
    print("\nBenefits of background removal:")
    print("  ✓ Model focuses on bean features only")
    print("  ✓ Better generalization to different backgrounds")
    print("  ✓ Cleaner, more professional dataset")
    print("  ✓ Reduces background noise in training")


if __name__ == "__main__":
    main()
