#!/usr/bin/env python3
"""
Wiring diagnostic — blinks each ULN2003 pin one at a time, 3 sec each.
Watch the LEDs on the ULN2003 board and the motor.
Run from SSH: python3 ~/bean_sorter/test_wiring.py
"""
import lgpio, time

PINS = [
    (25, "IN1"),
    (5,  "IN2"),
    (6,  "IN3"),
    (16, "IN4"),
]

h = lgpio.gpiochip_open(4)
for pin, name in PINS:
    try:
        lgpio.gpio_free(h, pin)
    except Exception:
        pass
    lgpio.gpio_claim_output(h, pin, 0)

print("All pins LOW (all coils OFF). Check: all 4 LEDs should be OFF now.", flush=True)
time.sleep(3)

for pin, name in PINS:
    print(f"  {name} (GPIO{pin}) HIGH — that LED should be ON, motor coil energised", flush=True)
    lgpio.gpio_write(h, pin, 1)
    time.sleep(3)
    lgpio.gpio_write(h, pin, 0)
    print(f"  {name} LOW — LED off", flush=True)
    time.sleep(1)

print("\nNow running slow step sequence (one step every 500ms)...", flush=True)
print("You should see LEDs light in order: A -> B -> C -> D -> A ...", flush=True)
FULL_STEP = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
]
for cycle in range(16):  # 4 full rotations worth of steps
    seq = FULL_STEP[cycle % 4]
    names = [PINS[i][1] for i in range(4) if seq[i]]
    print(f"  Step {cycle+1}: {names[0]} ON", flush=True)
    for i, (pin, _) in enumerate(PINS):
        lgpio.gpio_write(h, pin, seq[i])
    time.sleep(0.5)

print("\nAll coils OFF.", flush=True)
for pin, _ in PINS:
    lgpio.gpio_write(h, pin, 0)

lgpio.gpiochip_close(h)
print("Done. Report what you saw.", flush=True)
