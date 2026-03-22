#!/usr/bin/env python3
"""
Camera Detection Module for Coffee Bean Sorter
Captures images and detects beans in the feed lane
"""

import time
import subprocess
from datetime import datetime
import os

class CameraDetector:
    """
    Handles camera operations for bean detection
    
    Uses rpicam-still for fast image capture
    """
    
    def __init__(self, output_dir="/home/beans/bean_images"):
        """
        Initialize camera detector
        
        Args:
            output_dir: Directory to save captured images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Camera settings optimized for fast capture
        self.width = 1536  # Lower resolution for speed
        self.height = 864
        self.timeout = 500  # 500ms capture timeout
        
        print("✓ Camera detector initialized")
        print(f"  Resolution: {self.width}x{self.height}")
        print(f"  Output dir: {self.output_dir}")
    
    def capture_image(self, filename=None, save=True):
        """
        Capture single image
        
        Args:
            filename: Output filename (auto-generated if None)
            save: Whether to save image to disk
        
        Returns:
            str: Path to captured image
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"bean_{timestamp}.jpg"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Use rpicam-still for fast capture
        cmd = [
            "rpicam-still",
            "-o", filepath,
            "--width", str(self.width),
            "--height", str(self.height),
            "--timeout", str(self.timeout),
            "--nopreview",  # No preview window
            "--immediate"   # Capture immediately
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and os.path.exists(filepath):
                return filepath
            else:
                print(f"✗ Capture failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("✗ Capture timeout")
            return None
        except Exception as e:
            print(f"✗ Capture error: {e}")
            return None
    
    def detect_bean_in_zone(self):
        """
        Detect if bean is in detection zone
        
        This is a placeholder - implement actual detection logic:
        - Motion detection
        - Object detection
        - Trigger sensor
        
        Returns:
            bool: True if bean detected
        """
        # TODO: Implement actual detection
        # For now, return True for testing
        return True
    
    def wait_for_bean(self, timeout=10):
        """
        Wait for bean to enter detection zone
        
        Args:
            timeout: Maximum seconds to wait
        
        Returns:
            bool: True if bean detected, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.detect_bean_in_zone():
                return True
            time.sleep(0.01)  # 10ms polling
        
        return False
    
    def test_capture(self, num_images=3):
        """Test camera by capturing multiple images"""
        print("\n" + "="*50)
        print("Camera Capture Test")
        print("="*50)
        
        for i in range(num_images):
            print(f"\nCapturing image {i+1}/{num_images}...")
            filepath = self.capture_image()
            
            if filepath:
                size = os.path.getsize(filepath) / 1024  # KB
                print(f"✓ Saved: {filepath} ({size:.1f} KB)")
            else:
                print("✗ Capture failed")
            
            time.sleep(1)
        
        print("\n✓ Camera test complete")


# Test code
if __name__ == "__main__":
    detector = CameraDetector()
    detector.test_capture(num_images=5)
