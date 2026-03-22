# Coffee Bean Sorter - Wiring Diagram

Visual guide for connecting all components to Raspberry Pi.

---

## Complete System Wiring

```
                    COFFEE BEAN SORTING SYSTEM
                    ==========================

┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│                      RASPBERRY PI 4                               │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                                                           │    │
│  │  (1) 3V3    ●────────────────────────────────────●  5V (2)   │──┐
│  │  (3) GPIO2  ●                                     ●  5V (4)   │  │
│  │  (5) GPIO3  ●                                     ● GND (6)   │──┼──┐
│  │  (7) GPIO4  ●                                     ● GPIO14(8) │  │  │
│  │  (9) GND    ●                                     ● GPIO15(10)│  │  │
│  │ (11) GPIO17 ●─────[LED]──────────────────────────────────────┼──┼──┼──┐
│  │ (13) GPIO27 ●─────[LED]──────────────────────────────────────┼──┼──┼──┼──┐
│  │ (15) GPIO22 ●                                     ● GND (14)  │  │  │  │  │
│  │ (17) 3V3    ●                                     ● GPIO23(16)│──┼──┼──┼──┼──┐
│  │ (19) GPIO10 ●                                     ● GPIO24(18)│──┼──┼──┼──┼──┼──┐
│  │ (21) GPIO9  ●                                     ● GND (20)  │  │  │  │  │  │  │
│  │ (23) GPIO11 ●                                     ● GPIO25(22)│──┼──┼──┼──┼──┼──┼──┐
│  │ (25) GND    ●                                     ● GPIO8 (24)│──┼──┼──┼──┼──┼──┼──┼──┐
│  │ (27) ID_SD  ●                                     ● GPIO7 (26)│  │  │  │  │  │  │  │  │
│  │                                                           │    │  │  │  │  │  │  │  │  │
│  │  [Camera CSI Port]                                       │    │  │  │  │  │  │  │  │  │
│  │                                                           │    │  │  │  │  │  │  │  │  │
│  └─────────────────────────────────────────────────────────┘    │  │  │  │  │  │  │  │  │
│                                                                   │  │  │  │  │  │  │  │  │
└───────────────────────────────────────────────────────────────────┘  │  │  │  │  │  │  │  │
                                                                        │  │  │  │  │  │  │  │
                                                                        │  │  │  │  │  │  │  │
┌───────────────────────────────────────────────────────────────────────┘  │  │  │  │  │  │  │
│ SERVO MOTOR (Gate Control)                                               │  │  │  │  │  │  │
│ ┌─────────────────┐                                                      │  │  │  │  │  │  │
│ │   SG90 / MG996R │                                                      │  │  │  │  │  │  │
│ │                 │                                                      │  │  │  │  │  │  │
│ │  VCC  ──────────┼──────────────────────────────────────────────────────┘  │  │  │  │  │  │
│ │  (Red)          │                                                         │  │  │  │  │  │
│ │                 │                                                         │  │  │  │  │  │
│ │  GND  ──────────┼─────────────────────────────────────────────────────────┘  │  │  │  │  │
│ │  (Brown)        │                                                            │  │  │  │  │
│ │                 │                                                            │  │  │  │  │
│ │  Signal ────────┼────────────────────────────────────────────────────────────┘  │  │  │  │
│ │  (Orange)       │  GPIO 18 (Pin 12)                                            │  │  │  │
│ └─────────────────┘                                                              │  │  │  │
└──────────────────────────────────────────────────────────────────────────────────┘  │  │  │
                                                                                       │  │  │
┌──────────────────────────────────────────────────────────────────────────────────────┘  │  │
│ GREEN LED (Good Beans Indicator)                                                       │  │
│ ┌──────────────────────────────────┐                                                   │  │
│ │  GPIO17 ──[220Ω]──[LED+]──[LED-]──GND                                                │  │
│ └──────────────────────────────────┘                                                   │  │
└────────────────────────────────────────────────────────────────────────────────────────┘  │
                                                                                            │
┌───────────────────────────────────────────────────────────────────────────────────────────┘
│ RED LED (Bad Beans Indicator)
│ ┌──────────────────────────────────┐
│ │  GPIO27 ──[220Ω]──[LED+]──[LED-]──GND
│ └──────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────────────────


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ BTS7960 MOTOR DRIVER (Conveyor Belt)                                                     │
│                                                                                           │
│  ┌──────────────────────────────────────────────────────────────────────────────┐       │
│  │                         BTS7960 43A H-Bridge                                  │       │
│  │                                                                               │       │
│  │  LOGIC POWER (from Raspberry Pi):                                            │       │
│  │  ┌──────────┐                                                                │       │
│  │  │ VCC  ────┼─── 5V (Pin 2 or 4)                                             │       │
│  │  │ GND  ────┼─── GND (Pin 14)                                                │       │
│  │  └──────────┘                                                                │       │
│  │                                                                               │       │
│  │  CONTROL SIGNALS:                                                            │       │
│  │  ┌──────────┐                                                                │       │
│  │  │ RPWM ────┼─── GPIO 23 (Pin 16) - Right PWM (Forward)                     │       │
│  │  │ LPWM ────┼─── GPIO 24 (Pin 18) - Left PWM (Backward)                     │       │
│  │  │ R_EN ────┼─── GPIO 25 (Pin 22) - Right Enable                            │       │
│  │  │ L_EN ────┼─── GPIO 8  (Pin 24) - Left Enable                             │       │
│  │  └──────────┘                                                                │       │
│  │                                                                               │       │
│  │  MOTOR POWER (from External 12V Supply):                                     │       │
│  │  ┌──────────┐                                                                │       │
│  │  │ VCC  ────┼─── 12V Power Supply (+)                                        │       │
│  │  │ GND  ────┼─── 12V Power Supply (-)                                        │       │
│  │  └──────────┘                                                                │       │
│  │                                                                               │       │
│  │  MOTOR OUTPUT:                                                               │       │
│  │  ┌──────────┐                                                                │       │
│  │  │ B+   ────┼─── DC Motor (+)                                                │       │
│  │  │ B-   ────┼─── DC Motor (-)                                                │       │
│  │  └──────────┘                                                                │       │
│  │                                                                               │       │
│  └──────────────────────────────────────────────────────────────────────────────┘       │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ POWER SUPPLIES                                                                            │
│                                                                                           │
│  ┌────────────────────┐          ┌────────────────────┐                                 │
│  │  5V 3A Power Supply│          │ 12V 5A Power Supply│                                 │
│  │  (Raspberry Pi)    │          │ (Motor Driver)     │                                 │
│  │                    │          │                    │                                 │
│  │  (+) ──────────────┼──────────┼─── Raspberry Pi    │                                 │
│  │  (-) ──────────────┼──────────┼─── GND             │                                 │
│  │                    │          │                    │                                 │
│  └────────────────────┘          │  (+) ──────────────┼─── BTS7960 VCC (Motor Power)   │
│                                  │  (-) ──────────────┼─── BTS7960 GND (Motor Power)   │
│                                  │                    │                                 │
│                                  └────────────────────┘                                 │
│                                                                                           │
│  ⚠️  IMPORTANT: DO NOT connect 12V to Raspberry Pi!                                      │
│  ⚠️  Keep power supplies separate - only share GND if needed                            │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ CAMERA MODULE                                                                             │
│                                                                                           │
│  ┌────────────────────────────────────────────────────────────────┐                     │
│  │  Raspberry Pi Camera Module V2 / V3                            │                     │
│  │                                                                 │                     │
│  │  [Ribbon Cable] ──────────────────────────────────────────────────────────────────┐  │
│  │                                                                 │                  │  │
│  └─────────────────────────────────────────────────────────────────                  │  │
│                                                                                        │  │
│                                                                                        │  │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │  │
│  │                      Raspberry Pi                                               │ │  │
│  │                                                                                 │ │  │
│  │  [Camera CSI Port] ◄────────────────────────────────────────────────────────────┘  │
│  │  (Between HDMI and USB ports)                                                   │    │
│  │                                                                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Connection Summary Table

| Component | Pin/Wire | Raspberry Pi GPIO | Notes |
|-----------|----------|-------------------|-------|
| **Servo Motor** | | | |
| VCC (Red) | Power | 5V (Pin 2 or 4) | Stable 5V required |
| GND (Brown) | Ground | GND (Pin 6) | Common ground |
| Signal (Orange) | Control | GPIO 18 (Pin 12) | PWM signal |
| **BTS7960 Motor Driver** | | | |
| VCC (Logic) | Power | 5V (Pin 2) | Logic power |
| GND (Logic) | Ground | GND (Pin 14) | Logic ground |
| RPWM | Control | GPIO 23 (Pin 16) | Forward PWM |
| LPWM | Control | GPIO 24 (Pin 18) | Backward PWM |
| R_EN | Control | GPIO 25 (Pin 22) | Right enable |
| L_EN | Control | GPIO 8 (Pin 24) | Left enable |
| VCC (Motor) | Power | 12V External | Motor power |
| GND (Motor) | Ground | 12V External GND | Motor ground |
| B+ | Output | DC Motor (+) | Motor positive |
| B- | Output | DC Motor (-) | Motor negative |
| **LED Indicators** | | | |
| Green LED | Anode | GPIO 17 (Pin 11) | Via 220Ω resistor |
| Red LED | Anode | GPIO 27 (Pin 13) | Via 220Ω resistor |
| Both LEDs | Cathode | GND | Common ground |
| **Camera** | | | |
| Ribbon Cable | Data | Camera CSI Port | Between HDMI/USB |

---

## Physical Layout Suggestion

```
                    TOP VIEW OF SYSTEM
                    ==================

    [Camera Module]
           │
           │ (Looking down at conveyor)
           ▼
    ┌──────────────────────────────────┐
    │                                  │
    │     ═══════════════════════      │  ◄── Conveyor Belt
    │     ═══════════════════════      │      (Moving →)
    │                                  │
    │              ┌─┐                 │
    │              │█│ ◄── Servo Gate  │
    │              └─┘                 │
    │                                  │
    │     Good Beans ←─┐  ┌─→ Bad Beans│
    │     (to side)    │  │  (straight)│
    │                  │  │            │
    │     [Container]  │  │ [Container]│
    │                  │  │            │
    └──────────────────┴──┴────────────┘

    [Raspberry Pi] ──── [BTS7960] ──── [12V Motor]
         │
         └──── [5V Power Supply]

    [12V Power Supply] ──── [BTS7960 Motor Power]
```

---

## Safety Checklist

Before powering on:

- [ ] All connections are secure
- [ ] No exposed wires touching each other
- [ ] 5V power supply connected to Raspberry Pi only
- [ ] 12V power supply connected to BTS7960 motor power only
- [ ] Servo connected to 5V (not 12V!)
- [ ] Camera ribbon cable properly seated
- [ ] Motor driver enable pins configured
- [ ] Emergency power switch accessible

---

## Testing Order

1. ✅ Power on Raspberry Pi (5V only)
2. ✅ Test camera: `libcamera-hello`
3. ✅ Test servo: `python3 test_hardware.py servo`
4. ✅ Test LEDs: `python3 test_hardware.py led`
5. ✅ Power on 12V supply
6. ✅ Test motor: `python3 test_hardware.py motor`
7. ✅ Test complete system: `python3 test_hardware.py all`
8. ✅ Run sorting system: `python3 bean_sorter.py best_model.keras`

---

**Wiring Complete!** Double-check all connections before powering on. 🔌
