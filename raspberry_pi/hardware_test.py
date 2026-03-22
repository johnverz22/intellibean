#!/usr/bin/env python3
"""
Bean Sorter - Hardware Test + Live Detection
Pi 5 — ALL GPIO via lgpio (gpiochip4)
SERVO=22 | Conveyor BTS7960: RPWM=13,LPWM=26,R_EN=27,L_EN=21
Bean Sim ULN2003: IN1=25,IN2=5,IN3=6,IN4=16
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import os
import numpy as np
import lgpio
from picamera2 import Picamera2
from PIL import Image, ImageTk, ImageEnhance
from datetime import datetime

if 'DISPLAY' not in os.environ:
    os.environ['DISPLAY'] = ':0'

try:
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    from tflite_runtime.interpreter import Interpreter

CAPTURE_DIR = os.path.expanduser('~/bean_sorter/test_captures')
os.makedirs(CAPTURE_DIR, exist_ok=True)

_base = os.path.expanduser('~/bean_sorter')
MODEL_PATH = next(
    (os.path.join(_base, f) for f in ('best_model_new.tflite', 'best_model_v2.tflite')
     if os.path.exists(os.path.join(_base, f))),
    os.path.join(os.path.dirname(__file__), 'best_model_v2.tflite')
)
print(f"Using model: {MODEL_PATH}", flush=True)

# ── GPIO BCM pin numbers ───────────────────────────────────────────────────────
SERVO_PIN  = 22
MOTOR_RPWM = 13
MOTOR_LPWM = 26
MOTOR_R_EN = 27
MOTOR_L_EN = 21
SIM_PINS   = [16, 6, 5, 25]   # ULN2003 IN4→IN1 (reversed for CW rotation)

# ── Push buttons (internal pull-up — active LOW) ──────────────────────────────
BTN_START  = 19   # starts conveyor + singulator
BTN_STOP   = 24   # stops conveyor + singulator

# ── Status LEDs ───────────────────────────────────────────────────────────────
LED_RUNNING     = 20   # GREEN — system running
LED_NOT_RUNNING = 12   # RED   — system stopped

# ── MG996R ────────────────────────────────────────────────────────────────────
# MG996R spec: 50Hz, 0°=500µs, 90°=1500µs, 180°=2500µs
SERVO_FREQ    = 50
SERVO_0       = 500    # µs — 0°
SERVO_90      = 1500   # µs — 90°
SERVO_180     = 2500   # µs — 180°
SERVO_DEFAULT = SERVO_0

# Hardcoded exact pulse widths — no math, no drift
SERVO_POS_120 = 1833   # µs — 120° = default/retracted (good beans pass freely)
SERVO_POS_180 = 2500   # µs — 180° = flick position (sweeps bad bean off belt)

# ── Prediction-ahead gate delay ───────────────────────────────────────────────
# Time (seconds) between camera detection and servo flick.
# Set this to belt_speed_cm_per_sec / camera_to_gate_distance_cm
# Default 0.4s — tune via HMI slider
GATE_DELAY_S  = 0.4
FLICK_HOLD_S  = 0.5   # how long servo stays at 180° before returning to 120°

# ── 28BYJ-48 dual-coil sequence (ported from working Arduino code) ────────────
# Two coils energised at once = more torque, faster rotation
# Reversed from Arduino dir=false to get clockwise rotation
STEP_SEQ = [
    [1, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 1, 1, 0],
    [1, 1, 0, 0],
]

def deg_to_us(deg):
    """Convert 0-180° to pulse width µs, clamped strictly."""
    deg = max(0, min(180, deg))
    return int(SERVO_0 + (deg / 180.0) * (SERVO_180 - SERVO_0))

PREVIEW_W      = 420
PREVIEW_H      = 315
CONFIDENCE_MIN = 0.65


class HardwareTest:
    def __init__(self):
        # ── model ─────────────────────────────────────────────────────────────
        print("Loading model...", flush=True)
        self._interpreter = Interpreter(model_path=MODEL_PATH)
        self._interpreter.allocate_tensors()
        self._input  = self._interpreter.get_input_details()
        self._output = self._interpreter.get_output_details()
        print("Model loaded.", flush=True)

        # ── lgpio — Pi 5 uses gpiochip4 ───────────────────────────────────────
        try:
            self._lg = lgpio.gpiochip_open(4)
            print("lgpio: opened gpiochip4 (Pi 5)", flush=True)
        except Exception as e:
            print(f"lgpio: gpiochip4 failed ({e}), trying gpiochip0", flush=True)
            self._lg = lgpio.gpiochip_open(0)

        # Claim all output pins LOW at start
        # gpio_free first to release any stale claim from a previous crash
        all_out_pins = [MOTOR_RPWM, MOTOR_LPWM, MOTOR_R_EN, MOTOR_L_EN,
                        SERVO_PIN, LED_RUNNING, LED_NOT_RUNNING] + SIM_PINS
        for pin in all_out_pins:
            try:
                lgpio.gpio_free(self._lg, pin)
            except Exception:
                pass
            try:
                lgpio.gpio_claim_output(self._lg, pin, 0)
                print(f"  claimed output GPIO{pin}", flush=True)
            except Exception as e:
                print(f"  GPIO{pin} claim failed: {e}", flush=True)

        # Claim push buttons as inputs with internal pull-up
        for pin in [BTN_START, BTN_STOP]:
            try:
                lgpio.gpio_free(self._lg, pin)
            except Exception:
                pass
            try:
                lgpio.gpio_claim_input(self._lg, pin, lgpio.SET_PULL_UP)
                print(f"  claimed input GPIO{pin} (pull-up)", flush=True)
            except Exception as e:
                print(f"  GPIO{pin} input claim failed: {e}", flush=True)

        self._conveyor_on  = False
        self._conveyor_dir = 'fwd'
        self._sim_running  = False
        self._sim_on       = False
        self._step_delay   = 0.005   # 5ms/step — slower, more controlled
        self._step_idx     = 0
        self._servo_busy   = False
        self._servo_pos_us = SERVO_DEFAULT
        self._servo_target = SERVO_DEFAULT
        self._system_on    = False

        # LED: not running at start
        lgpio.gpio_write(self._lg, LED_RUNNING,     0)
        lgpio.gpio_write(self._lg, LED_NOT_RUNNING, 1)

        # Move servo to 120° on start (retracted — good beans flow freely)
        self._servo_move_blocking(SERVO_POS_120)

        # ── camera ────────────────────────────────────────────────────────────
        # DO NOT CHANGE — see docs/CAMERA_SETTINGS.md
        self.cam = Picamera2()
        cfg = self.cam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            controls={"AfMode": 2, "AfRange": 2, "AfSpeed": 1, "Sharpness": 3.0}
        )
        self.cam.configure(cfg)
        self.cam.start()
        time.sleep(2)

        self._tk_img      = None
        self._capturing   = False
        self._infer_frame = None
        self._prev_frame  = None
        self._detect_mode = 'moving'

        self._build_ui()
        threading.Thread(target=self._inference_loop, daemon=True).start()
        threading.Thread(target=self._button_poll, daemon=True).start()
        self.root.after(66, self._update_camera)

    # ── conveyor ──────────────────────────────────────────────────────────────
    def _conv_speed(self):
        return int(self.conv_speed_slider.get())

    def _start_conveyor(self):
        spd = self._conv_speed()
        lgpio.gpio_write(self._lg, MOTOR_R_EN, 1)
        lgpio.gpio_write(self._lg, MOTOR_L_EN, 1)
        lgpio.tx_pwm(self._lg, MOTOR_RPWM, 1000, spd)
        lgpio.tx_pwm(self._lg, MOTOR_LPWM, 1000, 0)
        self._conveyor_on  = True
        self._conveyor_dir = 'fwd'
        self.conv_lbl.config(text=f"Belt: FWD ● {spd}%", fg='#2ECC71')
        self.conv_btn.config(text="■ STOP", bg='#E74C3C')
        print(f"[BELT] Fwd {spd}%", flush=True)

    def _reverse_conveyor(self):
        spd = self._conv_speed()
        lgpio.gpio_write(self._lg, MOTOR_R_EN, 1)
        lgpio.gpio_write(self._lg, MOTOR_L_EN, 1)
        lgpio.tx_pwm(self._lg, MOTOR_RPWM, 1000, 0)
        lgpio.tx_pwm(self._lg, MOTOR_LPWM, 1000, spd)
        self._conveyor_on  = True
        self._conveyor_dir = 'rev'
        self.conv_lbl.config(text=f"Belt: REV ● {spd}%", fg='#F39C12')
        self.conv_btn.config(text="■ STOP", bg='#E74C3C')
        print(f"[BELT] Rev {spd}%", flush=True)

    def _stop_conveyor(self):
        lgpio.tx_pwm(self._lg, MOTOR_RPWM, 0, 0)
        lgpio.tx_pwm(self._lg, MOTOR_LPWM, 0, 0)
        lgpio.gpio_write(self._lg, MOTOR_RPWM, 0)
        lgpio.gpio_write(self._lg, MOTOR_LPWM, 0)
        lgpio.gpio_write(self._lg, MOTOR_R_EN, 0)
        lgpio.gpio_write(self._lg, MOTOR_L_EN, 0)
        self._conveyor_on = False
        self.conv_lbl.config(text="Belt: STOPPED", fg='#E74C3C')
        self.conv_btn.config(text="▶ FWD", bg='#27AE60')
        print("[BELT] Stopped", flush=True)

    def toggle_conveyor(self):
        if self._conveyor_on:
            self._stop_conveyor()
        else:
            self._start_conveyor()

    def on_conv_speed(self, val):
        spd = int(float(val))
        if not self._conveyor_on:
            return
        if self._conveyor_dir == 'fwd':
            lgpio.tx_pwm(self._lg, MOTOR_RPWM, 1000, spd)
            self.conv_lbl.config(text=f"Belt: FWD ● {spd}%", fg='#2ECC71')
        else:
            lgpio.tx_pwm(self._lg, MOTOR_LPWM, 1000, spd)
            self.conv_lbl.config(text=f"Belt: REV ● {spd}%", fg='#F39C12')

    # ── stepper (ULN2003 + 28BYJ-48) ─────────────────────────────────────────
    def _step_loop(self):
        print("[SIM] Step loop started", flush=True)
        while self._sim_running:
            seq = STEP_SEQ[self._step_idx % 4]
            for i, pin in enumerate(SIM_PINS):
                lgpio.gpio_write(self._lg, pin, seq[i])
            self._step_idx += 1
            time.sleep(self._step_delay)
        # All coils off
        for pin in SIM_PINS:
            lgpio.gpio_write(self._lg, pin, 0)
        print("[SIM] Step loop ended, coils off", flush=True)

    def _start_sim(self):
        if self._sim_running:
            return
        self._sim_running = True
        self._sim_on      = True
        threading.Thread(target=self._step_loop, daemon=True).start()
        self.sim_lbl.config(text="Sim: RUNNING ●", fg='#2ECC71')
        self.sim_btn.config(text="■ STOP", bg='#E74C3C')
        print("[SIM] Started", flush=True)

    def _stop_sim(self):
        self._sim_running = False
        self._sim_on      = False
        self.sim_lbl.config(text="Sim: STOPPED", fg='#E74C3C')
        self.sim_btn.config(text="▶ START", bg='#27AE60')

    def toggle_sim(self):
        if self._sim_on:
            self._stop_sim()
        else:
            self._start_sim()

    # ── system start / stop (conveyor + singulator together) ──────────────────
    def _set_leds(self, running):
        lgpio.gpio_write(self._lg, LED_RUNNING,     1 if running else 0)
        lgpio.gpio_write(self._lg, LED_NOT_RUNNING, 0 if running else 1)
        self.root.after(0, lambda: self.sys_lbl.config(
            text="● RUNNING" if running else "● STOPPED",
            fg='#2ECC71' if running else '#E74C3C'))

    def system_start(self):
        self._system_on = True
        if not self._conveyor_on:
            self._start_conveyor()
        if not self._sim_on:
            self._start_sim()
        self._set_leds(True)
        self.root.after(0, self._flash_start_btn)

    def system_stop(self):
        self._system_on = False
        self._stop_conveyor()
        self._stop_sim()
        self._set_leds(False)
        self.root.after(0, self._flash_stop_btn)

    def _flash_start_btn(self):
        self.sys_start_btn.config(bg='#F39C12')
        self.root.after(300, lambda: self.sys_start_btn.config(bg='#27AE60'))

    def _flash_stop_btn(self):
        self.sys_stop_btn.config(bg='#F39C12')
        self.root.after(300, lambda: self.sys_stop_btn.config(bg='#E74C3C'))

    # ── physical button polling ────────────────────────────────────────────────
    def _button_poll(self):
        prev_start = 1
        prev_stop  = 1
        last_start_time = 0
        last_stop_time  = 0
        DEBOUNCE = 0.3   # 300ms — ignore repeated presses within this window
        while True:
            try:
                cur_start = lgpio.gpio_read(self._lg, BTN_START)
                cur_stop  = lgpio.gpio_read(self._lg, BTN_STOP)
                now = time.time()
                if prev_start == 1 and cur_start == 0 and (now - last_start_time) > DEBOUNCE:
                    last_start_time = now
                    print("[BTN] START pressed", flush=True)
                    self.root.after(0, self.system_start)
                if prev_stop == 1 and cur_stop == 0 and (now - last_stop_time) > DEBOUNCE:
                    last_stop_time = now
                    print("[BTN] STOP pressed", flush=True)
                    self.root.after(0, self.system_stop)
                prev_start = cur_start
                prev_stop  = cur_stop
            except Exception as e:
                print(f"[BTN] {e}", flush=True)
            time.sleep(0.05)

    # ── servo ─────────────────────────────────────────────────────────────────
    def _servo_move_blocking(self, target_us):
        """Simple move-and-kill. Exact pulse, no ramp, no drift."""
        duty = (target_us / 20000.0) * 100
        lgpio.tx_pwm(self._lg, SERVO_PIN, SERVO_FREQ, duty)
        time.sleep(0.7)                          # hold long enough to reach position
        lgpio.tx_pwm(self._lg, SERVO_PIN, 0, 0) # kill PWM
        lgpio.gpio_write(self._lg, SERVO_PIN, 0)
        self._servo_pos_us = target_us
        self._servo_busy   = False
        deg = 120 if target_us == SERVO_POS_120 else 180
        print(f"[SERVO] At {deg}°  ({target_us}µs)", flush=True)

    def servo_move(self, us):
        # Always accept new move — overwrite any in-progress
        self._servo_busy = True
        self._servo_target = us  # track latest requested target
        def _move(target):
            # Only execute if this is still the latest request
            if target != self._servo_target:
                self._servo_busy = False
                return
            self._servo_move_blocking(target)
            if target == self._servo_target:  # still latest
                deg = 120 if target == SERVO_POS_120 else 180
                self.root.after(0, lambda: self.servo_lbl.config(
                    text=f"Servo: {deg}°", fg='#2ECC71'))
        threading.Thread(target=_move, args=(us,), daemon=True).start()

    # ── inference ─────────────────────────────────────────────────────────────
    def _inference_loop(self):
        while True:
            # Only run inference when system is ON
            if not self._system_on:
                self.root.after(0, lambda: self.detect_lbl.config(
                    text="⬤  SYSTEM OFF", bg='#2C3E50', fg='#566573'))
                time.sleep(0.3)
                continue
            frame = self._infer_frame
            if frame is None:
                time.sleep(0.1)
                continue
            try:
                w, h = frame.size
                cx, cy = w // 2, h // 2

                # Motion check — skip static frames in moving mode
                roi       = frame.crop((cx-80, cy-60, cx+80, cy+60))
                small_arr = np.array(roi.resize((40, 30)).convert("L"), dtype=np.float32)
                diff = np.abs(small_arr - self._prev_frame).mean() \
                       if self._prev_frame is not None else 99.0
                self._prev_frame = small_arr

                if self._detect_mode == 'moving' and diff < 2.5:
                    self.root.after(0, lambda: self.detect_lbl.config(
                        text="⬤  NO BEAN", bg='#2C3E50', fg='#566573'))
                    self.root.after(0, self._on_no_bean)
                    time.sleep(0.15)
                    continue

                # Crop and resize for model
                margin = min(w, h) // 3
                crop = frame.crop((cx-margin, cy-margin, cx+margin, cy+margin))
                img  = crop.resize((224, 224), Image.LANCZOS)

                # Run model — confidence IS the bean presence check
                # Belt scores low confidence on both classes → shows SCANNING
                # Beans score high confidence on good or bad → triggers action
                arr  = (np.array(img, dtype=np.float32) / 127.5) - 1.0
                arr  = np.expand_dims(arr, axis=0)
                self._interpreter.set_tensor(self._input[0]['index'], arr)
                self._interpreter.invoke()
                preds      = self._interpreter.get_tensor(self._output[0]['index'])[0]
                confidence = float(np.max(preds))
                is_good    = int(np.argmax(preds)) == 1

                self.root.after(0, lambda g=is_good, c=confidence:
                                self._update_detection_ui(g, c))
                time.sleep(0.5 if self._detect_mode == 'static' else 0.15)
            except Exception as e:
                print(f"[MODEL] {e}", flush=True)
                time.sleep(0.2)


    def _update_detection_ui(self, is_good, confidence):
        pct = f"{confidence*100:.0f}%"
        if confidence < CONFIDENCE_MIN:
            self.detect_lbl.config(text=f"SCANNING {pct}", bg='#2C3E50', fg='#95A5A6')
        elif is_good:
            # Good bean — servo stays at 120°, nothing to do
            self.detect_lbl.config(text=f"✔ GOOD  {pct}", bg='#27AE60', fg='white')
        else:
            # Bad bean — flick servo after gate delay, then return
            self.detect_lbl.config(text=f"✘ BAD   {pct}", bg='#E74C3C', fg='white')
            if not self._servo_busy:
                threading.Thread(target=self._flick_bad_bean, daemon=True).start()

    def _flick_bad_bean(self):
        """Wait gate delay, flick to 180°, hold, return to 120°."""
        delay = self._gate_delay_var.get() if hasattr(self, '_gate_delay_var') else GATE_DELAY_S
        time.sleep(delay)
        # Flick to 180° (sweep bad bean off belt)
        self._servo_move_blocking(SERVO_POS_180)
        self.root.after(0, lambda: self.servo_lbl.config(text="Servo: 180° FLICK", fg='#E74C3C'))
        time.sleep(FLICK_HOLD_S)
        # Return to 120° (ready for next bean)
        self._servo_move_blocking(SERVO_POS_120)
        self.root.after(0, lambda: self.servo_lbl.config(text="Servo: 120° READY", fg='#2ECC71'))

    def _on_no_bean(self):
        """No bean — ensure servo is at default 120° (retracted)."""
        if not self._servo_busy and self._servo_pos_us != SERVO_POS_120:
            self.servo_move(SERVO_POS_120)

    def toggle_detect_mode(self):
        if self._detect_mode == 'moving':
            self._detect_mode = 'static'
            self.mode_btn.config(text="STATIC MODE 🔍", bg='#D35400')
        else:
            self._detect_mode = 'moving'
            self.mode_btn.config(text="MOVING MODE 🎞", bg='#1A5276')

    # ── camera ────────────────────────────────────────────────────────────────
    # DO NOT CHANGE — see docs/CAMERA_SETTINGS.md
    def _update_camera(self):
        def _grab():
            try:
                frame = self.cam.capture_array()
                img   = Image.fromarray(frame).convert("RGB")
                r, g, b = img.split()
                img = Image.merge("RGB", (b, g, r))
                self._infer_frame = img
                img = img.resize((PREVIEW_W, PREVIEW_H), Image.LANCZOS)
                img = ImageEnhance.Sharpness(img).enhance(3.0)
                img = ImageEnhance.Contrast(img).enhance(1.2)
                tk_img = ImageTk.PhotoImage(img)
                self._tk_img = tk_img
                self.root.after(0, self._apply_frame)
            except Exception as e:
                print(f"[CAM] {e}", flush=True)
            self.root.after(66, self._update_camera)
        threading.Thread(target=_grab, daemon=True).start()

    def _apply_frame(self):
        if self._tk_img:
            self.cam_lbl.config(image=self._tk_img)
            self.cam_lbl.image = self._tk_img

    # ── UI — two-column scrollable layout ─────────────────────────────────────
    def _build_ui(self):
        BG  = '#1A252F'
        RED = '#E74C3C'
        WHT = '#ECF0F1'
        DRK = '#0D1B2A'

        self.root = tk.Tk()
        self.root.title("Bean Sorter")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=BG)
        self.root.bind('<Escape>', lambda e: self.exit_app())

        # Get screen size
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        fnt_hdr  = tkfont.Font(family='Arial', size=14, weight='bold')
        fnt_btn  = tkfont.Font(family='Arial', size=12, weight='bold')
        fnt_stat = tkfont.Font(family='Arial', size=11)
        fnt_det  = tkfont.Font(family='Arial', size=16, weight='bold')

        # Title bar with EXIT always visible
        title_bar = tk.Frame(self.root, bg='#2C3E50')
        title_bar.pack(fill=tk.X)
        tk.Label(title_bar, text="⚙ BEAN SORTER — HARDWARE TEST",
                 font=fnt_hdr, bg='#2C3E50', fg=WHT, pady=6).pack(side=tk.LEFT, padx=8)
        tk.Button(title_bar, text="✕ EXIT",
                  font=fnt_btn, bg='#E74C3C', fg='white',
                  relief=tk.RAISED, bd=2, padx=10,
                  command=self.exit_app).pack(side=tk.RIGHT, padx=8, pady=4)

        # Main row
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # ── LEFT col: camera ──────────────────────────────────────────────────
        left = tk.Frame(main, bg=DRK, relief=tk.SUNKEN, bd=2)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        tk.Label(left, text="LIVE CAMERA", font=fnt_stat,
                 bg=DRK, fg='#7F8C8D').pack(pady=(4, 2))
        self.cam_lbl = tk.Label(left, bg='black',
                                width=PREVIEW_W, height=PREVIEW_H)
        self.cam_lbl.pack(padx=4)

        self.detect_lbl = tk.Label(
            left, text="⬤  WAITING...",
            font=fnt_det, bg='#2C3E50', fg='#95A5A6',
            width=22, pady=8, relief=tk.RAISED, bd=2)
        self.detect_lbl.pack(padx=4, pady=4, fill=tk.X)

        self.mode_btn = tk.Button(
            left, text="MOVING MODE 🎞",
            font=fnt_btn, bg='#1A5276', fg='white',
            height=2, relief=tk.RAISED, bd=2,
            command=self.toggle_detect_mode)
        self.mode_btn.pack(padx=4, pady=2, fill=tk.X)

        self.cap_btn = tk.Button(
            left, text="📷 CAPTURE",
            font=fnt_btn, bg='#2980B9', fg='white',
            height=2, relief=tk.RAISED, bd=2,
            command=self.capture_sample)
        self.cap_btn.pack(padx=4, pady=(2, 6), fill=tk.X)

        # ── RIGHT col: controls (scrollable canvas) ───────────────────────────
        right_outer = tk.Frame(main, bg=BG)
        right_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(right_outer, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(right_outer, orient=tk.VERTICAL,
                                 command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ctrl = tk.Frame(canvas, bg=BG)
        canvas_window = canvas.create_window((0, 0), window=ctrl, anchor='nw')

        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)
        ctrl.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)

        def section(title):
            tk.Frame(ctrl, bg='#2C3E50', height=2).pack(fill=tk.X, pady=(6, 3))
            tk.Label(ctrl, text=title, font=fnt_btn, bg=BG, fg=WHT).pack()

        # ── SYSTEM START / STOP ───────────────────────────────────────────────
        section("SYSTEM CONTROL")
        sys_row = tk.Frame(ctrl, bg=BG)
        sys_row.pack(pady=4, padx=6, fill=tk.X)
        self.sys_start_btn = tk.Button(sys_row, text="▶ START ALL",
            font=fnt_btn, bg='#27AE60', fg='white',
            height=2, relief=tk.RAISED, bd=2,
            command=self.system_start)
        self.sys_start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,3))
        self.sys_stop_btn = tk.Button(sys_row, text="■ STOP ALL",
            font=fnt_btn, bg='#E74C3C', fg='white',
            height=2, relief=tk.RAISED, bd=2,
            command=self.system_stop)
        self.sys_stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(3,0))

        self.sys_lbl = tk.Label(ctrl, text="● STOPPED",
                                font=fnt_stat, bg=BG, fg=RED)
        self.sys_lbl.pack()

        # ── CONVEYOR ──────────────────────────────────────────────────────────
        section("CONVEYOR BELT")
        self.conv_lbl = tk.Label(ctrl, text="Belt: STOPPED",
                                 font=fnt_stat, bg=BG, fg=RED)
        self.conv_lbl.pack()

        spd_row = tk.Frame(ctrl, bg=BG)
        spd_row.pack(fill=tk.X, padx=6)
        tk.Label(spd_row, text="Spd:", font=fnt_stat, bg=BG, fg=WHT).pack(side=tk.LEFT)
        self.conv_speed_slider = tk.Scale(
            spd_row, from_=0, to=100, orient=tk.HORIZONTAL,
            font=fnt_stat, bg=BG, fg=WHT, troughcolor='#2C3E50',
            highlightthickness=0, command=self.on_conv_speed)
        self.conv_speed_slider.set(50)
        self.conv_speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        conv_row = tk.Frame(ctrl, bg=BG)
        conv_row.pack(pady=3)
        self.conv_btn = tk.Button(conv_row, text="▶ FWD",
            font=fnt_btn, bg='#27AE60', fg='white',
            width=9, height=2, relief=tk.RAISED, bd=2,
            command=self.toggle_conveyor)
        self.conv_btn.pack(side=tk.LEFT, padx=3)
        self.rev_btn = tk.Button(conv_row, text="◀ REV",
            font=fnt_btn, bg='#8E44AD', fg='white',
            width=9, height=2, relief=tk.RAISED, bd=2,
            command=self._reverse_conveyor)
        self.rev_btn.pack(side=tk.LEFT, padx=3)

        # ── BEAN SIM MOTOR ────────────────────────────────────────────────────
        section("BEAN SIM MOTOR")
        self.sim_lbl = tk.Label(ctrl, text="Sim: STOPPED",
                                font=fnt_stat, bg=BG, fg=RED)
        self.sim_lbl.pack()

        self.sim_btn = tk.Button(ctrl, text="▶ START",
            font=fnt_btn, bg='#27AE60', fg='white',
            height=2, relief=tk.RAISED, bd=2,
            command=self.toggle_sim)
        self.sim_btn.pack(padx=6, pady=3, fill=tk.X)

        # ── SERVO ─────────────────────────────────────────────────────────────
        section("SERVO GATE")
        self.servo_lbl = tk.Label(ctrl, text="Servo: 120° READY",
                                  font=fnt_stat, bg=BG, fg='#2ECC71')
        self.servo_lbl.pack()

        # Gate delay slider — tune prediction-ahead timing
        delay_row = tk.Frame(ctrl, bg=BG)
        delay_row.pack(fill=tk.X, padx=6, pady=(2,0))
        tk.Label(delay_row, text="Gate delay (s):", font=fnt_stat,
                 bg=BG, fg=WHT).pack(side=tk.LEFT)
        self._gate_delay_var = tk.DoubleVar(value=GATE_DELAY_S)
        self._gate_delay_lbl = tk.Label(delay_row, text=f"{GATE_DELAY_S:.1f}s",
                                        font=fnt_stat, bg=BG, fg='#F39C12', width=4)
        self._gate_delay_lbl.pack(side=tk.RIGHT)
        tk.Scale(delay_row, from_=0.0, to=2.0, resolution=0.1,
                 orient=tk.HORIZONTAL, variable=self._gate_delay_var,
                 font=fnt_stat, bg=BG, fg=WHT, troughcolor='#2C3E50',
                 highlightthickness=0,
                 command=lambda v: self._gate_delay_lbl.config(
                     text=f"{float(v):.1f}s")).pack(side=tk.LEFT, fill=tk.X, expand=True)

        srv_row = tk.Frame(ctrl, bg=BG)
        srv_row.pack(pady=3)
        tk.Button(srv_row, text="120°", font=fnt_btn,
                  bg='#2980B9', fg='white',
                  width=10, height=2, relief=tk.RAISED, bd=2,
                  command=lambda: self.servo_move(SERVO_POS_120)).pack(side=tk.LEFT, padx=4)
        tk.Button(srv_row, text="180°", font=fnt_btn,
                  bg='#2980B9', fg='white',
                  width=10, height=2, relief=tk.RAISED, bd=2,
                  command=lambda: self.servo_move(SERVO_POS_180)).pack(side=tk.LEFT, padx=4)

        # (EXIT is in the title bar — always visible)

    # ── capture ───────────────────────────────────────────────────────────────
    def capture_sample(self):
        if self._capturing:
            return
        self._capturing = True
        self.cap_btn.config(text="Saving...", state=tk.DISABLED)
        def _do():
            try:
                ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(CAPTURE_DIR, f"capture_{ts}.jpg")
                self.cam.capture_file(path)
                self.root.after(0, lambda: self.cap_btn.config(
                    text="✓ Saved!", state=tk.NORMAL, bg='#27AE60'))
                self.root.after(2000, lambda: self.cap_btn.config(
                    text="📷 CAPTURE", bg='#2980B9'))
            except Exception as e:
                print(f"Capture error: {e}", flush=True)
                self.root.after(0, lambda: self.cap_btn.config(
                    text="📷 CAPTURE", state=tk.NORMAL))
            self._capturing = False
        threading.Thread(target=_do, daemon=True).start()

    # ── cleanup ───────────────────────────────────────────────────────────────
    def exit_app(self):
        try:
            self._sim_running = False
            time.sleep(0.05)
            for pin in [MOTOR_RPWM, MOTOR_LPWM]:
                try:
                    lgpio.tx_pwm(self._lg, pin, 0, 0)
                except Exception:
                    pass
            for pin in [MOTOR_RPWM, MOTOR_LPWM, MOTOR_R_EN, MOTOR_L_EN,
                        SERVO_PIN, LED_RUNNING, LED_NOT_RUNNING] + SIM_PINS:
                try:
                    lgpio.gpio_write(self._lg, pin, 0)
                except Exception:
                    pass
            lgpio.gpiochip_close(self._lg)
            self.cam.stop()
        except Exception:
            pass
        os._exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HardwareTest()
    app.run()
