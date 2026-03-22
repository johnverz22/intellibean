#!/usr/bin/env python3
"""
Deploy Coffee Bean Sorter code to Raspberry Pi
"""

import subprocess
import sys
import os

# Configuration
RPI_HOST = "192.168.100.197"
RPI_USER = "beans"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519_rpi")
REMOTE_DIR = "~/coffee-sorter"

def run_ssh_command(command):
    """Execute command on Raspberry Pi via SSH"""
    cmd = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no', 
           f'{RPI_USER}@{RPI_HOST}', command]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def transfer_directory(local_dir, remote_path):
    """Transfer directory to Raspberry Pi via SCP"""
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no', '-r',
           local_dir, f'{RPI_USER}@{RPI_HOST}:{remote_path}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("Deploying Coffee Bean Sorter to Raspberry Pi")
    print("=" * 60)
    print(f"Target: {RPI_USER}@{RPI_HOST}")
    print(f"Remote directory: {REMOTE_DIR}")
    print("=" * 60)
    
    # Create remote directory
    print("\n1. Creating remote directory...")
    stdout, stderr, code = run_ssh_command(f"mkdir -p {REMOTE_DIR}")
    if code == 0:
        print("✓ Directory created")
    else:
        print(f"✗ Failed: {stderr}")
        return 1
    
    # Transfer source code
    print("\n2. Transferring source code...")
    if transfer_directory('src/', f'{REMOTE_DIR}/'):
        print("✓ Source code transferred")
    else:
        print("✗ Transfer failed")
        return 1
    
    # Transfer documentation
    print("\n3. Transferring documentation...")
    if transfer_directory('docs/', f'{REMOTE_DIR}/'):
        print("✓ Documentation transferred")
    else:
        print("⚠ Documentation transfer failed (non-critical)")
    
    # Transfer scripts
    print("\n4. Transferring scripts...")
    if transfer_directory('scripts/', f'{REMOTE_DIR}/'):
        print("✓ Scripts transferred")
    else:
        print("⚠ Scripts transfer failed (non-critical)")
    
    # Set permissions
    print("\n5. Setting permissions...")
    stdout, stderr, code = run_ssh_command(f"chmod +x {REMOTE_DIR}/src/controller/*.py {REMOTE_DIR}/src/ml/*.py {REMOTE_DIR}/scripts/*.sh {REMOTE_DIR}/scripts/*.py")
    if code == 0:
        print("✓ Permissions set")
    
    # Test installation
    print("\n6. Testing installation...")
    stdout, stderr, code = run_ssh_command(f"cd {REMOTE_DIR} && python3 -c 'import sys; sys.path.insert(0, \"src/controller\"); from servo_controller import ServoController; print(\"Import successful\")'")
    
    if "Import successful" in stdout:
        print("✓ Installation verified")
    else:
        print("⚠ Import test failed (may need RPi.GPIO)")
    
    print("\n" + "=" * 60)
    print("Deployment Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print(f"1. SSH to Pi: ssh -i {SSH_KEY} {RPI_USER}@{RPI_HOST}")
    print(f"2. Navigate: cd {REMOTE_DIR}")
    print("\nFor Sorting System:")
    print("3. Test servos: python3 src/controller/servo_controller.py")
    print("4. Test camera: python3 src/controller/camera_detector.py")
    print("5. Run sorter: python3 src/controller/bean_sorter.py --mode test")
    print("\nFor Dataset Collection:")
    print("3. Setup OpenCV: ./scripts/setup_dataset_collection.sh")
    print("4. Test detection: python3 scripts/test_opencv_detection.py")
    print("5. Launch GUI: python3 src/ml/dataset_collector.py")
    print("\nSee docs/ for detailed guides:")
    print("- QUICK_START.md - Sorting system setup")
    print("- DATASET_COLLECTION_GUIDE.md - Dataset collection")
    print("- OPENCV_SETUP.md - OpenCV installation")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
