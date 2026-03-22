#!/usr/bin/env python3
"""
Visualize bean detection without cropping
Shows what will be detected with bounding boxes
"""

import cv2
import numpy as np
import os
import sys

def visualize_detection(image_path, output_path="detection_visualization.jpg"):
    """
    Detect beans and create visualization only (no cropping)
    """
    print("="*70)
    print("Bean Detection Visualization (No Cropping)")
    print("="*70)
    
    # Read image
    print(f"\n1. Reading image: {image_path}")
    img = cv2.imread(image_path)
    
    if img is None:
        print("✗ Failed to read image")
        return 0
    
    print(f"✓ Image loaded: {img.shape[1]}x{img.shape[0]} pixels")
    
    # Convert to grayscale
    print("\n2. Converting to grayscale...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    print("3. Applying Gaussian blur...")
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply threshold
    print("4. Applying Otsu's threshold...")
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations
    print("5. Applying morphological operations...")
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Find contours
    print("6. Finding contours...")
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"✓ Found {len(contours)} contours")
    
    # Filter contours by area
    print("7. Filtering contours...")
    min_area = 100
    max_area = 50000
    
    valid_beans = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if min_area < area < max_area:
            # Calculate shape features
            perimeter = cv2.arcLength(contour, True)
            
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Coffee beans are somewhat circular
                if circularity > 0.2:
                    valid_beans.append(contour)
    
    print(f"✓ {len(valid_beans)} valid beans detected")
    
    # Sort by position
    valid_beans.sort(key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    
    # Create visualization
    result_img = img.copy()
    
    print("\n8. Creating visualization...")
    for i, contour in enumerate(valid_beans):
        x, y, w, h = cv2.boundingRect(contour)
        
        # Draw contour in green
        cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 4)
        
        # Draw bounding box in blue
        cv2.rectangle(result_img, (x, y), (x+w, y+h), (255, 0, 0), 3)
        
        # Add label with bean number
        label = f"{i+1}"
        cv2.putText(result_img, label, (x+10, y+30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 3)
    
    # Save visualization
    cv2.imwrite(output_path, result_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"\n✓ Visualization saved: {output_path}")
    
    # Statistics
    print("\n" + "="*70)
    print("DETECTION RESULTS")
    print("="*70)
    print(f"Image size: {img.shape[1]}x{img.shape[0]} pixels")
    print(f"Area thresholds: {min_area}-{max_area} pixels")
    print(f"Total contours found: {len(contours)}")
    print(f"Valid beans detected: {len(valid_beans)}")
    print("="*70)
    
    # Detection rate
    print(f"\nDetected: {len(valid_beans)} beans")
    
    if len(valid_beans) >= 45 and len(valid_beans) <= 55:
        print("✅ EXCELLENT! Detection rate is perfect for 50 beans")
    elif len(valid_beans) >= 90 and len(valid_beans) <= 110:
        print("✅ EXCELLENT! Detection rate is perfect for 100 beans")
    elif len(valid_beans) < 45:
        print("⚠ Low detection - check setup")
    else:
        print("⚠ High detection - may have false positives")
    
    print(f"\n✓ Open {output_path} to review detected beans")
    
    return len(valid_beans)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python visualize_detection.py <image_path>")
        sys.exit(1)
    
    if not os.path.exists(image_path):
        print(f"✗ Error: Image not found: {image_path}")
        sys.exit(1)
    
    # Create visualization
    bean_count = visualize_detection(image_path)
    
    print(f"\n{'='*70}")
    print(f"✓ COMPLETE! {bean_count} beans detected")
    print(f"{'='*70}")
    print(f"\nVisualization saved as: detection_visualization.jpg")
    print(f"Review the image to verify detection accuracy")
