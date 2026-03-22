#!/usr/bin/env python3
"""
Voltage test — holds each pin HIGH for 10 seconds.
While running, measure voltage at ULN2003 IN pin with multimeter.
Should read ~3.3V when HIGH, ~0V when LOW.
"""
import lgpio, time

PINS = [(25,"IN1"), (5,"IN2"), (6,"IN3"), (16,"IN4")]

h = lgpio.gpiochip_open(4)
for pin, _ in PINS:
    try: lgpio.gpio_free(h, pin)
    except: pass
    lgpio.gpio_claim_output(h, pin, 0)

print("ALL PINS LOW — measure voltage at IN1,IN2,IN3,IN4 — should all be 0V", flush=True)
time.sleep(5)

for pin, name in PINS:
    lgpio.gpio_write(h, pin, 1)
    print(f"{name} (GPIO{pin}) HIGH for 10s — measure voltage at ULN2003 {name} pin now", flush=True)
    time.sleep(10)
    lgpio.gpio_write(h, pin, 0)
    print(f"  {name} back LOW", flush=True)
    time.sleep(2)

for pin, _ in PINS:
    lgpio.gpio_write(h, pin, 0)
lgpio.gpiochip_close(h)
print("Done.", flush=True)
