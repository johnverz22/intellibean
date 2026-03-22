# Headless Raspberry Pi Dataset Collector Guide

## Overview
Run the dataset collector directly on Raspberry Pi without needing a monitor, keyboard, or mouse. Control it from your laptop via:
1. **Web Interface** (Recommended - easiest)
2. **Command-Line** (via SSH)
3. **Remote Commands** (from laptop terminal)

---

## Quick Start (Web Interface)

### Step 1: Deploy to Raspberry Pi
```bash
python deploy_headless.py
```

### Step 2: Start Web Server
```bash
python start_web_collector.py
```

This will:
- Start the web server on Raspberry Pi
- Automatically open your browser to http://192.168.100.197:8080
- You can now control everything from the browser!

### Step 3: Use the Web Interface
- Select category (good/bad, curve/back)
- Click "📷 Capture Image"
- Adjust LED brightness with slider
- View progress in real-time
- Page auto-refreshes every 10 seconds

---

## Option 1: Web Interface (Recommended)

### Features
✅ No SSH needed after setup
✅ Works from any device on network
✅ Visual progress bars
✅ LED brightness control
✅ One-click capture
✅ Auto-refresh status
✅ Mobile-friendly

### Manual Start
```bash
# SSH into Raspberry Pi
ssh beans@192.168.100.197

# Start web server
python3 rpi_web_collector.py

# Or start in background
nohup python3 rpi_web_collector.py > web_collector.log 2>&1 &
```

### Access
Open browser on your laptop:
```
http://192.168.100.197:8080
```

### Stop Web Server
```bash
ssh beans@192.168.100.197
pkill -f rpi_web_collector.py
```

---

## Option 2: Command-Line Interface

### SSH into Raspberry Pi
```bash
ssh beans@192.168.100.197
```

### Check Status
```bash
python3 rpi_headless_collector.py status
```

Output:
```
============================================================
Coffee Bean Dataset Collection Status
============================================================

Good - Curve:
  Sets: 5/21 (23.8%)
  Beans: 250/1050

Good - Back:
  Sets: 2/9 (22.2%)
  Beans: 100/450

Bad - Curve:
  Sets: 8/21 (38.1%)
  Beans: 400/1050

Bad - Back:
  Sets: 3/9 (33.3%)
  Beans: 150/450

Total Progress: 18/60 sets (30.0%)
============================================================
```

### Capture Image
```bash
# Syntax
python3 rpi_headless_collector.py capture <category>

# Examples
python3 rpi_headless_collector.py capture bad_curve
python3 rpi_headless_collector.py capture good_back
python3 rpi_headless_collector.py capture bad_back
python3 rpi_headless_collector.py capture good_curve
```

Output:
```
Capturing bad curve - Set 9/21
Make sure 50 beans are arranged...
Capturing...
✓ Captured: bad_curve_set09.jpg
  Sets: 9/21
  Beans: 450/1050
```

### Camera Preview
```bash
python3 rpi_headless_collector.py preview
```

This opens a live camera preview on the Raspberry Pi (if you have a monitor connected). Press Ctrl+C to stop.

---

## Option 3: Remote Commands from Laptop

Run commands from your laptop without SSH session:

### Check Status
```bash
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197 "python3 rpi_headless_collector.py status"
```

### Capture Image
```bash
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197 "python3 rpi_headless_collector.py capture bad_curve"
```

### Create Shortcut Scripts

**Windows (capture_bad_curve.bat):**
```batch
@echo off
ssh -i %USERPROFILE%\.ssh\id_ed25519_rpi beans@192.168.100.197 "python3 rpi_headless_collector.py capture bad_curve"
pause
```

**Linux/Mac (capture_bad_curve.sh):**
```bash
#!/bin/bash
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197 "python3 rpi_headless_collector.py capture bad_curve"
```

---

## Deployment

### Initial Setup
```bash
# Deploy files to Raspberry Pi
python deploy_headless.py
```

This uploads:
- `rpi_headless_collector.py` - Command-line interface
- `rpi_web_collector.py` - Web interface

### Verify Deployment
```bash
ssh beans@192.168.100.197 "ls -la rpi_*.py"
```

---

## Web Interface Details

### Main Page Features

**Progress Status**
- Shows all 4 categories
- Progress bars for each
- Set counts and bean counts
- Auto-refreshes every 10 seconds

**Capture Controls**
- Category dropdown selector
- Capture button
- Preview button (opens new window)

**LED Brightness**
- Slider (0-100%)
- Real-time control
- Connects to light daemon

### Browser Compatibility
- Chrome ✓
- Firefox ✓
- Edge ✓
- Safari ✓
- Mobile browsers ✓

