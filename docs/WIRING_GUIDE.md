## Detailed Wiring Instructions

### Step 1: Prepare Components

**What you need:**
- Raspberry Pi 5
- 2x Servo motors (SG90 or MG996R)
- External 5V power supply (2-3A)
- Jumper wires (Female-to-Female)
- Breadboard (optional, for organization)

### Step 2: Servo Motor Wire Colors

**Standard Servo Wire Colors:**
- **Brown/Black**: Ground (GND)
- **Red**: Power (VCC, 5V)
- **Orange/Yellow/White**: Signal (PWM control)

### Step 3: Connect Servo 1 (Good Lane Gate)

```
Servo 1 → Raspberry Pi 5
─────────────────────────
Brown/Black → Pin 14 (GND)
Red         → External 5V Power Supply (+)
Orange      → Pin 12 (GPIO 18)
```

**Physical Connection:**
1. Locate Pin 12 on Raspberry Pi (GPIO 18)
2. Connect servo signal wire (orange) to Pin 12
3. Connect servo ground (brown) to Pin 14 (GND)
4. Connect servo power (red) to external power supply

### Step 4: Connect Servo 2 (Bad Lane Gate)

```
Servo 2 → Raspberry Pi 5
─────────────────────────
Brown/Black → Pin 34 (GND)
Red         → External 5V Power Supply (+)
Orange      → Pin 32 (GPIO 12)
```

**Physical Connection:**
1. Locate Pin 32 on Raspberry Pi (GPIO 12)
2. Connect servo signal wire (orange) to Pin 32
3. Connect servo ground (brown) to Pin 34 (GND)
4. Connect servo power (red) to external power supply

### Step 5: External Power Supply

**Why external power?**
- Servos draw high current (up to 1A each under load)
- Raspberry Pi GPIO can't provide enough current
- Prevents Pi from crashing or rebooting

**Connection:**
```
External 5V Power Supply
────────────────────────
(+) → Both servo VCC (red wires)
(-) → Raspberry Pi GND (Pin 39 or any GND pin)
```

⚠️ **CRITICAL**: Connect power supply GND to Raspberry Pi GND!
This creates a common ground reference for proper PWM signal.

### Step 6: Verify Connections

**Checklist:**
- [ ] Servo 1 signal → GPIO 18 (Pin 12)
- [ ] Servo 2 signal → GPIO 12 (Pin 32)
- [ ] Both servo grounds → Pi GND
- [ ] Both servo power → External 5V
- [ ] External power GND → Pi GND
- [ ] No shorts between power and ground
- [ ] All connections secure

### Step 7: Power On Sequence

**Correct startup order:**
1. Connect servos to Raspberry Pi (signal and ground only)
2. Power on Raspberry Pi
3. Wait for Pi to boot completely
4. Connect external power supply to servos
5. Run test program

**Shutdown order:**
1. Stop program (Ctrl+C)
2. Disconnect external power supply
3. Shutdown Raspberry Pi: `sudo shutdown now`

### Troubleshooting

**Servo jitters/vibrates:**
- Check power supply voltage (should be 5V ±0.5V)
- Ensure common ground connection
- Add capacitor (100-470µF) across power supply

**Servo doesn't move:**
- Check signal wire connection
- Verify GPIO pin number in code
- Test with servo calibration mode
- Check servo with multimeter (should see PWM signal)

**Pi reboots when servo moves:**
- Power supply insufficient
- Use external power supply
- Check power supply current rating (min 2A)

**Servo moves to wrong position:**
- Run calibration mode
- Adjust GATE_CLOSED_ANGLE and GATE_OPEN_ANGLE in code
- Different servos have different angle ranges

### Safety Notes

⚠️ **Important Safety Information:**

1. **Never connect servo power to Pi 5V pins**
   - Pi can only provide ~1A total
   - Servos can draw 1A each
   - Will damage Pi or cause crashes

2. **Always use external power supply**
   - Rated for at least 2A
   - Regulated 5V output
   - Common ground with Pi

3. **Check polarity before connecting**
   - Wrong polarity can damage servos
   - Red = positive, Brown/Black = negative

4. **Don't hot-plug servos**
   - Connect/disconnect with power off
   - Prevents voltage spikes

5. **Mechanical safety**
   - Ensure gates can't pinch fingers
   - Add emergency stop button
   - Test without beans first

### Testing Procedure

**After wiring, test in this order:**

1. **Visual inspection**
   ```bash
   # Check all connections match diagram
   ```

2. **Power test**
   ```bash
   # Power on Pi, check for boot
   # No smoke, no unusual sounds
   ```

3. **Servo calibration**
   ```bash
   python3 servo_controller.py calibrate
   ```

4. **Gate test**
   ```bash
   python3 servo_controller.py
   ```

5. **Full system test**
   ```bash
   python3 bean_sorter.py --mode test --beans 5
   ```

### Advanced: Adding Sensors

**Optional trigger sensor (for automatic detection):**

```
IR Sensor → Raspberry Pi
────────────────────────
VCC → Pin 1 (3.3V)
GND → Pin 6 (GND)
OUT → Pin 11 (GPIO 17)
```

Update code to read sensor:
```python
import RPi.GPIO as GPIO

TRIGGER_SENSOR = 17
GPIO.setup(TRIGGER_SENSOR, GPIO.IN)

def detect_bean_in_zone(self):
    return GPIO.input(TRIGGER_SENSOR) == GPIO.LOW
```
