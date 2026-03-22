# LED Light Control System

## Overview
The LED light control system uses a persistent daemon on the Raspberry Pi to maintain GPIO 13 active for continuous PWM control of the LED driver.

## Hardware Setup
- **LED Driver**: DC-DC Step-Up (Boost) Converter with PWM Dimming
- **Output Current**: 700mA (constant current)
- **GPIO Pin**: GPIO 13 (Physical Pin 33) - PWM1 channel
- **PWM Frequency**: 1000 Hz (1 kHz)
- **Duty Cycle**: 0-100% (INVERTED - see below)
- **PWM Signal**: Active-LOW (inverted)

### Important: Inverted PWM Signal
This step-up converter uses an **active-low** PWM input, meaning:
- **0% brightness** = 100% PWM duty cycle (GPIO HIGH = LED OFF)
- **100% brightness** = 0% PWM duty cycle (GPIO LOW = LED ON)

The daemon automatically handles this inversion, so you can use normal brightness values (0-100%) in the GUI and commands.

## Wiring
See `docs/LED_DRIVER_WIRING.md` and `docs/LIGHT_CONTROL_WIRING.md` for detailed wiring diagrams.

```
Raspberry Pi GPIO 13 (Pin 33) → LED Driver PWM input
Raspberry Pi GND (Pin 39)     → LED Driver GND
```

## Software Architecture

### 1. Light Daemon (`light_daemon.py`)
Persistent service running on Raspberry Pi that:
- Initializes GPIO 13 with PWM
- Listens on port 9999 for brightness commands
- Keeps GPIO active (no cleanup until shutdown)
- Responds to commands: brightness (0-100), 'status', 'quit'

### 2. GUI Integration (`remote_dataset_collector.py`)
Windows GUI that:
- Connects to daemon via socket (port 9999)
- Provides brightness slider (0-100%)
- Offers quick preset buttons (Off, 25%, 50%, 75%, 100%)
- Default brightness: 80%

## Deployment

### Automatic Deployment
Run the deployment script to upload and start the daemon:

```bash
python deploy_and_start_light.py
```

This will:
1. Upload `light_daemon.py` to Raspberry Pi
2. Make it executable
3. Stop any existing daemon
4. Start daemon in background
5. Verify it's running
6. Test brightness control

### Manual Deployment

#### Upload daemon:
```bash
scp -i ~/.ssh/id_ed25519_rpi light_daemon.py beans@192.168.100.197:~/
```

#### Start daemon on Raspberry Pi:
```bash
ssh beans@192.168.100.197
python3 light_daemon.py
```

#### Or run in background:
```bash
nohup python3 light_daemon.py > light_daemon.log 2>&1 &
```

## Usage

### From GUI
1. Run the dataset collector GUI:
   ```bash
   python remote_dataset_collector.py
   ```

2. Use the brightness slider or preset buttons in the "LED Light Control" section

### From Command Line
Test brightness control directly:

```bash
# Set brightness to 80%
echo '80' | nc 192.168.100.197 9999

# Check status
echo 'status' | nc 192.168.100.197 9999

# Turn off
echo '0' | nc 192.168.100.197 9999

# Turn on full
echo '100' | nc 192.168.100.197 9999
```

### From Raspberry Pi
```bash
# Set brightness locally
echo '80' | nc localhost 9999

# Check status
echo 'status' | nc localhost 9999
```

## Monitoring

### Check if daemon is running:
```bash
ssh beans@192.168.100.197 "pgrep -f light_daemon.py"
```

### View daemon logs:
```bash
ssh beans@192.168.100.197 "tail -f ~/light_daemon.log"
```

### Check current brightness:
```bash
echo 'status' | nc 192.168.100.197 9999
```

## Troubleshooting

### Brightness is inverted (backwards)
This is normal! The LED driver uses an active-low PWM input. The daemon automatically inverts the signal, so:
- Setting 100% in GUI = LED at full brightness
- Setting 0% in GUI = LED off

