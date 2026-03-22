#!/usr/bin/env python3
"""
Convert best_model.keras -> best_model_v2.tflite using keras export.
Run once: python3 convert_model.py
"""
import os
os.environ['KERAS_BACKEND'] = 'numpy'   # avoid needing TF/JAX/torch

KERAS_PATH  = "/home/beans/bean_sorter/best_model.keras"
OUTPUT_PATH = "/home/beans/bean_sorter/best_model_v2.tflite"

import keras
print(f"Keras {keras.__version__}")
print("Loading model...")
model = keras.models.load_model(KERAS_PATH)
print("Model loaded. Exporting to TFLite...")

# keras 3.x built-in TFLite export (no TF required)
model.export(OUTPUT_PATH, format="tflite")
size = os.path.getsize(OUTPUT_PATH)
print(f"Saved: {OUTPUT_PATH} ({size//1024} KB)")
