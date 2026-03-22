#!/usr/bin/env python3
"""
Advanced Coffee Bean Cropping with Watershed Algorithm
Uses 4-step pipeline for accurate bean separation
"""

import cv2
import numpy as np
import os
import sys
import argparse

def crop_beans_watershed(image_path, output_dir="cropped_beans_watershed",
                        min_area=200, max_area=8000,
                        distance_threshold=0.4,
                        show_steps=True):
    """
    Detect and crop individual coffee beans using watershed algorithm
    
    4-Step Pipeline:
    1. Binarization: Grayscale + Otsu's Thresholding
    2. Distance Transform: Create heatmap of bean centers
    3. Find Markers: Identify peaks (sure foreground)
    4. Watershed: Grow markers to separate touching beans
    
    Args:
        image_path: Path to input image
        output_dir: Directory to save cropped beans
        min_area: Minimum bean area in pixels
        max_area: Maximum bean area in pixels
        distance_threshold: Threshold for distance transform (0.3-0.6)
        show_steps: Save intermediate processing steps
    
    Returns:
        Number of beans detected and cropped
    """
    print("="*70)
    print("Advanced Coffee Bean Cropping - Watershed Algorithm")
    print("="*70)
    print(f"\nParameters:")
    print(f"  min_area: {min_area}")
    print(f"  max_area: {max_area}")
    print(f"  distance_threshold: {distance_threshold}")
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
    
    # STEP 1: BINARIZATION
    print("\n" + "="*70)
    print("STEP 1: BINARIZATION (Grayscale + Otsu's Thresholding)")
    print("="*70)
    
    # Convert to grayscale
    print("  Converting to grayscale...")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    print("  Applying Gaussian blur...")
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Otsu's thresholding
    print("  Applying Otsu's thresholding...")
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations to clean up
    print("  Applying morphological operations...")
    kernel = np.ones((3, 3), np.uint8)
    
    # Opening to remove noise
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Closing to fill small holes
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    
    print("✓ Binarization complete")
    
    # STEP 2: DISTANCE TRANSFORM
    print("\n" + "="*70)
    print("STEP 2: DISTANCE TRANSFORM (Create bean center heatmap)")
    print("="*70)
    
    print("  Computing distance transform...")
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    
    # Normalize for visualization
    dist_normalized = cv2.normalize(dist_transform, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    
    print(f"✓ Distance transform complete (max distance: {dist_transform.max():.2f})")
    
    # STEP 3: FIND MARKERS (Sure Foreground)
    print("\n" + "="*70)
    print("STEP 3: FIND MARKERS (Identify bean centers)")
    print("="*70)
    
    print(f"  Thresholding distance map (threshold: {distance_threshold})...")
    _, sure_fg = cv2.threshold(dist_transform, 
                               distance_threshold * dist_transform.max(), 
                               255, 0)
    
    # Convert to uint8
    sure_fg = np.uint8(sure_fg)
    
    # Find unknown region
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Label markers
    print("  Labeling markers...")
    ret, markers = cv2.connectedComponents(sure_fg)
    
    # Add 1 to all labels so background is not 0, but 1
    markers = markers + 1
    
    # Mark unknown region as 0
    markers[unknown == 255] = 0
    
    print(f"✓ Found {ret} markers (potential beans)")
    
    # STEP 4: WATERSHED
    print("\n" + "="*70)
    print("STEP 4: WATERSHED (Separate touching beans)")
    print("="*70)
    
    print("  Applying watershed algorithm...")
    markers = cv2.watershed(img, markers)
    
    # Count unique markers (excluding -1 for boundaries and 1 for background)
    unique_markers = np.unique(markers)
    num_beans = len(unique_markers) - 2  # Exclude -1 (boundary) and 1 (background)
    
    print(f"✓ Watershed complete - {num_beans} beans separated")
    
    # Create visualization
    print("\n" + "="*70)
    print("PROCESSING RESULTS")
    print("="*70)
    
    result_img = img.copy()
    
    # Mark boundaries in red
    result_img[markers == -1] = [0, 0, 255]
    
    # Extract and save each bean
    print("\nExtracting and saving beans...")
    saved_count = 0
    valid_beans = []
    
    for marker_id in range(2, markers.max() + 1):
        # Create mask for this marker
        mask = np.zeros(gray.shape, dtype=np.uint8)
        mask[markers == marker_id] = 255
        
        # Find contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            continue
        
        contour = contours[0]
        area = cv2.contourArea(contour)
        
        # Filter by area
        if min_area < area < max_area:
            # Additional shape filtering
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                # Coffee beans are somewhat circular (0.2-1.0)
                if circularity > 0.15:
                    valid_beans.append((marker_id, contour, area))
    
    # Sort by position (top to bottom, left to right)
    valid_beans.sort(key=lambda x: (cv2.boundingRect(x[1])[1], cv2.boundingRect(x[1])[0]))
    
    print(f"Valid beans after filtering: {len(valid_beans)}")
    
    # Save each bean
    for i, (marker_id, contour, area) in enumerate(valid_beans):
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add padding
        padding = 15
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
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1} beans...")
    
    # Save visualization
    viz_path = os.path.join(output_dir, "detection_visualization.jpg")
    cv2.imwrite(viz_path, result_img)
    print(f"\n✓ Visualization saved: {viz_path}")
    
    # Save processing steps
    if show_steps:
        cv2.imwrite(os.path.join(output_dir, "step1_gray.jpg"), gray)
        cv2.imwrite(os.path.join(output_dir, "step2_thresh.jpg"), thresh)
        cv2.imwrite(os.path.join(output_dir, "step3_opening.jpg"), opening)
        cv2.imwrite(os.path.join(output_dir, "step4_distance.jpg"), dist_normalized)
        cv2.imwrite(os.path.join(output_dir, "step5_markers.jpg"), np.uint8(sure_fg))
        
        # Create colored watershed result
        watershed_colored = np.zeros_like(img)
        for marker_id in range(2, markers.max() + 1):
            color = np.random.randint(0, 255, 3).tolist()
            watershed_colored[markers == marker_id] = color
        cv2.imwrite(os.path.join(output_dir, "step6_watershed.jpg"), watershed_colored)
        
        print(f"✓ Processing steps saved to: {output_dir}/")
    
    # Statistics
    print("\n" + "="*70)
    print("DETECTION RESULTS")
    print("="*70)
    print(f"Watershed markers found: {num_beans}")
    print(f"Valid beans after filtering: {len(valid_beans)}")
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
        print("  1. Use WHITE background (high contrast)")
        print("  2. Improve lighting (even, no shadows)")
        print("  3. Space beans 5-10mm apart")
        print("  4. Ensure camera is focused")
        print("\nSoftware tuning recommendations:")
        print(f"  - Try lower min_area: --min-area {max(100, min_area - 100)}")
        print(f"  - Try higher distance_threshold: --distance-threshold {min(0.6, distance_threshold + 0.1)}")
    elif saved_count > 260:
        print("\n⚠ Too many detections (possible false positives)!")
        print("\nRecommendations:")
        print("  - Clean background (remove dust/stains)")
        print("  - Reduce shadows")
        print(f"  - Try higher min_area: --min-area {min_area + 100}")
        print(f"  - Try lower distance_threshold: --distance-threshold {max(0.3, distance_threshold - 0.1)}")
    else:
        print("\n✓ Excellent detection rate! (90-100%)")
        print("Ready for dataset collection!")
    
    return saved_count


