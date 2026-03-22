#!/usr/bin/env python3
"""Test the original best_model.tflite to see if it gives sane predictions."""
import numpy as np
from ai_edge_litert.interpreter import Interpreter

for model_file in ['best_model.tflite', 'best_model_v2.tflite']:
    print(f"\n=== {model_file} ===")
    try:
        interp = Interpreter(model_path=model_file)
        interp.allocate_tensors()
        inp = interp.get_input_details()
        out = interp.get_output_details()
        print(f"Input: {inp[0]['shape']} {inp[0]['dtype']}")

        for tag, data in [
            ("zeros ", np.zeros(inp[0]['shape'], np.float32)),
            ("rand1 ", np.random.uniform(-1,1,inp[0]['shape']).astype(np.float32)),
            ("rand2 ", np.random.uniform(-1,1,inp[0]['shape']).astype(np.float32)),
            ("white ", np.ones(inp[0]['shape'], np.float32)),
            ("black ", np.full(inp[0]['shape'], -1.0, np.float32)),
        ]:
            interp.set_tensor(inp[0]['index'], data)
            interp.invoke()
            p = interp.get_tensor(out[0]['index'])[0]
            print(f"  {tag} -> bad={p[0]:.4f} good={p[1]:.4f} => {'GOOD' if np.argmax(p)==1 else 'BAD'}")
    except Exception as e:
        print(f"  ERROR: {e}")
