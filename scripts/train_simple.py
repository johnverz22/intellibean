#!/usr/bin/env python3
"""
Simple Coffee Bean Classifier Training - MobileNetV2
Memory-efficient version for RTX 3050
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from sklearn.metrics import confusion_matrix
import seaborn as sns

# Enable memory growth
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"✓ GPU detected: {len(gpus)} device(s)")
else:
    print("⚠ No GPU detected - using CPU")

def create_model():
    """Create MobileNetV2 model"""
    base_model = keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False
    
    model = keras.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.Rescaling(1./127.5, offset=-1),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(2, activation='softmax')
    ])
    
    return model, base_model

def create_datasets(train_dir, val_dir, batch_size=16):
    """Create datasets with augmentation"""
    
    # Training dataset with augmentation
    train_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=True,
        seed=42
    )
    
    # Validation dataset
    val_ds = keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=False,
        seed=42
    )
    
    # Get class names before transformations
    class_names = train_ds.class_names
    
    # Data augmentation
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.2),
        layers.RandomZoom(0.2),
    ])
    
    # Apply augmentation
    train_ds = train_ds.map(
        lambda x, y: (data_augmentation(x, training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    
    # Optimize
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
    
    return train_ds, val_ds, class_names

def train_model(train_dir, val_dir, output_dir, epochs=50, batch_size=16):
    """Train the model"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*70)
    print("Coffee Bean Classifier Training")
    print("="*70)
    
    # Create datasets
    print("\n1. Loading datasets...")
    train_ds, val_ds, class_names = create_datasets(train_dir, val_dir, batch_size)
    print(f"   Classes: {class_names}")
    
    # Create model
    print("\n2. Creating model...")
    model, base_model = create_model()
    
    # Compile
    model.compile(
        optimizer=keras.optimizers.Adam(0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            os.path.join(output_dir, 'best_model.keras'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Stage 1: Train with frozen base
    print("\n" + "="*70)
    print("STAGE 1: Training with frozen base")
    print("="*70)
    
    history1 = model.fit(
        train_ds,
        epochs=epochs,
        validation_data=val_ds,
        callbacks=callbacks,
        verbose=1
    )
    
    # Stage 2: Fine-tuning
    print("\n" + "="*70)
    print("STAGE 2: Fine-tuning")
    print("="*70)
    
    base_model.trainable = True
    for layer in base_model.layers[:100]:
        layer.trainable = False
    
    model.compile(
        optimizer=keras.optimizers.Adam(0.0001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history2 = model.fit(
        train_ds,
        epochs=30,
        validation_data=val_ds,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    print("\n3. Saving models...")
    model.save(os.path.join(output_dir, 'final_model.keras'))
    
    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(os.path.join(output_dir, 'model.tflite'), 'wb') as f:
        f.write(tflite_model)
    print("   ✓ TFLite model saved")
    
    # Plot history
    print("\n4. Generating plots...")
    
    acc = history1.history['accuracy'] + history2.history['accuracy']
    val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']
    loss = history1.history['loss'] + history2.history['loss']
    val_loss = history1.history['val_loss'] + history2.history['val_loss']
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(acc, label='Train Accuracy')
    plt.plot(val_acc, label='Val Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(loss, label='Train Loss')
    plt.plot(val_loss, label='Val Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_history.png'))
    print("   ✓ Training plots saved")
    
    # Evaluate
    print("\n5. Final evaluation...")
    val_loss_final, val_acc_final = model.evaluate(val_ds)
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Final Validation Accuracy: {val_acc_final*100:.2f}%")
    print(f"Final Validation Loss: {val_loss_final:.4f}")
    print(f"Best Validation Accuracy: {max(val_acc)*100:.2f}%")
    print(f"\nModels saved to: {output_dir}/")
    print("="*70)
    
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('train_dir')
    parser.add_argument('val_dir')
    parser.add_argument('--output', default='./models')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=16)
    
    args = parser.parse_args()
    
    train_model(args.train_dir, args.val_dir, args.output, args.epochs, args.batch_size)

if __name__ == "__main__":
    main()
