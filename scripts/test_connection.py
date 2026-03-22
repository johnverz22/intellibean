#!/usr/bin/env python3
"""
Test SSH connection to Raspberry Pi
"""

import subprocess
import os

RPI_HOST = "192.168.100.197"
RPI_USER = "beans"

# Get SSH key path
ssh_key_path = os.path.expanduser("~/.ssh/id_ed25519_rpi")
ssh_key = ssh_key_path.replace('/', '\\')

print("="*60)
print("Testing SSH Connection to Raspberry Pi")
print("="*60)
print(f"Host: {RPI_HOST}")
print(f"User: {RPI_USER}")
print(f"SSH Key: {ssh_key}")
print()

# Test 1: Ping
print("Test 1: Ping Raspberry Pi...")
try:
    result = subprocess.run(['ping', '-n', '2', RPI_HOST], 
                          capture_output=True, text=True, timeout=5)
    if "Reply from" in result.stdout:
        print("✓ Raspberry Pi is reachable")
    else:
        print("✗ Raspberry Pi is not reachable")
        print(result.stdout)
except Exception as e:
    print(f"✗ Ping failed: {e}")

print()

# Test 2: SSH Connection
print("Test 2: SSH Connection...")
cmd = ['ssh', '-i', ssh_key, 
       '-o', 'StrictHostKeyChecking=no',
       '-o', 'ConnectTimeout=10',
       f'{RPI_USER}@{RPI_HOST}', 
       'echo "Connected" && hostname']

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        print("✓ SSH connection successful")
        print(f"  Output: {result.stdout.strip()}")
    else:
        print("✗ SSH connection failed")
        print(f"  Error: {result.stderr}")
except subprocess.TimeoutExpired:
    print("✗ SSH connection timeout")
except Exception as e:
    print(f"✗ SSH error: {e}")

print()

# Test 3: Camera Test
print("Test 3: Camera Test...")
cmd = ['ssh', '-i', ssh_key, 
       '-o', 'StrictHostKeyChecking=no',
       '-o', 'ConnectTimeout=10',
       f'{RPI_USER}@{RPI_HOST}', 
       'rpicam-hello --list-cameras']

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0:
        print("✓ Camera detected")
        print(f"  {result.stdout.strip()[:100]}...")
    else:
        print("✗ Camera test failed")
        print(f"  Error: {result.stderr}")
except subprocess.TimeoutExpired:
    print("✗ Camera test timeout")
except Exception as e:
    print(f"✗ Camera error: {e}")

print()

# Test 4: Light Daemon Status
print("Test 4: Light Daemon Status...")
cmd = ['ssh', '-i', ssh_key, 
       '-o', 'StrictHostKeyChecking=no',
       '-o', 'ConnectTimeout=10',
       f'{RPI_USER}@{RPI_HOST}', 
       'pgrep -f light_daemon.py']

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode == 0 and result.stdout.strip():
        print(f"✓ Light daemon running (PID: {result.stdout.strip()})")
    else:
        print("⚠ Light daemon not running")
        print("  Run: python deploy_and_start_light.py")
except subprocess.TimeoutExpired:
    print("✗ Daemon check timeout")
except Exception as e:
    print(f"✗ Daemon check error: {e}")

print()
print("="*60)
print("Connection Test Complete")
print("="*60)
