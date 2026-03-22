#!/usr/bin/env python3
"""
Standalone stepper test — no display needed, run from SSH.
Tests ULN2003 + 28BYJ-48 on GPIO 25,5,6,16
"""
import lgpio, time, sys

SIM_PINS = [25, 5, 6, 16]
# ULN2003 is inverting: 0 = coil ON, 1 = coil OFF
STEP_SEQ = [
    [0, 1, 1, 1],
    [0, 0, 1, 1],
    [1, 0, 1, 1],
    [1, 0, 0, 1],
    [1, 1, 0, 1],
    [1, 1, 0, 0],
    [1, 1, 1, 0],
    [0, 1, 1, 0],
]

print("Opening gpiochip...", flush=True)
try:
    h = lgpio.gpiochip_open(4)
    print("Opened gpiochip4 (Pi 5)", flush=True)
except Exception as e:
    print(f"gpiochip4 failed: {e}, trying 0", flush=True)
    h = lgpio.gpiochip_open(0)

print("Claiming pins...", flush=True)
for pin in SIM_PINS:
    try:
        lgpio.gpio_free(h, pin)
    except Exception:
        pass
    ret = lgpio.gpio_claim_output(h, pin, 0)
    print(f"  GPIO{pin}: {'OK' if ret == 0 else f'ERROR {ret}'}", flush=True)

print("\nTesting each pin individually (1 sec each)...", flush=True)
for i, pin in enumerate(SIM_PINS):
    print(f"  GPIO{pin} HIGH (IN{i+1})", flush=True)
    lgpio.gpio_write(h, pin, 1)
    time.sleep(1)
    lgpio.gpio_write(h, pin, 0)
    time.sleep(0.2)

print("\nRunning stepper sequence for 5 seconds...", flush=True)
step_delay = 0.003
start = time.time()
idx = 0
while time.time() - start < 5:
    seq = STEP_SEQ[idx % 8]
    for i, pin in enumerate(SIM_PINS):
        lgpio.gpio_write(h, pin, seq[i])
    idx += 1
    time.sleep(step_delay)

print("Stopping — all coils off (write 1 = deactivate for ULN2003)", flush=True)
for pin in SIM_PINS:
    lgpio.gpio_write(h, pin, 1)

lgpio.gpiochip_close(h)
print("Done.", flush=True)
