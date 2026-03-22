#!/usr/bin/env python3
"""
Model Testing Script (Fixed for categorical labels)
Evaluate trained model on test set
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import argparse
import json
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


def test_model(test_dir, model_path, output_dir=None):
    """Test model on test dataset"""
    
    print("="*70)
    print("MODEL TESTING")
    print("="*70)
    print(f"Test directory: {test_dir}")
    print(f"Model: {model_path}")
    print()
    
    # Load model
    print("Loading model...")
    model = keras.models.load_model(model_path)
    
    # Recompile with categorical crossentropy to match data generator
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print("✓ Model loaded and recompiled")
    print()
    
    # Create test data generator (no augmentation)
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    
    test_datagen = ImageDataGenerator()
    
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=False  # Important for correct label alignment
    )
    
    print(f"Test samples: {test_generator.samples}")
    print(f"Classes: {test_generator.class_indices}")
    print()
    
    # Evaluate
    print("Evaluating model on test set...")
    test_loss, test_accuracy = model.evaluate(test_generator, verbose=1)
    
    print()
    print("-"*70)
    print("TEST RESULTS")
    print("-"*70)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy*100:.2f}%")
    print()
    
    # Get predictions
    print("Generating predictions...")
    predictions = model.predict(test_generator, verbose=1)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = test_generator.classes
    class_labels = list(test_generator.class_indices.keys())
    
    # Classification report
    print()
    print("-"*70)
    print("CLASSIFICATION REPORT")
    print("-"*70)
    print(classification_report(true_classes, predicted_classes, 
                                target_names=class_labels, digits=4))
    
    # Confusion matrix
    cm = confusion_matrix(true_classes, predicted_classes)
    
    print("-"*70)
    print("CONFUSION MATRIX")
    print("-"*70)
    print(f"              Predicted")
    print(f"              {class_labels[0]:>8} {class_labels[1]:>8}")
    print(f"Actual {class_labels[0]:>6}  {cm[0][0]:>8} {cm[0][1]:>8}")
    print(f"       {class_labels[1]:>6}  {cm[1][0]:>8} {cm[1][1]:>8}")
    print()
    
    # Calculate per-class metrics
    for i, label in enumerate(class_labels):
        total = np.sum(true_classes == i)
        correct = cm[i][i]
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"{label.capitalize()} beans: {correct}/{total} correct ({accuracy:.2f}%)")
    
    # Save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save metrics
        results = {
            'test_loss': float(test_loss),
            'test_accuracy': float(test_accuracy),
            'confusion_matrix': cm.tolist(),
            'class_labels': class_labels,
            'total_samples': int(test_generator.samples)
        }
        
        results_file = output_path / 'test_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {results_file}")
        
        # Plot confusion matrix
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_labels,
                   yticklabels=class_labels,
                   cbar_kws={'label': 'Count'},
                   annot_kws={'size': 16, 'weight': 'bold'})
        plt.title('Confusion Matrix - Bean Quality Classification', fontsize=14, fontweight='bold', pad=20)
        plt.ylabel('True Label', fontsize=12, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
        plt.xticks(fontsize=11)
        plt.yticks(fontsize=11)
        
        cm_file = output_path / 'confusion_matrix.png'
        plt.savefig(cm_file, dpi=300, bbox_inches='tight')
        print(f"✓ Confusion matrix saved to {cm_file}")
        plt.close()
        
        # Plot per-class accuracy
        plt.figure(figsize=(10, 6))
        accuracies = []
        for i in range(len(class_labels)):
            total = np.sum(true_classes == i)
            correct = cm[i][i]
            acc = (correct / total * 100) if total > 0 else 0
            accuracies.append(acc)
        
        colors = ['#2ecc71' if acc >= 85 else '#e74c3c' for acc in accuracies]
        bars = plt.bar(class_labels, accuracies, color=colors, edgecolor='black', linewidth=1.5)
        plt.ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        plt.xlabel('Bean Quality', fontsize=12, fontweight='bold')
        plt.title('Per-Class Accuracy', fontsize=14, fontweight='bold', pad=20)
        plt.ylim(0, 100)
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        for i, (v, bar) in enumerate(zip(accuracies, bars)):
            plt.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold', fontsize=12)
        
        acc_file = output_path / 'per_class_accuracy.png'
        plt.savefig(acc_file, dpi=300, bbox_inches='tight')
        print(f"✓ Per-class accuracy plot saved to {acc_file}")
        plt.close()
    
    print()
    print("="*70)
    print("TESTING COMPLETE")
    print("="*70)
    
    # Interpretation
    if test_accuracy >= 0.95:
        print("✓ Excellent performance (95%+)")
    elif test_accuracy >= 0.90:
        print("✓ Very good performance (90-95%)")
    elif test_accuracy >= 0.85:
        print("✓ Good performance (85-90%)")
    elif test_accuracy >= 0.80:
        print("⚠ Acceptable performance (80-85%)")
    else:
        print("✗ Poor performance (<80%) - consider retraining")
    
    print("="*70)
    
    return test_accuracy, cm


def main():
    parser = argparse.ArgumentParser(
        description='Test trained model on test dataset'
    )
    parser.add_argument('test_dir', help='Test data directory')
    parser.add_argument('model_path', help='Path to trained model (.keras)')
    parser.add_argument('--output', default='./test_results', 
                       help='Output directory for results (default: ./test_results)')
    
    args = parser.parse_args()
    
    # Verify paths
    if not Path(args.test_dir).exists():
        print(f"Error: Test directory not found: {args.test_dir}")
        return
    
    if not Path(args.model_path).exists():
        print(f"Error: Model file not found: {args.model_path}")
        return
    
    test_model(args.test_dir, args.model_path, args.output)


if __name__ == "__main__":
    main()
