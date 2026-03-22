#!/usr/bin/env python3
"""
Optimized Coffee Bean Cropping for 100 beans per image
Combines best techniques for high accuracy
"""

import cv2
import numpy as np
import os
import sys

def crop_beans_optimized(image_path, output_dir="cropped_beans_optimized"):
    """
    Optimized detection for 100 beans in 4608x2592 images
    """
    print("="*70)
    print("Optimized Coffee Bean Cropping - 100 Beans Target")
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
    
    # Apply bilateral filter to preserve edges
    print("3. Applying bilateral filter...")
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Try multiple threshold methods and combine results
    print("4. Applying multiple thresholding methods...")
    
    # Method 1: Otsu's thresholding
    blurred1 = cv2.GaussianBlur(filtered, (5, 5), 0)
    _, thresh1 = cv2.threshold(blurred1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Method 2: Adaptive thresholding
    thresh2 = cv2.adaptiveThreshold(filtered, 255, 
                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY_INV, 21, 5)
    
    # Combine both methods (take intersection for more reliable detection)
    thresh_combined = cv2.bitwise_and(thresh1, thresh2)
    
    # Morphological operations
    print("5. Applying morphological operations...")
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Opening to remove noise
    opening = cv2.morphologyEx(thresh_combined, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Closing to fill small holes
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    print("6. Finding contours...")
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"✓ Found {len(contours)} contours")
    
    # Calculate adaptive area thresholds based on image size
    img_area = img.shape[0] * img.shape[1]
    
    # For 100 beans in 4608x2592 image:
    # Average bean area ≈ (4608*2592) / 100 / 50 = ~2,388 pixels
    # But beans don't fill entire image, so adjust
    
    # Empirical values for 4608x2592 with 100 beans
    min_area = 800      # Minimum bean size
    max_area = 20000    # Maximum bean size
    
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
                
                # Solidity (ratio of contour area to convex hull area)
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                # Coffee beans characteristics:
                # - Circularity: 0.3-1.0 (oval to circular)
                # - Aspect ratio: 0.4-2.5 (can be elongated)
                # - Extent: 0.5-1.0 (fills bounding box)
                # - Solidity: 0.8-1.0 (mostly convex)
                
                if (circularity > 0.3 and 
                    0.4 < aspect_ratio < 2.5 and 
                    extent > 0.5 and
                    solidity > 0.75):
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
    
    # Sort by position (top to bottom, left to right)
    valid_beans.sort(key=lambda x: (x['bbox'][1], x['bbox'][0]))
    
    # Create visualization
    result_img = img.copy()
    
    # Extract and save each bean
    print("\n8. Cropping and saving beans...")
    saved_count = 0
    
    for i, bean in enumerate(valid_beans):
        contour = bean['contour']
        x, y, w, h = bean['bbox']
        
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
        
        # Add label with bean number
        label = f"{i+1}"
        cv2.putText(result_img, label, (x+5, y+25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1} beans...")
    
    # Save visualization
    viz_path = os.path.join(output_dir, "detection_visualization.jpg")
    cv2.imwrite(viz_path, result_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"\n✓ Visualization saved: {viz_path}")
    
    # Save processing steps for debugging
    cv2.imwrite(os.path.join(output_dir, "step1_gray.jpg"), gray)
    cv2.imwrite(os.path.join(output_dir, "step2_filtered.jpg"), filtered)
    cv2.imwrite(os.path.join(output_dir, "step3_thresh1_otsu.jpg"), thresh1)
    cv2.imwrite(os.path.join(output_dir, "step4_thresh2_adaptive.jpg"), thresh2)
    cv2.imwrite(os.path.join(output_dir, "step5_combined.jpg"), thresh_combined)
    cv2.imwrite(os.path.join(output_dir, "step6_opening.jpg"), opening)
    cv2.imwrite(os.path.join(output_dir, "step7_closing.jpg"), closing)
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
    
    # Calculate detection rate for 100 beans
    target = 100
    detection_rate = (saved_count / target) * 100
    print(f"\nDetection rate: {detection_rate:.1f}% ({saved_count}/{target} beans)")
    
    # Provide feedback
    if 95 <= saved_count <= 105:
        print("\n✅ EXCELLENT! Detection is spot-on (95-105%)")
        print("Perfect for dataset collection!")
    elif 90 <= saved_count <= 110:
        print("\n✓ VERY GOOD! Detection is accurate (90-110%)")
        print("Ready for dataset collection!")
    elif 85 <= saved_count <= 115:
        print("\n✓ GOOD! Detection is acceptable (85-115%)")
        print("Can proceed with dataset collection")
    elif saved_count < 85:
        print(f"\n⚠ LOW detection rate ({saved_count}/100 beans)")
        print("\nLikely issues:")
        if saved_count < 50:
            print("  1. Image may contain fewer than 100 beans")
            print("  2. Background contrast is too low")
            print("  3. Lighting is very uneven")
        else:
            print("  1. Some beans may be touching (detected as one)")
            print("  2. Background contrast could be improved")
            print("  3. Lighting may have shadows")
        print("\nRecommendations:")
        print("  ✓ Check visualization to see which beans were missed")
        print("  ✓ Use WHITE poster board background")
        print("  ✓ Improve lighting (even, no shadows)")
        print("  ✓ Space beans 5-10mm apart")
        print("  ✓ Count beans manually to verify 100 beans present")
    else:
        print(f"\n⚠ HIGH detection rate ({saved_count}/100 beans)")
        print("\nLikely issues:")
        print("  1. False positives (dust, stains, shadows)")
        print("  2. Some beans split into multiple detections")
        print("\nRecommendations:")
        print("  ✓ Clean background thoroughly")
        print("  ✓ Reduce shadows")
        print("  ✓ Check visualization for false detections")
    
    # Show quality metrics
    if valid_beans:
        avg_area = np.mean([b['area'] for b in valid_beans])
        avg_circ = np.mean([b['circularity'] for b in valid_beans])
        avg_solid = np.mean([b['solidity'] for b in valid_beans])
        
        print(f"\nQuality Metrics:")
        print(f"  Average bean area: {avg_area:.0f} pixels")
        print(f"  Average circularity: {avg_circ:.2f}")
        print(f"  Average solidity: {avg_solid:.2f}")
    
    return saved_count


if __name__ == "__main__":
    # Check if image path provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Look for most recent capture
        temp_dir = "temp_captures"
        if os.path.exists(temp_dir):
            files = [f for f in os.listdir(temp_dir) if f.endswith('.jpg')]
            if files:
                files.sort(reverse=True)
                image_path = os.path.join(temp_dir, files[0])
                print(f"Using most recent capture: {image_path}")
            else:
                print("No images found in temp_captures/")
                print("\nUsage: python crop_beans_optimized.py <image_path>")
                sys.exit(1)
        else:
            print("Usage: python crop_beans_optimized.py <image_path>")
            sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"✗ Error: Image not found: {image_path}")
        sys.exit(1)
    
    # Process image
    output_dir = "cropped_beans_optimized"
    bean_count = crop_beans_optimized(image_path, output_dir)
    
    print(f"\n{'='*70}")
    print(f"✓ COMPLETE! {bean_count} beans cropped and saved")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"  1. Open {output_dir}/detection_visualization.jpg to review")
    print(f"  2. Check individual crops in {output_dir}/")
    print(f"  3. If detection is good (90-110%), proceed with dataset collection")
    print(f"  4. If detection is off, adjust physical setup and retry")
