#!/bin/bash
# Detect Camera Module 3 on Raspberry Pi 5

echo "=========================================="
echo "Camera Module 3 Detection"
echo "=========================================="

echo ""
echo "1. Checking camera detection..."
vcgencmd get_camera

echo ""
echo "2. Listing cameras with rpicam..."
rpicam-hello --list-cameras

echo ""
echo "3. Checking I2C devices (camera should be on i2c-10)..."
i2cdetect -y 10 2>/dev/null || echo "Camera not on i2c-10"

echo ""
echo "4. Checking device tree..."
dtoverlay -l | grep -i camera

echo ""
echo "5. Checking for camera in dmesg..."
dmesg | grep -i camera | tail -10

echo ""
echo "=========================================="
echo "Camera Module 3 should auto-detect on Pi 5"
echo "If not detected:"
echo "1. Check ribbon cable connection (blue side to camera)"
echo "2. Check cable is in CAM0 or CAM1 port"
echo "3. Try: sudo reboot"
echo "=========================================="
