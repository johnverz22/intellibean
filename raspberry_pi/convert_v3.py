#!/usr/bin/env python3
import tensorflow as tf
import numpy as np

print(f"TF {tf.__version__}")
model = tf.keras.models.load_model('best_model.keras')
print("Loaded. Layers:", len(model.layers))

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite = converter.convert()

with open('best_model_v3.tflite', 'wb') as f:
    f.write(tflite)
print(f"Saved best_model_v3.tflite ({len(tflite)//1024} KB)")

interp = tf.lite.Interpreter(model_content=tflite)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()
for tag, arr in [
    ("zeros ", np.zeros(inp[0]['shape'], np.float32)),
    ("random", np.random.uniform(-1,1,inp[0]['shape']).astype(np.float32)),
]:
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    p = interp.get_tensor(out[0]['index'])[0]
    print(f"{tag} -> bad={p[0]:.4f} good={p[1]:.4f} => {'GOOD' if np.argmax(p)==1 else 'BAD'}")
print("Done.")
