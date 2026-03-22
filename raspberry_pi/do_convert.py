#!/usr/bin/env python3
import tensorflow as tf
import numpy as np

print("TF:", tf.__version__)
model = tf.keras.models.load_model('models/best_model.keras')
print("Model loaded. Output layer:", model.layers[-1].get_config())

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('models/best_model_v3.tflite', 'wb') as f:
    f.write(tflite_model)
print(f"Saved models/best_model_v3.tflite ({len(tflite_model)//1024} KB)")

# Sanity check
interp = tf.lite.Interpreter(model_content=tflite_model)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()

for label, arr in [
    ("zeros ", np.zeros(inp[0]['shape'], dtype=np.float32)),
    ("random", np.random.uniform(-1,1, inp[0]['shape']).astype(np.float32)),
    ("white ", np.ones(inp[0]['shape'], dtype=np.float32)),
]:
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    p = interp.get_tensor(out[0]['index'])[0]
    print(f"{label} -> bad={p[0]:.3f} good={p[1]:.3f}  => {'GOOD' if np.argmax(p)==1 else 'BAD'}")

print("Done.")
