#!/usr/bin/env python3
"""
Quick parameter testing script
Tests multiple parameter combinations to find optimal settings
"""

import subprocess
import os
import sys

def test_parameters(image_path):
    """Test different parameter combinations"""
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    print("="*70)
    print("Testing Different Parameter Combinations")
    print("="*70)
    print(f"Image: {image_path}")
    print("Target: 240 beans")
    print("="*70)
    
    # Parameter combinations to test
    tests = [
        {
            "name": "Default (Original)",
            "params": ["--min-area", "500", "--max-area", "10000"]
        },
        {
            "name": "Recommended (Lower thresholds)",
            "params": ["--min-area", "200", "--max-area", "5000"]
        },
        {
            "name": "More Sensitive",
            "params": ["--min-area", "150", "--max-area", "6000"]
        },
        {
            "name": "Less Sensitive",
            "params": ["--min-area", "300", "--max-area", "4000"]
        },
        {
            "name": "Adaptive Threshold",
            "params": ["--min-area", "200", "--max-area", "5000", "--threshold", "adaptive"]
        },
        {
            "name": "With Watershed",
            "params": ["--min-area", "200", "--max-area", "5000", "--separate-touching"]
        },
        {
            "name": "Aggressive Morphology",
            "params": ["--min-area", "200", "--max-area", "5000", 
                      "--morph-close", "3", "--morph-open", "2"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(tests)}: {test['name']}")
        print(f"{'='*70}")
        
        # Create unique output directory
        output_dir = f"test_results/test_{i}_{test['name'].replace(' ', '_').lower()}"
        
        # Build command
        cmd = [
            sys.executable,  # Use current Python interpreter
            "crop_beans_tunable.py",
            image_path,
            "-o", output_dir
        ] + test['params']
        
        print(f"Command: {' '.join(cmd)}")
        print()
        
        # Run test
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse output to get bean count
            output = result.stdout
            bean_count = 0
            
            for line in output.split('\n'):
                if "Beans cropped and saved:" in line:
                    try:
                        bean_count = int(line.split(':')[1].strip())
                    except:
                        pass
            
            detection_rate = (bean_count / 240) * 100
            
            results.append({
                "name": test['name'],
                "count": bean_count,
                "rate": detection_rate,
                "output_dir": output_dir
            })
            
            print(f"✓ Result: {bean_count} beans detected ({detection_rate:.1f}%)")
            
        except subprocess.TimeoutExpired:
            print("✗ Test timed out")
            results.append({
                "name": test['name'],
                "count": 0,
                "rate": 0,
                "output_dir": output_dir
            })
        except Exception as e:
            print(f"✗ Test failed: {e}")
            results.append({
                "name": test['name'],
                "count": 0,
                "rate": 0,
                "output_dir": output_dir
            })
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY - All Test Results")
    print("="*70)
    print(f"{'Test Name':<30} {'Beans':<10} {'Rate':<10} {'Status'}")
    print("-"*70)
    
    best_result = None
    best_rate = 0
    
    for result in results:
        count = result['count']
        rate = result['rate']
        
        # Determine status
        if 228 <= count <= 252:  # 95-105% of target
            status = "✓ EXCELLENT"
            color = ""
        elif 216 <= count <= 264:  # 90-110% of target
            status = "✓ Good"
            color = ""
        elif count > 0:
            status = "⚠ Needs tuning"
            color = ""
        else:
            status = "✗ Failed"
            color = ""
        
        print(f"{result['name']:<30} {count:<10} {rate:>5.1f}%    {status}")
        
        # Track best result (closest to 240)
        if abs(count - 240) < abs(best_rate - 240):
            best_result = result
            best_rate = count
    
    print("="*70)
    
    if best_result and best_result['count'] > 0:
        print(f"\n🏆 Best Result: {best_result['name']}")
        print(f"   Detected: {best_result['count']} beans ({best_result['rate']:.1f}%)")
        print(f"   Visualization: {best_result['output_dir']}/detection_visualization.jpg")
        
        if 228 <= best_result['count'] <= 252:
            print("\n✓ Excellent detection rate! Ready for dataset collection.")
        elif 216 <= best_result['count'] <= 264:
            print("\n✓ Good detection rate. Consider minor adjustments to physical setup.")
        else:
            print("\n⚠ Detection rate needs improvement.")
            print("   Focus on physical setup:")
            print("   1. White background")
            print("   2. Even lighting")
            print("   3. Bean spacing (5-10mm)")
    else:
        print("\n✗ All tests failed. Check:")
        print("   1. Image file is valid")
        print("   2. OpenCV is installed")
        print("   3. Physical setup (background, lighting, spacing)")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "temp_captures/sampletopcv.jpg"
    
    print(f"\nUsage: python {sys.argv[0]} <image_path>")
    print(f"Using: {image_path}\n")
    
    test_parameters(image_path)
