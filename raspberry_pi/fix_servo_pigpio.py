#!/usr/bin/env python3
"""
Servo test using pigpio for hardware-accurate PWM on Pi 5
GPIO SERVO_PIN = 23
Run: sudo pigpiod first, then python3 fix_servo_pigpio.py
"""

import pigpio
import time

SERVO_PIN = 23

# pigpio uses microseconds for servo pulsewidth
# Standard servo: 500us=0deg, 1500us=90deg, 2500us=180deg
SERVO_0   = 500
SERVO_90  = 1500
SERVO_180 = 2500

pi = pigpio.pi()
if not pi.connected:
    print("ERROR: pigpiod daemon not running. Run: sudo pigpiod")
    exit(1)

print(f"pigpio connected. Testing servo on GPIO {SERVO_PIN}")
print("Pulsewidth: 500us=0deg, 1500us=90deg, 2500us=180deg\n")

positions = [
    (SERVO_0,   "0 deg   (min)"),
    (SERVO_90,  "90 deg  (center)"),
    (SERVO_180, "180 deg (max)"),
    (SERVO_90,  "90 deg  (back to center)"),
]

for pw, label in positions:
    print(f"  pulsewidth={pw}us -> {label}")
    pi.set_servo_pulsewidth(SERVO_PIN, pw)
    time.sleep(2)

# Stop servo signal
pi.set_servo_pulsewidth(SERVO_PIN, 0)
pi.stop()
print("\nDone.")
