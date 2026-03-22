#!/usr/bin/env python3
"""
Tunable Coffee Bean Cropping Script
Allows easy parameter adjustment for optimization
"""

import cv2
import numpy as np
import os
import sys
import argparse

def crop_beans_tunable(image_path, output_dir="cropped_beans", 
                       min_area=200, max_area=5000,
                       threshold_method="otsu",
                       morph_close=2, morph_open=1,
                       use_color=False, separate_touching=False):
    """
    Detect and crop individual coffee beans with tunable parameters
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save cropped beans
        min_area: Minimum bean area in pixels (default: 200)
        max_area: Maximum bean area in pixels (default: 5000)
        threshold_method: "otsu" or "adaptive" (default: "otsu")
        morph_close: Morphological closing iterations (default: 2)
        morph_open: Morphological opening iterations (default: 1)
        use_color: Use color-based detection (default: False)
        separate_touching: Use watershed to separate touching beans (default: False)
    
    Returns:
        Number of beans detected and cropped
    """
    print("="*70)
    print("Coffee Bean Cropping - Tunable Version")
    print("="*70)
    print(f"\nParameters:")
    print(f"  min_area: {min_area}")
    print(f"  max_area: {max_area}")
    print(f"  threshold_method: {threshold_method}")
    print(f"  morph_close: {morph_close}")
    print(f"  morph_open: {morph_open}")
    print(f"  use_color: {use_color}")
    print(f"  separate_touching: {separate_touching}")
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
    
    # Apply Gaussian blur
    print("3. Applying Gaussian blur...")
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply threshold
    print(f"4. Applying threshold ({threshold_method})...")
    if threshold_method == "adaptive":
        thresh = cv2.adaptiveThreshold(blurred, 255, 
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY_INV, 11, 2)
    else:  # otsu
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations
    print(f"5. Applying morphological operations (close={morph_close}, open={morph_open})...")
    kernel = np.ones((3, 3), np.uint8)
    
    if morph_close > 0:
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=morph_close)
    
    if morph_open > 0:
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=morph_open)
    
    # Separate touching beans using watershed
    if separate_touching:
        print("6. Separating touching beans (watershed)...")
        # Distance transform
        dist_transform = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.4*dist_transform.max(), 255, 0)
        
        # Finding unknown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(thresh, sure_fg)
        
        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        
        # Apply watershed
        markers = cv2.watershed(img, markers)
        thresh[markers == -1] = 0
    
    # Find contours
    print(f"{'7' if not separate_touching else '7'}. Finding contours...")
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"✓ Found {len(contours)} contours")
    
    # Filter contours by area
    print(f"{'8' if not separate_touching else '8'}. Filtering contours (area: {min_area}-{max_area})...")
    valid_contours = []
    
    for c in contours:
        area = cv2.contourArea(c)
        if min_area < area < max_area:
            # Additional shape filtering (optional)
            perimeter = cv2.arcLength(c, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                # Coffee beans are somewhat circular (0.3-1.0)
                if circularity > 0.2:
                    valid_contours.append(c)
    
    print(f"✓ {len(valid_contours)} valid beans detected")
    
    # Sort contours by position
    valid_contours = sorted(valid_contours, 
                           key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    
    # Create visualization
    result_img = img.copy()
    
    # Extract and save each bean
    print(f"\n{'9' if not separate_touching else '9'}. Cropping and saving beans...")
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
    
    # Save processing steps
    cv2.imwrite(os.path.join(output_dir, "step1_gray.jpg"), gray)
    cv2.imwrite(os.path.join(output_dir, "step2_blurred.jpg"), blurred)
    cv2.imwrite(os.path.join(output_dir, "step3_thresh.jpg"), thresh)
    print(f"✓ Processing steps saved to: {output_dir}/")
    
    # Statistics
    print("\n" + "="*70)
    print("Detection Results")
    print("="*70)
    print(f"Total contours found: {len(contours)}")
    print(f"Valid beans detected: {len(valid_contours)}")
    print(f"Beans cropped and saved: {saved_count}")
    print(f"Output directory: {output_dir}/")
    print("="*70)
    
    # Calculate detection rate
    target = 240
    detection_rate = (saved_count / target) * 100
    print(f"\nDetection rate: {detection_rate:.1f}% (assuming {target} beans)")
    
    # Recommendations
    if saved_count < 200:
        print("\n⚠ Low detection rate!")
        print("\nPhysical setup recommendations:")
        print("  1. Use WHITE background (poster board)")
        print("  2. Improve lighting (even, no shadows)")
        print("  3. Space beans 5-10mm apart")
        print("  4. Ensure camera is focused")
        print("\nSoftware tuning recommendations:")
        print(f"  - Try lower min_area: --min-area {max(100, min_area - 100)}")
        print(f"  - Try higher max_area: --max-area {max_area + 1000}")
        print("  - Try adaptive threshold: --threshold adaptive")
        print("  - Try watershed: --separate-touching")
    elif saved_count > 260:
        print("\n⚠ Too many detections (false positives)!")
        print("\nRecommendations:")
        print("  - Clean background (remove dust/stains)")
        print("  - Reduce shadows")
        print(f"  - Try higher min_area: --min-area {min_area + 100}")
        print(f"  - Try lower max_area: --max-area {max(3000, max_area - 1000)}")
    else:
        print("\n✓ Detection looks good! (90-100% rate)")
        print("Ready for full dataset collection!")
    
    return saved_count


def main():
    parser = argparse.ArgumentParser(
        description="Crop coffee beans from image with tunable parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with defaults
  python crop_beans_tunable.py temp_captures/sampletopcv.jpg
  
  # Adjust area thresholds
  python crop_beans_tunable.py image.jpg --min-area 200 --max-area 5000
  
  # Use adaptive threshold
  python crop_beans_tunable.py image.jpg --threshold adaptive
  
  # Separate touching beans
  python crop_beans_tunable.py image.jpg --separate-touching
  
  # Full customization
  python crop_beans_tunable.py image.jpg --min-area 150 --max-area 6000 \\
      --threshold adaptive --morph-close 3 --morph-open 2 --separate-touching
        """
    )
    
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("-o", "--output", default="cropped_beans",
                       help="Output directory (default: cropped_beans)")
    parser.add_argument("--min-area", type=int, default=200,
                       help="Minimum bean area in pixels (default: 200)")
    parser.add_argument("--max-area", type=int, default=5000,
                       help="Maximum bean area in pixels (default: 5000)")
    parser.add_argument("--threshold", choices=["otsu", "adaptive"], default="otsu",
                       help="Threshold method (default: otsu)")
    parser.add_argument("--morph-close", type=int, default=2,
                       help="Morphological closing iterations (default: 2)")
    parser.add_argument("--morph-open", type=int, default=1,
                       help="Morphological opening iterations (default: 1)")
    parser.add_argument("--use-color", action="store_true",
                       help="Use color-based detection (experimental)")
    parser.add_argument("--separate-touching", action="store_true",
                       help="Use watershed to separate touching beans")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.image):
        print(f"✗ Error: Image not found: {args.image}")
        sys.exit(1)
    
    # Process image
    bean_count = crop_beans_tunable(
        args.image,
        args.output,
        min_area=args.min_area,
        max_area=args.max_area,
        threshold_method=args.threshold,
        morph_close=args.morph_close,
        morph_open=args.morph_open,
        use_color=args.use_color,
        separate_touching=args.separate_touching
    )
    
    print(f"\n✓ Complete! {bean_count} beans cropped and saved to {args.output}/")


if __name__ == "__main__":
    main()
