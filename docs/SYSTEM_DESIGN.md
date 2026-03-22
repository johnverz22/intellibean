# Coffee Bean Sorter - System Design

## Overview
A 2-lane parallel coffee bean sorting system using Raspberry Pi 5, Camera Module 3, and servo-controlled gates.

## System Logic

### Sorting Flow
```
                    Camera (Single, views both lanes)
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
   LEFT LANE                                   RIGHT LANE
        │                                           │
   Detection Zone                            Detection Zone
        │                                           │
   [Servo Gate 1]                           [Servo Gate 2]
        │                                           │
    ┌───┴───┐                                   ┌───┴───┐
    │       │                                   │       │
  GOOD    BAD                                 GOOD    BAD
  (Left)  (Straight)                          (Right) (Straight)
```

### Detection & Sorting Logic

**LEFT LANE:**
- Camera detects bean in left detection zone
- ML classifies: GOOD or BAD
- **GOOD Bean**: Gate CLOSED → bean drops LEFT to good collection
- **BAD Bean**: Gate OPENS → bean goes STRAIGHT to bad collection

**RIGHT LANE:**
- Camera detects bean in right detection zone  
- ML classifies: GOOD or BAD
- **GOOD Bean**: Gate CLOSED → bean drops RIGHT to good collection
- **BAD Bean**: Gate OPENS → bean goes STRAIGHT to bad collection

**BAD Beans Collection:**
- Both lanes' bad beans go STRAIGHT FORWARD
- Single bad beans collection bin (center/front)

**GOOD Beans Collection:**
- Left lane good beans drop to LEFT bin
- Right lane good beans drop to RIGHT bin
- Two separate good beans bins

### Key Points
1. **2 parallel lanes** process beans simultaneously
2. **1 camera** monitors both lanes (split view or alternating)
3. **2 servo gates** (one per lane)
4. **3 collection bins**: Left Good, Right Good, Center Bad

## Hardware Components

### Required Parts
1. **Raspberry Pi 5** (4GB or 8GB)
2. **Camera Module 3** (already installed)
3. **2x Servo Motors** (SG90 or MG996R)
   - Servo 1: Left lane gate
   - Servo 2: Right lane gate
4. **Power Supply**
   - 5V 3A for Raspberry Pi
   - Separate 5V 2A for servos (recommended)
5. **Vibrating Feeder** (optional, for consistent bean flow)
6. **LED Lighting** (for consistent image quality)
7. **Chute/Ramp System** (physical structure)

### GPIO Pin Connections

```
Raspberry Pi 5 GPIO Layout:
┌─────────────────────────────┐
│  3V3  (1) (2)  5V           │
│  GPIO2 (3) (4)  5V          │
│  GPIO3 (5) (6)  GND         │
│  GPIO4 (7) (8)  GPIO14      │
│  GND   (9) (10) GPIO15      │
│  GPIO17(11)(12) GPIO18 ←────┼─── Servo 1 (LEFT Lane Gate)
│  GPIO27(13)(14) GND         │
│  GPIO22(15)(16) GPIO23      │
│  3V3  (17)(18) GPIO24       │
│  GPIO10(19)(20) GND         │
│  GPIO9 (21)(22) GPIO25      │
│  GPIO11(23)(24) GPIO8       │
│  GND  (25)(26) GPIO7        │
│  GPIO0 (27)(28) GPIO1       │
│  GPIO5 (29)(30) GND         │
│  GPIO6 (31)(32) GPIO12 ←────┼─── Servo 2 (RIGHT Lane Gate)
│  GPIO13(33)(34) GND         │
│  GPIO19(35)(36) GPIO16      │
│  GPIO26(37)(38) GPIO20      │
│  GND  (39)(40) GPIO21       │
└─────────────────────────────┘
```

### Servo Motor Wiring

**Servo 1 (LEFT Lane Gate) - GPIO 18 (Pin 12)**
```
Servo 1:
  Brown/Black  → GND (Pin 14)
  Red          → 5V External Power Supply
  Orange/Yellow → GPIO 18 (Pin 12)
```

**Servo 2 (RIGHT Lane Gate) - GPIO 12 (Pin 32)**
```
Servo 2:
  Brown/Black  → GND (Pin 34)
  Red          → 5V External Power Supply
  Orange/Yellow → GPIO 12 (Pin 32)
```

**Power Supply Connections**
```
External 5V Power Supply:
  (+) → Servo VCC (Red wires)
  (-) → Raspberry Pi GND (share common ground)
```

⚠️ **IMPORTANT**: Connect external power supply GND to Raspberry Pi GND for common ground!

## Physical Setup

