#!/usr/bin/env python3
"""Reconvert best_model_new.keras -> best_model_new.tflite cleanly."""
import os, numpy as np, tensorflow as tf
from tensorflow import keras

BASE   = os.path.expanduser('~/bean_sorter')
KERAS  = os.path.join(BASE, 'best_model_new.keras')
TFLITE = os.path.join(BASE, 'best_model_new.tflite')

print(f"Loading {KERAS} ...")
model = keras.models.load_model(KERAS)
print("Model loaded. Converting...")

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open(TFLITE, 'wb') as f:
    f.write(tflite_model)
print(f"Saved {TFLITE} ({len(tflite_model)//1024} KB)")

# Sanity check
print("\n--- Sanity check ---")
interp = tf.lite.Interpreter(model_content=tflite_model)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()

varied = []
for tag, arr in [
    ("zeros ", np.zeros(inp[0]['shape'], np.float32)),
    ("ones  ", np.ones(inp[0]['shape'], np.float32)),
    ("rand1 ", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
    ("rand2 ", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
]:
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    p = interp.get_tensor(out[0]['index'])[0]
    label = 'GOOD' if np.argmax(p) == 1 else 'BAD'
    print(f"  {tag} -> bad={p[0]:.4f}  good={p[1]:.4f}  => {label}")
    varied.append(np.argmax(p))

if len(set(varied)) > 1:
    print("\n✓ Model gives varied predictions — GOOD!")
else:
    print("\n✗ Still predicting same class — model weights may be corrupted.")
    print("  Try: python3 reconvert.py  (run again after checking keras model)")
