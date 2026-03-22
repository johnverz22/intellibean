# Coffee Bean Sorter - Complete HMI System

Your complete touchscreen interface for farmer-friendly coffee bean sorting!

---

## ✅ What's Been Created

### 🎯 Main HMI Files

1. **`raspberry_pi/bean_sorter_hmi.py`** ⭐
   - Full touchscreen interface for Raspberry Pi
   - Real hardware control
   - Live AI detection
   - Automatic sorting

2. **`raspberry_pi/bean_sorter_hmi_demo.py`** 🖥️
   - Demo version for PC testing
   - No hardware required
   - Simulated detection
   - Test all features

3. **`docs/TOUCHSCREEN_HMI_GUIDE.md`** 📚
   - Complete user guide
   - Installation instructions
   - Troubleshooting
   - Farmer training guide

4. **`raspberry_pi/HMI_README.md`** 📖
   - Quick reference
   - Feature comparison
   - Quick start guide

---

## 🖥️ Interface Features

### Large Touchscreen Buttons
```
┌─────────────────────────────────────────┐
│     ☕ COFFEE BEAN SORTER ☕            │
│                                         │
│        ● SORTING IN PROGRESS...         │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ GOOD BEANS   │  │  BAD BEANS   │   │
│  │              │  │              │   │
│  │     42       │  │     18       │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│      ┌────────────────────────┐        │
│      │ TOTAL BEANS SORTED     │        │
│      │                        │        │
│      │         60             │        │
│      └────────────────────────┘        │
│                                         │
│  [▶ START SORTING] [■ STOP & SUMMARY]  │
│                                         │
│                          [✕ Exit]      │
└─────────────────────────────────────────┘
```

### Real-Time Counters
- **GOOD BEANS** (Green background) - Quality beans
- **BAD BEANS** (Red background) - Defective beans
- **TOTAL BEANS** (Blue background) - All processed

### Status Indicators
- **● READY TO START** (Orange) - System ready
- **● SORTING IN PROGRESS...** (Green) - Active
- **● PROCESS COMPLETED** (Orange) - Finished

### Summary Window
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

---

## 🎮 How It Works

### For Farmers (Simple!)

**Step 1: Start**
- Tap big green "▶ START SORTING" button
- Conveyor starts automatically
- Watch numbers increase

**Step 2: Monitor**
- Green number = Good beans
- Red number = Bad beans
- Blue number = Total beans

**Step 3: Stop**
- Tap big red "■ STOP & SUMMARY" button
- See results on screen
- Tap "🔄 NEW SESSION" to start again

**That's it!** Only 3 steps, no training needed.

---

## 🔄 Complete Operation Flow

```
1. READY STATE
   ↓
   [Tap START button]
   ↓
2. SORTING STATE
   - Conveyor running
   - Camera detecting
   - Servo sorting
   - Counters updating
   ↓
   [Tap STOP button]
   ↓
3. SUMMARY DISPLAYED
   - Good beans count & %
   - Bad beans count & %
   - Total count
   - Duration
   ↓
   [Tap NEW SESSION]
   ↓
4. COUNTERS RESET
   - All counters → 0
   - Ready for next batch
   ↓
   Back to READY STATE
```

---

## 📊 What Gets Counted

### Good Beans Counter
- Increments when AI detects good quality bean
- Servo closes gate (bean goes to side)
- Green LED blinks
- Green counter increases

### Bad Beans Counter
- Increments when AI detects defective bean
- Servo opens gate (bean goes straight)
- Red LED blinks
- Red counter increases

### Total Counter
- Increments for every bean detected
- Sum of good + bad beans
- Shows total productivity

---

## 🎯 Key Features

### Automatic Operations
✅ Conveyor starts when START pressed
✅ Conveyor stops when STOP pressed
✅ Counters update automatically
✅ Summary appears automatically
✅ Counters reset on NEW SESSION

