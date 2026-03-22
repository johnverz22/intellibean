#!/usr/bin/env python3
"""Quick GPIO test - conveyor 3s then servo sweep"""
import RPi.GPIO as GPIO
import time

SERVO_PIN  = 23
MOTOR_RPWM = 13
MOTOR_LPWM = 26
MOTOR_R_EN = 27
MOTOR_L_EN = 21

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor
GPIO.setup(MOTOR_RPWM, GPIO.OUT)
GPIO.setup(MOTOR_LPWM, GPIO.OUT)
GPIO.setup(MOTOR_R_EN, GPIO.OUT)
GPIO.setup(MOTOR_L_EN, GPIO.OUT)
GPIO.output(MOTOR_R_EN, GPIO.HIGH)
GPIO.output(MOTOR_L_EN, GPIO.HIGH)
pwm_r = GPIO.PWM(MOTOR_RPWM, 1000)
pwm_l = GPIO.PWM(MOTOR_LPWM, 1000)
pwm_r.start(0)
pwm_l.start(0)

# Servo
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(7.5)

try:
    print("TEST 1: Conveyor ON at 50% for 3 seconds...")
    pwm_r.ChangeDutyCycle(50)
    time.sleep(3)
    pwm_r.ChangeDutyCycle(0)
    print("Conveyor OFF")
    time.sleep(1)

    print("TEST 2: Servo OPEN (180 deg)...")
    servo.ChangeDutyCycle(12.5)
    time.sleep(1)

    print("TEST 3: Servo NEUTRAL (90 deg)...")
    servo.ChangeDutyCycle(7.5)
    time.sleep(1)

    print("TEST 4: Servo CLOSED (0 deg)...")
    servo.ChangeDutyCycle(2.5)
    time.sleep(1)

    print("TEST 5: Servo back to NEUTRAL...")
    servo.ChangeDutyCycle(7.5)
    time.sleep(0.5)
    servo.ChangeDutyCycle(0)

    print("ALL TESTS DONE")

finally:
    pwm_r.stop()
    pwm_l.stop()
    servo.stop()
    GPIO.cleanup()
