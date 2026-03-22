#!/usr/bin/env python3
"""Evaluate best_model.keras on dataset/test and generate confusion matrix."""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import os

MODEL_PATH = 'models/best_model.keras'
TEST_DIR   = 'dataset/test'
OUT_DIR    = 'models'
IMG_SIZE   = (224, 224)
BATCH      = 32

print("Loading model...", flush=True)
model = keras.models.load_model(MODEL_PATH)

print("Loading test dataset...", flush=True)
test_ds = keras.utils.image_dataset_from_directory(
    TEST_DIR, image_size=IMG_SIZE, batch_size=BATCH,
    shuffle=False, seed=42)

class_names = test_ds.class_names
print(f"Classes: {class_names}")  # ['bad', 'good']

# Collect predictions
y_true, y_pred = [], []
for images, labels in test_ds:
    preds = model.predict(images, verbose=0)
    y_true.extend(labels.numpy())
    y_pred.extend(np.argmax(preds, axis=1))

y_true = np.array(y_true)
y_pred = np.array(y_pred)

# Overall accuracy
acc = np.mean(y_true == y_pred)
print(f"\nTest Accuracy: {acc*100:.2f}%")

# Classification report
print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=class_names))

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:")
print(cm)

# Plot
plt.figure(figsize=(7, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names,
            annot_kws={"size": 16})
plt.title(f'Confusion Matrix — Test Accuracy: {acc*100:.1f}%', fontsize=14)
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.tight_layout()
out_path = os.path.join(OUT_DIR, 'confusion_matrix.png')
plt.savefig(out_path, dpi=150)
print(f"\nSaved: {out_path}")
plt.show()