### Safety Features
✅ Can't start twice (button disabled)
✅ Can't stop when not running
✅ Servo returns to neutral after sorting
✅ Clean shutdown on exit

### User-Friendly
✅ Large buttons (easy to tap)
✅ Clear colors (green/red/blue)
✅ Simple language (no technical terms)
✅ Visual feedback (status changes)
✅ Automatic summary (no manual calculation)

---

## 🖱️ Testing the Demo

### Run on Your PC
```bash
# Windows
py -3.12 raspberry_pi/bean_sorter_hmi_demo.py

# Linux/Mac
python3 raspberry_pi/bean_sorter_hmi_demo.py
```

### What the Demo Does
- ✅ Shows full interface
- ✅ Simulates bean detection (random)
- ✅ Updates counters automatically
- ✅ Shows summary window
- ✅ Resets counters
- ✅ No hardware needed!

### Test Checklist
- [ ] Click START button
- [ ] Watch counters increase
- [ ] Click STOP button
- [ ] View summary window
- [ ] Check percentages
- [ ] Click NEW SESSION
- [ ] Verify counters reset to 0
- [ ] Click START again
- [ ] Click Exit button

---

## 🔧 Installation on Raspberry Pi

### Quick Install
```bash
# 1. Install dependencies
sudo apt install -y python3-tk
pip3 install tensorflow RPi.GPIO numpy opencv-python

# 2. Transfer files
scp raspberry_pi/bean_sorter_hmi.py pi@raspberrypi.local:~/bean_sorter/
scp models/best_model.keras pi@raspberrypi.local:~/bean_sorter/

# 3. Run HMI
ssh pi@raspberrypi.local
cd ~/bean_sorter
python3 bean_sorter_hmi.py best_model.keras
```

