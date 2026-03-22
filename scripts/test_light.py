#!/usr/bin/env python3
"""Quick test script for LED brightness control"""

import socket
import time

RPI_HOST = "192.168.100.197"
RPI_PORT = 9999

def send_command(command):
    """Send command to light daemon"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((RPI_HOST, RPI_PORT))
        sock.sendall(f"{command}\n".encode())
        response = sock.recv(1024).decode().strip()
        sock.close()
        return response
    except Exception as e:
        return f"Error: {e}"

def main():
    print("="*60)
    print("LED Light Brightness Test")
    print("="*60)
    
    tests = [
        ("Off (0%)", "0"),
        ("25%", "25"),
        ("50%", "50"),
        ("75%", "75"),
        ("100% (Full)", "100"),
        ("Back to 80%", "80"),
    ]
    
    for label, brightness in tests:
        print(f"\nSetting: {label}")
        response = send_command(brightness)
        print(f"Response: {response}")
        time.sleep(2)
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    main()
