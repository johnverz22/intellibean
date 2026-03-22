#!/usr/bin/env python3
"""
Stepper test v2 — slow and simple, run from SSH.
Uses FULL-STEP sequence (easier for ULN2003 to drive).
GPIO 25=IN1, 5=IN2, 6=IN3, 16=IN4
"""
import lgpio, time

SIM_PINS = [25, 5, 6, 16]  # IN1, IN2, IN3, IN4

# Full-step sequence (4 steps) — simpler, more torque than half-step
# ULN2003 is NOT inverting when used with 28BYJ-48 in the standard wiring
# The IN pins directly drive the transistor base: HIGH = transistor ON = coil energised
FULL_STEP = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
]

print("Opening gpiochip4...", flush=True)
h = lgpio.gpiochip_open(4)

print("Claiming pins (with free first)...", flush=True)
for pin in SIM_PINS:
    try:
        lgpio.gpio_free(h, pin)
    except Exception:
        pass
    ret = lgpio.gpio_claim_output(h, pin, 0)
    print(f"  GPIO{pin}: {'OK' if ret == 0 else f'ERROR {ret}'}", flush=True)

# All off first
for pin in SIM_PINS:
    lgpio.gpio_write(h, pin, 0)
time.sleep(0.5)

print("\nTesting each coil individually (2 sec each)...", flush=True)
for i, pin in enumerate(SIM_PINS):
    print(f"  Energising IN{i+1} (GPIO{pin}) — LED should light", flush=True)
    lgpio.gpio_write(h, pin, 1)
    time.sleep(2)
    lgpio.gpio_write(h, pin, 0)
    time.sleep(0.3)

print("\nRunning FULL-STEP at 10ms/step for 5 seconds...", flush=True)
DELAY = 0.010  # 10ms per step — slow enough to see movement
start = time.time()
idx = 0
while time.time() - start < 5:
    seq = FULL_STEP[idx % 4]
    for i, pin in enumerate(SIM_PINS):
        lgpio.gpio_write(h, pin, seq[i])
    idx += 1
    time.sleep(DELAY)

print("All coils off.", flush=True)
for pin in SIM_PINS:
    lgpio.gpio_write(h, pin, 0)

lgpio.gpiochip_close(h)
print("Done.", flush=True)
