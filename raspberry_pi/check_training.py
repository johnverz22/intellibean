#!/usr/bin/env python3
"""
Quick check: is training done? Is the new model any good?
Run on Pi: python3 ~/bean_sorter/check_training.py
"""
import os, sys, numpy as np

BASE = os.path.expanduser('~/bean_sorter')
KERAS  = os.path.join(BASE, 'best_model_new.keras')
TFLITE = os.path.join(BASE, 'best_model_new.tflite')

print("=== Training Status Check ===")

# Check if process still running
import subprocess
r = subprocess.run(['pgrep', '-f', 'retrain.py'], capture_output=True, text=True)
if r.stdout.strip():
    print(f"Training still running (PID {r.stdout.strip()})")
else:
    print("Training process: DONE (not running)")

# Check files
print(f"\nKeras model:  {'EXISTS' if os.path.exists(KERAS) else 'MISSING'}", end='')
if os.path.exists(KERAS):
    print(f"  ({os.path.getsize(KERAS)//1024} KB)")
else:
    print()

print(f"TFLite model: {'EXISTS' if os.path.exists(TFLITE) else 'MISSING'}", end='')
if os.path.exists(TFLITE):
    print(f"  ({os.path.getsize(TFLITE)//1024} KB)")
else:
    print()

if not os.path.exists(TFLITE):
    print("\nTFLite not ready yet — training still in progress or failed.")
    sys.exit(1)

# Sanity test the tflite
print("\n=== TFLite Sanity Test ===")
try:
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        from tflite_runtime.interpreter import Interpreter

    interp = Interpreter(model_path=TFLITE)
    interp.allocate_tensors()
    inp = interp.get_input_details()
    out = interp.get_output_details()
    print(f"Input shape:  {inp[0]['shape']}")
    print(f"Output shape: {out[0]['shape']}")

    results = []
    for tag, arr in [
        ("zeros  ", np.zeros(inp[0]['shape'], np.float32)),
        ("ones   ", np.ones(inp[0]['shape'], np.float32)),
        ("rand1  ", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
        ("rand2  ", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
        ("rand3  ", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
    ]:
        interp.set_tensor(inp[0]['index'], arr)
        interp.invoke()
        p = interp.get_tensor(out[0]['index'])[0]
        label = 'GOOD' if np.argmax(p) == 1 else 'BAD'
        print(f"  {tag} -> bad={p[0]:.4f}  good={p[1]:.4f}  => {label}")
        results.append(np.argmax(p))

    unique = len(set(results))
    if unique > 1:
        print("\n✓ Model gives VARIED predictions — looks healthy!")
    else:
        print("\n✗ Model predicts the SAME class for everything — still broken!")
        sys.exit(1)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\n=== All good! hardware_test.py will auto-use best_model_new.tflite ===")
