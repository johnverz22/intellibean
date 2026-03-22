#!/usr/bin/env python3
"""
MobileNetV2 Bean Classifier — Local Training (Windows, RTX 4060)
Output model matches Pi inference exactly:
  - Rescaling(1./127.5, offset=-1) built-in
  - Dense(2, softmax)  — class 0=bad, class 1=good (alphabetical)
  - Saved as best_model.keras + best_model.tflite
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import numpy as np
import os

TRAIN_DIR  = 'dataset/train'
VAL_DIR    = 'dataset/val'
OUT_DIR    = 'models'
BATCH      = 32
IMG_SIZE   = (224, 224)

# ── GPU setup ─────────────────────────────────────────────────────────────────
def setup_gpu():
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            from tensorflow.keras import mixed_precision
            mixed_precision.set_global_policy('mixed_float16')
            print("RTX GPU: ENABLED (mixed_float16)")
        except RuntimeError as e:
            print(f"GPU setup error: {e}")
    else:
        print("No GPU — training on CPU")

# ── Model ─────────────────────────────────────────────────────────────────────
def build_model():
    base = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights='imagenet')
    base.trainable = False

    model = keras.Sequential([
        keras.Input(shape=(224, 224, 3)),
        layers.Rescaling(1./127.5, offset=-1),   # matches Pi preprocessing
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(2, activation='softmax', dtype='float32'),  # 0=bad, 1=good
    ])
    return model, base

# ── Training ──────────────────────────────────────────────────────────────────
def main():
    setup_gpu()
    os.makedirs(OUT_DIR, exist_ok=True)

    # Datasets
    train_ds = keras.utils.image_dataset_from_directory(
        TRAIN_DIR, image_size=IMG_SIZE, batch_size=BATCH,
        shuffle=True, seed=42)
    val_ds = keras.utils.image_dataset_from_directory(
        VAL_DIR, image_size=IMG_SIZE, batch_size=BATCH,
        shuffle=False)

    print("Classes:", train_ds.class_names)  # must be ['bad', 'good']

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds   = val_ds.prefetch(tf.data.AUTOTUNE)

    model, base = build_model()
    model.summary()

    CKPT = os.path.join(OUT_DIR, 'best_model.keras')

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            CKPT, monitor='val_accuracy',
            save_best_only=True, verbose=1),
        keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=5,
            restore_best_weights=True, verbose=1),
    ]

    # Stage 1 — frozen base
    model.compile(
        optimizer=keras.optimizers.Adam(1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'])

    print("\n=== Stage 1: frozen base (up to 20 epochs) ===")
    hist1 = model.fit(train_ds, validation_data=val_ds, epochs=20, callbacks=callbacks)

    # Stage 2 — fine-tune top layers
    print("\n=== Stage 2: fine-tuning top 30 layers ===")
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(1e-4),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'])

    hist2 = model.fit(train_ds, validation_data=val_ds, epochs=15, callbacks=callbacks)

    # Reload best checkpoint
    print(f"\nReloading best checkpoint: {CKPT}")
    best = keras.models.load_model(CKPT)

    # Sanity check
    for tag, x in [
        ("zeros", np.zeros((1, 224, 224, 3), dtype='float32')),
        ("rand",  np.random.uniform(0, 255, (1, 224, 224, 3)).astype('float32')),
    ]:
        p = best.predict(x, verbose=0)[0]
        print(f"  {tag}: bad={p[0]:.4f}  good={p[1]:.4f}")

    # ── Learning curve ────────────────────────────────────────────────────────
    acc     = hist1.history['accuracy']     + hist2.history['accuracy']
    val_acc = hist1.history['val_accuracy'] + hist2.history['val_accuracy']
    loss    = hist1.history['loss']         + hist2.history['loss']
    val_loss= hist1.history['val_loss']     + hist2.history['val_loss']
    epochs  = range(1, len(acc) + 1)
    stage2_start = len(hist1.history['accuracy']) + 1  # vertical line marker

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Bean Classifier — Training History', fontsize=14, fontweight='bold')

    ax1.plot(epochs, acc,     'b-o', markersize=4, label='Train Acc')
    ax1.plot(epochs, val_acc, 'r-o', markersize=4, label='Val Acc')
    ax1.axvline(x=stage2_start, color='gray', linestyle='--', alpha=0.6, label='Fine-tune start')
    ax1.set_title('Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 1])

    ax2.plot(epochs, loss,     'b-o', markersize=4, label='Train Loss')
    ax2.plot(epochs, val_loss, 'r-o', markersize=4, label='Val Loss')
    ax2.axvline(x=stage2_start, color='gray', linestyle='--', alpha=0.6, label='Fine-tune start')
    ax2.set_title('Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    chart_path = os.path.join(OUT_DIR, 'learning_curve.png')
    plt.savefig(chart_path, dpi=150)
    plt.show()
    print(f"Saved learning curve: {chart_path}")
    # ─────────────────────────────────────────────────────────────────────────

    # Convert to TFLite
    print("\nConverting to TFLite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(best)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite = converter.convert()

    TFLITE = os.path.join(OUT_DIR, 'best_model.tflite')
    with open(TFLITE, 'wb') as f:
        f.write(tflite)
    print(f"Saved {TFLITE} ({len(tflite)//1024} KB)")

    # Plot training history
    try:
        acc = best.history.history['accuracy'] if hasattr(best, 'history') else []
    except Exception:
        acc = []

    print("\nDone. Files saved to:", OUT_DIR)
    print("  best_model.keras  — full Keras model")
    print("  best_model.tflite — deploy to Pi")


if __name__ == "__main__":
    main()