If brightness still seems backwards, check:
1. LED driver PWM input is connected to GPIO 13
2. Daemon is running the latest version with inversion
3. Redeploy: `python deploy_and_start_light.py`

### LED not turning on
1. Check if daemon is running:
   ```bash
   ssh beans@192.168.100.197 "pgrep -f light_daemon.py"
   ```

2. Check daemon logs:
   ```bash
   ssh beans@192.168.100.197 "cat ~/light_daemon.log"
   ```

3. Verify GPIO 13 output with multimeter:
   - Should show PWM signal (0-3.3V)
   - Duty cycle should match brightness percentage

4. Check LED driver connections:
   - PWM input connected to GPIO 13
   - GND connected to Raspberry Pi GND
   - Power supply connected (5-35V)

### Daemon not responding
1. Restart daemon:
   ```bash
   ssh beans@192.168.100.197
   pkill -f light_daemon.py
   python3 light_daemon.py
   ```

2. Or use deployment script:
   ```bash
   python deploy_and_start_light.py
   ```

### GUI shows "daemon not running" error
1. Verify daemon is running on Raspberry Pi
2. Check network connectivity
3. Verify port 9999 is not blocked by firewall
4. Test manually: `echo '80' | nc 192.168.100.197 9999`

## Stopping the Daemon

### Graceful shutdown:
```bash
echo 'quit' | nc 192.168.100.197 9999
```

### Force kill:
```bash
ssh beans@192.168.100.197 "pkill -f light_daemon.py"
```

## Auto-start on Boot (Optional)

To start daemon automatically when Raspberry Pi boots:

1. Create systemd service:
   ```bash
   sudo nano /etc/systemd/system/light-daemon.service
   ```

2. Add content:
   ```ini
   [Unit]
   Description=LED Light Control Daemon
   After=network.target

   [Service]
   Type=simple
   User=beans
   WorkingDirectory=/home/beans
   ExecStart=/usr/bin/python3 /home/beans/light_daemon.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl enable light-daemon
   sudo systemctl start light-daemon
   ```

4. Check status:
   ```bash
   sudo systemctl status light-daemon
   ```

## Technical Details

### LED Driver Specifications
- **Model**: DC-DC Step-Up (Boost) Converter with PWM Dimming
- **Type**: Boost converter (increases voltage)
- **Output Current**: 700mA (constant current)
- **PWM Input**: Active-LOW (inverted)
- **Input Voltage**: Typically 3-12V DC (check your specific model)
- **Output Voltage**: Higher than input (boosted for LED)
- **PWM Frequency**: 1-20 kHz (we use 1 kHz)

### PWM Configuration
- **GPIO Pin**: GPIO 13 (BCM mode)
- **Physical Pin**: Pin 33
- **PWM Channel**: PWM1
- **Frequency**: 1000 Hz (1 kHz)
- **Resolution**: 0-100% duty cycle
- **Voltage**: 0-3.3V (Raspberry Pi GPIO output)

### Socket Protocol
- **Port**: 9999
- **Protocol**: TCP
- **Commands**:
  - `<number>` (0-100): Set brightness
  - `status`: Get current brightness
  - `quit`: Shutdown daemon
- **Responses**:
  - `OK: <brightness>%`: Success
  - `ERROR: <message>`: Error
  - `Brightness: <brightness>%`: Status response

### Why Persistent Daemon?
The previous implementation used one-shot GPIO commands that called `GPIO.cleanup()` after each brightness change, which turned off the GPIO pin. The persistent daemon keeps GPIO 13 active continuously, allowing the LED to stay on at the set brightness level.

## Files
- `light_daemon.py` - Persistent daemon for Raspberry Pi
- `deploy_and_start_light.py` - Deployment script
- `remote_dataset_collector.py` - GUI with light control
- `src/controller/light_controller.py` - Light controller class (legacy)
- `src/controller/light_service.py` - Service implementation (legacy)

## Status
✓ Deployed and running on GPIO 13
✓ Default brightness: 80%
✓ GUI integration complete
✓ Tested and verified working
