#!/bin/bash
# Check Raspberry Pi camera status and configuration

echo "=========================================="
echo "Raspberry Pi Camera Diagnostic"
echo "=========================================="

echo ""
echo "1. Checking for connected cameras..."
libcamera-hello --list-cameras

echo ""
echo "2. Checking camera modules loaded..."
lsmod | grep -i camera

echo ""
echo "3. Checking video devices..."
ls -l /dev/video*

echo ""
echo "4. Checking boot config..."
grep -i camera /boot/firmware/config.txt

echo ""
echo "5. System info..."
uname -a

echo ""
echo "=========================================="
echo "If no cameras found:"
echo "1. Check physical connection"
echo "2. Enable camera: sudo raspi-config"
echo "   -> Interface Options -> Legacy Camera -> Enable"
echo "3. Reboot: sudo reboot"
echo "=========================================="
