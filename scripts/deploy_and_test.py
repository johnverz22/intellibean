#!/usr/bin/env python3
"""
Deploy and run camera test on Raspberry Pi
"""

import subprocess
import sys
import os

# Configuration
RPI_HOST = "192.168.100.197"
RPI_USER = "beans"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519_rpi")

def run_ssh_command(command):
    """Execute command on Raspberry Pi via SSH"""
    cmd = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no', 
           f'{RPI_USER}@{RPI_HOST}', command]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def transfer_file(local_file, remote_path='~/'):
    """Transfer file to Raspberry Pi via SCP"""
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           local_file, f'{RPI_USER}@{RPI_HOST}:{remote_path}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("Deploying Camera Test to Raspberry Pi")
    print("=" * 60)
    
    # Transfer test script
    print("\n1. Transferring test_camera.py...")
    if not transfer_file('scripts/test_camera.py', '~/'):
        print("✗ Transfer failed")
        return 1
    print("✓ File transferred!")
    
    # Make executable
    print("\n2. Setting permissions...")
    stdout, stderr, code = run_ssh_command("chmod +x ~/test_camera.py")
    if code == 0:
        print("✓ Permissions set!")
    
    # Run camera test
    print("\n3. Running camera test on Raspberry Pi...")
    print("-" * 60)
    stdout, stderr, code = run_ssh_command("python3 ~/test_camera.py")
    print(stdout)
    if stderr:
        print("Errors:", stderr)
    print("-" * 60)
    
    if code == 0:
        print("\n✓ Camera test completed successfully!")
        print("\nTo view captured images, run:")
        print(f"  scp -i {SSH_KEY} {RPI_USER}@{RPI_HOST}:~/camera_test_*.jpg ./")
    else:
        print("\n✗ Camera test failed. Check output above.")
    
    return code

if __name__ == "__main__":
    sys.exit(main())
