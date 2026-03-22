#!/usr/bin/env python3
"""
Servo test using lgpio (native Pi 5 GPIO library)
GPIO SERVO_PIN = 23 (BCM)
lgpio uses hardware PWM via gpiochip4 on Pi 5
"""

import lgpio
import time

SERVO_PIN = 23  # BCM pin 23

# Servo PWM: 50Hz = 20ms period
# Pulsewidth in microseconds: 500=0deg, 1500=90deg, 2500=180deg
FREQ = 50  # Hz

def us_to_duty(us, freq=50):
    """Convert microseconds pulsewidth to duty cycle percent"""
    period_us = 1_000_000 / freq  # 20000us for 50Hz
    return (us / period_us) * 100

h = lgpio.gpiochip_open(4)  # Pi 5 uses gpiochip4

print(f"lgpio opened gpiochip4. Testing servo on GPIO {SERVO_PIN}")
print("Using hardware PWM via lgpio\n")

# Claim pin for PWM output
lgpio.gpio_claim_output(h, SERVO_PIN)

positions = [
    (500,  "0 deg   (min)"),
    (1500, "90 deg  (center)"),
    (2500, "180 deg (max)"),
    (1500, "90 deg  (back to center)"),
]

for pw_us, label in positions:
    duty = us_to_duty(pw_us)
    print(f"  pulsewidth={pw_us}us  duty={duty:.1f}%  -> {label}")
    lgpio.tx_pwm(h, SERVO_PIN, FREQ, duty)
    time.sleep(2)

# Stop PWM
lgpio.tx_pwm(h, SERVO_PIN, 0, 0)
lgpio.gpiochip_close(h)
print("\nDone.")
