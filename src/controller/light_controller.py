#!/usr/bin/env python3
"""
LED Light Controller for Dataset Collection
Controls brightness via PWM on Raspberry Pi 5
"""

import RPi.GPIO as GPIO
import time

class LightController:
    """
    Controls LED lighting brightness via PWM
    
    GPIO Pin: GPIO 13 (Pin 33) - PWM1
    Frequency: 1000 Hz (1 kHz)
    Duty Cycle: 0-100%
    """
    
    def __init__(self, gpio_pin=13, pwm_frequency=1000):
        """
        Initialize light controller
        
        Args:
            gpio_pin: GPIO pin number (BCM mode) - default GPIO 13
            pwm_frequency: PWM frequency in Hz - default 1000 Hz
        """
        self.gpio_pin = gpio_pin
        self.pwm_frequency = pwm_frequency
        self.pwm = None
        self.current_brightness = 0
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        
        # Initialize PWM
        self.pwm = GPIO.PWM(self.gpio_pin, self.pwm_frequency)
        self.pwm.start(0)  # Start with 0% brightness (off)
        
        print(f"Light Controller initialized on GPIO {self.gpio_pin}")
    
    def set_brightness(self, brightness):
        """
        Set LED brightness
        
        Args:
            brightness: 0-100 (percentage)
        """
        if brightness < 0:
            brightness = 0
        elif brightness > 100:
            brightness = 100
        
        self.pwm.ChangeDutyCycle(brightness)
        self.current_brightness = brightness
        print(f"Light brightness set to {brightness}%")
    
    def turn_on(self, brightness=100):
        """Turn light on at specified brightness"""
        self.set_brightness(brightness)
    
    def turn_off(self):
        """Turn light off"""
        self.set_brightness(0)
    
    def get_brightness(self):
        """Get current brightness level"""
        return self.current_brightness
    
    def fade_to(self, target_brightness, duration=1.0, steps=50):
        """
        Fade light to target brightness
        
        Args:
            target_brightness: Target brightness (0-100)
            duration: Fade duration in seconds
            steps: Number of steps in fade
        """
        start_brightness = self.current_brightness
        step_size = (target_brightness - start_brightness) / steps
        step_delay = duration / steps
        
        for i in range(steps):
            new_brightness = start_brightness + (step_size * (i + 1))
            self.set_brightness(int(new_brightness))
            time.sleep(step_delay)
        
        # Ensure final brightness is exact
        self.set_brightness(target_brightness)
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.pwm:
            self.pwm.stop()
        GPIO.cleanup(self.gpio_pin)
        print("Light Controller cleaned up")


def main():
    """Test light controller"""
    print("="*60)
    print("LED Light Controller Test")
    print("="*60)
    
    # Initialize controller
    light = LightController(gpio_pin=13)
    
    try:
        # Test sequence
        print("\nTest 1: Turn on at 50%")
        light.turn_on(50)
        time.sleep(2)
        
        print("\nTest 2: Increase to 100%")
        light.set_brightness(100)
        time.sleep(2)
        
        print("\nTest 3: Decrease to 25%")
        light.set_brightness(25)
        time.sleep(2)
        
        print("\nTest 4: Fade to 75% over 2 seconds")
        light.fade_to(75, duration=2.0)
        time.sleep(1)
        
        print("\nTest 5: Turn off")
        light.turn_off()
        time.sleep(1)
        
        print("\n✓ All tests completed")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        light.cleanup()


if __name__ == "__main__":
    main()
