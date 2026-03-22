#!/bin/bash
# Setup script for dataset collection on Raspberry Pi

echo "=========================================="
echo "Coffee Bean Dataset Collection Setup"
echo "=========================================="

# Update system
echo ""
echo "1. Updating system..."
sudo apt update

# Install OpenCV and dependencies
echo ""
echo "2. Installing OpenCV and dependencies..."
sudo apt install -y python3-opencv python3-tk python3-pil python3-pil.imagetk

# Install Python packages
echo ""
echo "3. Installing Python packages..."
pip3 install --break-system-packages opencv-python pillow numpy

# Create directories
echo ""
echo "4. Creating dataset directories..."
mkdir -p ~/coffee_dataset/good_beans/curve
mkdir -p ~/coffee_dataset/good_beans/back
mkdir -p ~/coffee_dataset/bad_beans/curve
mkdir -p ~/coffee_dataset/bad_beans/back
mkdir -p ~/temp_captures

# Set permissions
chmod 755 ~/coffee_dataset
chmod 755 ~/temp_captures

# Test OpenCV installation
echo ""
echo "5. Testing OpenCV installation..."
python3 << EOF
import cv2
import numpy as np
print(f"OpenCV version: {cv2.__version__}")
print("✓ OpenCV installed successfully!")
EOF

# Test camera
echo ""
echo "6. Testing camera..."
rpicam-hello --list-cameras

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review docs/DATASET_COLLECTION_GUIDE.md"
echo "2. Prepare your bean grid setup"
echo "3. Run: python3 src/ml/dataset_collector.py"
echo ""
echo "Dataset will be saved to: ~/coffee_dataset/"
echo "=========================================="
