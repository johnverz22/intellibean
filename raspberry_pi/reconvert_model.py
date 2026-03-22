#!/usr/bin/env python3
"""Reconvert best_model.keras -> best_model_v3.tflite on the Pi."""
import tensorflow as tf
import numpy as np

print("Loading keras model...")
model = tf.keras.models.load_model('best_model.keras')
model.summary()

print("\nConverting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

out_path = 'best_model_v3.tflite'
with open(out_path, 'wb') as f:
    f.write(tflite_model)
print(f"Saved: {out_path}  ({len(tflite_model)//1024} KB)")

# Quick sanity check
print("\nSanity check...")
interp = tf.lite.Interpreter(model_content=tflite_model)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()

# random image
arr = np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)
interp.set_tensor(inp[0]['index'], arr)
interp.invoke()
preds = interp.get_tensor(out[0]['index'])[0]
print(f"Random input -> {preds}  class={np.argmax(preds)} (0=bad,1=good)")

# all-zero
arr2 = np.zeros(inp[0]['shape'], dtype=np.float32)
interp.set_tensor(inp[0]['index'], arr2)
interp.invoke()
preds2 = interp.get_tensor(out[0]['index'])[0]
print(f"Zero input   -> {preds2}  class={np.argmax(preds2)}")

print("\nDone. Use best_model_v3.tflite")
