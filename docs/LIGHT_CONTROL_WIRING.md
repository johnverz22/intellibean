# LED Light Control Wiring Guide

## Overview
Control LED brightness for dataset collection using PWM from Raspberry Pi 5 with a DC-DC Step-Up (Boost) Converter.

---

## Hardware Used

**LED Driver**: DC-DC Step-Up (Boost) Converter with PWM Dimming - 700mA Constant Current

This converter:
- Boosts input voltage to higher output for LED
- Provides constant 700mA current
- Has built-in PWM dimming control
- **No MOSFET needed** - direct GPIO connection!

---

## GPIO Pin Assignment

**Recommended Pin: GPIO 13 (Physical Pin 33)**

### Why GPIO 13?
- ✅ Hardware PWM1 channel (smooth, flicker-free)
- ✅ Not used by servos (GPIO 18, GPIO 12)
- ✅ Not used by camera
- ✅ Available on Raspberry Pi 5

### Alternative Pins (if GPIO 13 unavailable):
- GPIO 19 (Pin 35) - Hardware PWM1
- GPIO 26 (Pin 37) - Software PWM

---

## Wiring Diagram (Step-Up Converter - No MOSFET Needed!)

### Simple Direct Connection:

```
Raspberry Pi 5              Step-Up Converter           LED
┌─────────────┐            ┌──────────────┐          ┌─────┐
│             │            │              │          │     │
│  GPIO 13 ───┼────────────┤ PWM/DIM      │          │     │
│  (Pin 33)   │            │              │          │     │
│             │            │ LED+ ────────┼──────────┤ +   │
│  GND ───────┼────────────┤ GND          │          │     │
│  (Pin 39)   │            │              │          │     │
│             │            │ LED- ────────┼──────────┤ -   │
└─────────────┘            │              │          │     │
                           │ VIN+ ────────┼──┐       └─────┘
Power Supply               │              │  │
┌─────────────┐            │ VIN- ────────┼──┤
│  3-12V DC   │            └──────────────┘  │
│  + ─────────┼───────────────────────────────┘
│             │                              │
│  - ─────────┼──────────────────────────────┘
└─────────────┘
```

**Note**: Step-up converter has built-in PWM control, so no external MOSFET needed!

---

## Step-by-Step Wiring

### Step 1: Raspberry Pi to Step-Up Converter
```
GPIO 13 (Pin 33) → Converter PWM/DIM pin
GND (Pin 39)     → Converter GND pin
```

### Step 2: Power Supply to Converter
```
Power Supply + (3-12V) → Converter VIN+
Power Supply - (GND)   → Converter VIN-
```

### Step 3: Converter to LED
```
Converter LED+ → LED + (Anode)
Converter LED- → LED - (Cathode)
```

**That's it!** No MOSFET, no resistors needed. The converter handles everything.

---

## Physical Pin Layout (Raspberry Pi 5)

```
     3.3V  [ 1] [ 2]  5V
    GPIO2  [ 3] [ 4]  5V
    GPIO3  [ 5] [ 6]  GND
    GPIO4  [ 7] [ 8]  GPIO14
      GND  [ 9] [10]  GPIO15
   GPIO17  [11] [12]  GPIO18  ← Servo 1 (Left Gate)
   GPIO27  [13] [14]  GND
   GPIO22  [15] [16]  GPIO23
     3.3V  [17] [18]  GPIO24
   GPIO10  [19] [20]  GND
    GPIO9  [21] [22]  GPIO25
   GPIO11  [23] [24]  GPIO8
      GND  [25] [26]  GPIO7
    GPIO0  [27] [28]  GPIO1
    GPIO5  [29] [30]  GND
    GPIO6  [31] [32]  GPIO12  ← Servo 2 (Right Gate)
   GPIO13  [33] [34]  GND     ← LED LIGHT CONTROL (PWM)
   GPIO19  [35] [36]  GPIO16
   GPIO26  [37] [38]  GPIO20
      GND  [39] [40]  GPIO21  ← Common GND for all
```

---

## Connection Summary

| Component | Raspberry Pi Pin | Converter Pin | Purpose |
|-----------|------------------|---------------|---------|
| PWM Signal | GPIO 13 (Pin 33) | PWM/DIM | Brightness control |
| Ground | GND (Pin 39) | GND | Common ground |
| Power + | External PSU + | VIN+ | Input power |
| Power - | External PSU - | VIN- | Input ground |
| LED + | - | LED+ | LED anode |
| LED - | - | LED- | LED cathode |

---

## Step-Up Converter Specifications

### DC-DC Boost Converter:
- **Type**: Step-up (boost) converter
- **Input Voltage**: Typically 3-12V DC (check your model)
- **Output Voltage**: Boosted (higher than input)
- **Output Current**: 700mA constant current
- **PWM Input**: Active-LOW (inverted)
- **PWM Frequency**: 1-20 kHz (we use 1 kHz)
- **Logic Level**: 3.3V compatible

