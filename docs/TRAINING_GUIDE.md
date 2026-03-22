# Coffee Bean Classifier Training Guide

Train a MobileNetV2 model to classify good vs bad coffee beans.

## Prerequisites

Install TensorFlow:
```bash
pip install tensorflow matplotlib
```

## Dataset Structure

Organize your cropped beans into this structure:

```
dataset/
├── train/
│   ├── good/
│   │   ├── bean_000001.jpg
│   │   ├── bean_000002.jpg
│   │   └── ...
│   └── bad/
│       ├── bean_000100.jpg
│       ├── bean_000101.jpg
│       └── ...
└── val/
    ├── good/
    │   └── ...
    └── bad/
        └── ...
```

## Quick Start

Basic training:
```bash
python scripts/train_mobilenet.py ./dataset/train ./dataset/val
```

With custom parameters:
```bash
python scripts/train_mobilenet.py ./dataset/train ./dataset/val \
    --output ./my_models \
    --epochs 50 \
    --fine-tune-epochs 30 \
    --batch-size 32 \
    --learning-rate 0.001
```

## Training Process

The script uses two-stage training:

### Stage 1: Transfer Learning (Default: 50 epochs)
- MobileNetV2 base frozen
- Only trains custom top layers
- Learning rate: 0.001

### Stage 2: Fine-Tuning (Default: 30 epochs)
- Unfreezes last layers of MobileNetV2
- Fine-tunes entire model
- Learning rate: 0.0001 (10x lower)

## Data Augmentation

Training images are augmented with:
- Random rotation (±40°)
- Width/height shift (±20%)
- Shear transformation (20%)
- Random zoom (±20%)
- Horizontal/vertical flips
- Brightness adjustment (80-120%)

Validation images are not augmented.

## Model Features

- Architecture: MobileNetV2 (pre-trained on ImageNet)
- Input size: 224x224x3
- Output: 2 classes (good/bad)
- Optimizer: Adam
- Loss: Categorical crossentropy

## Callbacks

The training includes:

1. **ModelCheckpoint**: Saves best model based on validation accuracy
2. **EarlyStopping**: Stops if validation loss doesn't improve for 10 epochs
3. **ReduceLROnPlateau**: Reduces learning rate when validation loss plateaus
4. **TensorBoard**: Logs for visualization

## Output Files

After training, you'll get:

```
models/
├── best_model.h5           # Best checkpoint (highest val accuracy)
├── final_model.h5          # Final model after all epochs
├── model.tflite            # Mobile-optimized model
├── training_history.png    # Accuracy/loss plots
├── training_info.json      # Training metadata
└── logs/                   # TensorBoard logs
```

## Monitoring Training

View TensorBoard logs:
```bash
tensorboard --logdir ./models/logs
```

Then open: http://localhost:6006

## Command-Line Options

```
python scripts/train_mobilenet.py --help

Arguments:
  train_dir              Training data directory
  val_dir                Validation data directory
  --output               Output directory (default: ./models)
  --epochs               Stage 1 epochs (default: 50)
  --fine-tune-epochs     Stage 2 epochs (default: 30)
  --batch-size           Batch size (default: 32)
  --learning-rate        Initial learning rate (default: 0.001)
```

## Example Training Session

```bash
$ python scripts/train_mobilenet.py ./dataset/train ./dataset/val

======================================================================
Coffee Bean Classifier Training - MobileNetV2
======================================================================

1. Creating data generators...
   Training samples: 2000
   Validation samples: 500
   Classes: {'bad': 0, 'good': 1}

2. Creating MobileNetV2 model...
Model: "model"
...

3. Compiling model...

======================================================================
STAGE 1: Training with frozen base model
======================================================================
Epoch 1/50
63/63 [==============================] - 45s 715ms/step - loss: 0.4521 - accuracy: 0.7850 - val_loss: 0.2134 - val_accuracy: 0.9120
...

======================================================================
STAGE 2: Fine-tuning (unfreezing base model)
======================================================================
Epoch 1/30
63/63 [==============================] - 52s 825ms/step - loss: 0.1234 - accuracy: 0.9520 - val_loss: 0.0987 - val_accuracy: 0.9640
...

======================================================================
TRAINING COMPLETE
======================================================================
Final Validation Accuracy: 96.40%
Final Validation Loss: 0.0987
Best Validation Accuracy: 97.20%

Models saved to: ./models/
  - best_model.h5 (best checkpoint)
  - final_model.h5 (final model)
  - model.tflite (mobile deployment)
  - training_history.png (plots)
  - training_info.json (metadata)
======================================================================
```

## Tips for Best Results

### Dataset Size
- Minimum: 500 images per class
- Recommended: 1000+ images per class
- Split: 80% train, 20% validation

### Data Quality
- All images should be 224x224
- Consistent lighting
- Clean backgrounds
- Properly labeled

### Hyperparameter Tuning

If accuracy is low:
- Increase epochs
- Reduce learning rate
- Add more training data
- Check data quality

If overfitting (train >> val accuracy):
- Increase dropout
- Add more augmentation
- Reduce model complexity
- Get more training data

If underfitting (both accuracies low):
- Increase model complexity
- Train longer
- Reduce regularization
- Check data labels

## Using the Trained Model

Load and use the model:

```python
import tensorflow as tf
import numpy as np
from PIL import Image

# Load model
model = tf.keras.models.load_model('./models/best_model.h5')

# Load and preprocess image
img = Image.open('bean.jpg').resize((224, 224))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)

# Predict
prediction = model.predict(img_array)
class_idx = np.argmax(prediction)
confidence = prediction[0][class_idx]

classes = ['bad', 'good']
print(f"Prediction: {classes[class_idx]} ({confidence*100:.2f}%)")
```

## TFLite Model (Mobile)

For Raspberry Pi or mobile deployment:

```python
import tensorflow as tf
import numpy as np

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path='./models/model.tflite')
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Prepare input
img_array = ...  # Your 224x224x3 image

# Run inference
interpreter.set_tensor(input_details[0]['index'], img_array)
interpreter.invoke()
output = interpreter.get_tensor(output_details[0]['index'])

print(f"Prediction: {output}")
```

## Troubleshooting

### Out of Memory
Reduce batch size:
```bash
python scripts/train_mobilenet.py ... --batch-size 16
```

### Training Too Slow
- Use GPU if available
- Reduce image size (not recommended)
- Reduce batch size

### Poor Accuracy
- Check dataset labels
- Increase training data
- Train longer
- Adjust learning rate

### Model Not Improving
- Check for data leakage
- Verify augmentation is working
- Try different learning rate
- Check class balance
