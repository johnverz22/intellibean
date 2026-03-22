#!/usr/bin/env python3
"""Emergency GPIO reset — kills stale processes then frees all pins."""
import lgpio, time, subprocess, sys

MOTOR_RPWM      = 13
MOTOR_LPWM      = 26
MOTOR_R_EN      = 27
MOTOR_L_EN      = 21
SERVO_PIN       = 22
SIM_PINS        = [25, 5, 6, 16]
LED_RUNNING     = 20
LED_NOT_RUNNING = 12
BTN_START       = 19
BTN_STOP        = 24

ALL_OUT_PINS = [MOTOR_RPWM, MOTOR_LPWM, MOTOR_R_EN, MOTOR_L_EN, SERVO_PIN,
                LED_RUNNING, LED_NOT_RUNNING] + SIM_PINS
ALL_IN_PINS  = [BTN_START, BTN_STOP]

# Kill any stale hardware_test or bean_sorter processes
print("Killing stale processes...", flush=True)
subprocess.run(['pkill', '-f', 'hardware_test'], capture_output=True)
subprocess.run(['pkill', '-f', 'bean_sorter'],   capture_output=True)
time.sleep(1.0)  # give OS time to release GPIOs

try:
    h = lgpio.gpiochip_open(4)
    print("Opened gpiochip4 (Pi 5)", flush=True)
except Exception as e:
    print(f"gpiochip4 failed ({e}), trying gpiochip0")
    h = lgpio.gpiochip_open(0)

for pin in ALL_OUT_PINS:
    try: lgpio.tx_pwm(h, pin, 0, 0)
    except Exception: pass
    try: lgpio.gpio_free(h, pin)
    except Exception: pass
    try:
        lgpio.gpio_claim_output(h, pin, 0)
        lgpio.gpio_write(h, pin, 0)
        lgpio.gpio_free(h, pin)
        print(f"  GPIO{pin} cleared", flush=True)
    except Exception as e:
        print(f"  GPIO{pin} error: {e}", flush=True)

for pin in ALL_IN_PINS:
    try: lgpio.gpio_free(h, pin)
    except Exception: pass
    try:
        lgpio.gpio_claim_input(h, pin, lgpio.SET_PULL_UP)
        lgpio.gpio_free(h, pin)
        print(f"  GPIO{pin} (input) cleared", flush=True)
    except Exception as e:
        print(f"  GPIO{pin} input error: {e}", flush=True)

lgpio.gpiochip_close(h)
print("GPIO reset complete.", flush=True)
