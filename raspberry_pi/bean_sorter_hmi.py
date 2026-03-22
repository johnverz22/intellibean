#!/usr/bin/env python3
"""
Coffee Bean Sorting System - Touchscreen HMI
Farmer-friendly interface with large buttons and clear display
"""

import tkinter as tk
from tkinter import font as tkfont
import numpy as np
import cv2
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import lgpio
import time
import threading
from datetime import datetime

# Use TFLite runtime (lightweight, works on Pi with Python 3.13)
try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    from tflite_runtime.interpreter import Interpreter

# ============================================================================
# GPIO PIN CONFIGURATION
# ============================================================================
SERVO_PIN = 22
MOTOR_RPWM = 13
MOTOR_LPWM = 26
MOTOR_R_EN = 27
MOTOR_L_EN = 21
LED_GOOD = 17
LED_BAD = 5

# ============================================================================
# SERVO & MOTOR SETTINGS (SG90: 50Hz, 1000us=0°, 1500us=90°, 2000us=180°)
# ============================================================================
SERVO_FREQ    = 50      # Hz
SERVO_CLOSED  = 1000    # us — 0°   (good beans)
SERVO_NEUTRAL = 1500    # us — 90°  (center)
SERVO_OPEN    = 2000    # us — 180° (bad beans)
CONVEYOR_SPEED = 50

# ============================================================================
# DETECTION SETTINGS
# ============================================================================
DETECTION_CONFIDENCE = 0.7
DETECTION_DELAY = 1.5
SERVO_ACTIVATION_DELAY = 0.8


