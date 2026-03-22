#!/usr/bin/env python3
"""
Advanced Coffee Bean Cropping - Optimized for High-Resolution Images
Combines multiple techniques for best accuracy
"""

import cv2
import numpy as np
import os
import sys

def crop_beans_advanced(image_path, output_dir="cropped_beans_advanced"):
    """
    Advanced bean detection optimized for 4608x2592 images
    """
    print("="*70)
    print("Advanced Coffee Bean Cropping - Optimized Detection")
    print("="*70)
    
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
    
    # Apply bilateral filter to preserve edges while reducing noise
    print("3. Applying bilateral filter...")
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply adaptive threshold for better handling of uneven lighting
    print("4. Applying adaptive threshold...")
    thresh = cv2.adaptiveThreshold(filtered, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 21, 5)
    
    # Morphological operations
    print("5. Applying morphological operations...")
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Opening to remove noise
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Closing to fill small holes
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    print("6. Finding contours...")
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"✓ Found {len(contours)} contours")
    
    # Calculate image-relative area thresholds
    img_area = img.shape[0] * img.shape[1]
    min_bean_ratio = 0.00001  # Minimum 0.001% of image
    max_bean_ratio = 0.001    # Maximum 0.1% of image
    
    min_area = int(img_area * min_bean_ratio)
    max_area = int(img_area * max_bean_ratio)
    
    print(f"7. Filtering contours (area: {min_area}-{max_area} pixels)...")
    
    valid_beans = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if min_area < area < max_area:
            # Calculate shape features
            perimeter = cv2.arcLength(contour, True)
            
            if perimeter > 0:
                # Circularity (1.0 = perfect circle)
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Aspect ratio
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Extent (ratio of contour area to bounding box area)
                rect_area = w * h
                extent = float(area) / rect_area if rect_area > 0 else 0
                
                # Coffee beans are somewhat circular/oval
                # Circularity: 0.2-1.0
                # Aspect ratio: 0.4-2.5 (can be elongated)
                # Extent: 0.5-1.0 (fills bounding box reasonably)
                
                if (circularity > 0.2 and 
                    0.3 < aspect_ratio < 3.0 and 
                    extent > 0.4):
                    valid_beans.append((contour, area, circularity, aspect_ratio, extent))
    
    print(f"✓ {len(valid_beans)} valid beans detected")
    
    # Sort by position (top to bottom, left to right)
    valid_beans.sort(key=lambda x: (cv2.boundingRect(x[0])[1], cv2.boundingRect(x[0])[0]))
    
    # Create visualization
    result_img = img.copy()
    
    # Extract and save each bean
    print("\n8. Cropping and saving beans...")
    saved_count = 0
    
    for i, (contour, area, circ, aspect, extent) in enumerate(valid_beans):
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add padding
        padding = 20
        x_pad = max(0, x - padding)
        y_pad = max(0, y - padding)
        w_pad = min(img.shape[1] - x_pad, w + 2 * padding)
        h_pad = min(img.shape[0] - y_pad, h + 2 * padding)
        
        # Crop bean
        bean_img = img[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
        
        # Save cropped bean
        filename = f"bean_{i+1:04d}.jpg"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, bean_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        saved_count += 1
        
        # Draw on visualization
        cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 3)
        cv2.rectangle(result_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Add label with info
        label = f"{i+1}"
        cv2.putText(result_img, label, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1} beans...")
    
    # Save visualization
    viz_path = os.path.join(output_dir, "detection_visualization.jpg")
    cv2.imwrite(viz_path, result_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"\n✓ Visualization saved: {viz_path}")
    
    # Save processing steps
    cv2.imwrite(os.path.join(output_dir, "step1_gray.jpg"), gray)
    cv2.imwrite(os.path.join(output_dir, "step2_filtered.jpg"), filtered)
    cv2.imwrite(os.path.join(output_dir, "step3_thresh.jpg"), thresh)
    cv2.imwrite(os.path.join(output_dir, "step4_opening.jpg"), opening)
    cv2.imwrite(os.path.join(output_dir, "step5_closing.jpg"), closing)
    print(f"✓ Processing steps saved to: {output_dir}/")
    
    # Statistics
    print("\n" + "="*70)
    print("DETECTION RESULTS")
    print("="*70)
    print(f"Image size: {img.shape[1]}x{img.shape[0]} pixels")
    print(f"Area thresholds: {min_area}-{max_area} pixels")
    print(f"Total contours found: {len(contours)}")
    print(f"Valid beans detected: {len(valid_beans)}")
    print(f"Beans cropped and saved: {saved_count}")
    print(f"Output directory: {output_dir}/")
    print("="*70)
    
    # Calculate detection rate
    target = 100
    detection_rate = (saved_count / target) * 100
    print(f"\nDetection rate: {detection_rate:.1f}% (assuming {target} beans)")
    
    # Provide specific recommendations
    if saved_count < 50:
        print("\n⚠ VERY LOW detection rate!")
        print("\nLikely issues:")
        print("  1. Image may not contain 100 beans")
        print("  2. Background has very low contrast with beans")
        print("  3. Lighting is extremely uneven")
        print("  4. Beans are heavily clustered/touching")
        print("\nImmediate actions:")
        print("  ✓ Check the visualization image to see what was detected")
        print("  ✓ Count actual beans in the image manually")
        print("  ✓ If background is dark, use WHITE poster board")
        print("  ✓ Add more lighting to increase contrast")
    elif saved_count < 85:
        print("\n⚠ Low detection rate!")
        print("\nPhysical setup recommendations:")
        print("  1. Use WHITE background (poster board)")
        print("  2. Improve lighting (even, no shadows)")
        print("  3. Space beans 5-10mm apart")
        print("  4. Ensure camera is focused")
    elif saved_count > 115:
        print("\n⚠ Too many detections!")
        print("\nRecommendations:")
        print("  - Clean background (remove dust/stains)")
        print("  - Reduce shadows")
        print("  - Check for false detections in visualization")
    else:
        print("\n✓ Excellent detection rate! (85-115%)")
        print("Ready for dataset collection!")
    
    return saved_count


if __name__ == "__main__":
    # Check if image path provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python crop_beans_advanced.py <image_path>")
        print("\nExample:")
        print("  python crop_beans_advanced.py coffee_dataset/bad_beans/curve/bad_curve_0011.jpg")
        sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"✗ Error: Image not found: {image_path}")
        sys.exit(1)
    
    # Process image
    output_dir = "cropped_beans_advanced"
    bean_count = crop_beans_advanced(image_path, output_dir)
    
    print(f"\n✓ Complete! {bean_count} beans cropped and saved to {output_dir}/")
    print(f"\nNext steps:")
    print(f"  1. Open {output_dir}/detection_visualization.jpg to review results")
    print(f"  2. Check processing steps in {output_dir}/ to debug if needed")
    print(f"  3. If detection is low, improve physical setup (background + lighting)")
