#!/usr/bin/env python3
"""
Crop individual coffee beans from a single image using OpenCV
"""

import cv2
import numpy as np
import os
import sys

def crop_beans(image_path, output_dir="cropped_beans"):
    """
    Detect and crop individual coffee beans from image
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save cropped beans
    
    Returns:
        Number of beans detected and cropped
    """
    print("="*60)
    print("Coffee Bean Cropping with OpenCV")
    print("="*60)
    
    # Read image
    print(f"\n1. Reading image: {image_path}")
    img = cv2.imread(image_path)
    
    if img is None:
        print("✗ Failed to read image")
        return 0
    
    print(f"✓ Image loaded: {img.shape[1]}x{img.shape[0]} pixels")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert to grayscale
    print("\n2. Converting to grayscale...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    print("3. Applying Gaussian blur...")
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply threshold
    print("4. Applying threshold...")
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations to clean up
    print("5. Applying morphological operations...")
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Find contours
    print("6. Finding contours...")
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"✓ Found {len(contours)} contours")
    
    # Filter contours by area (bean size)
    print("7. Filtering contours by area...")
    min_area = 300   # Minimum bean size (adjusted for high-res images)
    max_area = 15000  # Maximum bean size (adjusted for 4608x2592 resolution)
    
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if min_area < area < max_area:
            # Additional shape filtering
            perimeter = cv2.arcLength(c, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                # Coffee beans are somewhat circular/oval (0.2-1.0)
                if circularity > 0.2:
                    valid_contours.append(c)
    
    print(f"✓ {len(valid_contours)} valid beans detected")
    
    # Sort contours by position (top to bottom, left to right)
    valid_contours = sorted(valid_contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    
    # Create visualization image
    result_img = img.copy()
    
    # Extract and save each bean
    print("\n8. Cropping and saving beans...")
    saved_count = 0
    
    for i, contour in enumerate(valid_contours):
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add padding
        padding = 10
        x_pad = max(0, x - padding)
        y_pad = max(0, y - padding)
        w_pad = min(img.shape[1] - x_pad, w + 2 * padding)
        h_pad = min(img.shape[0] - y_pad, h + 2 * padding)
        
        # Crop bean
        bean_img = img[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
        
        # Save cropped bean
        filename = f"bean_{i+1:04d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, bean_img)
        saved_count += 1
        
        # Draw on visualization
        cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 2)
        cv2.rectangle(result_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(result_img, str(i+1), (x, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1} beans...")
    
    # Save visualization
    viz_path = os.path.join(output_dir, "detection_visualization.jpg")
    cv2.imwrite(viz_path, result_img)
    print(f"\n✓ Visualization saved: {viz_path}")
    
    # Save processing steps for debugging
    cv2.imwrite(os.path.join(output_dir, "step1_gray.jpg"), gray)
    cv2.imwrite(os.path.join(output_dir, "step2_blurred.jpg"), blurred)
    cv2.imwrite(os.path.join(output_dir, "step3_thresh.jpg"), thresh)
    print(f"✓ Processing steps saved to: {output_dir}/")
    
    # Statistics
    print("\n" + "="*60)
    print("Detection Results")
    print("="*60)
    print(f"Total contours found: {len(contours)}")
    print(f"Valid beans detected: {len(valid_contours)}")
    print(f"Beans cropped and saved: {saved_count}")
    print(f"Output directory: {output_dir}/")
    print("="*60)
    
    # Calculate detection rate (assuming target is 100 beans)
    target = 100
    detection_rate = (saved_count / target) * 100
    print(f"\nDetection rate: {detection_rate:.1f}% (assuming {target} beans)")
    
    if saved_count < 90:
        print("\n⚠ Low detection rate!")
        print("Tips to improve:")
        print("- Increase contrast between beans and background")
        print("- Improve lighting (use diffused light)")
        print("- Adjust min_area parameter (currently 300)")
        print("- Ensure beans are well-separated")
    elif saved_count > 110:
        print("\n⚠ Too many detections!")
        print("Tips to improve:")
        print("- Increase min_area to filter noise")
        print("- Clean background")
        print("- Reduce shadows")
    else:
        print("\n✓ EXCELLENT detection! (90-110%)")
    
    return saved_count


if __name__ == "__main__":
    # Check if image path provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default to sampletopcv.jpg in temp_captures
        image_path = "temp_captures/sampletopcv.jpg"
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"✗ Error: Image not found: {image_path}")
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <image_path>")
        print(f"\nExample:")
        print(f"  python {sys.argv[0]} temp_captures/sampletopcv.jpg")
        sys.exit(1)
    
    # Process image
    output_dir = "cropped_beans"
    bean_count = crop_beans(image_path, output_dir)
    
    print(f"\n✓ Complete! {bean_count} beans cropped and saved to {output_dir}/")
