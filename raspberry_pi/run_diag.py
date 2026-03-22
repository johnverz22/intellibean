#!/usr/bin/env python3
"""
Headless diagnostic — no display needed.
Captures 10 frames, runs TFLite model on each, logs pixel stats + predictions.
Output written to /tmp/bean_diag.txt
"""
import time, os, sys, subprocess
import numpy as np
from picamera2 import Picamera2
from PIL import Image

LOG = "/tmp/bean_diag.txt"

_base = os.path.expanduser('~/bean_sorter')

# Test ALL tflite models found
import glob
all_models = sorted(glob.glob(os.path.join(_base, '*.tflite')))

lines = []
def log(s):
    print(s, flush=True)
    lines.append(s)

log(f"=== Bean Diagnostic {time.strftime('%H:%M:%S')} ===")
log(f"Found models: {all_models}\n")

if not all_models:
    log("ERROR: No .tflite files found")
    open(LOG, 'w').write('\n'.join(lines))
    sys.exit(1)

try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    from tflite_runtime.interpreter import Interpreter

tests = {
    "pure white":   np.full((224,224,3), 220, dtype=np.float32),
    "mid grey":     np.full((224,224,3), 128, dtype=np.float32),
    "green sim":    np.array([[[60, 120, 40]]*224]*224, dtype=np.float32),
    "dark green":   np.array([[[30,  80, 20]]*224]*224, dtype=np.float32),
    "black":        np.full((224,224,3),   0, dtype=np.float32),
}

for MODEL_PATH in all_models:
    log(f"\n--- {os.path.basename(MODEL_PATH)} ---")
    try:
        interp = Interpreter(model_path=MODEL_PATH)
        interp.allocate_tensors()
        inp  = interp.get_input_details()
        out  = interp.get_output_details()
        log(f"  input={inp[0]['shape']}  dtype={inp[0]['dtype'].__name__}")
        for name, arr_rgb in tests.items():
            arr = (arr_rgb / 127.5) - 1.0
            arr = np.expand_dims(arr, axis=0).astype(np.float32)
            interp.set_tensor(inp[0]['index'], arr)
            interp.invoke()
            preds = interp.get_tensor(out[0]['index'])[0]
            label = "GOOD" if int(np.argmax(preds)) == 1 else "BAD"
            log(f"  {name:15s} bad={preds[0]:.3f} good={preds[1]:.3f} => {label} {max(preds)*100:.1f}%")
    except Exception as e:
        log(f"  ERROR: {e}")

log("\n=== Done ===")
open(LOG, 'w').write('\n'.join(lines))
