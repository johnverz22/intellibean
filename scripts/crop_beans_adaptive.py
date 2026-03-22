#!/usr/bin/env python3
"""
Adaptive Coffee Bean Cropping - Works with any background
Automatically adjusts to image characteristics
"""

import cv2
import numpy as np
import os
import sys

def crop_beans_adaptive(image_path, output_dir="cropped_beans_adaptive"):
    """
    Adaptive detection that works with various backgrounds
    """
    print("="*70)
    print("Adaptive Coffee Bean Cropping - Auto-Adjusting Detection")
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
    
    # Convert to different color spaces
    print("\n2. Analyzing image in multiple color spaces...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    
    # Use LAB color space (better for separating objects from background)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    print("3. Applying adaptive histogram equalization...")
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(l_channel)
    
    # Apply bilateral filter
    print("4. Applying bilateral filter...")
    filtered = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    # Try multiple thresholding methods
    print("5. Applying adaptive thresholding...")
    
    # Method 1: Adaptive threshold with large block size
    thresh1 = cv2.adaptiveThreshold(filtered, 255,
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 51, 10)
    
    # Method 2: Otsu's threshold
    blurred = cv2.GaussianBlur(filtered, (5, 5), 0)
    _, thresh2 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Method 3: Mean threshold
    mean_val = np.mean(filtered)
    _, thresh3 = cv2.threshold(filtered, mean_val - 20, 255, cv2.THRESH_BINARY_INV)
    
    # Combine all three methods (take pixels that appear in at least 2 methods)
    combined = np.zeros_like(thresh1)
    combined[(thresh1 == 255) & (thresh2 == 255)] = 255
    combined[(thresh1 == 255) & (thresh3 == 255)] = 255
    combined[(thresh2 == 255) & (thresh3 == 255)] = 255
    
    # Morphological operations
    print("6. Applying morphological operations...")
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    
    # Opening to remove noise
    opening = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=3)
    
    # Closing to fill holes
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    # Find contours
    print("7. Finding contours...")
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"✓ Found {len(contours)} contours")
    
    # Calculate adaptive area thresholds
    img_area = img.shape[0] * img.shape[1]
    
    # For 100 beans, each bean should be roughly 0.5-2% of image area
    # But accounting for spacing, use smaller percentages
    min_area = int(img_area * 0.00005)  # 0.005% of image
    max_area = int(img_area * 0.002)    # 0.2% of image
    
    print(f"8. Filtering contours (area: {min_area}-{max_area} pixels)...")
    
    valid_beans = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if min_area < area < max_area:
            # Calculate shape features
            perimeter = cv2.arcLength(contour, True)
            
            if perimeter > 0:
                # Circularity
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Bounding box
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Extent
                rect_area = w * h
                extent = float(area) / rect_area if rect_area > 0 else 0
                
                # Solidity
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                # Very relaxed filters for difficult backgrounds
                if (circularity > 0.15 and 
                    0.3 < aspect_ratio < 3.5 and 
                    extent > 0.3 and
                    solidity > 0.6):
                    valid_beans.append({
                        'contour': contour,
                        'area': area,
                        'circularity': circularity,
                        'aspect_ratio': aspect_ratio,
                        'extent': extent,
                        'solidity': solidity,
                        'bbox': (x, y, w, h)
                    })
    
    print(f"✓ {len(valid_beans)} valid beans detected")
    
    # Sort by position
    valid_beans.sort(key=lambda x: (x['bbox'][1], x['bbox'][0]))
    
    # Create visualization
    result_img = img.copy()
    
    # Extract and save each bean
    print("\n9. Cropping and saving beans...")
    saved_count = 0
    
    for i, bean in enumerate(valid_beans):
        contour = bean['contour']
        x, y, w, h = bean['bbox']
        
        # Add padding
        padding = 25
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
        cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 4)
        cv2.rectangle(result_img, (x, y), (x+w, y+h), (255, 0, 0), 3)
        
        # Add label
        label = f"{i+1}"
        cv2.putText(result_img, label, (x+10, y+30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1} beans...")
    
    # Save visualization
    viz_path = os.path.join(output_dir, "detection_visualization.jpg")
    cv2.imwrite(viz_path, result_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"\n✓ Visualization saved: {viz_path}")
    
    # Save processing steps
    cv2.imwrite(os.path.join(output_dir, "step1_gray.jpg"), gray)
    cv2.imwrite(os.path.join(output_dir, "step2_enhanced.jpg"), enhanced)
    cv2.imwrite(os.path.join(output_dir, "step3_filtered.jpg"), filtered)
    cv2.imwrite(os.path.join(output_dir, "step4_thresh1_adaptive.jpg"), thresh1)
    cv2.imwrite(os.path.join(output_dir, "step5_thresh2_otsu.jpg"), thresh2)
    cv2.imwrite(os.path.join(output_dir, "step6_thresh3_mean.jpg"), thresh3)
    cv2.imwrite(os.path.join(output_dir, "step7_combined.jpg"), combined)
    cv2.imwrite(os.path.join(output_dir, "step8_opening.jpg"), opening)
    cv2.imwrite(os.path.join(output_dir, "step9_closing.jpg"), closing)
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
    print(f"\nDetection rate: {detection_rate:.1f}% ({saved_count}/{target} beans)")
    
    # Provide feedback
    if 95 <= saved_count <= 105:
        print("\n✅ EXCELLENT! Detection is spot-on!")
    elif 85 <= saved_count <= 115:
        print("\n✓ GOOD! Detection is acceptable")
    elif saved_count < 50:
        print(f"\n⚠ VERY LOW detection rate!")
        print("\nCritical issues:")
        print("  1. Background color is too similar to beans")
        print("  2. Use WHITE or LIGHT-COLORED background")
        print("  3. Current background (green?) has poor contrast")
        print("\nIMPORTANT: Check the visualization to see what was detected")
    else:
        print(f"\n⚠ Low detection rate")
        print("Check visualization and improve setup")
    
    return saved_count


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python crop_beans_adaptive.py <image_path>")
        sys.exit(1)
    
    if not os.path.exists(image_path):
        print(f"✗ Error: Image not found: {image_path}")
        sys.exit(1)
    
    output_dir = "cropped_beans_adaptive"
    bean_count = crop_beans_adaptive(image_path, output_dir)
    
    print(f"\n{'='*70}")
    print(f"✓ COMPLETE! {bean_count} beans detected")
    print(f"{'='*70}")
    print(f"\nIMPORTANT: Open {output_dir}/detection_visualization.jpg")
    print(f"If detection is low, the background needs to be changed to WHITE")
