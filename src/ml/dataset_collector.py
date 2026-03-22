#!/usr/bin/env python3
"""
Coffee Bean Dataset Collector
GUI application for capturing and processing bean images
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import json
from datetime import datetime
import cv2
import numpy as np

class DatasetCollector:
    """
    GUI application for dataset collection
    
    Features:
    - One-click capture
    - Auto-crop with OpenCV
    - Progress tracking
    - Category selection
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Coffee Bean Dataset Collector")
        self.root.geometry("800x600")
        
        # Dataset configuration
        self.base_dir = "/home/beans/coffee_dataset"
        self.temp_dir = "/home/beans/temp_captures"
        
        # Target counts
        self.targets = {
            'good_curve': 1050,
            'good_back': 450,
            'bad_curve': 1050,
            'bad_back': 450
        }
        
        # Current counts
        self.counts = self.load_counts()
        
        # Create directories
        self.setup_directories()
        
        # Build GUI
        self.build_gui()
        
        # Update display
        self.update_progress()
    
    def setup_directories(self):
        """Create dataset directory structure"""
        dirs = [
            f"{self.base_dir}/good_beans/curve",
            f"{self.base_dir}/good_beans/back",
            f"{self.base_dir}/bad_beans/curve",
            f"{self.base_dir}/bad_beans/back",
            self.temp_dir
        ]
        
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def load_counts(self):
        """Load current image counts from file"""
        count_file = "/home/beans/dataset_counts.json"
        
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'good_curve': 0,
                'good_back': 0,
                'bad_curve': 0,
                'bad_back': 0
            }
    
    def save_counts(self):
        """Save current image counts to file"""
        count_file = "/home/beans/dataset_counts.json"
        with open(count_file, 'w') as f:
            json.dump(self.counts, f, indent=2)
    
    def build_gui(self):
        """Build the GUI interface"""
        # Title
        title = tk.Label(
            self.root,
            text="Coffee Bean Dataset Collector",
            font=("Arial", 24, "bold"),
            pady=20
        )
        title.pack()
        
        # Category selection
        category_frame = tk.LabelFrame(
            self.root,
            text="Select Category",
            font=("Arial", 14),
            padx=20,
            pady=20
        )
        category_frame.pack(pady=10, padx=20, fill="x")
        
        self.quality_var = tk.StringVar(value="good")
        self.side_var = tk.StringVar(value="curve")
        
        # Quality selection
        tk.Label(category_frame, text="Bean Quality:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Radiobutton(category_frame, text="Good Beans", variable=self.quality_var, value="good", font=("Arial", 11)).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(category_frame, text="Bad Beans", variable=self.quality_var, value="bad", font=("Arial", 11)).grid(row=0, column=2, sticky="w")
        
        # Side selection
        tk.Label(category_frame, text="Bean Side:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        tk.Radiobutton(category_frame, text="Curve Side", variable=self.side_var, value="curve", font=("Arial", 11)).grid(row=1, column=1, sticky="w")
        tk.Radiobutton(category_frame, text="Back Side", variable=self.side_var, value="back", font=("Arial", 11)).grid(row=1, column=2, sticky="w")
        
        # Capture button
        capture_btn = tk.Button(
            self.root,
            text="📷 CAPTURE & PROCESS",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=40,
            pady=20,
            command=self.capture_and_process
        )
        capture_btn.pack(pady=30)
        
        # Progress display
        progress_frame = tk.LabelFrame(
            self.root,
            text="Dataset Progress",
            font=("Arial", 14),
            padx=20,
            pady=20
        )
        progress_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Progress labels
        self.progress_labels = {}
        categories = [
            ('good_curve', 'Good Beans - Curve Side'),
            ('good_back', 'Good Beans - Back Side'),
            ('bad_curve', 'Bad Beans - Curve Side'),
            ('bad_back', 'Bad Beans - Back Side')
        ]
        
        for i, (key, label) in enumerate(categories):
            tk.Label(progress_frame, text=label + ":", font=("Arial", 11)).grid(row=i, column=0, sticky="w", pady=5)
            
            progress_label = tk.Label(progress_frame, text="", font=("Arial", 11, "bold"))
            progress_label.grid(row=i, column=1, sticky="w", padx=20)
            self.progress_labels[key] = progress_label
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
            progress_bar.grid(row=i, column=2, padx=10)
            self.progress_labels[f"{key}_bar"] = progress_bar
        
        # Total progress
        tk.Label(progress_frame, text="Total Progress:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", pady=15)
        self.total_label = tk.Label(progress_frame, text="", font=("Arial", 12, "bold"))
        self.total_label.grid(row=4, column=1, sticky="w", padx=20)
        
        total_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        total_bar.grid(row=4, column=2, padx=10)
        self.total_bar = total_bar
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready to capture",
            font=("Arial", 10),
            bg="#f0f0f0",
            anchor="w",
            padx=10
        )
        self.status_label.pack(side="bottom", fill="x")
    
    def update_progress(self):
        """Update progress display"""
        for key in ['good_curve', 'good_back', 'bad_curve', 'bad_back']:
            current = self.counts[key]
            target = self.targets[key]
            percentage = (current / target) * 100 if target > 0 else 0
            
            self.progress_labels[key].config(text=f"{current} / {target}")
            self.progress_labels[f"{key}_bar"]['value'] = percentage
        
        # Total progress
        total_current = sum(self.counts.values())
        total_target = sum(self.targets.values())
        total_percentage = (total_current / total_target) * 100 if total_target > 0 else 0
        
        self.total_label.config(text=f"{total_current} / {total_target} ({total_percentage:.1f}%)")
        self.total_bar['value'] = total_percentage
    
    def capture_image(self):
        """Capture high-resolution image"""
        self.status_label.config(text="Capturing image...")
        self.root.update()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file = f"{self.temp_dir}/capture_{timestamp}.jpg"
        
        # Capture with rpicam-still
        cmd = [
            "rpicam-still",
            "-o", temp_file,
            "--width", "4608",
            "--height", "2592",
            "--timeout", "1000",
            "--nopreview"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and os.path.exists(temp_file):
                return temp_file
            else:
                messagebox.showerror("Error", f"Capture failed: {result.stderr}")
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Capture error: {e}")
            return None
    
    def process_image(self, image_path, category):
        """Process image with OpenCV to extract individual beans"""
        self.status_label.config(text="Processing image with OpenCV...")
        self.root.update()
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            messagebox.showerror("Error", "Failed to read image")
            return 0
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Threshold
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area (bean size)
        min_area = 500  # Adjust based on your setup
        max_area = 5000
        valid_contours = [c for c in contours if min_area < cv2.contourArea(c) < max_area]
        
        # Sort contours by position (top to bottom, left to right)
        valid_contours = sorted(valid_contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
        
        # Extract and save each bean
        quality, side = category.split('_')
        output_dir = f"{self.base_dir}/{quality}_beans/{side}"
        
        saved_count = 0
        current_index = self.counts[category]
        
        for i, contour in enumerate(valid_contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(img.shape[1] - x, w + 2 * padding)
            h = min(img.shape[0] - y, h + 2 * padding)
            
            # Crop bean
            bean_img = img[y:y+h, x:x+w]
            
            # Save
            filename = f"{quality}_{side}_{current_index + i + 1:04d}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, bean_img)
            saved_count += 1
        
        return saved_count
    
    def capture_and_process(self):
        """Main capture and process workflow"""
        # Get selected category
        quality = self.quality_var.get()
        side = self.side_var.get()
        category = f"{quality}_{side}"
        
        # Check if target reached
        if self.counts[category] >= self.targets[category]:
            messagebox.showinfo("Complete", f"Target for {quality} {side} already reached!")
            return
        
        # Confirm
        remaining = self.targets[category] - self.counts[category]
        response = messagebox.askyesno(
            "Confirm Capture",
            f"Category: {quality.title()} Beans - {side.title()} Side\n"
            f"Current: {self.counts[category]} / {self.targets[category]}\n"
            f"Remaining: {remaining}\n\n"
            f"Ready to capture?"
        )
        
        if not response:
            return
        
        # Capture image
        image_path = self.capture_image()
        if not image_path:
            self.status_label.config(text="Capture failed")
            return
        
        # Process image
        saved_count = self.process_image(image_path, category)
        
        if saved_count > 0:
            # Update counts
            self.counts[category] += saved_count
            self.save_counts()
            self.update_progress()
            
            self.status_label.config(text=f"Success! Saved {saved_count} beans")
            messagebox.showinfo(
                "Success",
                f"Processed {saved_count} beans!\n"
                f"Total {quality} {side}: {self.counts[category]} / {self.targets[category]}"
            )
        else:
            self.status_label.config(text="No beans detected")
            messagebox.showwarning("Warning", "No beans detected in image")
        
        # Clean up temp file
        try:
            os.remove(image_path)
        except:
            pass
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = DatasetCollector()
    app.run()
