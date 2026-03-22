# Training Quick Start Guide

Step-by-step guide to train your coffee bean classifier.

## Step 1: Organize Your Dataset

After cropping beans, organize them into this structure:
train 70%
validation 15%
testing 15%
```
dataset/
├── train/
│   ├── good/
│   │   ├── bean_000001.jpg
│   │   ├── bean_000002.jpg
│   │   └── ... (700+ images)
│   └── bad/
│       ├── bean_000100.jpg
│       ├── bean_000101.jpg
│       └── ... (700+ images)
├── val/
│   ├── good/
│   │   └── ... (150+ images)
│   └── bad/
│       └── ... (150+ images)
└── test/
    ├── good/
    │   └── ... (150+ images)
    └── bad/
        └── ... (150+ images)
```

### Directory Breakdown

- `train/` - Training data (70% of your data)
  - `good/` - Good quality beans
  - `bad/` - Bad quality beans
- `val/` - Validation data (15% of your data)
  - Used during training to monitor performance
  - `good/` - Good quality beans
  - `bad/` - Bad quality beans
- `test/` - Test data (15% of your data)
  - Used AFTER training to evaluate final model
  - Never seen during training
  - `good/` - Good quality beans
  - `bad/` - Bad quality beans

### Recommended Split

For 1000 images per class:
- Training: 700 images per class (1400 total) - 70%
- Validation: 150 images per class (300 total) - 15%
- Test: 150 images per class (300 total) - 15%

## Step 2: Split Your Cropped Images

You have two options:

### Option A: Manual Split (Simple)

1. Create the directory structure:
```bash
mkdir -p dataset/train/good dataset/train/bad
mkdir -p dataset/val/good dataset/val/bad
mkdir -p dataset/test/good dataset/test/bad
```

2. Copy your cropped images:
```bash
# Copy first 700 good beans to training
# Copy next 150 good beans to validation
# Copy last 150 good beans to test
# Repeat for bad beans
```

### Option B: Automatic Split (Recommended)

Create a split script:

```bash
python scripts/split_dataset.py ./cropped_images/good ./cropped_images/bad ./dataset
```

This creates a 70/15/15 split by default. Customize with:

```bash
python scripts/split_dataset.py ./cropped_images/good ./cropped_images/bad ./dataset --train 0.7 --val 0.15
```

## Step 3: Verify Dataset

Check your dataset is ready:

```bash
python scripts/verify_dataset.py ./dataset
```

This will show:
- Number of images in each folder
- Class balance
- Image sizes
- Any issues

## Step 4: Install Dependencies

```bash
pip install tensorflow matplotlib
```

## Step 5: Train the Model

Basic training:
```bash
python scripts/train_mobilenet.py ./dataset/train ./dataset/val
```

With custom settings:
```bash
python scripts/train_mobilenet.py ./dataset/train ./dataset/val \
    --output ./my_models \
    --epochs 50 \
    --fine-tune-epochs 30 \
    --batch-size 32
```

## Step 6: Monitor Training

The script will show progress:

```
======================================================================
Coffee Bean Classifier Training - MobileNetV2
======================================================================

1. Creating data generators...
   Training samples: 1600
   Validation samples: 400
   Classes: {'bad': 0, 'good': 1}

======================================================================
STAGE 1: Training with frozen base model
======================================================================
Epoch 1/50
50/50 [==============================] - 45s - loss: 0.4521 - accuracy: 0.7850 - val_loss: 0.2134 - val_accuracy: 0.9120
Epoch 2/50
50/50 [==============================] - 42s - loss: 0.3012 - accuracy: 0.8650 - val_loss: 0.1823 - val_accuracy: 0.9280
...
```

## Step 7: Test the Model

After training, evaluate on the test set:

```bash
python scripts/test_model.py ./dataset/test ./models/best_model.h5
```

This will show:
- Test accuracy
- Per-class performance
- Confusion matrix
- Classification report

Output files:
```
test_results/
├── test_results.json          # Metrics in JSON
├── confusion_matrix.png        # Visual confusion matrix
└── per_class_accuracy.png      # Bar chart of accuracy
```

## Step 8: Check Results

After training completes, check the output:

```
models/
├── best_model.h5           # Use this for deployment
├── final_model.h5          # Final model
├── model.tflite            # For Raspberry Pi
├── training_history.png    # View accuracy/loss plots
├── training_info.json      # Training metadata
└── logs/                   # TensorBoard logs
```

View the training plot:
- Open `models/training_history.png`

View TensorBoard:
```bash
tensorboard --logdir ./models/logs
```

## Complete Example Workflow

```bash
# 1. Crop beans from raw images
python scripts/crop_beans_batch.py ./raw_images/good ./cropped_images/good
python scripts/crop_beans_batch.py ./raw_images/bad ./cropped_images/bad

# 2. Check cropped datasets
python scripts/report_dataset.py ./cropped_images/good
python scripts/report_dataset.py ./cropped_images/bad

# 3. Split into train/val/test
python scripts/split_dataset.py ./cropped_images/good ./cropped_images/bad ./dataset

# 4. Verify dataset
python scripts/verify_dataset.py ./dataset

# 5. Train model
python scripts/train_mobilenet.py ./dataset/train ./dataset/val --output ./models

# 6. Test model
python scripts/test_model.py ./dataset/test ./models/best_model.h5

# 7. View results
# Open models/training_history.png
# Open test_results/confusion_matrix.png
```

## Expected Training Time

- CPU: 2-4 hours (50 epochs + 30 fine-tune)
- GPU: 20-40 minutes

## Minimum Requirements

- Training images: 500+ per class (700+ recommended)
- Validation images: 100+ per class (150+ recommended)
- Test images: 100+ per class (150+ recommended)
- RAM: 8GB minimum
- Disk space: 2GB for models and logs

## What to Expect

Good training results:
- Training accuracy: 95-99%
- Validation accuracy: 90-97%
- Test accuracy: 90-95%
- Loss decreasing steadily

### Understanding the Splits

- **Training set**: Model learns from this data
- **Validation set**: Used during training to tune hyperparameters and prevent overfitting
- **Test set**: Final evaluation AFTER training - represents real-world performance

If validation accuracy is much lower than training:
- Model is overfitting
- Need more training data
- Increase augmentation

If both accuracies are low:
- Need more training epochs
- Check data quality
- Verify labels are correct

## Next Steps

After training:
1. Test the model on new images
2. Deploy to Raspberry Pi using `model.tflite`
3. Integrate with your sorting system

## Troubleshooting

### "No module named tensorflow"
```bash
pip install tensorflow
```

### "Out of memory"
Reduce batch size:
```bash
python scripts/train_mobilenet.py ... --batch-size 16
```

### "Found 0 images"
Check directory structure matches exactly:
```
dataset/train/good/
dataset/train/bad/
dataset/val/good/
dataset/val/bad/
dataset/test/good/
dataset/test/bad/
```

### Training accuracy stuck
- Increase learning rate
- Train longer
- Check data quality

### Validation accuracy not improving
- Add more validation data
- Check for data leakage
- Verify labels are correct
