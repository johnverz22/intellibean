#!/usr/bin/env python3
"""
Deploy Coffee Bean Sorter to Raspberry Pi
Copies all necessary files to a deployment folder
"""

import os
import shutil
from pathlib import Path


def create_deployment_package():
    """Create deployment package for Raspberry Pi"""
    
    print("="*70)
    print("CREATING RASPBERRY PI DEPLOYMENT PACKAGE")
    print("="*70)
    
    # Deployment folder
    deploy_dir = Path("raspberry_pi_deployment")
    
    # Remove old deployment if exists
    if deploy_dir.exists():
        print(f"\nRemoving old deployment folder...")
        shutil.rmtree(deploy_dir)
    
    # Create deployment structure
    print(f"\nCreating deployment structure...")
    deploy_dir.mkdir(exist_ok=True)
    (deploy_dir / "scripts").mkdir(exist_ok=True)
    (deploy_dir / "models").mkdir(exist_ok=True)
    (deploy_dir / "docs").mkdir(exist_ok=True)
    
    # Files to copy
    files_to_copy = {
        # Main scripts
        "raspberry_pi/bean_sorter.py": "scripts/bean_sorter.py",
        "raspberry_pi/bean_sorter_hmi.py": "scripts/bean_sorter_hmi.py",
        "raspberry_pi/test_camera.py": "scripts/test_camera.py",
        "raspberry_pi/test_hardware.py": "scripts/test_hardware.py",
        
        # Model
        "models/best_model.keras": "models/best_model.keras",
        
        # Documentation
        "docs/RASPBERRY_PI_SETUP.md": "docs/RASPBERRY_PI_SETUP.md",
        "docs/WIRING_DIAGRAM.md": "docs/WIRING_DIAGRAM.md",
        "docs/TOUCHSCREEN_HMI_GUIDE.md": "docs/TOUCHSCREEN_HMI_GUIDE.md",
        "RASPBERRY_PI_QUICK_START.md": "docs/QUICK_START.md",
        "HMI_COMPLETE_GUIDE.md": "docs/HMI_GUIDE.md",
        "COMPLETE_SYSTEM_OVERVIEW.md": "docs/SYSTEM_OVERVIEW.md",
    }
    
    # Copy files
    print("\nCopying files:")
    copied_count = 0
    for src, dst in files_to_copy.items():
        src_path = Path(src)
        dst_path = deploy_dir / dst
        
        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"  ✓ {src} → {dst}")
            copied_count += 1
        else:
            print(f"  ✗ {src} (not found)")
    
    # Create README
    readme_content = """# Coffee Bean Sorter - Raspberry Pi Deployment Package

This package contains everything needed to run the coffee bean sorting system on Raspberry Pi 5.

## 📁 Package Contents

```
raspberry_pi_deployment/
├── scripts/                    # Python scripts
│   ├── bean_sorter.py         # Command-line version
│   ├── bean_sorter_hmi.py     # Touchscreen HMI version ⭐
│   ├── test_camera.py         # Camera testing
│   └── test_hardware.py       # Hardware testing
│
├── models/                     # Trained model
│   └── best_model.keras       # AI model (89.33% accuracy)
│
├── docs/                       # Documentation
│   ├── RASPBERRY_PI_SETUP.md  # Complete setup guide
│   ├── WIRING_DIAGRAM.md      # Wiring diagrams
│   ├── TOUCHSCREEN_HMI_GUIDE.md # HMI user guide
│   ├── QUICK_START.md         # Quick start guide
│   ├── HMI_GUIDE.md           # Complete HMI guide
│   └── SYSTEM_OVERVIEW.md     # System overview
│
├── README.md                   # This file
├── install.sh                  # Installation script
└── setup_instructions.txt      # Step-by-step setup

```

## 🚀 Quick Setup

### Step 1: Transfer to Raspberry Pi

**Option A: Using SCP (from Windows)**
```bash
scp -r raspberry_pi_deployment pi@raspberrypi.local:~/
```

**Option B: Using USB Drive**
1. Copy entire `raspberry_pi_deployment` folder to USB drive
2. Insert USB into Raspberry Pi
3. Copy folder to home directory

**Option C: Using FileZilla/WinSCP**
1. Connect to Raspberry Pi
2. Upload entire `raspberry_pi_deployment` folder to `/home/pi/`

### Step 2: Install on Raspberry Pi

```bash
# SSH into Raspberry Pi
ssh pi@raspberrypi.local

# Navigate to deployment folder
cd ~/raspberry_pi_deployment

# Run installation script
chmod +x install.sh
./install.sh
```

### Step 3: Test Hardware

```bash
# Test all hardware
python3 scripts/test_hardware.py all

# Test camera
python3 scripts/test_camera.py models/best_model.keras
```

### Step 4: Run System

**Option A: Touchscreen HMI (Recommended for farmers)**
```bash
python3 scripts/bean_sorter_hmi.py models/best_model.keras
```

**Option B: Command Line**
```bash
python3 scripts/bean_sorter.py models/best_model.keras
```

## 📖 Documentation

- **Quick Start**: `docs/QUICK_START.md`
- **Complete Setup**: `docs/RASPBERRY_PI_SETUP.md`
- **Wiring Guide**: `docs/WIRING_DIAGRAM.md`
- **HMI Guide**: `docs/TOUCHSCREEN_HMI_GUIDE.md`
- **System Overview**: `docs/SYSTEM_OVERVIEW.md`

## 🔧 Hardware Requirements

- Raspberry Pi 5 (or Pi 4)
- Pi Camera Module V2/V3
- Servo Motor (SG90 or MG996R)
- BTS7960 Motor Driver
- DC Motor (12V)
- Power supplies (5V 3A + 12V 5A)
- Optional: 7" Touchscreen for HMI

## 📞 Support

See documentation files in `docs/` folder for detailed help.

---

**Ready to Deploy!** 🚀☕
"""
    
    with open(deploy_dir / "README.md", "w") as f:
        f.write(readme_content)
    print(f"  ✓ Created README.md")
    
    # Create installation script
    install_script = """#!/bin/bash
# Coffee Bean Sorter - Installation Script for Raspberry Pi

echo "======================================================================"
echo "COFFEE BEAN SORTER - INSTALLATION"
echo "======================================================================"
echo ""

# Update system
echo "Step 1: Updating system..."
sudo apt update

# Install dependencies
echo ""
echo "Step 2: Installing dependencies..."
sudo apt install -y python3-pip python3-opencv python3-picamera2 python3-tk

# Install Python packages
echo ""
echo "Step 3: Installing Python packages..."
pip3 install tensorflow RPi.GPIO numpy opencv-python --break-system-packages

# Enable camera
echo ""
echo "Step 4: Checking camera configuration..."
echo "Please enable camera in raspi-config if not already enabled"
echo "Run: sudo raspi-config"
echo "Navigate to: Interface Options → Camera → Enable"

# Create symlinks for easy access
echo ""
echo "Step 5: Creating convenient shortcuts..."
mkdir -p ~/bean_sorter
cp -r scripts/* ~/bean_sorter/
cp -r models ~/bean_sorter/
cp -r docs ~/bean_sorter/

# Make scripts executable
chmod +x ~/bean_sorter/*.py

echo ""
echo "======================================================================"
echo "INSTALLATION COMPLETE!"
echo "======================================================================"
echo ""
echo "Scripts installed to: ~/bean_sorter/"
echo ""
echo "Next steps:"
echo "1. Enable camera: sudo raspi-config"
echo "2. Reboot: sudo reboot"
echo "3. Test hardware: python3 ~/bean_sorter/test_hardware.py all"
echo "4. Test camera: python3 ~/bean_sorter/test_camera.py ~/bean_sorter/models/best_model.keras"
echo "5. Run HMI: python3 ~/bean_sorter/bean_sorter_hmi.py ~/bean_sorter/models/best_model.keras"
echo ""
echo "Documentation: ~/bean_sorter/docs/"
echo ""
echo "======================================================================"
"""
    
    with open(deploy_dir / "install.sh", "w", newline='\n') as f:
        f.write(install_script)
    print(f"  ✓ Created install.sh")
    
    # Create setup instructions
    setup_instructions = """COFFEE BEAN SORTER - SETUP INSTRUCTIONS
========================================

STEP-BY-STEP SETUP FOR RASPBERRY PI 5
======================================

1. TRANSFER FILES TO RASPBERRY PI
----------------------------------

Option A: Using SCP (from Windows PowerShell)
   scp -r raspberry_pi_deployment pi@raspberrypi.local:~/

Option B: Using USB Drive
   - Copy entire raspberry_pi_deployment folder to USB
   - Insert USB into Raspberry Pi
   - Copy folder to /home/pi/

Option C: Using FileZilla/WinSCP
   - Connect to Raspberry Pi
   - Upload raspberry_pi_deployment folder


2. CONNECT TO RASPBERRY PI
---------------------------

   ssh pi@raspberrypi.local
   (Default password: raspberry)


3. RUN INSTALLATION
-------------------

   cd ~/raspberry_pi_deployment
   chmod +x install.sh
   ./install.sh


4. ENABLE CAMERA
----------------

   sudo raspi-config
   
   Navigate to:
   - Interface Options
   - Camera
   - Enable
   
   Then reboot:
   sudo reboot


5. CONNECT HARDWARE
-------------------

See docs/WIRING_DIAGRAM.md for detailed wiring instructions.

Servo Motor:
   VCC → 5V (Pin 2)
   GND → GND (Pin 6)
   Signal → GPIO 18 (Pin 12)

BTS7960 Motor Driver:
   Logic VCC → 5V (Pin 2)
   Logic GND → GND (Pin 14)
   RPWM → GPIO 23 (Pin 16)
   LPWM → GPIO 24 (Pin 18)
   R_EN → GPIO 25 (Pin 22)
   L_EN → GPIO 8 (Pin 24)
   Motor Power → 12V External
   B+/B- → DC Motor


6. TEST HARDWARE
----------------

   cd ~/bean_sorter
   
   Test servo:
   python3 test_hardware.py servo
   
   Test motor:
   python3 test_hardware.py motor
   
   Test all:
   python3 test_hardware.py all


7. TEST CAMERA
--------------

   python3 test_camera.py models/best_model.keras
   
   Press 'c' to capture
   Press 'q' to quit


8. RUN SORTING SYSTEM
---------------------

Option A: Touchscreen HMI (Recommended)
   python3 bean_sorter_hmi.py models/best_model.keras

Option B: Command Line
   python3 bean_sorter.py models/best_model.keras


9. AUTO-START ON BOOT (Optional)
---------------------------------

   mkdir -p ~/.config/autostart
   nano ~/.config/autostart/bean-sorter.desktop
   
   Add:
   [Desktop Entry]
   Type=Application
   Name=Bean Sorter HMI
   Exec=/usr/bin/python3 /home/pi/bean_sorter/bean_sorter_hmi.py /home/pi/bean_sorter/models/best_model.keras
   Terminal=false


TROUBLESHOOTING
===============

Camera not working:
   libcamera-hello
   (If error, enable camera in raspi-config)

GPIO errors:
   python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

Touchscreen not responding:
   sudo apt install -y xinput-calibrator
   xinput_calibrator


DOCUMENTATION
=============

All documentation is in the docs/ folder:
- QUICK_START.md - Quick setup guide
- RASPBERRY_PI_SETUP.md - Complete setup
- WIRING_DIAGRAM.md - Wiring diagrams
- TOUCHSCREEN_HMI_GUIDE.md - HMI user guide
- HMI_GUIDE.md - Complete HMI guide
- SYSTEM_OVERVIEW.md - System overview


SUPPORT
=======

For detailed help, see documentation files.

Ready to sort coffee beans! ☕🚀
"""
    
    with open(deploy_dir / "setup_instructions.txt", "w") as f:
        f.write(setup_instructions)
    print(f"  ✓ Created setup_instructions.txt")
    
    # Create transfer script for Windows
    transfer_script = """@echo off
REM Transfer deployment package to Raspberry Pi
REM Edit the IP address below if needed

echo ======================================================================
echo TRANSFERRING TO RASPBERRY PI
echo ======================================================================
echo.

set PI_HOST=raspberrypi.local
set PI_USER=pi

echo Transferring raspberry_pi_deployment folder to %PI_USER%@%PI_HOST%...
echo.

scp -r raspberry_pi_deployment %PI_USER%@%PI_HOST%:~/

echo.
echo ======================================================================
echo TRANSFER COMPLETE!
echo ======================================================================
echo.
echo Next steps:
echo 1. SSH into Raspberry Pi: ssh %PI_USER%@%PI_HOST%
echo 2. Run installation: cd ~/raspberry_pi_deployment ^&^& chmod +x install.sh ^&^& ./install.sh
echo.
pause
"""
    
    with open(deploy_dir / "transfer_to_pi.bat", "w") as f:
        f.write(transfer_script)
    print(f"  ✓ Created transfer_to_pi.bat")
    
    # Summary
    print("\n" + "="*70)
    print("DEPLOYMENT PACKAGE CREATED!")
    print("="*70)
    print(f"\nLocation: {deploy_dir.absolute()}")
    print(f"Files copied: {copied_count}")
    print("\nPackage contents:")
    print("  📁 scripts/          - Python scripts (4 files)")
    print("  📁 models/           - Trained model")
    print("  📁 docs/             - Documentation (6 files)")
    print("  📄 README.md         - Package overview")
    print("  📄 install.sh        - Installation script")
    print("  📄 setup_instructions.txt - Step-by-step guide")
    print("  📄 transfer_to_pi.bat - Windows transfer script")
    
    print("\n" + "="*70)
    print("TRANSFER OPTIONS")
    print("="*70)
    
    print("\nOption 1: Using Windows batch script")
    print("  1. Double-click: raspberry_pi_deployment/transfer_to_pi.bat")
    print("  2. Enter Raspberry Pi password when prompted")
    
    print("\nOption 2: Using SCP command")
    print("  scp -r raspberry_pi_deployment pi@raspberrypi.local:~/")
    
    print("\nOption 3: Using USB drive")
    print("  1. Copy raspberry_pi_deployment folder to USB")
    print("  2. Insert USB into Raspberry Pi")
    print("  3. Copy to /home/pi/")
    
    print("\nOption 4: Using FileZilla/WinSCP")
    print("  1. Connect to Raspberry Pi")
    print("  2. Upload raspberry_pi_deployment folder")
    
    print("\n" + "="*70)
    print("AFTER TRANSFER")
    print("="*70)
    print("\nOn Raspberry Pi, run:")
    print("  cd ~/raspberry_pi_deployment")
    print("  chmod +x install.sh")
    print("  ./install.sh")
    
    print("\n" + "="*70)
    print("✓ READY TO DEPLOY!")
    print("="*70)
    
    return deploy_dir


if __name__ == "__main__":
    deploy_dir = create_deployment_package()
    print(f"\nDeployment package ready at: {deploy_dir.absolute()}")
