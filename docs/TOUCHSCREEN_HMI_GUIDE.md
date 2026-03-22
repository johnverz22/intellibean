# Coffee Bean Sorter - Touchscreen HMI Guide

Complete guide for the farmer-friendly touchscreen interface.

---

## 🖥️ Overview

The touchscreen HMI (Human-Machine Interface) provides an easy-to-use interface for farmers to operate the coffee bean sorting system without technical knowledge.

### Features
- ✅ Large, easy-to-tap buttons
- ✅ Real-time bean counters
- ✅ Clear status indicators
- ✅ Automatic session summary
- ✅ Counter reset after each session
- ✅ Simple START/STOP operation
- ✅ Farmer-friendly language

---

## 📱 Screen Layout

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│           ☕ COFFEE BEAN SORTER ☕                      │
│                                                         │
│              ● READY TO START                           │
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │   GOOD BEANS     │      │    BAD BEANS     │       │
│  │                  │      │                  │       │
│  │       42         │      │       18         │       │
│  └──────────────────┘      └──────────────────┘       │
│                                                         │
│           ┌──────────────────────────┐                 │
│           │  TOTAL BEANS SORTED      │                 │
│           │                          │                 │
│           │          60              │                 │
│           └──────────────────────────┘                 │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │  ▶ START SORTING │  │ ■ STOP & SUMMARY │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│                                          [✕ Exit]      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 How to Use

### Step 1: Start Sorting
1. Tap **"▶ START SORTING"** button
2. Status changes to **"● SORTING IN PROGRESS..."** (green)
3. Conveyor belt starts automatically
4. Counters begin updating as beans are detected

### Step 2: Monitor Progress
- **GOOD BEANS** counter (green) - Shows good quality beans
- **BAD BEANS** counter (red) - Shows defective beans
- **TOTAL BEANS SORTED** counter (blue) - Shows total processed

### Step 3: Stop Sorting
1. Tap **"■ STOP & SUMMARY"** button
2. Conveyor belt stops automatically
3. Summary window appears automatically

### Step 4: View Summary
Summary shows:
- Good beans count and percentage
- Bad beans count and percentage
- Total beans sorted
- Session duration

### Step 5: Start New Session
1. Tap **"🔄 NEW SESSION"** to reset counters
2. Or tap **"✓ CLOSE"** to keep current counts
3. Ready to start again!

---

## 🎨 Color Coding

| Color | Meaning |
|-------|---------|
| 🟢 Green | Good beans / Active sorting |
| 🔴 Red | Bad beans / Stop button |
| 🔵 Blue | Total count / Information |
| 🟠 Orange | Ready / Completed status |
| ⚪ White | Text and labels |

---

## 📊 Status Indicators

### Ready State
```
● READY TO START (Orange)
```
- System is ready
- Counters at zero or previous session
- Tap START to begin

### Sorting State
```
● SORTING IN PROGRESS... (Green)
```
- Conveyor belt running
- Camera detecting beans
- Counters updating automatically
- Tap STOP to end session

### Completed State
```
● PROCESS COMPLETED (Orange)
```
- Sorting stopped
- Summary displayed
- Ready for new session

---

## 🔄 Summary Window

### What It Shows

```
┌─────────────────────────────────────────┐
│       📊 SORTING SUMMARY                │
│                                         │
│  Good Beans:      42 beans    70.0%    │
│  Bad Beans:       18 beans    30.0%    │
│  Total Sorted:    60 beans    100%     │
│  Duration:        5m 23s               │
│                                         │
│  [🔄 NEW SESSION]  [✓ CLOSE]           │
└─────────────────────────────────────────┘
```

### Actions
- **🔄 NEW SESSION**: Resets all counters to zero, closes summary
- **✓ CLOSE**: Keeps current counts, closes summary only

---

## 🎮 Button Functions

### ▶ START SORTING
- **When**: System is ready
- **Action**: 
  - Starts conveyor belt
  - Begins bean detection
  - Enables STOP button
  - Disables START button
