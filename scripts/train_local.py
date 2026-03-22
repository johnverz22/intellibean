#!/usr/bin/env python3
"""
Train MobileNetV2 locally on Windows, export best_model_local.tflite
Stage 1 only (frozen base) — avoids catastrophic forgetting from fine-tune.
"""
import os, numpy as np
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL']  = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

DATASET  = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'train')
OUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(OUT_DIR, exist_ok=True)

KERAS_OUT  = os.path.join(OUT_DIR, 'best_model_local.keras')
TFLITE_OUT = os.path.join(OUT_DIR, 'best_model_local.tflite')
IMG_SIZE   = (224, 224)
BATCH      = 32

print(f"TF {tf.__version__}")
print(f"Dataset: {DATASET}")

train_ds = keras.utils.image_dataset_from_directory(
    DATASET, image_size=IMG_SIZE, batch_size=BATCH,
    shuffle=True, seed=42, validation_split=0.2, subset='training')
val_ds = keras.utils.image_dataset_from_directory(
    DATASET, image_size=IMG_SIZE, batch_size=BATCH,
    shuffle=False, seed=42, validation_split=0.2, subset='validation')

print("Classes:", train_ds.class_names)  # must be ['bad', 'good']

train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
val_ds   = val_ds.prefetch(tf.data.AUTOTUNE)

base = keras.applications.MobileNetV2(input_shape=(224,224,3), include_top=False, weights='imagenet')
base.trainable = False

model = keras.Sequential([
    keras.Input(shape=(224,224,3)),
    layers.Rescaling(1./127.5, offset=-1),
    base,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(2, activation='softmax')
])

model.compile(optimizer=keras.optimizers.Adam(1e-3),
              loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.summary()

cb = [
    keras.callbacks.ModelCheckpoint(KERAS_OUT,
        monitor='val_accuracy', save_best_only=True, verbose=1),
    keras.callbacks.EarlyStopping(monitor='val_loss', patience=5,
        restore_best_weights=True, verbose=1),
    keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5,
        patience=3, verbose=1),
]

print("\n--- Training (frozen base) ---")
model.fit(train_ds, validation_data=val_ds, epochs=25, callbacks=cb)

# Reload best checkpoint explicitly
print(f"\nReloading best checkpoint: {KERAS_OUT}")
best = keras.models.load_model(KERAS_OUT)
loss, acc = best.evaluate(val_ds, verbose=0)
print(f"Best val_accuracy={acc:.4f}  val_loss={loss:.4f}")

# Convert to TFLite
print("\nConverting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(best)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite = converter.convert()
with open(TFLITE_OUT, 'wb') as f:
    f.write(tflite)
print(f"Saved: {TFLITE_OUT}  ({len(tflite)//1024} KB)")

# Sanity check
interp = tf.lite.Interpreter(model_path=TFLITE_OUT)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()
results = []
for tag, arr in [
    ("zeros", np.zeros(inp[0]['shape'], np.float32)),
    ("rand1", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
    ("rand2", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
    ("rand3", np.random.uniform(-1, 1, inp[0]['shape']).astype(np.float32)),
]:
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    p = interp.get_tensor(out[0]['index'])[0]
    label = 'GOOD' if p[1] > p[0] else 'BAD'
    print(f"  {tag} -> bad={p[0]:.4f}  good={p[1]:.4f}  => {label}")
    results.append(label)

if len(set(results)) > 1:
    print("\nModel gives VARIED predictions — healthy!")
else:
    print(f"\nWARNING: All predictions are {results[0]}")

print("\nDone. Deploy models/best_model_local.tflite to Pi.")
