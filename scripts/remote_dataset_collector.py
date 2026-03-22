#!/usr/bin/env python3
"""
Remote Coffee Bean Dataset Collector
GUI runs on Windows laptop, controls Raspberry Pi camera via SSH
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import json
from datetime import datetime
import tempfile
from PIL import Image, ImageTk
import threading
import time

class RemoteDatasetCollector:
    """
    Remote GUI application for dataset collection
    
    Features:
    - GUI runs on Windows laptop
    - Controls Raspberry Pi camera via SSH
    - Downloads and processes images locally
    - Progress tracking
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Coffee Bean Dataset Collector (Remote)")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # SSH Configuration
        self.rpi_host = "192.168.100.197"
        self.rpi_user = "beans"
        # Use full path on Windows (expanduser converts ~ to full path)
        ssh_key_path = os.path.expanduser("~/.ssh/id_ed25519_rpi")
        # Convert to Windows path format if needed
        self.ssh_key = ssh_key_path.replace('/', '\\')
        
        # Find SSH executable on Windows
        self.ssh_cmd = self.find_ssh_command()
        self.scp_cmd = self.find_scp_command()
        
        # Light control
        self.current_brightness = 80  # Default 80%
        
        # Local dataset configuration
        self.base_dir = "./coffee_dataset_final"
        self.temp_dir = "./temp_captures"
        
        # Beans per capture
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
        
        # Current counts (number of sets captured)
        self.counts = self.load_counts()
        
        # Track last capture for recapture functionality
        self.last_capture = {
            'category': None,
            'set_number': None,
            'filepath': None
        }
        
        # Live preview state
        self.preview_active = False
        self.preview_thread = None
        self.preview_window = None
        
        # Create directories
        self.setup_directories()
        
        # Build GUI
        self.build_gui()
        
        # Update display
        self.update_progress()
        
        # Test connection
        self.test_connection()
    
    def find_ssh_command(self):
        """Find SSH command on Windows"""
        # Try common locations
        ssh_paths = [
            'ssh',  # In PATH
            'C:\\Windows\\System32\\OpenSSH\\ssh.exe',
            'C:\\Program Files\\Git\\usr\\bin\\ssh.exe'
        ]
        
        for ssh_path in ssh_paths:
            try:
                result = subprocess.run([ssh_path, '-V'], 
                                      capture_output=True, timeout=2)
                return ssh_path
            except:
                continue
        
        return 'ssh'  # Fallback
    
    def find_scp_command(self):
        """Find SCP command on Windows"""
        # Try common locations
        scp_paths = [
            'scp',  # In PATH
            'C:\\Windows\\System32\\OpenSSH\\scp.exe',
            'C:\\Program Files\\Git\\usr\\bin\\scp.exe'
        ]
        
        for scp_path in scp_paths:
            try:
                result = subprocess.run([scp_path, '-V'], 
                                      capture_output=True, timeout=2)
                return scp_path
            except:
                continue
        
        return 'scp'  # Fallback
    
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
        count_file = "dataset_counts_final.json"
        
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
        count_file = "dataset_counts_final.json"
        with open(count_file, 'w') as f:
            json.dump(self.counts, f, indent=2)
    
    def run_ssh_command(self, command):
        """Execute command on Raspberry Pi via SSH"""
        cmd = [self.ssh_cmd, '-i', self.ssh_key, 
               '-o', 'StrictHostKeyChecking=no',
               '-o', 'ConnectTimeout=10',
               '-o', 'ServerAliveInterval=5',
               '-o', 'ServerAliveCountMax=2',
               f'{self.rpi_user}@{self.rpi_host}', command]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "SSH command timeout (30s)", -1
        except Exception as e:
            return "", str(e), -1
    
    def download_file(self, remote_path, local_path):
        """Download file from Raspberry Pi via SCP"""
        cmd = [self.scp_cmd, '-i', self.ssh_key, 
               '-o', 'StrictHostKeyChecking=no',
               '-o', 'ConnectTimeout=10',
               '-o', 'ServerAliveInterval=5',
               '-o', 'ServerAliveCountMax=2',
               f'{self.rpi_user}@{self.rpi_host}:{remote_path}', local_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def test_connection(self):
        """Test SSH connection to Raspberry Pi"""
        self.status_label.config(text="Testing connection to Raspberry Pi...")
        self.root.update()
        
        stdout, stderr, code = self.run_ssh_command("echo 'Connected' && hostname")
        
        if code == 0 and "Connected" in stdout:
            self.status_label.config(text=f"✓ Connected to {stdout.strip().split()[1]}")
        else:
            self.status_label.config(text="✗ Connection failed - Check Raspberry Pi")
            messagebox.showwarning(
                "Connection Failed",
                f"Cannot connect to Raspberry Pi at {self.rpi_host}\n\n"
                f"Make sure:\n"
                f"1. Raspberry Pi is powered on\n"
                f"2. Connected to same network\n"
                f"3. SSH is enabled"
            )
    
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
        
        subtitle = tk.Label(
            self.root,
            text=f"Remote Control - 50 beans per set - GUI on Laptop, Camera on Raspberry Pi",
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
        
        # Light control frame
        light_frame = tk.LabelFrame(
            self.root,
            text="💡 LED Light Control",
            font=("Arial", 14),
            padx=20,
            pady=15
        )
        light_frame.pack(pady=10, padx=20, fill="x")
        
        # Brightness slider
        tk.Label(light_frame, text="Brightness:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.brightness_var = tk.IntVar(value=self.current_brightness)
        brightness_slider = tk.Scale(
            light_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.brightness_var,
            command=self.on_brightness_change,
            length=300,
            font=("Arial", 10)
        )
        brightness_slider.grid(row=0, column=1, padx=10, pady=5)
        
        self.brightness_label = tk.Label(light_frame, text=f"{self.current_brightness}%", font=("Arial", 11, "bold"))
        self.brightness_label.grid(row=0, column=2, padx=5)
        
        # Quick brightness buttons
        button_frame = tk.Frame(light_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        tk.Button(button_frame, text="Off", command=lambda: self.set_brightness(0), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="25%", command=lambda: self.set_brightness(25), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="50%", command=lambda: self.set_brightness(50), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="75%", command=lambda: self.set_brightness(75), width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="100%", command=lambda: self.set_brightness(100), width=8).pack(side=tk.LEFT, padx=5)
        
        # Capture buttons frame
        capture_frame = tk.Frame(self.root)
        capture_frame.pack(pady=20)
        
        # Live preview button
        preview_btn = tk.Button(
            capture_frame,
            text="📹 LIVE PREVIEW",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            padx=20,
            pady=20,
            command=self.toggle_live_preview
        )
        preview_btn.pack(side=tk.LEFT, padx=10)
        
        # Main capture button
        capture_btn = tk.Button(
            capture_frame,
            text="📷 CAPTURE IMAGE",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=40,
            pady=20,
            command=self.capture_image
        )
        capture_btn.pack(side=tk.LEFT, padx=10)
        
        # Recapture button
        self.recapture_btn = tk.Button(
            capture_frame,
            text="🔄 RECAPTURE LAST",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            padx=20,
            pady=20,
            command=self.recapture_image,
            state=tk.DISABLED  # Disabled until first capture
        )
        self.recapture_btn.pack(side=tk.LEFT, padx=10)
        
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
    
    def on_brightness_change(self, value):
        """Handle brightness slider change"""
        brightness = int(value)
        self.brightness_label.config(text=f"{brightness}%")
    
    def set_brightness(self, brightness):
        """Set LED brightness on Raspberry Pi via daemon"""
        self.brightness_var.set(brightness)
        self.brightness_label.config(text=f"{brightness}%")
        self.current_brightness = brightness
        
        # Update status
        self.status_label.config(text=f"💡 Setting brightness to {brightness}%...")
        self.root.update()
        
        # Send command to light daemon via socket
        cmd = f"echo '{brightness}' | nc {self.rpi_host} 9999"
        
        stdout, stderr, code = self.run_ssh_command(cmd)
        
        if code == 0 and "OK" in stdout:
            self.status_label.config(text=f"✓ Brightness set to {brightness}%")
        else:
            self.status_label.config(text=f"✗ Failed to set brightness - Is daemon running?")
            messagebox.showerror(
                "Light Control Error",
                f"Failed to control light. Make sure light daemon is running on Raspberry Pi.\n\n"
                f"To start daemon:\n"
                f"ssh beans@{self.rpi_host}\n"
                f"python3 light_daemon.py\n\n"
                f"Error: {stderr if stderr else 'No response from daemon'}"
            )
    
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
        
        # Total progress
        total_sets_done = sum(self.counts.values())
        total_sets_needed = sum(self.sets_needed.values())
        total_beans_collected = total_sets_done * self.beans_per_set
        total_beans_target = sum(self.targets.values())
        total_percentage = (total_sets_done / total_sets_needed) * 100 if total_sets_needed > 0 else 0
        
        self.total_label.config(
            text=f"Set {total_sets_done}/{total_sets_needed} ({total_beans_collected}/{total_beans_target} beans) - {total_percentage:.1f}%"
        )
        self.total_bar['value'] = total_percentage
    
    def capture_image(self):
        """Capture image from Raspberry Pi camera"""
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
        
        # Confirm
        current_set = self.counts[category] + 1
        total_sets = self.sets_needed[category]
        beans_so_far = self.counts[category] * self.beans_per_set
        beans_after = current_set * self.beans_per_set
        
        response = messagebox.askyesno(
            "Confirm Capture",
            f"Category: {quality.title()} Beans - {side.title()} Side\n"
            f"Current: Set {self.counts[category]}/{total_sets}\n"
            f"This will be: Set {current_set}/{total_sets}\n"
            f"Beans: {beans_so_far} → {beans_after} (of {self.targets[category]} target)\n\n"
            f"Arrange {self.beans_per_set} beans and click OK to capture"
        )
        
        if not response:
            return
        
        # Update status
        self.status_label.config(text="📷 Capturing image on Raspberry Pi...")
        self.root.update()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_file = f"/home/beans/temp_capture_{timestamp}.jpg"
        local_file = f"{self.temp_dir}/capture_{timestamp}.jpg"
        
        # Capture on Raspberry Pi Camera Module 3 STANDARD (with IR filter)
        # Optimized for close-up (15-16cm) with accurate colors
        capture_cmd = (
            f"rpicam-still -o {remote_file} "
            f"--width 4608 --height 2592 "  # Max resolution
            f"--timeout 5000 "  # Allow time for autofocus
            f"--autofocus-mode auto "
            f"--autofocus-range macro "  # Macro mode for 15-16cm distance
            f"--autofocus-speed normal "  # Better accuracy
            f"--lens-position 0.0 "  # Closest focus
            f"--ev 0.0 "  # Neutral exposure
            f"--brightness 0.0 "  # Neutral brightness
            f"--contrast 1.2 "  # Moderate contrast for edge detection
            f"--sharpness 1.8 "  # High sharpness for clarity
            f"--saturation 1.0 "  # Normal saturation (Standard module has good colors)
            f"--awb auto "  # Auto white balance (Standard module is accurate)
            f"--denoise cdn_hq "  # High quality denoise
            f"--quality 95 "  # High JPEG quality
            f"--nopreview"
        )
        
        stdout, stderr, code = self.run_ssh_command(capture_cmd)
        
        if code != 0:
            self.status_label.config(text="✗ Capture failed")
            messagebox.showerror("Error", f"Failed to capture image:\n{stderr}")
            return
        
        # Download image
        self.status_label.config(text="⬇ Downloading image...")
        self.root.update()
        
        if not self.download_file(remote_file, local_file):
            self.status_label.config(text="✗ Download failed")
            messagebox.showerror("Error", "Failed to download image from Raspberry Pi")
            return
        
        # Save to dataset
        output_dir = f"{self.base_dir}/{quality}_beans/{side}"
        current_set = self.counts[category] + 1
        filename = f"{quality}_{side}_set{current_set:02d}.jpg"
        final_path = os.path.join(output_dir, filename)
        
        # Copy to final location
        import shutil
        shutil.copy(local_file, final_path)
        
        # Track this capture for recapture functionality
        self.last_capture = {
            'category': category,
            'set_number': current_set,
            'filepath': final_path,
            'quality': quality,
            'side': side
        }
        
        # Enable recapture button
        self.recapture_btn.config(state=tk.NORMAL)
        
        # Update counts (increment set count)
        self.counts[category] += 1
        self.save_counts()
        self.update_progress()
        
        # Clean up
        try:
            os.remove(local_file)
            self.run_ssh_command(f"rm {remote_file}")
        except:
            pass
        
        # Calculate progress
        beans_collected = self.counts[category] * self.beans_per_set
        sets_remaining = self.sets_needed[category] - self.counts[category]
        
        self.status_label.config(text=f"✓ Set {current_set} saved: {filename}")
        messagebox.showinfo(
            "Success",
            f"Set {current_set} captured and saved!\n\n"
            f"File: {filename}\n"
            f"Sets: {self.counts[category]}/{self.sets_needed[category]}\n"
            f"Beans collected: {beans_collected}/{self.targets[category]}\n"
            f"Sets remaining: {sets_remaining}\n\n"
            f"Next: Arrange {self.beans_per_set} beans for next set"
        )
    
    def recapture_image(self):
        """Recapture the last image without incrementing counter"""
        if not self.last_capture['category']:
            messagebox.showwarning("No Previous Capture", "No previous capture to replace!")
            return
        
        category = self.last_capture['category']
        set_number = self.last_capture['set_number']
        quality = self.last_capture['quality']
        side = self.last_capture['side']
        
        # Confirm recapture
        response = messagebox.askyesno(
            "Confirm Recapture",
            f"Recapture Set {set_number}?\n\n"
            f"Category: {quality.title()} Beans - {side.title()} Side\n"
            f"Set: {set_number}/{self.sets_needed[category]}\n\n"
            f"This will REPLACE the existing image.\n"
            f"Counter will NOT increment.\n\n"
            f"Arrange {self.beans_per_set} beans and click OK"
        )
        
        if not response:
            return
        
        # Update status
        self.status_label.config(text="📷 Recapturing image on Raspberry Pi...")
        self.root.update()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_file = f"/home/beans/temp_capture_{timestamp}.jpg"
        local_file = f"{self.temp_dir}/capture_{timestamp}.jpg"
        
        # Capture on Raspberry Pi Camera Module 3 STANDARD (with IR filter)
        # Optimized for close-up (15-16cm) with accurate colors
        capture_cmd = (
            f"rpicam-still -o {remote_file} "
            f"--width 4608 --height 2592 "  # Max resolution
            f"--timeout 5000 "  # Allow time for autofocus
            f"--autofocus-mode auto "
            f"--autofocus-range macro "  # Macro mode for 15-16cm distance
            f"--autofocus-speed normal "  # Better accuracy
            f"--lens-position 0.0 "  # Closest focus
            f"--ev 0.0 "  # Neutral exposure
            f"--brightness 0.0 "  # Neutral brightness
            f"--contrast 1.2 "  # Moderate contrast for edge detection
            f"--sharpness 1.8 "  # High sharpness for clarity
            f"--saturation 1.0 "  # Normal saturation (Standard module has good colors)
            f"--awb auto "  # Auto white balance (Standard module is accurate)
            f"--denoise cdn_hq "  # High quality denoise
            f"--quality 95 "  # High JPEG quality
            f"--nopreview"
        )
        
        stdout, stderr, code = self.run_ssh_command(capture_cmd)
        
        if code != 0:
            self.status_label.config(text="✗ Recapture failed")
            messagebox.showerror("Error", f"Failed to recapture image:\n{stderr}")
            return
        
        # Download image
        self.status_label.config(text="⬇ Downloading image...")
        self.root.update()
        
        if not self.download_file(remote_file, local_file):
            self.status_label.config(text="✗ Download failed")
            messagebox.showerror("Error", "Failed to download image from Raspberry Pi")
            return
        
        # Replace the existing file
        import shutil
        shutil.copy(local_file, self.last_capture['filepath'])
        
        # Clean up
        try:
            os.remove(local_file)
            self.run_ssh_command(f"rm {remote_file}")
        except:
            pass
        
        # Show success
        filename = os.path.basename(self.last_capture['filepath'])
        self.status_label.config(text=f"✓ Set {set_number} recaptured: {filename}")
        messagebox.showinfo(
            "Recapture Success",
            f"Set {set_number} recaptured!\n\n"
            f"File: {filename}\n"
            f"Category: {quality.title()} - {side.title()}\n"
            f"Counter unchanged: {self.counts[category]}/{self.sets_needed[category]}\n\n"
            f"Image has been replaced."
        )
    
    def toggle_live_preview(self):
        """Toggle live camera preview"""
        if self.preview_active:
            self.stop_live_preview()
        else:
            self.start_live_preview()
    
    def start_live_preview(self):
        """Start live camera preview"""
        if self.preview_active:
            return
        
        self.preview_active = True
        
        # Create preview window
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("Live Camera Preview - Position Your Beans")
        self.preview_window.geometry("800x600")
        self.preview_window.protocol("WM_DELETE_WINDOW", self.stop_live_preview)
        
        # Instructions
        instructions = tk.Label(
            self.preview_window,
            text="Position your 50 beans in the frame. Preview updates every 2 seconds.",
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
            pady=10
        )
        instructions.pack(fill="x")
        
        # Image label
        self.preview_label = tk.Label(self.preview_window, bg="black")
        self.preview_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Status label
        self.preview_status = tk.Label(
            self.preview_window,
            text="Starting preview...",
            font=("Arial", 10),
            pady=5
        )
        self.preview_status.pack(fill="x")
        
        # Close button
        close_btn = tk.Button(
            self.preview_window,
            text="Close Preview",
            font=("Arial", 12, "bold"),
            bg="#f44336",
            fg="white",
            command=self.stop_live_preview,
            pady=10
        )
        close_btn.pack(fill="x", padx=10, pady=10)
        
        # Start preview thread
        self.preview_thread = threading.Thread(target=self.preview_loop, daemon=True)
        self.preview_thread.start()
        
        self.status_label.config(text="📹 Live preview active")
    
    def preview_loop(self):
        """Continuous preview loop"""
        frame_count = 0
        
        while self.preview_active:
            try:
                frame_count += 1
                
                # Update status
                if self.preview_window and self.preview_window.winfo_exists():
                    self.preview_status.config(text=f"Capturing frame {frame_count}...")
                
                # Capture preview image from Raspberry Pi
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                remote_file = f"/home/beans/preview_{timestamp}.jpg"
                local_file = f"{self.temp_dir}/preview_{timestamp}.jpg"
                
                # Quick capture with lower resolution for speed
                capture_cmd = (
                    f"rpicam-still -o {remote_file} "
                    f"--width 1920 --height 1080 "  # Lower res for speed
                    f"--timeout 1000 "  # Quick capture
                    f"--autofocus-mode auto "
                    f"--autofocus-range macro "
                    f"--lens-position 0.0 "
                    f"--quality 85 "  # Lower quality for speed
                    f"--nopreview"
                )
                
                stdout, stderr, code = self.run_ssh_command(capture_cmd)
                
                if code == 0:
                    # Download image
                    if self.download_file(remote_file, local_file):
                        # Display in preview window
                        if self.preview_window and self.preview_window.winfo_exists():
                            self.display_preview_image(local_file)
                            self.preview_status.config(text=f"Frame {frame_count} - Live")
                        
                        # Clean up
                        try:
                            os.remove(local_file)
                            self.run_ssh_command(f"rm {remote_file}")
                        except:
                            pass
                    else:
                        if self.preview_window and self.preview_window.winfo_exists():
                            self.preview_status.config(text=f"Frame {frame_count} - Download failed")
                else:
                    if self.preview_window and self.preview_window.winfo_exists():
                        self.preview_status.config(text=f"Frame {frame_count} - Capture failed")
                
                # Wait before next frame (2 seconds for smooth preview)
                time.sleep(2)
                
            except Exception as e:
                print(f"Preview error: {e}")
                if self.preview_window and self.preview_window.winfo_exists():
                    self.preview_status.config(text=f"Error: {str(e)}")
                time.sleep(2)
    
    def display_preview_image(self, image_path):
        """Display image in preview window"""
        try:
            # Open and resize image to fit window
            img = Image.open(image_path)
            
            # Get preview label size
            label_width = self.preview_label.winfo_width()
            label_height = self.preview_label.winfo_height()
            
            # Use default size if window not yet rendered
            if label_width <= 1:
                label_width = 780
            if label_height <= 1:
                label_height = 450
            
            # Calculate scaling to fit
            img_ratio = img.width / img.height
            label_ratio = label_width / label_height
            
            if img_ratio > label_ratio:
                # Image is wider
                new_width = label_width
                new_height = int(label_width / img_ratio)
            else:
                # Image is taller
                new_height = label_height
                new_width = int(label_height * img_ratio)
            
            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.preview_label.config(image=photo)
            self.preview_label.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def stop_live_preview(self):
        """Stop live camera preview"""
        self.preview_active = False
        
        if self.preview_window:
            try:
                self.preview_window.destroy()
            except:
                pass
            self.preview_window = None
        
        self.status_label.config(text="📹 Live preview stopped")
    
    def on_closing(self):
        """Handle window close event"""
        # Stop preview if active
        if self.preview_active:
            self.stop_live_preview()
        
        # Close main window
        self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    print("="*60)
    print("Remote Coffee Bean Dataset Collector")
    print("="*60)
    print("GUI runs on your laptop")
    print("Camera captures on Raspberry Pi")
    print("50 beans per set")
    print("="*60)
    
    app = RemoteDatasetCollector()
    app.run()
