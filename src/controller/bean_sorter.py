#!/usr/bin/env python3
"""
Main Coffee Bean Sorter Application
Integrates camera detection, ML classification, and servo control
"""

import time
import sys
import os
from datetime import datetime

# Import our modules
from servo_controller import ServoController
from camera_detector import CameraDetector

class BeanSorter:
    """
    Main sorter application
    
    Workflow:
    1. Wait for bean in detection zone
    2. Capture image
    3. Classify bean (ML model)
    4. Calculate timing delay
    5. Actuate gate at right moment
    """
    
    def __init__(self, travel_time=1.5):
        """
        Initialize bean sorter
        
        Args:
            travel_time: Time (seconds) for bean to travel from camera to gate
        """
        print("="*60)
        print("Coffee Bean Sorter - Initializing")
        print("="*60)
        
        # Initialize components
        self.servo = ServoController()
        self.camera = CameraDetector()
        
        # Timing configuration
        self.travel_time = travel_time  # Camera to gate travel time
        self.processing_time = 0.1      # ML inference time estimate
        
        # Statistics
        self.stats = {
            'total': 0,
            'good': 0,
            'bad': 0,
            'errors': 0
        }
        
        print(f"\n✓ Sorter initialized")
        print(f"  Travel time: {self.travel_time}s")
        print(f"  Processing time: {self.processing_time}s")
    
    def classify_bean(self, image_path):
        """
        Classify bean as GOOD or BAD using ML model
        
        Args:
            image_path: Path to captured image
        
        Returns:
            str: 'good' or 'bad'
            float: Confidence score (0-1)
        
        TODO: Implement actual ML model
        For now, returns random classification for testing
        """
        # Placeholder - replace with actual ML model
        import random
        
        # Simulate processing time
        time.sleep(self.processing_time)
        
        # Random classification for testing
        classification = random.choice(['good', 'bad'])
        confidence = random.uniform(0.7, 0.99)
        
        return classification, confidence
    
    def process_bean(self):
        """
        Process single bean through the system
        
        Returns:
            bool: True if successful, False if error
        """
        try:
            # 1. Capture image
            print("\n📷 Capturing bean image...")
            image_path = self.camera.capture_image()
            
            if not image_path:
                print("✗ Failed to capture image")
                self.stats['errors'] += 1
                return False
            
            print(f"✓ Image captured: {image_path}")
            
            # 2. Classify bean
            print("🤖 Classifying bean...")
            classification, confidence = self.classify_bean(image_path)
            
            print(f"✓ Classification: {classification.upper()} ({confidence:.1%} confidence)")
            
            # 3. Calculate actuation delay
            # Delay = travel_time - processing_time (already spent)
            actuation_delay = max(0, self.travel_time - self.processing_time)
            
            # 4. Sort bean
            self.servo.sort_bean(classification, delay=actuation_delay)
            
            # 5. Update statistics
            self.stats['total'] += 1
            if classification == 'good':
                self.stats['good'] += 1
            else:
                self.stats['bad'] += 1
            
            return True
            
        except Exception as e:
            print(f"✗ Error processing bean: {e}")
            self.stats['errors'] += 1
            return False
    
    def run_continuous(self, max_beans=None):
        """
        Run sorter in continuous mode
        
        Args:
            max_beans: Maximum beans to process (None = infinite)
        """
        print("\n" + "="*60)
        print("Starting Continuous Sorting Mode")
        print("="*60)
        print("Press Ctrl+C to stop\n")
        
        bean_count = 0
        
        try:
            while True:
                # Check if reached max beans
                if max_beans and bean_count >= max_beans:
                    print(f"\n✓ Processed {max_beans} beans")
                    break
                
                # Wait for bean
                print(f"\n[Bean #{bean_count + 1}] Waiting for bean...")
                
                # In real system, wait for trigger sensor
                # For testing, use keyboard input
                input("Press Enter when bean is in detection zone...")
                
                # Process bean
                success = self.process_bean()
                
                if success:
                    bean_count += 1
                
                # Brief pause between beans
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Stopped by user")
        
        self.print_statistics()
    
    def run_test_mode(self, num_beans=10):
        """
        Run sorter in test mode (simulated beans)
        
        Args:
            num_beans: Number of beans to simulate
        """
        print("\n" + "="*60)
        print(f"Test Mode - Processing {num_beans} simulated beans")
        print("="*60)
        
        for i in range(num_beans):
            print(f"\n{'='*60}")
            print(f"Bean #{i+1}/{num_beans}")
            print('='*60)
            
            self.process_bean()
            
            # Pause between beans
            time.sleep(2)
        
        self.print_statistics()
    
    def print_statistics(self):
        """Print sorting statistics"""
        print("\n" + "="*60)
        print("Sorting Statistics")
        print("="*60)
        print(f"Total beans processed: {self.stats['total']}")
        print(f"Good beans: {self.stats['good']} ({self.stats['good']/max(1,self.stats['total'])*100:.1f}%)")
        print(f"Bad beans: {self.stats['bad']} ({self.stats['bad']/max(1,self.stats['total'])*100:.1f}%)")
        print(f"Errors: {self.stats['errors']}")
        print("="*60)
    
    def calibrate_timing(self):
        """
        Interactive timing calibration
        Helps determine optimal travel_time
        """
        print("\n" + "="*60)
        print("Timing Calibration Mode")
        print("="*60)
        print("\nThis helps you find the correct travel_time")
        print("(time for bean to travel from camera to gate)")
        print("\nSteps:")
        print("1. Place a bean at the camera detection point")
        print("2. Press Enter to start timer")
        print("3. Watch the bean travel")
        print("4. Press Enter when bean reaches the gate")
        print("="*60)
        
        measurements = []
        
        for i in range(3):
            input(f"\nMeasurement {i+1}/3 - Press Enter to start...")
            start_time = time.time()
            
            input("Press Enter when bean reaches gate...")
            travel_time = time.time() - start_time
            
            measurements.append(travel_time)
            print(f"  Measured: {travel_time:.2f}s")
        
        avg_time = sum(measurements) / len(measurements)
        print(f"\n✓ Average travel time: {avg_time:.2f}s")
        print(f"\nUpdate your code:")
        print(f"  sorter = BeanSorter(travel_time={avg_time:.2f})")
    
    def cleanup(self):
        """Cleanup resources"""
        print("\nShutting down...")
        self.servo.cleanup()
        print("✓ Shutdown complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Coffee Bean Sorter')
    parser.add_argument('--mode', choices=['continuous', 'test', 'calibrate-timing', 'calibrate-servo'],
                       default='test', help='Operating mode')
    parser.add_argument('--beans', type=int, default=10,
                       help='Number of beans to process (test mode)')
    parser.add_argument('--travel-time', type=float, default=1.5,
                       help='Bean travel time from camera to gate (seconds)')
    
    args = parser.parse_args()
    
    # Create sorter
    sorter = BeanSorter(travel_time=args.travel_time)
    
    try:
        if args.mode == 'continuous':
            sorter.run_continuous()
        elif args.mode == 'test':
            sorter.run_test_mode(num_beans=args.beans)
        elif args.mode == 'calibrate-timing':
            sorter.calibrate_timing()
        elif args.mode == 'calibrate-servo':
            sorter.servo.calibrate()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        sorter.cleanup()


if __name__ == "__main__":
    main()
