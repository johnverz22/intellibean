#!/usr/bin/env python3
"""
Test Raspberry Pi Camera Module 3
Uses rpicam-still for capturing images
"""

import subprocess
import sys
from datetime import datetime
import os

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def test_camera():
    """Test Camera Module 3 and capture sample images"""
    print("=" * 60)
    print("Raspberry Pi Camera Module 3 Test")
    print("=" * 60)
    
    # Check camera detection
    print("\n1. Detecting camera...")
    stdout, stderr, code = run_command("rpicam-hello --list-cameras")
    
    if code != 0 or "No cameras available" in stdout:
        print("✗ No camera detected!")
        print(stdout)
        return 1
    
    print("✓ Camera detected!")
    print(stdout)
    
    # Create output directory
    output_dir = "/home/beans/camera_tests"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Capture test images with different settings
    print("\n2. Capturing test images...")
    
    test_configs = [
        {
            "name": "default",
            "args": ""
        },
        {
            "name": "high_res",
            "args": "--width 4608 --height 2592"
        },
        {
            "name": "medium_res",
            "args": "--width 2304 --height 1296"
        }
    ]
    
    for i, config in enumerate(test_configs, 1):
        filename = f"{output_dir}/test_{timestamp}_{config['name']}.jpg"
        print(f"\n   Test {i}/3: {config['name']}")
        
        cmd = f"rpicam-still {config['args']} -o {filename} --timeout 2000"
        print(f"   Command: {cmd}")
        
        stdout, stderr, code = run_command(cmd)
        
        if code == 0 and os.path.exists(filename):
            size = os.path.getsize(filename) / 1024  # KB
            print(f"   ✓ Captured: {filename} ({size:.1f} KB)")
        else:
            print(f"   ✗ Failed to capture")
            if stderr:
                print(f"   Error: {stderr}")
    
    # Test video capture
    print("\n3. Testing video capture (5 seconds)...")
    video_file = f"{output_dir}/test_{timestamp}_video.h264"
    cmd = f"rpicam-vid -o {video_file} --timeout 5000 --width 1920 --height 1080"
    
    stdout, stderr, code = run_command(cmd)
    
    if code == 0 and os.path.exists(video_file):
        size = os.path.getsize(video_file) / 1024  # KB
        print(f"✓ Video captured: {video_file} ({size:.1f} KB)")
    else:
        print(f"✗ Video capture failed")
        if stderr:
            print(f"Error: {stderr}")
    
    print("\n" + "=" * 60)
    print("Camera test completed!")
    print("=" * 60)
    print(f"\nTest files saved in: {output_dir}/")
    print("\nTo download images to your PC:")
    print(f"  scp -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197:{output_dir}/* ./")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_camera())
