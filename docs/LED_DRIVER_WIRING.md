# LED Driver Wiring Guide (DC-DC Step-Up Boost Converter)

## Component: DC-DC Step-Up (Boost) Converter with PWM Dimming - 700mA Constant Current

This is a boost converter that increases voltage to power high-brightness LEDs.

---

## Simple Wiring (No MOSFET Needed!)

The LED driver has built-in PWM dimming, so you can connect directly to Raspberry Pi.

### Connections:

```
Raspberry Pi 5              LED Driver Module           LED
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
│             │            └──────────────┘  │
│  + ─────────┼───────────────────────────────┘
│             │                              │
│  - ─────────┼──────────────────────────────┘
└─────────────┘
```

---

## Step-by-Step Wiring

### Step 1: Raspberry Pi to LED Driver
```
GPIO 13 (Pin 33) → LED Driver PWM/DIM pin
GND (Pin 39)     → LED Driver GND pin
```

### Step 2: Power Supply to LED Driver
```
Power Supply + (12V-24V) → LED Driver VIN+
Power Supply - (GND)     → LED Driver VIN-
```

### Step 3: LED Driver to LED
```
LED Driver LED+ → LED + (Anode)
LED Driver LED- → LED - (Cathode)
```

---

## LED Driver Pinout

Typical DC-DC Step-Up Converter has 6 pins:

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

**Note**: Step-up converter boosts input voltage to higher output voltage for LED.

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
   GPIO13  [33] [34]  GND     ← LED LIGHT PWM CONTROL
   GPIO19  [35] [36]  GPIO16
   GPIO26  [37] [38]  GPIO20
      GND  [39] [40]  GPIO21  ← COMMON GND
```

---

## Connection Summary

| Component | Raspberry Pi Pin | LED Driver Pin |
|-----------|------------------|----------------|
| PWM Signal | GPIO 13 (Pin 33) | PWM/DIM |
| Ground | GND (Pin 39) | GND |
| Power + | External PSU + | VIN+ |
| Power - | External PSU - | VIN- |
| LED + | - | LED+ |
| LED - | - | LED- |

---

## PWM Settings

### For DC-DC Step-Up Boost Converter:
- **PWM Frequency**: 1000 Hz (1 kHz)
- **Duty Cycle**: 0-100% (INVERTED - active-low)
  - 0% brightness = 100% duty cycle (LED OFF)
  - 100% brightness = 0% duty cycle (LED ON)
- **Logic Level**: 3.3V (Raspberry Pi compatible)
- **Note**: Daemon automatically inverts signal for you

---

## Wiring Checklist

- [ ] GPIO 13 (Pin 33) → LED Driver PWM pin
- [ ] GND (Pin 39) → LED Driver GND pin
- [ ] Power Supply + → LED Driver VIN+
- [ ] Power Supply - → LED Driver VIN-
- [ ] LED Driver LED+ → LED +
- [ ] LED Driver LED- → LED -
- [ ] All grounds connected together

---

## Safety Notes

⚠️ **IMPORTANT**:

1. **Power Supply Voltage**
   - Step-up converter BOOSTS input voltage
   - Input: Typically 3-12V DC (check your model)
   - Output: Higher voltage for LED (e.g., 12V input → 24V output)
   - Ensure input voltage is within converter's range

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

5. **Boost Converter Specifics**
   - Output voltage is HIGHER than input
   - Don't exceed converter's maximum output voltage
   - Ensure adequate cooling for high-power operation

---

## Testing

### Test 1: Check Connections
```bash
# On Raspberry Pi
python3 src/controller/light_controller.py
```

### Test 2: Verify PWM Signal
- LED should turn on/off
- Brightness should change smoothly
- No flickering

### Test 3: Full Range
- Test 0%, 25%, 50%, 75%, 100%
- Verify smooth transitions

---

## Troubleshooting

### Problem: LED doesn't turn on
- [ ] Check power supply is ON
- [ ] Verify LED polarity
- [ ] Check all connections
- [ ] Test LED Driver VIN voltage

### Problem: LED always on (no dimming)
- [ ] Check GPIO 13 connection to PWM pin
- [ ] Verify GND connection
- [ ] Try different PWM frequency (100Hz or 10kHz)

### Problem: LED flickers
- [ ] Increase PWM frequency to 1000Hz
- [ ] Check for loose connections
- [ ] Ensure stable power supply

---

## Quick Reference

**Type**: DC-DC Step-Up (Boost) Converter  
**GPIO Pin**: GPIO 13 (Physical Pin 33)  
**Ground**: GND (Physical Pin 39)  
**PWM Frequency**: 1000 Hz  
**PWM Mode**: Active-LOW (inverted by daemon)  
**Output Current**: 700mA constant current  
**Input Voltage**: Typically 3-12V DC (check your model)  
**Output Voltage**: Boosted (higher than input)