### Network Requirements
- Laptop and Raspberry Pi on same network
- Port 8080 accessible
- Stable WiFi connection

---

## Workflow Examples

### Workflow 1: Web Interface (Easiest)
1. Run `python start_web_collector.py` on laptop
2. Browser opens automatically
3. Select category
4. Arrange 50 beans
5. Click "Capture Image"
6. Repeat for next set
7. Page shows updated progress

### Workflow 2: SSH Commands
1. SSH into Raspberry Pi
2. Run `python3 rpi_headless_collector.py status`
3. Arrange 50 beans
4. Run `python3 rpi_headless_collector.py capture bad_curve`
5. Check status again
6. Repeat

### Workflow 3: Remote Commands
1. Create batch/shell scripts on laptop
2. Arrange beans
3. Double-click script to capture
4. Script runs SSH command automatically
5. No need to type commands

---

## Advantages of Headless Operation

### No GUI Needed
- ✅ No monitor required on Raspberry Pi
- ✅ No keyboard/mouse needed
- ✅ Raspberry Pi can be placed anywhere
- ✅ Saves desk space

### Remote Control
- ✅ Control from laptop
- ✅ Control from phone/tablet
- ✅ Multiple people can access
- ✅ Works from anywhere on network

### Reliability
- ✅ No GUI crashes
- ✅ Lightweight operation
- ✅ Runs in background
- ✅ Auto-restart possible

### Flexibility
- ✅ Web interface for ease
- ✅ Command-line for automation
- ✅ Remote commands for scripting
- ✅ Choose what works best

---

## Troubleshooting

### Web Interface Not Loading

**Check if server is running:**
```bash
ssh beans@192.168.100.197 "pgrep -f rpi_web_collector.py"
```

**Start server:**
```bash
python start_web_collector.py
```

**Check logs:**
```bash
ssh beans@192.168.100.197 "tail -20 ~/web_collector.log"
```

### Cannot SSH to Raspberry Pi

**Check network:**
```bash
ping 192.168.100.197
```

**Check SSH key:**
```bash
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197 "echo test"
```

### Camera Not Working

**Test camera:**
```bash
ssh beans@192.168.100.197 "rpicam-hello --list-cameras"
```

**Check camera cable:**
- Ensure camera is properly connected
- Check for loose connections

### Light Control Not Working

**Check daemon:**
```bash
ssh beans@192.168.100.197 "pgrep -f light_daemon.py"
```

**Restart daemon:**
```bash
python deploy_and_start_light.py
```

---

## Auto-Start on Boot (Optional)

### Make Web Server Start Automatically

Create systemd service:
```bash
ssh beans@192.168.100.197
sudo nano /etc/systemd/system/web-collector.service
```

Add content:
```ini
[Unit]
Description=Coffee Bean Web Collector
After=network.target

[Service]
Type=simple
User=beans
WorkingDirectory=/home/beans
ExecStart=/usr/bin/python3 /home/beans/rpi_web_collector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable web-collector
sudo systemctl start web-collector
```

Check status:
```bash
sudo systemctl status web-collector
```

Now web interface starts automatically when Raspberry Pi boots!

---

## Comparison: GUI vs Headless

| Feature | Windows GUI | Web Interface | Command-Line |
|---------|-------------|---------------|--------------|
| Setup | Medium | Easy | Easy |
| Ease of Use | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Network Needed | Yes | Yes | Yes |
| Monitor Needed | No | No | No |
| Keyboard Needed | No | No | No |
| Mobile Access | No | Yes | No |
| Automation | No | Yes | Yes |
| Background Run | No | Yes | Yes |
| Visual Feedback | ★★★★★ | ★★★★☆ | ★★☆☆☆ |

---

## Best Practices

### For Web Interface
1. Keep browser tab open
2. Check progress regularly
3. Use auto-refresh feature
4. Bookmark the URL
5. Test on mobile too

### For Command-Line
1. Create alias commands
2. Use shell history (up arrow)
3. Check status before capture
4. Keep SSH session open
5. Use screen/tmux for persistence

### For Remote Commands
1. Create shortcut scripts
2. Test commands first
3. Add error handling
4. Log outputs
5. Use batch processing

---

## Summary

The headless operation gives you flexibility:

**Use Web Interface when:**
- You want easy point-and-click
- Multiple people need access
- You want visual feedback
- You're using mobile device

**Use Command-Line when:**
- You're comfortable with terminal
- You want quick commands
- You're already SSH'd in
- You want to script operations

**Use Remote Commands when:**
- You want automation
- You're creating workflows
- You want one-click shortcuts
- You're batch processing

All three methods work with the same dataset and counters!