- **Status**: Changes to "SORTING IN PROGRESS"

### ■ STOP & SUMMARY
- **When**: Sorting is active
- **Action**:
  - Stops conveyor belt
  - Stops detection
  - Shows summary window
  - Enables START button
  - Disables STOP button
- **Status**: Changes to "PROCESS COMPLETED"

### 🔄 NEW SESSION (in summary)
- **When**: Summary is displayed
- **Action**:
  - Resets all counters to 0
  - Closes summary window
  - Returns to ready state

### ✓ CLOSE (in summary)
- **When**: Summary is displayed
- **Action**:
  - Closes summary window
  - Keeps current counts
  - Returns to ready state

### ✕ Exit
- **When**: Anytime
- **Action**:
  - Stops sorting if active
  - Closes application
  - Cleans up hardware

---

## 📝 Operation Workflow

```
1. READY
   ↓ (Tap START)
   
2. SORTING
   - Conveyor running
   - Detecting beans
   - Updating counters
   ↓ (Tap STOP)
   
3. SUMMARY
   - View results
   - See percentages
   - Check duration
   ↓ (Tap NEW SESSION or CLOSE)
   
4. READY (back to step 1)
```

---

## 🔧 Installation on Raspberry Pi

### 1. Install Dependencies
```bash
sudo apt install -y python3-tk
pip3 install tensorflow RPi.GPIO numpy opencv-python
```

### 2. Enable Touchscreen
```bash
# For official Raspberry Pi touchscreen
sudo apt install -y raspberrypi-ui-mods
```

### 3. Transfer Files
```bash
scp raspberry_pi/bean_sorter_hmi.py pi@raspberrypi.local:~/bean_sorter/
scp models/best_model.keras pi@raspberrypi.local:~/bean_sorter/
```

### 4. Run HMI
```bash
cd ~/bean_sorter
python3 bean_sorter_hmi.py best_model.keras
```

---

## 🖱️ Testing on PC (Demo Mode)

### Run Demo Version
```bash
# On Windows
py -3.12 raspberry_pi/bean_sorter_hmi_demo.py

# On Linux/Mac
python3 raspberry_pi/bean_sorter_hmi_demo.py
```

### Demo Features
- ✅ Full UI without hardware
- ✅ Simulated bean detection
- ✅ Random good/bad classification
- ✅ All buttons functional
- ✅ Summary window works
- ✅ Counter reset works

---

## ⚙️ Customization

### Adjust Detection Speed
Edit in `bean_sorter_hmi.py`:
```python
DETECTION_DELAY = 1.5  # Seconds between detections
```

### Adjust Conveyor Speed
Edit in `bean_sorter_hmi.py`:
```python
CONVEYOR_SPEED = 50  # PWM duty cycle (0-100)
```

### Change Colors
Edit in `bean_sorter_hmi.py`:
```python
self.good_color = '#27AE60'  # Green
self.bad_color = '#E74C3C'   # Red
self.total_color = '#3498DB' # Blue
```

### Change Font Sizes
Edit in `bean_sorter_hmi.py`:
```python
self.title_font = tkfont.Font(family='Arial', size=36, weight='bold')
self.counter_font = tkfont.Font(family='Arial', size=48, weight='bold')
self.button_font = tkfont.Font(family='Arial', size=28, weight='bold')
```

---

## 🎓 Farmer Training Guide

### Quick Training (5 minutes)

**Step 1: Show the Screen**
- Point to each counter
- Explain green = good, red = bad, blue = total

**Step 2: Demonstrate START**
- Tap START button
- Show counters updating
- Explain conveyor is running

**Step 3: Demonstrate STOP**
- Tap STOP button
- Show summary window
- Explain the results

**Step 4: Practice**
- Let farmer tap START
- Wait for a few beans
- Let farmer tap STOP
- Review summary together

**Step 5: New Session**
- Show NEW SESSION button
- Explain counters reset
- Ready for next batch!

### Common Questions

**Q: What if I tap START by accident?**
A: Just tap STOP immediately. No problem!

