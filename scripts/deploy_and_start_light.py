#!/usr/bin/env python3
"""
Deploy and start light daemon on Raspberry Pi
"""

import subprocess
import os
import time

RPI_HOST = "192.168.100.197"
RPI_USER = "beans"
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519_rpi")

def run_ssh(command):
    """Run SSH command"""
    cmd = ['ssh', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           f'{RPI_USER}@{RPI_HOST}', command]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def upload_file(local_path, remote_path):
    """Upload file via SCP"""
    cmd = ['scp', '-i', SSH_KEY, '-o', 'StrictHostKeyChecking=no',
           local_path, f'{RPI_USER}@{RPI_HOST}:{remote_path}']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("="*60)
    print("Deploy and Start Light Daemon")
    print("="*60)
    
    # Step 1: Upload daemon script
    print("\n1. Uploading light_daemon.py...")
    if upload_file('light_daemon.py', '~/light_daemon.py'):
        print("   ✓ Upload successful")
    else:
        print("   ✗ Upload failed")
        return
    
    # Step 2: Make executable
    print("\n2. Making executable...")
    stdout, stderr, code = run_ssh("chmod +x ~/light_daemon.py")
    if code == 0:
        print("   ✓ Permissions set")
    else:
        print(f"   ✗ Failed: {stderr}")
        return
    
    # Step 3: Kill any existing daemon
    print("\n3. Stopping any existing daemon...")
    run_ssh("pkill -f light_daemon.py")
    time.sleep(1)
    print("   ✓ Cleaned up")
    
    # Step 4: Start daemon in background
    print("\n4. Starting light daemon...")
    stdout, stderr, code = run_ssh(
        "nohup python3 ~/light_daemon.py > ~/light_daemon.log 2>&1 & echo $!"
    )
    
    if code == 0:
        pid = stdout.strip()
        print(f"   ✓ Daemon started (PID: {pid})")
    else:
        print(f"   ✗ Failed to start: {stderr}")
        return
    
    # Step 5: Wait and verify
    print("\n5. Verifying daemon...")
    time.sleep(2)
    
    stdout, stderr, code = run_ssh("pgrep -f light_daemon.py")
    if code == 0 and stdout.strip():
        print(f"   ✓ Daemon running (PID: {stdout.strip()})")
    else:
        print("   ✗ Daemon not running")
        print("\n   Checking logs:")
        stdout, stderr, code = run_ssh("tail -20 ~/light_daemon.log")
        print(stdout)
        return
    
    # Step 6: Test brightness control
    print("\n6. Testing brightness control...")
    print("   Setting brightness to 80%...")
    stdout, stderr, code = run_ssh("echo '80' | nc localhost 9999")
    
    if code == 0 and "OK" in stdout:
        print(f"   ✓ Test successful: {stdout.strip()}")
    else:
        print(f"   ⚠ Test response: {stdout.strip()}")
    
    print("\n" + "="*60)
    print("✓ Deployment Complete!")
    print("="*60)
    print(f"\nLight daemon is running on GPIO 13")
    print(f"Default brightness: 80%")
    print(f"\nTo check status:")
    print(f"  ssh beans@{RPI_HOST}")
    print(f"  echo 'status' | nc localhost 9999")
    print(f"\nTo view logs:")
    print(f"  ssh beans@{RPI_HOST}")
    print(f"  tail -f ~/light_daemon.log")
    print(f"\nNow you can run the GUI:")
    print(f"  python remote_dataset_collector.py")
    print()

if __name__ == "__main__":
    main()