### Pinout:
```
┌─────────────────────────┐
│  DC-DC Step-Up Boost    │
│  700mA PWM Dimming      │
├─────────────────────────┤
│ VIN+   ← Power Supply + │
│ VIN-   ← Power Supply - │
│ LED+   → LED Anode (+)  │
│ LED-   → LED Cathode(-) │
│ PWM    ← GPIO 13        │
│ GND    ← Raspberry GND  │
└─────────────────────────┘
```

---

## Safety Notes

⚠️ **IMPORTANT SAFETY WARNINGS**:

1. **Power Supply Voltage**
   - Step-up converter BOOSTS input voltage
   - Input: Typically 3-12V DC (check your model)
   - Output: Higher voltage for LED (boosted)
   - Don't exceed converter's maximum input voltage

2. **Current Rating**
   - Converter outputs 700mA constant current
   - Ensure LED can handle 700mA
   - Most high-power LEDs are rated 700mA-1000mA

3. **Common Ground**
   - Connect Raspberry Pi GND to Converter GND
   - This is CRITICAL for PWM signal to work

4. **Polarity**
   - Double-check LED polarity (+/-)
   - Reversed polarity can damage LED
   - Use multimeter to verify

5. **Boost Converter Heat**
   - Converter may get warm during operation
   - Ensure adequate ventilation
   - Add heatsink if needed

6. **PWM Signal**
   - Converter uses active-LOW PWM (inverted)
   - Daemon automatically handles inversion
   - Don't worry about signal polarity

---

## Testing Procedure

### Step 1: Test Daemon
```bash
# On your laptop
python test_light.py
```
- Should cycle through 0%, 25%, 50%, 75%, 100%
- LED should change brightness smoothly

### Step 2: Test with GUI
```bash
python remote_dataset_collector.py
```
- Use brightness slider
- Try preset buttons (Off, 25%, 50%, 75%, 100%)
- Verify smooth dimming

### Step 3: Full Range Test
1. Test 0% (off)
2. Test 25%, 50%, 75%, 100%
3. Verify no flicker
4. Check converter temperature (should be warm, not hot)

---

## Troubleshooting

### Problem: LEDs don't turn on
**Check**:
- [ ] Power supply connected and ON
- [ ] Input voltage within converter range (3-12V)
- [ ] LED polarity correct (+/-)
- [ ] Converter PWM pin connected to GPIO 13
- [ ] Common ground connected (Raspberry Pi GND to Converter GND)
- [ ] Daemon running: `ssh beans@192.168.100.197 "pgrep -f light_daemon.py"`

### Problem: LEDs always on (no dimming)
**Check**:
- [ ] GPIO 13 connected to converter PWM pin
- [ ] Converter supports PWM dimming
- [ ] Daemon running with correct inversion
- [ ] Try redeploying: `python deploy_and_start_light.py`

### Problem: LEDs flicker
**Check**:
- [ ] Use hardware PWM pin (GPIO 13)
- [ ] Check for loose connections
- [ ] Ensure stable power supply
- [ ] Converter may need different PWM frequency

### Problem: Brightness is backwards
**Check**:
- [ ] Daemon should automatically invert signal
- [ ] Redeploy daemon: `python deploy_and_start_light.py`
- [ ] Check daemon logs: `ssh beans@192.168.100.197 "tail ~/light_daemon.log"`

### Problem: Converter gets hot
**Check**:
- [ ] Normal for boost converters under load
- [ ] Add heatsink if very hot (>60°C)
- [ ] Ensure adequate ventilation
- [ ] Check input voltage is within range

---

## Quick Reference

### Hardware: **DC-DC Step-Up (Boost) Converter - 700mA**
### GPIO Pin: **GPIO 13 (Physical Pin 33)**
### Ground: **GND (Physical Pin 39)**
### PWM Frequency: **1000 Hz**
### PWM Mode: **Active-LOW (inverted by daemon)**
### Input Voltage: **3-12V DC (typical)**
### Output Current: **700mA constant**

### Wiring Checklist:
- [ ] GPIO 13 (Pin 33) → Converter PWM pin
- [ ] GND (Pin 39) → Converter GND pin
- [ ] Power Supply + → Converter VIN+
- [ ] Power Supply - → Converter VIN-
- [ ] Converter LED+ → LED +
- [ ] Converter LED- → LED -
- [ ] All grounds connected

### No MOSFET or resistors needed - converter has built-in PWM control!

---

## Integration with Dataset Collector

The light control will be integrated into the GUI with:
- Brightness slider (0-100%)
- On/Off toggle
- Preset brightness levels
- Auto-adjust for captures

See `remote_dataset_collector.py` for GUI integration.