def main():
    parser = argparse.ArgumentParser(
        description="Crop coffee beans using advanced watershed algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python crop_beans_watershed.py image.jpg
  
  # Adjust area thresholds
  python crop_beans_watershed.py image.jpg --min-area 200 --max-area 8000
  
  # Adjust distance threshold (higher = more separation)
  python crop_beans_watershed.py image.jpg --distance-threshold 0.5
  
  # Full customization
  python crop_beans_watershed.py image.jpg --min-area 150 --max-area 10000 \\
      --distance-threshold 0.45 --output watershed_results
        """
    )
    
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("-o", "--output", default="cropped_beans_watershed",
                       help="Output directory (default: cropped_beans_watershed)")
    parser.add_argument("--min-area", type=int, default=200,
                       help="Minimum bean area in pixels (default: 200)")
    parser.add_argument("--max-area", type=int, default=8000,
                       help="Maximum bean area in pixels (default: 8000)")
    parser.add_argument("--distance-threshold", type=float, default=0.4,
                       help="Distance transform threshold 0.3-0.6 (default: 0.4)")
    parser.add_argument("--no-steps", action="store_true",
                       help="Don't save intermediate processing steps")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.image):
        print(f"✗ Error: Image not found: {args.image}")
        sys.exit(1)
    
    # Process image
    bean_count = crop_beans_watershed(
        args.image,
        args.output,
        min_area=args.min_area,
        max_area=args.max_area,
        distance_threshold=args.distance_threshold,
        show_steps=not args.no_steps
    )
    
    print(f"\n✓ Complete! {bean_count} beans cropped and saved to {args.output}/")


if __name__ == "__main__":
    main()
