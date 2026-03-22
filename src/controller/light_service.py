#!/usr/bin/env python3
"""
Persistent LED Light Service
Keeps GPIO 13 active for continuous light control
"""

import RPi.GPIO as GPIO
import sys
import time

# GPIO Configuration
GPIO_PIN = 13
PWM_FREQ = 1000  # 1 kHz

def setup_light():
    """Initialize GPIO and PWM"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(GPIO_PIN, PWM_FREQ)
    pwm.start(0)
    return pwm

def set_brightness(pwm, brightness):
    """Set brightness (0-100)"""
    if brightness < 0:
        brightness = 0
    elif brightness > 100:
        brightness = 100
    pwm.ChangeDutyCycle(brightness)
    print(f"Brightness set to {brightness}%")

def main():
    """Main service loop"""
    if len(sys.argv) < 2:
        print("Usage: python3 light_service.py <brightness>")
        print("Example: python3 light_service.py 80")
        sys.exit(1)
    
    try:
        brightness = int(sys.argv[1])
    except ValueError:
        print("Error: Brightness must be a number (0-100)")
        sys.exit(1)
    
    # Setup
    pwm = setup_light()
    
    # Set brightness
    set_brightness(pwm, brightness)
    
    # Keep running (don't cleanup)
    print(f"Light service running at {brightness}%")
    print("GPIO 13 active - Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping light service...")
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
