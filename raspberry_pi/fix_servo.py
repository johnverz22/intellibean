#!/usr/bin/env python3
"""
Servo Fix Test - tries different duty cycles to find what works
GPIO SERVO_PIN = 23
"""

import RPi.GPIO as GPIO
import time

SERVO_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(7.5)  # start at neutral, keep signal alive
time.sleep(1)

print("Testing servo on GPIO 23 (BCM) = physical pin 16")
print("Keeping PWM signal CONTINUOUS (no stop between moves)\n")

positions = [
    (2.5,  "0 deg   (min)"),
    (5.0,  "45 deg"),
    (7.5,  "90 deg  (center)"),
    (10.0, "135 deg"),
    (12.5, "180 deg (max)"),
    (7.5,  "90 deg  (back to center)"),
]

for duty, label in positions:
    print(f"  duty={duty:5.1f}  -> {label}")
    servo.ChangeDutyCycle(duty)
    time.sleep(2)   # hold position 2 seconds

print("\nDone. Stopping PWM.")
servo.stop()
GPIO.cleanup()