**Q: Can I see previous results?**
A: No, counters reset after NEW SESSION. Write down results if needed.

**Q: What if power goes off?**
A: Counters will reset. Start a new session.

**Q: How do I know it's working?**
A: Watch the counters increase as beans pass through.

**Q: What if counters don't move?**
A: Check if beans are on the belt. Call technician if problem persists.

---

## 🐛 Troubleshooting

### Screen Not Responding
```bash
# Calibrate touchscreen
sudo apt install -y xinput-calibrator
xinput_calibrator
```

### Buttons Too Small
Edit font sizes in `bean_sorter_hmi.py` (see Customization section)

### Fullscreen Not Working
```bash
# Run with fullscreen flag
python3 bean_sorter_hmi.py best_model.keras
```

### Exit Button Not Visible
- Press `Alt+F4` to close
- Or add keyboard shortcut: `Ctrl+Q`

---

## 🚀 Auto-Start HMI on Boot

### Create Desktop Entry
```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/bean-sorter.desktop
```

Add:
```ini
[Desktop Entry]
Type=Application
Name=Bean Sorter HMI
Exec=/usr/bin/python3 /home/pi/bean_sorter/bean_sorter_hmi.py /home/pi/bean_sorter/best_model.keras
Terminal=false
```

### Or Use Systemd
```bash
sudo nano /etc/systemd/system/bean-sorter-hmi.service
```

Add:
```ini
[Unit]
Description=Coffee Bean Sorter HMI
After=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
WorkingDirectory=/home/pi/bean_sorter
ExecStart=/usr/bin/python3 /home/pi/bean_sorter/bean_sorter_hmi.py /home/pi/bean_sorter/best_model.keras
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Enable:
```bash
sudo systemctl enable bean-sorter-hmi.service
sudo systemctl start bean-sorter-hmi.service
```

---

## 📊 Sample Session

```
Time: 10:00 AM
Action: Farmer taps START

10:00:05 - Good: 1, Bad: 0, Total: 1
10:00:07 - Good: 1, Bad: 1, Total: 2
10:00:09 - Good: 2, Bad: 1, Total: 3
10:00:11 - Good: 3, Bad: 1, Total: 4
...
10:05:23 - Good: 42, Bad: 18, Total: 60

Action: Farmer taps STOP

Summary Displayed:
- Good Beans: 42 beans (70.0%)
- Bad Beans: 18 beans (30.0%)
- Total Sorted: 60 beans
- Duration: 5m 23s

Action: Farmer taps NEW SESSION
Counters reset to 0
Ready for next batch!
```

---

## 💡 Tips for Best Results

### For Farmers
1. Wait for "READY TO START" before tapping START
2. Don't tap buttons multiple times
3. Let summary display before starting new session
4. Write down results if needed for records
5. Call technician if counters stop moving

### For Technicians
1. Test touchscreen calibration regularly
2. Clean screen weekly
3. Check button responsiveness
4. Verify counter accuracy
5. Update software as needed

---

## 📞 Support

### Quick Checks
1. Is screen responding to touch?
2. Are counters updating?
3. Is START/STOP working?
4. Does summary appear?
5. Does NEW SESSION reset counters?

### If Problems Persist
1. Restart Raspberry Pi
2. Check hardware connections
3. Run hardware test: `python3 test_hardware.py all`
4. Check logs: `journalctl -u bean-sorter-hmi.service`

---

## 📝 Summary

**HMI Features:**
- ✅ Large touchscreen buttons
- ✅ Real-time counters (Good, Bad, Total)
- ✅ Clear status indicators
- ✅ Automatic summary with percentages
- ✅ Counter reset functionality
- ✅ Simple START/STOP operation
- ✅ Farmer-friendly design

**Files:**
- `raspberry_pi/bean_sorter_hmi.py` - Full version (Raspberry Pi)
- `raspberry_pi/bean_sorter_hmi_demo.py` - Demo version (PC testing)

**Ready to Use!** The touchscreen interface is designed for easy operation by farmers with no technical training required. 🚀☕
