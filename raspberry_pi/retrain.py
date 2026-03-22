#!/usr/bin/env python3
"""
Retrain MobileNetV2 on Pi — Stage 1 only (frozen base).
Stage 1 alone achieves ~97% val accuracy. Fine-tuning is skipped
because it destabilises the model at this dataset size.
Saves: best_model_new.keras + best_model_new.tflite
"""
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np, os

DATASET  = os.path.expanduser('~/bean_sorter/dataset')
OUT      = os.path.expanduser('~/bean_sorter')
IMG_SIZE = (224, 224)
BATCH    = 8

print(f"TF {tf.__version__}", flush=True)

train_ds = keras.utils.image_dataset_from_directory(
    f'{DATASET}/train', image_size=IMG_SIZE, batch_size=BATCH,
    shuffle=True, seed=42, validation_split=0.2, subset='training')
val_ds = keras.utils.image_dataset_from_directory(
    f'{DATASET}/train', image_size=IMG_SIZE, batch_size=BATCH,
    shuffle=False, seed=42, validation_split=0.2, subset='validation')

print("Classes:", train_ds.class_names, flush=True)  # ['bad', 'good']

train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
val_ds   = val_ds.prefetch(tf.data.AUTOTUNE)

base = keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base.trainable = False

model = keras.Sequential([
    keras.Input(shape=(224, 224, 3)),
    layers.Rescaling(1./127.5, offset=-1),
    base,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(2, activation='softmax'),
])

model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'])

CKPT = os.path.join(OUT, 'best_model_new.keras')
callbacks = [
    keras.callbacks.ModelCheckpoint(
        CKPT, monitor='val_accuracy',
        save_best_only=True, verbose=1),
    keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=5,
        restore_best_weights=True, verbose=1),
]

print("\n--- Training (frozen base, up to 20 epochs) ---", flush=True)
model.fit(train_ds, validation_data=val_ds, epochs=20, callbacks=callbacks)

# Reload the best checkpoint explicitly before converting
print(f"\nReloading best checkpoint from {CKPT} ...", flush=True)
best_model = keras.models.load_model(CKPT)

# Verify keras model before converting
print("Verifying keras model...", flush=True)
for tag, x in [
    ("zeros", np.zeros((1,224,224,3), dtype='float32')),
    ("rand1", np.random.uniform(-1,1,(1,224,224,3)).astype('float32')),
]:
    p = best_model.predict(x, verbose=0)[0]
    print(f"  {tag}: bad={p[0]:.4f}  good={p[1]:.4f}", flush=True)

# Convert to TFLite
print("\nConverting to TFLite...", flush=True)
converter = tf.lite.TFLiteConverter.from_keras_model(best_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

TFLITE = os.path.join(OUT, 'best_model_new.tflite')
with open(TFLITE, 'wb') as f:
    f.write(tflite_model)
print(f"Saved {TFLITE} ({len(tflite_model)//1024} KB)", flush=True)

# Sanity check TFLite
print("\n--- TFLite sanity check ---", flush=True)
interp = tf.lite.Interpreter(model_content=tflite_model)
interp.allocate_tensors()
inp = interp.get_input_details()
out = interp.get_output_details()
results = []
for tag, arr in [
    ("zeros ", np.zeros(inp[0]['shape'], np.float32)),
    ("ones  ", np.ones(inp[0]['shape'], np.float32)),
    ("rand1 ", np.random.uniform(-1,1,inp[0]['shape']).astype(np.float32)),
    ("rand2 ", np.random.uniform(-1,1,inp[0]['shape']).astype(np.float32)),
]:
    interp.set_tensor(inp[0]['index'], arr)
    interp.invoke()
    p = interp.get_tensor(out[0]['index'])[0]
    label = 'GOOD' if np.argmax(p) == 1 else 'BAD'
    print(f"  {tag} -> bad={p[0]:.4f}  good={p[1]:.4f}  => {label}", flush=True)
    results.append(np.argmax(p))

if len(set(results)) > 1:
    print("\n✓ TFLite model gives varied predictions — DONE!", flush=True)
else:
    print("\n✗ TFLite still broken — check keras model predictions above.", flush=True)
