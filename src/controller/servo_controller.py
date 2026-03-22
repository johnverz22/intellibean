#!/usr/bin/env python3
"""
Servo Motor Controller for Coffee Bean Sorter
Controls 2 servo motors for gate actuation
"""

import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Warning: RPi.GPIO not available (running on non-Pi system)")
    GPIO = None

class ServoController:
    """
    Controls servo motors for 2-lane sorting gates
    
    Logic:
    LEFT LANE:
    - GOOD beans: Gate CLOSED → bean drops LEFT
    - BAD beans: Gate OPENS → bean goes STRAIGHT
    
    RIGHT LANE:
    - GOOD beans: Gate CLOSED → bean drops RIGHT  
    - BAD beans: Gate OPENS → bean goes STRAIGHT
    
    Both lanes' bad beans go to center collection bin
    """
    
    # GPIO Pin assignments
    SERVO_LEFT_LANE = 18   # GPIO 18 (Pin 12) - Left lane gate
    SERVO_RIGHT_LANE = 12  # GPIO 12 (Pin 32) - Right lane gate
    
    # Servo angles (adjust based on your servo and gate design)
    GATE_CLOSED_ANGLE = 0    # Gate closed (default position)
    GATE_OPEN_ANGLE = 90     # Gate open (let bean through)
    
    # Timing
    GATE_OPEN_DURATION = 0.3  # seconds - how long gate stays open
    SERVO_SETTLE_TIME = 0.05  # seconds - time for servo to reach position
    
    def __init__(self):
        """Initialize servo controller"""
        if GPIO is None:
            print("Warning: GPIO not available, running in simulation mode")
            self.simulation_mode = True
            return
        
        self.simulation_mode = False
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setwarnings(False)
        
        # Setup servo pins
        GPIO.setup(self.SERVO_LEFT_LANE, GPIO.OUT)
        GPIO.setup(self.SERVO_RIGHT_LANE, GPIO.OUT)
        
        # Create PWM instances (50Hz for servos)
        self.pwm_left = GPIO.PWM(self.SERVO_LEFT_LANE, 50)
        self.pwm_right = GPIO.PWM(self.SERVO_RIGHT_LANE, 50)
        
        # Start PWM with 0 duty cycle
        self.pwm_left.start(0)
        self.pwm_right.start(0)
        
        # Initialize gates to closed position
        self.close_all_gates()
        
        print("✓ Servo controller initialized")
        print(f"  Left lane gate: GPIO {self.SERVO_LEFT_LANE}")
        print(f"  Right lane gate: GPIO {self.SERVO_RIGHT_LANE}")
    
    def _angle_to_duty_cycle(self, angle):
        """
        Convert angle (0-180°) to PWM duty cycle (2-12%)
        
        Servo PWM:
        - 50Hz = 20ms period
        - 1ms pulse = 0° (5% duty cycle)
        - 1.5ms pulse = 90° (7.5% duty cycle)
        - 2ms pulse = 180° (10% duty cycle)
        """
        # Map 0-180° to 2-12% duty cycle
        duty_cycle = 2 + (angle / 180.0) * 10
        return duty_cycle
    
    def _set_servo_angle(self, pwm, angle):
        """Set servo to specific angle"""
        if self.simulation_mode:
            print(f"  [SIM] Setting servo to {angle}°")
            return
        
        duty_cycle = self._angle_to_duty_cycle(angle)
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(self.SERVO_SETTLE_TIME)
        pwm.ChangeDutyCycle(0)  # Stop sending signal to prevent jitter
    
    def close_gate(self, lane='left'):
        """
        Close specified gate
        
        Args:
            lane: 'left' or 'right'
        """
        if lane == 'left':
            self._set_servo_angle(self.pwm_left, self.GATE_CLOSED_ANGLE)
            print(f"✓ Left lane gate CLOSED ({self.GATE_CLOSED_ANGLE}°)")
        elif lane == 'right':
            self._set_servo_angle(self.pwm_right, self.GATE_CLOSED_ANGLE)
            print(f"✓ Right lane gate CLOSED ({self.GATE_CLOSED_ANGLE}°)")
    
    def open_gate(self, lane='left', duration=None):
        """
        Open specified gate for specified duration
        
        Args:
            lane: 'left' or 'right'
            duration: seconds to keep gate open (None = use default)
        """
        if duration is None:
            duration = self.GATE_OPEN_DURATION
        
        if lane == 'left':
            self._set_servo_angle(self.pwm_left, self.GATE_OPEN_ANGLE)
            print(f"✓ Left lane gate OPENED ({self.GATE_OPEN_ANGLE}°)")
            time.sleep(duration)
            self.close_gate('left')
        elif lane == 'right':
            self._set_servo_angle(self.pwm_right, self.GATE_OPEN_ANGLE)
            print(f"✓ Right lane gate OPENED ({self.GATE_OPEN_ANGLE}°)")
            time.sleep(duration)
            self.close_gate('right')
    
    def close_all_gates(self):
        """Close all gates (default/safe position)"""
        self.close_gate('left')
        self.close_gate('right')
        print("✓ All gates closed (safe position)")
    
    def sort_bean(self, lane, classification, delay=0):
        """
        Sort bean based on classification for specified lane
        
        Args:
            lane: 'left' or 'right'
            classification: 'good' or 'bad'
            delay: seconds to wait before actuating (for bean travel time)
        
        Logic:
        - GOOD bean: Gate stays closed, bean drops to side (left/right)
        - BAD bean: Gate opens briefly, bean goes straight to center
        """
        if delay > 0:
            print(f"⏱ Waiting {delay:.2f}s for bean to reach gate...")
            time.sleep(delay)
        
        lane_name = lane.upper()
        
        if classification.lower() == 'good':
            print(f"✓ {lane_name} LANE: GOOD bean - Gate remains CLOSED")
            print(f"  → Bean drops to {lane_name} good collection")
            # Gate already closed by default, no action needed
        elif classification.lower() == 'bad':
            print(f"✗ {lane_name} LANE: BAD bean - Opening gate")
            print(f"  → Bean goes STRAIGHT to center bad collection")
            self.open_gate(lane)
        else:
            print(f"⚠ Unknown classification: {classification}")
    
    def test_gates(self):
        """Test both gates - open and close sequence"""
        print("\n" + "="*50)
        print("Testing Gates")
        print("="*50)
        
        print("\n1. Testing LEFT lane gate...")
        self.close_gate('left')
        time.sleep(1)
        self.open_gate('left', duration=1)
        time.sleep(1)
        
        print("\n2. Testing RIGHT lane gate...")
        self.close_gate('right')
        time.sleep(1)
        self.open_gate('right', duration=1)
        time.sleep(1)
        
        print("\n3. Closing all gates...")
        self.close_all_gates()
        
        print("\n✓ Gate test complete")
    
    def calibrate(self):
        """
        Interactive calibration to find optimal angles
        Helps you adjust GATE_CLOSED_ANGLE and GATE_OPEN_ANGLE
        """
        print("\n" + "="*50)
        print("Servo Calibration Mode")
        print("="*50)
        print("Commands:")
        print("  l <angle> - Set left lane gate angle (0-180)")
        print("  r <angle> - Set right lane gate angle (0-180)")
        print("  q - Quit calibration")
        print("="*50)
        
        while True:
            try:
                cmd = input("\nEnter command: ").strip().lower()
                
                if cmd == 'q':
                    break
                
                parts = cmd.split()
                if len(parts) != 2:
                    print("Invalid command. Use: l <angle> or r <angle>")
                    continue
                
                lane = parts[0]
                angle = int(parts[1])
                
                if angle < 0 or angle > 180:
                    print("Angle must be between 0 and 180")
                    continue
                
                if lane == 'l':
                    self._set_servo_angle(self.pwm_left, angle)
                    print(f"Left lane gate set to {angle}°")
                elif lane == 'r':
                    self._set_servo_angle(self.pwm_right, angle)
                    print(f"Right lane gate set to {angle}°")
                else:
                    print("Invalid lane. Use 'l' or 'r'")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.close_all_gates()
        print("\n✓ Calibration complete")
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.simulation_mode:
            return
        
        print("\nCleaning up...")
        self.close_all_gates()
        self.pwm_left.stop()
        self.pwm_right.stop()
        GPIO.cleanup()
        print("✓ GPIO cleanup complete")


# Test code
if __name__ == "__main__":
    import sys
    
    print("="*50)
    print("Servo Controller Test")
    print("="*50)
    
    controller = ServoController()
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == 'calibrate':
            controller.calibrate()
        else:
            # Run test sequence
            controller.test_gates()
            
            # Simulate sorting
            print("\n" + "="*50)
            print("Simulating Bean Sorting (2 Lanes)")
            print("="*50)
            
            print("\nLEFT Lane - Bean 1: GOOD")
            controller.sort_bean('left', 'good', delay=0.5)
            time.sleep(1)
            
            print("\nRIGHT Lane - Bean 1: BAD")
            controller.sort_bean('right', 'bad', delay=0.5)
            time.sleep(1)
            
            print("\nLEFT Lane - Bean 2: BAD")
            controller.sort_bean('left', 'bad', delay=0.5)
            time.sleep(1)
            
            print("\nRIGHT Lane - Bean 2: GOOD")
            controller.sort_bean('right', 'good', delay=0.5)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        controller.cleanup()
