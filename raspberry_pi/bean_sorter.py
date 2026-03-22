#!/usr/bin/env python3
"""
Coffee Bean Sorting System - Raspberry Pi
Real-time detection and sorting using trained model
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import cv2
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import lgpio
import time
from collections import deque
import threading

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================
# Servo Motor (SG90 or MG996R)
SERVO_PIN = 22
MOTOR_RPWM = 13
MOTOR_LPWM = 26
MOTOR_R_EN = 27
MOTOR_L_EN = 21
LED_GOOD = 17
LED_BAD = 5

# ============================================================================
# SERVO POSITIONS (SG90: 50Hz, 1000us=0°, 1500us=90°, 2000us=180°)
# ============================================================================
SERVO_FREQ    = 50
SERVO_CLOSED  = 1000   # us — 0°   (good beans to side)
SERVO_NEUTRAL = 1500   # us — 90°  (center)
SERVO_OPEN    = 2000   # us — 180° (bad beans straight)

# ============================================================================
# MOTOR SPEEDS
# ============================================================================
CONVEYOR_SPEED = 50  # PWM duty cycle (0-100)

# ============================================================================
# DETECTION SETTINGS
# ============================================================================
DETECTION_CONFIDENCE = 0.7  # Minimum confidence threshold
DETECTION_DELAY = 1.5       # Seconds between detections
SERVO_ACTIVATION_DELAY = 0.8  # Time for bean to reach servo gate


class BeanSorter:
    """Main bean sorting system"""
    
    def __init__(self, model_path):
        """Initialize the sorting system"""
        print("="*70)
        print("COFFEE BEAN SORTING SYSTEM")
        print("="*70)
        
        # Load model
        print("Loading model...")
        self.model = keras.models.load_model(model_path)
        print("✓ Model loaded")
        
        # Setup GPIO
        print("Setting up GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self._setup_gpio()
        print("✓ GPIO configured")
        
        # Setup camera
        print("Initializing camera...")
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        self.camera.configure(config)
        self.camera.start()
        time.sleep(2)  # Camera warm-up
        print("✓ Camera ready")
        
        # Detection state
        self.running = False
        self.last_detection_time = 0
        self.detection_queue = deque(maxlen=5)  # Smooth predictions
        
        # Statistics
        self.stats = {
            'good_beans': 0,
            'bad_beans': 0,
            'total_processed': 0
        }
        
        print("✓ System ready!")
        print("="*70)
    
    def _setup_gpio(self):
        """Configure GPIO pins"""
        # Servo via lgpio (hardware-accurate PWM on Pi 5)
        self._lg = lgpio.gpiochip_open(4)
        lgpio.gpio_claim_output(self._lg, SERVO_PIN)
        self._set_servo_us(SERVO_NEUTRAL)

        # Motor driver via RPi.GPIO
        GPIO.setup(MOTOR_RPWM, GPIO.OUT)
        GPIO.setup(MOTOR_LPWM, GPIO.OUT)
        GPIO.setup(MOTOR_R_EN, GPIO.OUT)
        GPIO.setup(MOTOR_L_EN, GPIO.OUT)

        self.motor_rpwm = GPIO.PWM(MOTOR_RPWM, 1000)
        self.motor_lpwm = GPIO.PWM(MOTOR_LPWM, 1000)

        GPIO.output(MOTOR_R_EN, GPIO.HIGH)
        GPIO.output(MOTOR_L_EN, GPIO.HIGH)

        # LED setup
        GPIO.setup(LED_GOOD, GPIO.OUT)
        GPIO.setup(LED_BAD, GPIO.OUT)
        GPIO.output(LED_GOOD, GPIO.LOW)
        GPIO.output(LED_BAD, GPIO.LOW)

    def _set_servo_us(self, pulsewidth_us):
        """Set SG90 servo via lgpio pulsewidth (us)"""
        period_us = 1_000_000 / SERVO_FREQ
        duty = (pulsewidth_us / period_us) * 100
        lgpio.tx_pwm(self._lg, SERVO_PIN, SERVO_FREQ, duty)
    
    def set_servo_position(self, pulsewidth_us):
        """Set servo position (us), hold, then idle"""
        self._set_servo_us(pulsewidth_us)
        time.sleep(0.4)
        lgpio.tx_pwm(self._lg, SERVO_PIN, 0, 0)
    
    def start_conveyor(self, speed=CONVEYOR_SPEED):
        """Start conveyor belt forward"""
        self.motor_rpwm.start(speed)
        self.motor_lpwm.start(0)
    
    def stop_conveyor(self):
        """Stop conveyor belt"""
        self.motor_rpwm.ChangeDutyCycle(0)
        self.motor_lpwm.ChangeDutyCycle(0)
    
    def preprocess_image(self, frame):
        """Preprocess camera frame for model"""
        # Resize to model input size
        img = cv2.resize(frame, (224, 224))
        # Convert to array and normalize
        img_array = np.array(img, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def predict_bean_quality(self, frame):
        """Predict if bean is good or bad"""
        # Preprocess
        img_array = self.preprocess_image(frame)
        
        # Predict
        predictions = self.model.predict(img_array, verbose=0)
        confidence = np.max(predictions[0])
        predicted_class = np.argmax(predictions[0])
        
        # Class 0 = bad, Class 1 = good
        is_good = predicted_class == 1
        
        return is_good, confidence
    
    def sort_bean(self, is_good):
        """Control servo to sort bean"""
        if is_good:
            # Good bean: Close gate (bean goes to side)
            print("  → GOOD BEAN: Gate CLOSED (to side)")
            self.set_servo_position(SERVO_CLOSED)
            GPIO.output(LED_GOOD, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(LED_GOOD, GPIO.LOW)
            self.stats['good_beans'] += 1
        else:
            # Bad bean: Open gate (bean goes straight)
            print("  → BAD BEAN: Gate OPEN (straight)")
            self.set_servo_position(SERVO_OPEN)
            GPIO.output(LED_BAD, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(LED_BAD, GPIO.LOW)
            self.stats['bad_beans'] += 1
        
        self.stats['total_processed'] += 1
        
        # Return to neutral after delay
        time.sleep(0.5)
        self.set_servo_position(SERVO_NEUTRAL)
    
    def detect_and_sort(self, frame):
        """Main detection and sorting logic"""
        current_time = time.time()
        
        # Check if enough time has passed since last detection
        if current_time - self.last_detection_time < DETECTION_DELAY:
            return None
        
        # Predict
        is_good, confidence = self.predict_bean_quality(frame)
        
        # Only act if confidence is high enough
        if confidence >= DETECTION_CONFIDENCE:
            self.last_detection_time = current_time
            
            # Schedule servo activation after delay (bean travel time)
            threading.Timer(
                SERVO_ACTIVATION_DELAY,
                self.sort_bean,
                args=(is_good,)
            ).start()
            
            return is_good, confidence
        
        return None
    
    def draw_overlay(self, frame, detection_result=None):
        """Draw detection overlay on frame"""
        # Draw detection zone
        h, w = frame.shape[:2]
        zone_x1, zone_y1 = w//4, h//4
        zone_x2, zone_y2 = 3*w//4, 3*h//4
        cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), 
                     (255, 255, 0), 2)
        cv2.putText(frame, "DETECTION ZONE", (zone_x1, zone_y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Draw detection result
        if detection_result:
            is_good, confidence = detection_result
            label = "GOOD BEAN" if is_good else "BAD BEAN"
            color = (0, 255, 0) if is_good else (0, 0, 255)
            
            cv2.putText(frame, f"{label} ({confidence*100:.1f}%)", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, color, 2)
        
        # Draw statistics
        cv2.putText(frame, f"Good: {self.stats['good_beans']}", 
                   (10, h-70), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Bad: {self.stats['bad_beans']}", 
                   (10, h-40), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"Total: {self.stats['total_processed']}", 
                   (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        
        return frame
    
    def run(self):
        """Main sorting loop"""
        print("\nStarting sorting system...")
        print("Press 'q' to quit, 's' to toggle conveyor")
        print("-"*70)
        
        self.running = True
        conveyor_running = False
        
        try:
            while self.running:
                # Capture frame
                frame = self.camera.capture_array()
                
                # Detect and sort
                detection_result = self.detect_and_sort(frame)
                
                # Draw overlay
                display_frame = self.draw_overlay(frame.copy(), detection_result)
                
                # Show frame
                cv2.imshow('Bean Sorter', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nShutting down...")
                    break
                elif key == ord('s'):
                    conveyor_running = not conveyor_running
                    if conveyor_running:
                        print("Conveyor: STARTED")
                        self.start_conveyor()
                    else:
                        print("Conveyor: STOPPED")
                        self.stop_conveyor()
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")
        
        # Stop conveyor
        self.stop_conveyor()

        # Reset servo to neutral then close lgpio
        self._set_servo_us(SERVO_NEUTRAL)
        time.sleep(0.5)
        lgpio.tx_pwm(self._lg, SERVO_PIN, 0, 0)
        lgpio.gpiochip_close(self._lg)

        # Stop PWM
        self.motor_rpwm.stop()
        self.motor_lpwm.stop()

        # Cleanup GPIO
        GPIO.cleanup()
        
        # Stop camera
        self.camera.stop()
        cv2.destroyAllWindows()
        
        # Print final statistics
        print("\n" + "="*70)
        print("SORTING SESSION COMPLETE")
        print("="*70)
        print(f"Good beans sorted: {self.stats['good_beans']}")
        print(f"Bad beans sorted: {self.stats['bad_beans']}")
        print(f"Total processed: {self.stats['total_processed']}")
        if self.stats['total_processed'] > 0:
            good_rate = (self.stats['good_beans'] / self.stats['total_processed']) * 100
            print(f"Good bean rate: {good_rate:.1f}%")
        print("="*70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Coffee Bean Sorting System'
    )
    parser.add_argument('model', help='Path to trained model (.keras)')
    parser.add_argument('--speed', type=int, default=CONVEYOR_SPEED,
                       help='Conveyor speed (0-100)')
    parser.add_argument('--confidence', type=float, default=DETECTION_CONFIDENCE,
                       help='Detection confidence threshold (0-1)')
    
    args = parser.parse_args()
    
    # Update global settings
    global CONVEYOR_SPEED, DETECTION_CONFIDENCE
    CONVEYOR_SPEED = args.speed
    DETECTION_CONFIDENCE = args.confidence
    
    # Create and run sorter
    sorter = BeanSorter(args.model)
    sorter.run()


if __name__ == "__main__":
    main()