### Chute Design (Top View)
```
                    Camera
                       ↓
    ┌─────────────────●─────────────────┐
    │                                   │
    │   LEFT LANE          RIGHT LANE   │
    │   ═══════════        ═══════════   │
    │       ↓                  ↓         │
    │   Detection          Detection     │
    │   Zone 1             Zone 2        │
    │       ↓                  ↓         │
    │   ═══════════        ═══════════   │
    │       ↓                  ↓         │
    │   [Gate 1]           [Gate 2]     │
    │       ↓                  ↓         │
    │   ┌───┴───┐          ┌───┴───┐    │
    │   │       │          │       │    │
    │ GOOD    BAD        GOOD    BAD    │
    │  (L)     ↓          (R)     ↓     │
    │   ↓      ↓           ↓      ↓     │
    │   ↓      └───────────┴──────┘     │
    │   ↓              ↓                │
    │ [Left]      [Bad Beans]    [Right]│
    │ [Good]       (Center)      [Good] │
    └───────────────────────────────────┘
```

### Side View
```
    Feed → → →
         ↓
    ┌────────┐
    │ Camera │
    └────────┘
         ↓
    ═════════  ← Detection Zone
         ↓
    ┌────────┐
    │  Gate  │ ← Servo controlled
    └────┬───┘
         │
    ┌────┴────┐
    │         │
  GOOD      BAD
  (Drop)  (Straight)
```

### Measurements
- **Lane Width**: 3-4cm each (single bean width)
- **Lane Spacing**: 5-6cm between lanes
- **Detection Point to Gate**: 10-20cm
- **Gate Opening**: 2-3cm (enough for one bean)
- **Angle**: 30-45° slope for gravity feed

## Camera Detection Strategy

### Option 1: Split View (Recommended)
- Camera positioned to see both lanes
- Image processing splits into left/right regions
- Process both lanes from single image
- Faster, simpler

### Option 2: Alternating Detection
- Camera focuses on one lane at a time
- Alternate between left and right
- Requires precise timing
- More complex

## Timing Calculations

### Bean Travel Time (Per Lane)
```python
# Example calculation
distance = 15  # cm from camera to gate
bean_velocity = 10  # cm/s (depends on slope angle)
travel_time = distance / bean_velocity  # 1.5 seconds

# Add processing time
processing_time = 0.1  # seconds for ML inference
total_delay = travel_time + processing_time  # 1.6 seconds
```

### Gate Timing
```python
gate_open_time = 0.3  # seconds (enough for bean to pass)
gate_close_time = 0.1  # seconds (return to closed position)
```

## System States (Per Lane)

### State Machine
```
IDLE → DETECTING → CLASSIFYING → ACTUATING → IDLE
  ↑                                            ↓
  └────────────────────────────────────────────┘
```

1. **IDLE**: Waiting for bean
2. **DETECTING**: Bean in detection zone, capture image
3. **CLASSIFYING**: ML model processing
4. **ACTUATING**: Control gate based on classification
5. Return to IDLE

## Collection Bins Layout

```
Front View:

┌─────────┐  ┌─────────┐  ┌─────────┐
│  LEFT   │  │   BAD   │  │  RIGHT  │
│  GOOD   │  │  BEANS  │  │  GOOD   │
│  BEANS  │  │ (Both)  │  │  BEANS  │
└─────────┘  └─────────┘  └─────────┘
```

## Sorting Logic Summary

**For Each Lane:**
```python
if bean_classification == "GOOD":
    gate.stay_closed()  # Bean drops to side (left/right)
else:  # BAD
    gate.open()         # Bean goes straight to center
    wait(0.3)
    gate.close()
```

**Parallel Processing:**
- Both lanes operate independently
- Can process 2 beans simultaneously
- Doubles throughput

## Performance Metrics

- **Throughput**: 60-120 beans/minute (2 lanes)
- **Accuracy**: Depends on ML model (target >95%)
- **Response Time**: <200ms per lane
- **Gate Actuation**: <100ms

## Safety Features

1. **Gate Default Position**: CLOSED (fail-safe)
2. **Timeout Protection**: Gate auto-closes after max time
3. **Emergency Stop**: Button to halt system
4. **Servo Current Limiting**: Prevent motor burnout
5. **Independent Lane Control**: One lane failure doesn't affect other

## Advantages of 2-Lane Design

1. **Double Throughput**: Process 2 beans at once
2. **Redundancy**: One lane can continue if other fails
3. **Efficiency**: Better use of camera and processing power
4. **Scalability**: Easy to add more lanes

## Next Steps

1. Build physical 2-lane chute system
2. Mount camera to view both lanes
3. Install servo motors at each gate
4. Calibrate timing delays for each lane
5. Train ML model with coffee bean dataset
6. Test and tune system
