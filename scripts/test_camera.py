#!/usr/bin/env python3
"""
Test Raspberry Pi Camera Module
Captures test images and verifies camera functionality
"""

import sys
import time
from datetime import datetime

try:
    from picamera2 import Picamera2
    try:
        from libcamera import controls
    except ImportError:
        controls = None
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "picamera2", "--break-system-packages"])
    from picamera2 import Picamera2
    try:
        from libcamera import controls
    except ImportError:
        controls = None

def test_camera():
    """Test camera module and capture sample images"""
    print("=" * 60)
    print("Raspberry Pi Camera Module Test")
    print("=" * 60)
    
    try:
        # Initialize camera
        print("\n1. Initializing camera...")
        picam2 = Picamera2()
        
        # Get camera properties
        print("✓ Camera detected!")
        camera_config = picam2.create_still_configuration()
        print(f"   Resolution: {camera_config['main']['size']}")
        print(f"   Format: {camera_config['main']['format']}")
        
        # Configure camera
        print("\n2. Configuring camera...")
        picam2.configure(camera_config)
        
        # Start camera
        print("\n3. Starting camera...")
        picam2.start()
        time.sleep(2)  # Allow camera to warm up
        print("✓ Camera started!")
        
        # Set auto-focus (if supported)
        if controls:
            try:
                picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
                print("✓ Auto-focus enabled")
            except:
                print("⚠ Auto-focus not available (may be fixed-focus)")
        else:
            print("⚠ libcamera controls not available")
        
        # Capture test images
        print("\n4. Capturing test images...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i in range(3):
            filename = f"/home/beans/camera_test_{timestamp}_{i+1}.jpg"
            print(f"   Capturing image {i+1}/3...")
            picam2.capture_file(filename)
            print(f"   ✓ Saved: {filename}")
            time.sleep(1)
        
        # Get camera metadata
        print("\n5. Camera metadata:")
        metadata = picam2.capture_metadata()
        if 'ExposureTime' in metadata:
            print(f"   Exposure Time: {metadata['ExposureTime']} µs")
        if 'AnalogueGain' in metadata:
            print(f"   Analog Gain: {metadata['AnalogueGain']:.2f}")
        if 'ColourGains' in metadata:
            print(f"   Color Gains: {metadata['ColourGains']}")
        
        # Stop camera
        print("\n6. Stopping camera...")
        picam2.stop()
        picam2.close()
        print("✓ Camera stopped")
        
        print("\n" + "=" * 60)
        print("Camera test completed successfully!")
        print("=" * 60)
        print(f"\nTest images saved in /home/beans/")
        print("You can view them or transfer to your PC for inspection.")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check if camera is properly connected")
        print("2. Enable camera: sudo raspi-config -> Interface Options -> Camera")
        print("3. Reboot after enabling: sudo reboot")
        print("4. Check camera detection: libcamera-hello --list-cameras")
        return 1

if __name__ == "__main__":
    sys.exit(test_camera())
