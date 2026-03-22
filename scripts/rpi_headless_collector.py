#!/usr/bin/env python3
"""
Headless Dataset Collector for Raspberry Pi
Runs directly on Raspberry Pi without GUI
Control via SSH commands or web interface
"""

import os
import json
from datetime import datetime
import subprocess
import sys

class HeadlessCollector:
    """
    Headless dataset collector for Raspberry Pi
    No GUI needed - runs in terminal
    """
    
    def __init__(self):
        # Dataset configuration
        self.base_dir = "/home/beans/coffee_dataset_final"
        self.beans_per_set = 50
        
        # Target counts
        self.targets = {
            'good_curve': 1050,
            'good_back': 450,
            'bad_curve': 1050,
            'bad_back': 450
        }
        
        # Calculate sets needed
        self.sets_needed = {
            'good_curve': 21,
            'good_back': 9,
            'bad_curve': 21,
            'bad_back': 9
        }
        
        # Current counts
        self.counts = self.load_counts()
        
        # Setup directories
        self.setup_directories()
    
    def setup_directories(self):
        """Create dataset directory structure"""
        dirs = [
            f"{self.base_dir}/good_beans/curve",
            f"{self.base_dir}/good_beans/back",
            f"{self.base_dir}/bad_beans/curve",
            f"{self.base_dir}/bad_beans/back"
        ]
        
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def load_counts(self):
        """Load current counts"""
        count_file = "/home/beans/dataset_counts_final.json"
        
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'good_curve': 0,
                'good_back': 0,
                'bad_curve': 0,
                'bad_back': 0
            }
    
    def save_counts(self):
        """Save current counts"""
        count_file = "/home/beans/dataset_counts_final.json"
        with open(count_file, 'w') as f:
            json.dump(self.counts, f, indent=2)
    
    def show_status(self):
        """Show current progress"""
        print("\n" + "="*60)
        print("Coffee Bean Dataset Collection Status")
        print("="*60)
        
        for key in ['good_curve', 'good_back', 'bad_curve', 'bad_back']:
            current = self.counts[key]
            needed = self.sets_needed[key]
            beans_collected = current * self.beans_per_set
            total_beans = self.targets[key]
            percentage = (current / needed) * 100 if needed > 0 else 0
            
            quality, side = key.split('_')
            print(f"\n{quality.title()} - {side.title()}:")
            print(f"  Sets: {current}/{needed} ({percentage:.1f}%)")
            print(f"  Beans: {beans_collected}/{total_beans}")
        
        total_sets = sum(self.counts.values())
        total_needed = sum(self.sets_needed.values())
        total_percentage = (total_sets / total_needed) * 100 if total_needed > 0 else 0
        
        print(f"\nTotal Progress: {total_sets}/{total_needed} sets ({total_percentage:.1f}%)")
        print("="*60 + "\n")
    
    def capture_image(self, category):
        """Capture image for specified category"""
        # Parse category
        if category not in self.counts:
            print(f"Error: Invalid category '{category}'")
            print("Valid: good_curve, good_back, bad_curve, bad_back")
            return False
        
        # Check if target reached
        if self.counts[category] >= self.sets_needed[category]:
            print(f"Target for {category} already reached!")
            return False
        
        quality, side = category.split('_')
        current_set = self.counts[category] + 1
        
        print(f"\nCapturing {quality} {side} - Set {current_set}/{self.sets_needed[category]}")
        print("Make sure 50 beans are arranged...")
        
        # Generate filename
        output_dir = f"{self.base_dir}/{quality}_beans/{side}"
        filename = f"{quality}_{side}_set{current_set:02d}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # Capture image
        print("Capturing...")
        capture_cmd = [
            "rpicam-still", "-o", filepath,
            "--width", "4608", "--height", "2592",
            "--timeout", "5000",
            "--autofocus-mode", "auto",
            "--autofocus-range", "macro",
            "--lens-position", "0.0",
            "--contrast", "1.2",
            "--sharpness", "1.8",
            "--saturation", "1.0",
            "--quality", "95",
            "--nopreview"
        ]
        
        try:
            result = subprocess.run(capture_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Update counts
                self.counts[category] += 1
                self.save_counts()
                
                beans_collected = self.counts[category] * self.beans_per_set
                print(f"✓ Captured: {filename}")
                print(f"  Sets: {self.counts[category]}/{self.sets_needed[category]}")
                print(f"  Beans: {beans_collected}/{self.targets[category]}")
                return True
            else:
                print(f"✗ Capture failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def preview_camera(self):
        """Show camera preview"""
        print("\nStarting camera preview...")
        print("Press Ctrl+C to stop")
        
        try:
            subprocess.run([
                "rpicam-hello",
                "--timeout", "0",  # Continuous
                "--autofocus-mode", "auto",
                "--autofocus-range", "macro"
            ])
        except KeyboardInterrupt:
            print("\nPreview stopped")


def main():
    """Main entry point"""
    collector = HeadlessCollector()
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 rpi_headless_collector.py status")
        print("  python3 rpi_headless_collector.py capture <category>")
        print("  python3 rpi_headless_collector.py preview")
        print("\nCategories:")
        print("  good_curve, good_back, bad_curve, bad_back")
        print("\nExamples:")
        print("  python3 rpi_headless_collector.py status")
        print("  python3 rpi_headless_collector.py capture bad_curve")
        print("  python3 rpi_headless_collector.py preview")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        collector.show_status()
    
    elif command == "capture":
        if len(sys.argv) < 3:
            print("Error: Category required")
            print("Usage: python3 rpi_headless_collector.py capture <category>")
            sys.exit(1)
        
        category = sys.argv[2].lower()
        collector.capture_image(category)
    
    elif command == "preview":
        collector.preview_camera()
    
    else:
        print(f"Unknown command: {command}")
        print("Valid commands: status, capture, preview")
        sys.exit(1)


if __name__ == "__main__":
    main()
