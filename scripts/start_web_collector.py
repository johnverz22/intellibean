#!/usr/bin/env python3
"""
Start web collector on Raspberry Pi from your laptop
Then open browser automatically
"""

import subprocess
import os
import time
import webbrowser

RPI_HOST = "192.168.100.197"
RPI_USER = "beans"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519_rpi").replace('/', '\\')
WEB_PORT = 8080

def run_ssh(command):
    """Run SSH command"""
    cmd = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           '-o', 'ConnectTimeout=10',
           f'{RPI_USER}@{RPI_HOST}', command]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode

print("="*60)
print("Starting Web Collector on Raspberry Pi")
print("="*60)

# Check if already running
print("\n1. Checking if web collector is already running...")
stdout, stderr, code = run_ssh("pgrep -f rpi_web_collector.py")

if code == 0 and stdout.strip():
    print(f"   ✓ Web collector already running (PID: {stdout.strip()})")
else:
    print("   Starting web collector...")
    
    # Start in background
    stdout, stderr, code = run_ssh(
        "nohup python3 ~/rpi_web_collector.py > ~/web_collector.log 2>&1 & echo $!"
    )
    
    if code == 0:
        pid = stdout.strip()
        print(f"   ✓ Web collector started (PID: {pid})")
        print("   Waiting for server to start...")
        time.sleep(3)
    else:
        print(f"   ✗ Failed to start: {stderr}")
        exit(1)

# Open browser
print("\n2. Opening browser...")
url = f"http://{RPI_HOST}:{WEB_PORT}"
print(f"   URL: {url}")

try:
    webbrowser.open(url)
    print("   ✓ Browser opened")
except Exception as e:
    print(f"   ⚠ Could not open browser automatically: {e}")
    print(f"   Please open manually: {url}")

print("\n" + "="*60)
print("✓ Web Collector is Ready!")
print("="*60)
print(f"\nAccess at: {url}")
print("\nTo stop the web collector:")
print(f"  ssh beans@{RPI_HOST}")
print("  pkill -f rpi_web_collector.py")
print("\nTo view logs:")
print(f"  ssh beans@{RPI_HOST}")
print("  tail -f ~/web_collector.log")
print()
