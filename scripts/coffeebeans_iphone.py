#!/usr/bin/env python3
"""
Coffee Beans iPhone Dataset Organizer
Upload photos from iPhone, organize, and auto-crop beans
Supports HEIC format from iPhone
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import shutil
from datetime import datetime
from PIL import Image, ImageTk
import cv2
import numpy as np

# Try to import HEIC support
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    print("Warning: pillow-heif not installed. HEIC files will be converted.")
    print("Install with: pip install pillow-heif")

class CoffeeBeansIPhone:
    """
    iPhone photo organizer and bean cropper
    
    Features:
    - Upload photos from PC/iPhone
    - Organize into categories
    - Auto-crop individual beans
    - Progress tracking
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Coffee Beans iPhone Dataset Organizer")
        self.root.geometry("900x700")
        
        # Dataset configuration
        self.base_dir = "./coffeebeans_iphone"
        self.cropped_dir = "./coffeebeans_iphone_cropped"
        self.beans_per_set = 50
        
        # Target counts (total beans needed)
        self.targets = {
            'good_curve': 1050,
            'good_back': 450,
            'bad_curve': 1050,
            'bad_back': 450
        }
        
        # Calculate sets needed
        self.sets_needed = {
            'good_curve': 21,  # 1050 / 50 = 21
            'good_back': 9,    # 450 / 50 = 9
            'bad_curve': 21,   # 1050 / 50 = 21
            'bad_back': 9      # 450 / 50 = 9
        }
        
        # Current counts (number of sets uploaded)
        self.counts = self.load_counts()
        
        # Current uploaded image
        self.current_image_path = None
        
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
            f"{self.cropped_dir}/good_beans/curve",
            f"{self.cropped_dir}/good_beans/back",
            f"{self.cropped_dir}/bad_beans/curve",
            f"{self.cropped_dir}/bad_beans/back"
        ]
        
        for d in dirs:
            os.makedirs(d, exist_ok=True)
    
    def load_counts(self):
        """Load current image counts from file"""
        count_file = "coffeebeans_iphone_counts.json"
        
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
        count_file = "coffeebeans_iphone_counts.json"
        with open(count_file, 'w') as f:
            json.dump(self.counts, f, indent=2)
    
    def build_gui(self):
        """Build the GUI interface"""
        # Title
        title = tk.Label(
            self.root,
            text="Coffee Beans iPhone Dataset Organizer",
            font=("Arial", 24, "bold"),
            pady=20
        )
        title.pack()
        
        subtitle = tk.Label(
            self.root,
            text="Upload iPhone photos → Auto-organize → Auto-crop beans",
            font=("Arial", 10, "italic"),
            fg="gray"
        )
        subtitle.pack()
        
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
        
        # Upload button
        upload_btn = tk.Button(
            self.root,
            text="📁 UPLOAD PHOTO FROM PC",
            font=("Arial", 18, "bold"),
            bg="#2196F3",
            fg="white",
            padx=40,
            pady=20,
            command=self.upload_photo
        )
        upload_btn.pack(pady=20)
        
        # Image preview
        preview_frame = tk.LabelFrame(
            self.root,
            text="Image Preview",
            font=("Arial", 12),
            padx=10,
            pady=10
        )
        preview_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.preview_label = tk.Label(preview_frame, text="No image loaded", bg="lightgray")
        self.preview_label.pack(expand=True, fill="both")
        
        # Progress display
        progress_frame = tk.LabelFrame(
            self.root,
            text="Dataset Progress",
            font=("Arial", 14),
            padx=20,
            pady=20
        )
        progress_frame.pack(pady=10, padx=20, fill="x")
        
        # Progress labels
        self.progress_labels = {}
        categories = [
            ('good_curve', 'Good Beans - Curve Side'),
            ('good_back', 'Good Beans - Back Side'),
            ('bad_curve', 'Bad Beans - Curve Side'),
            ('bad_back', 'Bad Beans - Back Side')
        ]
        
        for i, (key, label) in enumerate(categories):
            tk.Label(progress_frame, text=label + ":", font=("Arial", 10)).grid(row=i, column=0, sticky="w", pady=3)
            
            progress_label = tk.Label(progress_frame, text="", font=("Arial", 10, "bold"))
            progress_label.grid(row=i, column=1, sticky="w", padx=20)
            self.progress_labels[key] = progress_label
            
            # Progress bar
            progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
            progress_bar.grid(row=i, column=2, padx=10)
            self.progress_labels[f"{key}_bar"] = progress_bar
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready to upload photos",
            font=("Arial", 10),
            bg="#f0f0f0",
            anchor="w",
            padx=10
        )
        self.status_label.pack(side="bottom", fill="x")
    
    def update_progress(self):
        """Update progress display"""
        for key in ['good_curve', 'good_back', 'bad_curve', 'bad_back']:
            current_sets = self.counts[key]
            needed_sets = self.sets_needed[key]
            total_beans = self.targets[key]
            
            # Calculate beans collected so far
            beans_collected = current_sets * self.beans_per_set
            
            # Calculate percentage based on sets
            percentage = (current_sets / needed_sets) * 100 if needed_sets > 0 else 0
            
            # Display: "Set 5/11 (500/1050 beans)"
            self.progress_labels[key].config(
                text=f"Set {current_sets}/{needed_sets} ({beans_collected}/{total_beans} beans)"
            )
            self.progress_labels[f"{key}_bar"]['value'] = percentage
    
    def upload_photo(self):
        """Upload photo from PC"""
        # Get selected category
        quality = self.quality_var.get()
        side = self.side_var.get()
        category = f"{quality}_{side}"
        
        # Check if target reached
        if self.counts[category] >= self.sets_needed[category]:
            messagebox.showinfo("Complete", f"Target for {quality} {side} already reached!\n\n"
                              f"Sets completed: {self.counts[category]}/{self.sets_needed[category]}\n"
                              f"Total beans: {self.counts[category] * self.beans_per_set}/{self.targets[category]}")
            return
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select iPhone Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.heic"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Show preview
        self.show_preview(file_path)
        
        # Confirm
        current_set = self.counts[category] + 1
        total_sets = self.sets_needed[category]
        
        response = messagebox.askyesno(
            "Confirm Upload",
            f"Category: {quality.title()} Beans - {side.title()} Side\n"
            f"Current: Set {self.counts[category]}/{total_sets}\n"
            f"This will be: Set {current_set}/{total_sets}\n\n"
            f"Upload this photo and auto-crop beans?"
        )
        
        if not response:
            return
        
        # Process image
        self.process_image(file_path, category, current_set)
    
    def show_preview(self, image_path):
        """Show image preview (supports HEIC)"""
        try:
            # Open image (HEIC will be handled by pillow-heif if installed)
            img = Image.open(image_path)
            
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize to fit preview
            max_size = (400, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
            
            self.current_image_path = image_path
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}\n\nIf this is a HEIC file, install: pip install pillow-heif")
    
    def process_image(self, source_path, category, set_number):
        """Process image: convert HEIC if needed, save original and crop beans"""
        quality, side = category.split('_')
        
        # Update status
        self.status_label.config(text="Processing image...")
        self.root.update()
        
        # Output paths
        output_dir = f"{self.base_dir}/{quality}_beans/{side}"
        filename = f"{quality}_{side}_set{set_number:02d}.jpg"
        dest_path = os.path.join(output_dir, filename)
        
        try:
            # Check if HEIC file
            if source_path.lower().endswith('.heic'):
                self.status_label.config(text="Converting HEIC to JPG...")
                self.root.update()
                
                # Convert HEIC to JPG
                img = Image.open(source_path)
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(dest_path, 'JPEG', quality=95)
            else:
                # Copy original
                shutil.copy(source_path, dest_path)
            
            # Crop beans
            self.status_label.config(text="Cropping individual beans...")
            self.root.update()
            
            beans_cropped = self.crop_beans(dest_path, category, set_number)
            
            # Update counts
            self.counts[category] += 1
            self.save_counts()
            self.update_progress()
            
            # Show success
            beans_collected = self.counts[category] * self.beans_per_set
            sets_remaining = self.sets_needed[category] - self.counts[category]
            
            self.status_label.config(text=f"✓ Set {set_number} processed: {beans_cropped} beans cropped")
            messagebox.showinfo(
                "Success",
                f"Set {set_number} uploaded and processed!\n\n"
                f"File: {filename}\n"
                f"Beans cropped: {beans_cropped}\n"
                f"Sets: {self.counts[category]}/{self.sets_needed[category]}\n"
                f"Total beans: {beans_collected}/{self.targets[category]}\n"
                f"Sets remaining: {sets_remaining}"
            )
            
        except Exception as e:
            self.status_label.config(text="✗ Processing failed")
            messagebox.showerror("Error", f"Failed to process image:\n{e}")
    
    def crop_beans(self, image_path, category, set_number):
        """Crop individual beans using OpenCV with background removal and fixed size output"""
        quality, side = category.split('_')
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return 0
        
        # Target size for ML training (224x224 is optimal for most models)
        target_size = 224
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Threshold to create mask
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and crop beans
        cropped_dir = f"{self.cropped_dir}/{quality}_beans/{side}"
        bean_count = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area (adjust these values based on your images)
            if 100 < area < 50000:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Add padding
                padding = 10
                x_pad = max(0, x - padding)
                y_pad = max(0, y - padding)
                w_pad = min(img.shape[1] - x_pad, w + 2 * padding)
                h_pad = min(img.shape[0] - y_pad, h + 2 * padding)
                
                # Crop bean and mask
                bean_img = img[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad].copy()
                bean_mask = thresh[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad].copy()
                
                # Remove background
                bean_no_bg = self.remove_background(bean_img, bean_mask)
                
                # Resize to fixed size (224x224) while maintaining aspect ratio
                resized_bean = self.resize_with_padding(bean_no_bg, target_size)
                
                # Save cropped bean
                bean_count += 1
                bean_filename = f"{quality}_{side}_set{set_number:02d}_bean{bean_count:03d}.jpg"
                bean_path = os.path.join(cropped_dir, bean_filename)
                cv2.imwrite(bean_path, resized_bean)
        
        return bean_count
    
    def remove_background(self, img, mask):
        """
        Remove background using mask
        Returns image with white background
        """
        # Create white background
        result = np.ones_like(img) * 255
        
        # Apply mask
        result[mask > 0] = img[mask > 0]
        
        return result
    
    def resize_with_padding(self, img, target_size):
        """
        Resize image to target size while maintaining aspect ratio
        Adds white padding to make it square
        """
        h, w = img.shape[:2]
        
        # Calculate scaling factor
        scale = target_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize
        resized = cv2.resize(img, (new_w, new_h))
        
        # Create square canvas with white padding
        canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
        canvas.fill(255)  # White background
        
        # Calculate position to center the image
        x_offset = (target_size - new_w) // 2
        y_offset = (target_size - new_h) // 2
        
        # Place resized image on canvas
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    print("="*60)
    print("Coffee Beans iPhone Dataset Organizer")
    print("="*60)
    print("Upload photos from iPhone/PC")
    print("Auto-organize and crop beans")
    print("50 beans per set")
    print("="*60)
    
    app = CoffeeBeansIPhone()
    app.run()
