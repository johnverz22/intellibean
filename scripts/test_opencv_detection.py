#!/usr/bin/env python3
"""
Test OpenCV bean detection
Use this to tune detection parameters before collecting dataset
"""

import cv2
import numpy as np
import sys
import os

def test_detection(image_path, show_steps=True):
    """
    Test bean detection on a sample image
    
    Args:
        image_path: Path to test image
        show_steps: Show intermediate processing steps
    """
    print("="*60)
    print("OpenCV Bean Detection Test")
    print("="*60)
    
    # Read image
    print(f"\n1. Reading image: {image_path}")
    img = cv2.imread(image_path)
    
    if img is None:
        print("✗ Failed to read image")
        return
    
    print(f"✓ Image loaded: {img.shape[1]}x{img.shape[0]} pixels")
    
    # Convert to grayscale
    print("\n2. Converting to grayscale...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    print("3. Applying Gaussian blur...")
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold
    print("4. Applying threshold...")
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
    
    # Filter by area
    print("7. Filtering contours by area...")
    min_area = 500
    max_area = 5000
    valid_contours = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
    print(f"✓ {len(valid_contours)} valid beans detected")
    
    # Draw results
    print("\n8. Drawing results...")
    result_img = img.copy()
    
    for i, contour in enumerate(valid_contours):
        # Draw contour
        cv2.drawContours(result_img, [contour], -1, (0, 255, 0), 2)
        
        # Draw bounding box
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(result_img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Add number
        cv2.putText(result_img, str(i+1), (x, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Save results
    output_dir = "/home/beans/test_results"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = f"{output_dir}/detection_result.jpg"
    cv2.imwrite(output_path, result_img)
    print(f"✓ Result saved: {output_path}")
    
    if show_steps:
        cv2.imwrite(f"{output_dir}/step1_gray.jpg", gray)
        cv2.imwrite(f"{output_dir}/step2_blurred.jpg", blurred)
        cv2.imwrite(f"{output_dir}/step3_thresh.jpg", thresh)
        print(f"✓ Processing steps saved to: {output_dir}/")
    
    # Statistics
    print("\n" + "="*60)
    print("Detection Statistics")
    print("="*60)
    print(f"Total contours found: {len(contours)}")
    print(f"Valid beans detected: {len(valid_contours)}")
    print(f"Detection rate: {len(valid_contours)/240*100:.1f}% (assuming 240 beans)")
    
    if len(valid_contours) < 200:
        print("\n⚠ Warning: Low detection rate!")
        print("Tips:")
        print("- Increase contrast between beans and background")
        print("- Improve lighting")
        print("- Adjust min_area and max_area parameters")
        print("- Ensure beans are well-separated")
    elif len(valid_contours) > 250:
        print("\n⚠ Warning: Too many detections!")
        print("Tips:")
        print("- Increase min_area to filter noise")
        print("- Check for shadows or artifacts")
        print("- Improve background uniformity")
    else:
        print("\n✓ Detection looks good!")
    
    print("="*60)


def capture_test_image():
    """Capture a test image for detection testing"""
    print("Capturing test image...")
    
    output_path = "/home/beans/test_capture.jpg"
    
    cmd = [
        "rpicam-still",
        "-o", output_path,
        "--width", "4608",
        "--height", "2592",
        "--timeout", "1000",
        "--nopreview"
    ]
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✓ Test image captured: {output_path}")
        return output_path
    else:
        print(f"✗ Capture failed: {result.stderr}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test with provided image
        image_path = sys.argv[1]
        test_detection(image_path)
    else:
        # Capture and test
        print("No image provided. Capturing test image...")
        print("Make sure beans are arranged on grid!\n")
        input("Press Enter to capture...")
        
        image_path = capture_test_image()
        if image_path:
            test_detection(image_path)