### Auto-Start on Boot
```bash
# Create autostart entry
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

---

## ⚙️ Customization Options

### Change Detection Speed
In `bean_sorter_hmi.py`:
```python
DETECTION_DELAY = 1.5  # Seconds between detections
# Increase = slower, more accurate
# Decrease = faster, may miss beans
```

### Change Conveyor Speed
```python
CONVEYOR_SPEED = 50  # PWM duty cycle (0-100)
# Increase = faster belt
# Decrease = slower belt
```

### Change Button Sizes
```python
self.button_font = tkfont.Font(family='Arial', size=28, weight='bold')
# Increase size = bigger buttons
# Decrease size = smaller buttons
```

### Change Colors
```python
self.good_color = '#27AE60'  # Green
self.bad_color = '#E74C3C'   # Red
self.total_color = '#3498DB' # Blue
```

---

## 📚 Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| `HMI_COMPLETE_GUIDE.md` | This file - Complete overview | Everyone |
| `docs/TOUCHSCREEN_HMI_GUIDE.md` | Detailed guide | Technicians |
| `raspberry_pi/HMI_README.md` | Quick reference | Operators |
| `RASPBERRY_PI_QUICK_START.md` | Setup guide | Installers |

---

## 🎓 Training Guide for Farmers

### 5-Minute Training Session

**Minute 1: Show the Screen**
- "This is the coffee bean sorter"
- "Green = good beans, Red = bad beans, Blue = total"

**Minute 2: Demonstrate START**
- "Tap this big green button to start"
- "Watch the numbers go up"
- "The machine is working now"

**Minute 3: Let Them Watch**
- "See the green number? Those are good beans"
- "See the red number? Those are bad beans"
- "The blue number is the total"

**Minute 4: Demonstrate STOP**
- "Tap this big red button to stop"
- "This window shows your results"
- "70% good, 30% bad"

**Minute 5: Practice**
- "Now you try - tap the green button"
- "Good! Now tap the red button"
- "Perfect! Tap NEW SESSION to start again"

**Done!** Farmer is trained.

---

## 🐛 Troubleshooting

### Problem: Touchscreen not responding
**Solution**:
```bash
sudo apt install -y xinput-calibrator
xinput_calibrator
```

### Problem: Buttons too small
**Solution**: Edit font sizes in script (see Customization)

### Problem: Counters not updating
**Solution**: 
1. Check camera connection
2. Check model file
3. Run hardware test

### Problem: Can't exit
**Solution**: Press `Alt+F4` or tap small Exit button

### Problem: Summary doesn't appear
**Solution**: Check if STOP button was pressed

---

## 📊 Comparison: HMI vs Other Versions

| Feature | HMI | Command Line | Original |
|---------|-----|--------------|----------|
| **Interface** | Touchscreen | Keyboard | Keyboard |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Farmer-Friendly** | Yes | No | No |
| **Counters** | Large, visible | Text | Text |
| **Summary** | Automatic | Manual | Manual |
| **Reset** | One button | Command | Command |
| **Training Needed** | 5 minutes | 30 minutes | 1 hour |
| **Technical Skills** | None | Basic | Advanced |

---

## 💡 Best Practices

### For Daily Operation
1. Clean touchscreen before use
2. Start with NEW SESSION
3. Monitor counters during sorting
4. Review summary after each batch
5. Write down results if needed

### For Maintenance
1. Calibrate touchscreen monthly
2. Clean screen weekly
3. Test buttons regularly
4. Check counter accuracy
5. Update software as needed

### For Troubleshooting
1. Try restarting first
2. Check hardware connections
3. Run demo version to test UI
4. Check logs if problems persist
5. Call technician if needed

---

## 🎯 Success Criteria

Your HMI is working correctly when:
- ✅ Touchscreen responds to taps
- ✅ START button starts conveyor
- ✅ Counters update in real-time
- ✅ STOP button stops conveyor
- ✅ Summary appears automatically
- ✅ Percentages are correct
- ✅ NEW SESSION resets counters
- ✅ Exit button closes app

---

## 📞 Support Resources

### Quick Help
1. **Demo Version**: Test UI without hardware
2. **Hardware Test**: `python3 test_hardware.py all`
3. **Camera Test**: `python3 test_camera.py best_model.keras`

### Documentation
1. **This Guide**: Complete overview
2. **HMI Guide**: `docs/TOUCHSCREEN_HMI_GUIDE.md`
3. **Setup Guide**: `docs/RASPBERRY_PI_SETUP.md`
4. **Wiring**: `docs/WIRING_DIAGRAM.md`

### Testing
1. **Demo**: `python3 bean_sorter_hmi_demo.py`
2. **Full**: `python3 bean_sorter_hmi.py best_model.keras`

---

## 🎉 System Complete!

```
✅ Touchscreen HMI Created
✅ Large Buttons (Easy to Tap)
✅ Real-Time Counters (Good/Bad/Total)
✅ Automatic Summary (With Percentages)
✅ Counter Reset (NEW SESSION button)
✅ Status Indicators (Clear Feedback)
✅ Demo Version (PC Testing)
✅ Full Documentation (Complete Guides)
✅ Farmer Training (5-Minute Guide)
✅ Auto-Start Option (Boot Ready)

🚀 READY FOR DEPLOYMENT!
```

---

## 📝 Final Summary

**What You Have:**
- Complete touchscreen interface
- Farmer-friendly design
- Real-time bean counting
- Automatic summary with percentages
- Counter reset functionality
- Demo version for testing
- Complete documentation

**How to Use:**
1. Run demo on PC: `python3 bean_sorter_hmi_demo.py`
2. Test all features
3. Deploy to Raspberry Pi
4. Train farmers (5 minutes)
5. Start sorting!

**Training Time**: 5 minutes
**Technical Skills Required**: None
**Farmer-Friendly**: Yes ⭐⭐⭐⭐⭐

---

**Your touchscreen HMI is ready!** Easy enough for any farmer to use, powerful enough for professional sorting. ☕🚀

For questions, see the documentation files or run the demo version to test!
