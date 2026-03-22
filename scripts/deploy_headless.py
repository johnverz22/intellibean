#!/usr/bin/env python3
"""
Deploy headless collector to Raspberry Pi
"""

import subprocess
import os

RPI_HOST = "192.168.100.197"
RPI_USER = "beans"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519_rpi").replace('/', '\\')

def upload_file(local_file, remote_file):
    """Upload file to Raspberry Pi"""
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           local_file, f'{RPI_USER}@{RPI_HOST}:{remote_file}']
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0

def run_ssh(command):
    """Run SSH command"""
    cmd = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           '-o', 'ConnectTimeout=10',
           f'{RPI_USER}@{RPI_HOST}', command]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode

print("="*60)
print("Deploying Headless Collector to Raspberry Pi")
print("="*60)

# Upload files
print("\n1. Uploading files...")
files = [
    ('rpi_headless_collector.py', '~/rpi_headless_collector.py'),
    ('rpi_web_collector.py', '~/rpi_web_collector.py')
]

for local, remote in files:
    print(f"   Uploading {local}...")
    if upload_file(local, remote):
        print(f"   ✓ {local} uploaded")
    else:
        print(f"   ✗ {local} failed")

# Make executable
print("\n2. Making files executable...")
stdout, stderr, code = run_ssh("chmod +x ~/rpi_headless_collector.py ~/rpi_web_collector.py")
if code == 0:
    print("   ✓ Files are executable")
else:
    print(f"   ✗ Failed: {stderr}")

# Create directories
print("\n3. Creating directories...")
stdout, stderr, code = run_ssh("mkdir -p ~/coffee_dataset_final/{good_beans,bad_beans}/{curve,back}")
if code == 0:
    print("   ✓ Directories created")
else:
    print(f"   ✗ Failed: {stderr}")

print("\n" + "="*60)
print("✓ Deployment Complete!")
print("="*60)

print("\n" + "="*60)
print("USAGE OPTIONS")
print("="*60)

print("\nOption 1: Command-Line Interface")
print("-" * 60)
print("SSH into Raspberry Pi and run commands:")
print("")
print("  ssh beans@192.168.100.197")
print("  python3 rpi_headless_collector.py status")
print("  python3 rpi_headless_collector.py capture bad_curve")
print("  python3 rpi_headless_collector.py preview")

print("\nOption 2: Web Interface (RECOMMENDED)")
print("-" * 60)
print("Start web server on Raspberry Pi:")
print("")
print("  ssh beans@192.168.100.197")
print("  python3 rpi_web_collector.py")
print("")
print("Then open in your laptop browser:")
print("  http://192.168.100.197:8080")
print("")
print("Or start in background:")
print("  nohup python3 rpi_web_collector.py > web_collector.log 2>&1 &")

print("\nOption 3: Remote Commands from Laptop")
print("-" * 60)
print("Run commands from your laptop without SSH:")
print("")
print("  # Check status")
print(f"  ssh -i {SSH_KEY} beans@192.168.100.197 'python3 rpi_headless_collector.py status'")
print("")
print("  # Capture image")
print(f"  ssh -i {SSH_KEY} beans@192.168.100.197 'python3 rpi_headless_collector.py capture bad_curve'")

print("\n" + "="*60)
