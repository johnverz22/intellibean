#!/usr/bin/env python3
"""
Persistent LED Light Daemon for Raspberry Pi
Keeps GPIO 13 active and listens for brightness commands
"""

import RPi.GPIO as GPIO
import socket
import sys
import signal

# Configuration
GPIO_PIN = 13
PWM_FREQ = 1000  # 1 kHz
SOCKET_PORT = 9999
SOCKET_HOST = '0.0.0.0'

class LightDaemon:
    """Persistent light control daemon"""
    
    def __init__(self):
        self.pwm = None
        self.current_brightness = 0
        self.running = True
        
        try:
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Clean up any existing GPIO usage
            try:
                GPIO.cleanup(GPIO_PIN)
            except:
                pass
            
            GPIO.setup(GPIO_PIN, GPIO.OUT)
            
            # Initialize PWM
            self.pwm = GPIO.PWM(GPIO_PIN, PWM_FREQ)
            self.pwm.start(100)  # Start at 100% duty (0% brightness due to inversion)
            
            print(f"✓ GPIO {GPIO_PIN} initialized with PWM at {PWM_FREQ} Hz")
            print(f"✓ PWM signal is INVERTED (active-low LED driver)")
            
        except Exception as e:
            print(f"✗ GPIO initialization failed: {e}")
            raise
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def set_brightness(self, brightness):
        """Set LED brightness (0-100)"""
        if brightness < 0:
            brightness = 0
        elif brightness > 100:
            brightness = 100
        
        # INVERT PWM: LED driver is active-low
        # 0% brightness = 100% duty cycle (high)
        # 100% brightness = 0% duty cycle (low)
        inverted_duty = 100 - brightness
        
        self.pwm.ChangeDutyCycle(inverted_duty)
        self.current_brightness = brightness
        print(f"Brightness: {brightness}% (PWM duty: {inverted_duty}%)")
        return brightness
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down...")
        self.running = False
    
    def start_server(self):
        """Start socket server to listen for commands"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((SOCKET_HOST, SOCKET_PORT))
        sock.listen(1)
        sock.settimeout(1.0)  # Timeout to check running flag
        
        print(f"✓ Light daemon listening on port {SOCKET_PORT}")
        print("Commands: <brightness> (0-100), 'status', 'quit'")
        print("Press Ctrl+C to stop\n")
        
        while self.running:
            try:
                conn, addr = sock.accept()
                with conn:
                    data = conn.recv(1024).decode().strip()
                    
                    if not data:
                        continue
                    
                    # Handle commands
                    if data.lower() == 'quit':
                        conn.sendall(b"Shutting down\n")
                        self.running = False
                    elif data.lower() == 'status':
                        response = f"Brightness: {self.current_brightness}%\n"
                        conn.sendall(response.encode())
                    else:
                        try:
                            brightness = int(data)
                            actual = self.set_brightness(brightness)
                            response = f"OK: {actual}%\n"
                            conn.sendall(response.encode())
                        except ValueError:
                            conn.sendall(b"ERROR: Invalid brightness value\n")
            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error: {e}")
        
        sock.close()
    
    def cleanup(self):
        """Cleanup GPIO"""
        if self.pwm:
            self.pwm.stop()
        GPIO.cleanup()
        print("✓ GPIO cleaned up")


def main():
    """Main entry point"""
    print("="*60)
    print("LED Light Daemon - Persistent GPIO Control")
    print("="*60)
    
    daemon = LightDaemon()
    
    try:
        daemon.start_server()
    finally:
        daemon.cleanup()


if __name__ == "__main__":
    main()
