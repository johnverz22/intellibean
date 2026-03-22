#!/usr/bin/env python3
"""Test if tflite model loads correctly."""
import sys

MODEL = "/home/beans/bean_sorter/best_model.tflite"

try:
    from ai_edge_litert.interpreter import Interpreter
    print("Using ai_edge_litert")
except ImportError:
    from tflite_runtime.interpreter import Interpreter
    print("Using tflite_runtime")

print("Loading model...")
interp = Interpreter(model_path=MODEL)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()
print("Input:", inp[0]['shape'], inp[0]['dtype'])
print("Output:", out[0]['shape'], out[0]['dtype'])
print("Model OK")