class BeanSorterHMI:
    """Touchscreen HMI for Bean Sorting System"""
    
    def __init__(self, model_path):
        """Initialize HMI"""
        
        # Main window
        self.root = tk.Tk()
        self.root.title("Coffee Bean Sorter")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2C3E50')
        
        # Fonts
        self.title_font = tkfont.Font(family='Arial', size=36, weight='bold')
        self.counter_font = tkfont.Font(family='Arial', size=48, weight='bold')
        self.label_font = tkfont.Font(family='Arial', size=24)
        self.button_font = tkfont.Font(family='Arial', size=28, weight='bold')
        self.status_font = tkfont.Font(family='Arial', size=20, weight='bold')
        
        # Colors
        self.bg_color = '#2C3E50'
        self.good_color = '#27AE60'
        self.bad_color = '#E74C3C'
        self.total_color = '#3498DB'
        self.start_color = '#27AE60'
        self.stop_color = '#E74C3C'
        self.text_color = '#ECF0F1'
        
        # State
        self.is_running = False
        self.good_count = 0
        self.bad_count = 0
        self.total_count = 0
        self.session_start_time = None
        
        # Load TFLite model
        print("Loading model...")
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        print("✓ Model loaded")
        
        # Setup GPIO
        print("Setting up GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self._setup_gpio()
        print("✓ GPIO configured")
        
        # Setup camera
        print("Initializing camera...")
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        self.camera.configure(config)
        self.camera.start()
        time.sleep(2)
        print("✓ Camera ready")
        
        self.last_detection_time = 0
        
        # Create UI
        self._create_ui()
        
        # Start detection thread
        self.detection_thread = None
        
        print("✓ HMI ready!")
    
    def _setup_gpio(self):
        """Configure GPIO pins"""
        # Servo via lgpio (hardware-accurate PWM on Pi 5)
        self._lg = lgpio.gpiochip_open(4)
        lgpio.gpio_claim_output(self._lg, SERVO_PIN)
        self._set_servo_us(SERVO_NEUTRAL)

        # Motor driver via RPi.GPIO
        GPIO.setup(MOTOR_RPWM, GPIO.OUT)
        GPIO.setup(MOTOR_LPWM, GPIO.OUT)
        GPIO.setup(MOTOR_R_EN, GPIO.OUT)
        GPIO.setup(MOTOR_L_EN, GPIO.OUT)

        self.motor_rpwm = GPIO.PWM(MOTOR_RPWM, 1000)
        self.motor_lpwm = GPIO.PWM(MOTOR_LPWM, 1000)

        GPIO.output(MOTOR_R_EN, GPIO.HIGH)
        GPIO.output(MOTOR_L_EN, GPIO.HIGH)

        # LEDs
        GPIO.setup(LED_GOOD, GPIO.OUT)
        GPIO.setup(LED_BAD, GPIO.OUT)
        GPIO.output(LED_GOOD, GPIO.LOW)
        GPIO.output(LED_BAD, GPIO.LOW)

    def _set_servo_us(self, pulsewidth_us):
        """Set SG90 servo position via lgpio pulsewidth (us)"""
        period_us = 1_000_000 / SERVO_FREQ  # 20000 us
        duty = (pulsewidth_us / period_us) * 100
        lgpio.tx_pwm(self._lg, SERVO_PIN, SERVO_FREQ, duty)
    
    def _create_ui(self):
        """Create user interface"""
        
        # Title
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="☕ COFFEE BEAN SORTER ☕",
            font=self.title_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack()
        
        # Status indicator
        self.status_frame = tk.Frame(self.root, bg=self.bg_color)
        self.status_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="● READY TO START",
            font=self.status_font,
            bg=self.bg_color,
            fg='#F39C12'
        )
        self.status_label.pack()
        
        # Counters frame
        counters_frame = tk.Frame(self.root, bg=self.bg_color)
        counters_frame.pack(pady=30)
        
        # Good beans counter
        good_frame = tk.Frame(counters_frame, bg=self.good_color, relief=tk.RAISED, bd=5)
        good_frame.grid(row=0, column=0, padx=20, pady=10, ipadx=30, ipady=20)
        
        tk.Label(
            good_frame,
            text="GOOD BEANS",
            font=self.label_font,
            bg=self.good_color,
            fg='white'
        ).pack()
        
        self.good_label = tk.Label(
            good_frame,
            text="0",
            font=self.counter_font,
            bg=self.good_color,
            fg='white'
        )
        self.good_label.pack()
        
        # Bad beans counter
        bad_frame = tk.Frame(counters_frame, bg=self.bad_color, relief=tk.RAISED, bd=5)
        bad_frame.grid(row=0, column=1, padx=20, pady=10, ipadx=30, ipady=20)
        
        tk.Label(
            bad_frame,
            text="BAD BEANS",
            font=self.label_font,
            bg=self.bad_color,
            fg='white'
        ).pack()
        
        self.bad_label = tk.Label(
            bad_frame,
            text="0",
            font=self.counter_font,
            bg=self.bad_color,
            fg='white'
        )
        self.bad_label.pack()
        
        # Total counter
        total_frame = tk.Frame(self.root, bg=self.total_color, relief=tk.RAISED, bd=5)
        total_frame.pack(pady=20, ipadx=50, ipady=20)
        
        tk.Label(
            total_frame,
            text="TOTAL BEANS SORTED",
            font=self.label_font,
            bg=self.total_color,
            fg='white'
        ).pack()
        
        self.total_label = tk.Label(
            total_frame,
            text="0",
            font=self.counter_font,
            bg=self.total_color,
            fg='white'
        )
        self.total_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=40)
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ START SORTING",
            font=self.button_font,
            bg=self.start_color,
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            width=18,
            height=2,
            relief=tk.RAISED,
            bd=5,
            command=self.start_sorting
        )
        self.start_button.grid(row=0, column=0, padx=20)
        
        self.stop_button = tk.Button(
            button_frame,
            text="■ STOP & SUMMARY",
            font=self.button_font,
            bg=self.stop_color,
            fg='white',
            activebackground='#C0392B',
            activeforeground='white',
            width=18,
            height=2,
            relief=tk.RAISED,
            bd=5,
            command=self.stop_sorting,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=20)
        
        # Exit button (small, bottom right)
        exit_button = tk.Button(
            self.root,
            text="✕ Exit",
            font=tkfont.Font(family='Arial', size=14),
            bg='#95A5A6',
            fg='white',
            command=self.exit_app,
            width=8,
            height=1
        )
        exit_button.place(relx=0.98, rely=0.98, anchor='se')
    
    def update_counters(self):
        """Update counter displays"""
        self.good_label.config(text=str(self.good_count))
        self.bad_label.config(text=str(self.bad_count))
        self.total_label.config(text=str(self.total_count))
    
    def update_status(self, text, color):
        """Update status indicator"""
        self.status_label.config(text=text, fg=color)
    
    def start_sorting(self):
        """Start the sorting process"""
        if self.is_running:
            return
        
        self.is_running = True
        self.session_start_time = datetime.now()
        
        # Update UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("● SORTING IN PROGRESS...", '#27AE60')
        
        # Start conveyor
        self.motor_rpwm.start(CONVEYOR_SPEED)
        self.motor_lpwm.start(0)
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
        
        print("Sorting started!")
    
    def stop_sorting(self):
        """Stop sorting and show summary"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop conveyor
        self.motor_rpwm.ChangeDutyCycle(0)
        self.motor_lpwm.ChangeDutyCycle(0)

        # Reset servo
        self.set_servo_position(SERVO_NEUTRAL)

        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("● PROCESS COMPLETED", '#F39C12')
        
        # Show summary
        self.show_summary()
        
        print("Sorting stopped!")
    
    def show_summary(self):
        """Show sorting session summary"""
        # Calculate session duration
        if self.session_start_time:
            duration = datetime.now() - self.session_start_time
            minutes = int(duration.total_seconds() / 60)
            seconds = int(duration.total_seconds() % 60)
            duration_str = f"{minutes}m {seconds}s"
        else:
            duration_str = "N/A"
        
        # Calculate percentages
        if self.total_count > 0:
            good_percent = (self.good_count / self.total_count) * 100
            bad_percent = (self.bad_count / self.total_count) * 100
        else:
            good_percent = 0
            bad_percent = 0
        
        # Create summary window
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Sorting Summary")
        summary_window.geometry("700x600")
        summary_window.configure(bg='#34495E')
        summary_window.attributes('-topmost', True)
        
        # Title
        tk.Label(
            summary_window,
            text="📊 SORTING SUMMARY",
            font=tkfont.Font(family='Arial', size=32, weight='bold'),
            bg='#34495E',
            fg='white'
        ).pack(pady=20)
        
        # Summary frame
        summary_frame = tk.Frame(summary_window, bg='#34495E')
        summary_frame.pack(pady=20)
        
        # Results
        results = [
            ("Good Beans:", self.good_count, f"{good_percent:.1f}%", self.good_color),
            ("Bad Beans:", self.bad_count, f"{bad_percent:.1f}%", self.bad_color),
            ("Total Sorted:", self.total_count, "100%", self.total_color),
            ("Duration:", duration_str, "", '#95A5A6')
        ]
        
        for i, (label, value, percent, color) in enumerate(results):
            frame = tk.Frame(summary_frame, bg='#34495E')
            frame.pack(pady=10, fill=tk.X)
            
            tk.Label(
                frame,
                text=label,
                font=tkfont.Font(family='Arial', size=20),
                bg='#34495E',
                fg='white',
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT, padx=10)
            
            if isinstance(value, int):
                value_text = f"{value} beans"
            else:
                value_text = value
            
            tk.Label(
                frame,
                text=value_text,
                font=tkfont.Font(family='Arial', size=20, weight='bold'),
                bg='#34495E',
                fg=color,
                width=15
            ).pack(side=tk.LEFT, padx=10)
            
            if percent:
                tk.Label(
                    frame,
                    text=percent,
                    font=tkfont.Font(family='Arial', size=20),
                    bg='#34495E',
                    fg='white',
                    width=10
                ).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        button_frame = tk.Frame(summary_window, bg='#34495E')
        button_frame.pack(pady=30)
        
        # New session button
        tk.Button(
            button_frame,
            text="🔄 NEW SESSION",
            font=tkfont.Font(family='Arial', size=18, weight='bold'),
            bg='#27AE60',
            fg='white',
            width=15,
            height=2,
            command=lambda: [self.reset_counters(), summary_window.destroy()]
        ).pack(side=tk.LEFT, padx=10)
        
        # Close button
        tk.Button(
            button_frame,
            text="✓ CLOSE",
            font=tkfont.Font(family='Arial', size=18, weight='bold'),
            bg='#3498DB',
            fg='white',
            width=15,
            height=2,
            command=summary_window.destroy
        ).pack(side=tk.LEFT, padx=10)
    
    def reset_counters(self):
        """Reset all counters"""
        self.good_count = 0
        self.bad_count = 0
        self.total_count = 0
        self.update_counters()
        self.update_status("● READY TO START", '#F39C12')
        print("Counters reset!")
    
    def set_servo_position(self, pulsewidth_us):
        """Set servo position and hold briefly, then idle"""
        self._set_servo_us(pulsewidth_us)
        time.sleep(0.4)
        lgpio.tx_pwm(self._lg, SERVO_PIN, 0, 0)  # idle signal
    
    def sort_bean(self, is_good):
        """Control servo to sort bean"""
        if is_good:
            self.set_servo_position(SERVO_CLOSED)
            GPIO.output(LED_GOOD, GPIO.HIGH)
            self.good_count += 1
        else:
            self.set_servo_position(SERVO_OPEN)
            GPIO.output(LED_BAD, GPIO.HIGH)
            self.bad_count += 1
        
        self.total_count += 1
        
        # Update UI
        self.root.after(0, self.update_counters)
        
        # Turn off LED
        time.sleep(0.2)
        GPIO.output(LED_GOOD, GPIO.LOW)
        GPIO.output(LED_BAD, GPIO.LOW)
        
        # Return to neutral
        time.sleep(0.5)
        self.set_servo_position(SERVO_NEUTRAL)
    
    def preprocess_image(self, frame):
        """Preprocess camera frame for model"""
        img = cv2.resize(frame, (224, 224))
        img_array = np.array(img, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def predict_bean_quality(self, frame):
        """Predict if bean is good or bad using TFLite"""
        img_array = self.preprocess_image(frame)
        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)
        self.interpreter.invoke()
        predictions = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        confidence = float(np.max(predictions))
        predicted_class = int(np.argmax(predictions))
        is_good = predicted_class == 1
        return is_good, confidence
    
    def detection_loop(self):
        """Main detection loop"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check if enough time has passed
                if current_time - self.last_detection_time < DETECTION_DELAY:
                    time.sleep(0.1)
                    continue
                
                # Capture frame
                frame = self.camera.capture_array()
                
                # Predict
                is_good, confidence = self.predict_bean_quality(frame)
                
                # Only act if confidence is high enough
                if confidence >= DETECTION_CONFIDENCE:
                    self.last_detection_time = current_time
                    
                    # Schedule servo activation after delay
                    threading.Timer(
                        SERVO_ACTIVATION_DELAY,
                        self.sort_bean,
                        args=(is_good,)
                    ).start()
            
            except Exception as e:
                print(f"Detection error: {e}")
                time.sleep(0.1)
    
    def exit_app(self):
        """Exit application"""
        if self.is_running:
            self.stop_sorting()
        
        self.cleanup()
        self.root.quit()
        self.root.destroy()
    
    def cleanup(self):
        """Clean up resources"""
        print("\nCleaning up...")

        # Stop conveyor
        self.motor_rpwm.ChangeDutyCycle(0)
        self.motor_lpwm.ChangeDutyCycle(0)

        # Reset servo then stop lgpio
        self._set_servo_us(SERVO_NEUTRAL)
        time.sleep(0.5)
        lgpio.tx_pwm(self._lg, SERVO_PIN, 0, 0)
        lgpio.gpiochip_close(self._lg)

        # Stop motor PWM
        self.motor_rpwm.stop()
        self.motor_lpwm.stop()

        # Cleanup RPi.GPIO
        GPIO.cleanup()

        # Stop camera
        self.camera.stop()

        print("✓ Cleanup complete")
    
    def run(self):
        """Run the HMI"""
        self.root.mainloop()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Coffee Bean Sorter - Touchscreen HMI'
    )
    parser.add_argument('model', help='Path to TFLite model (.tflite)')
    
    args = parser.parse_args()
    
    # Create and run HMI
    hmi = BeanSorterHMI(args.model)
    hmi.run()


if __name__ == "__main__":
    main()
