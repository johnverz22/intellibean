#!/usr/bin/env python3
"""Convert best_model.keras to TFLite for Pi deployment."""
import tensorflow as tf
import os

KERAS_PATH  = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model.keras')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'best_model_v2.tflite')

print(f"TensorFlow {tf.__version__}")
print("Loading model...")
model = tf.keras.models.load_model(KERAS_PATH)
model.summary()

print("Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open(OUTPUT_PATH, 'wb') as f:
    f.write(tflite_model)

size = os.path.getsize(OUTPUT_PATH)
print(f"Saved: {OUTPUT_PATH} ({size//1024} KB)")
