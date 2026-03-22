#!/usr/bin/env python3
"""
Camera diagnostic — prints HSV stats for center ROI.
Run this on the Pi to calibrate belt vs bean thresholds.

Usage:
  python3 cam_diagnose.py          # prints stats every second
  python3 cam_diagnose.py --save   # also saves sample frames as PNG
"""
import sys, time, cv2, numpy as np
from picamera2 import Picamera2

SAVE = '--save' in sys.argv

cam = Picamera2()
cfg = cam.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"},
    controls={"AfMode": 2, "AfRange": 2, "AfSpeed": 1, "Sharpness": 3.0}
)
cam.configure(cfg)
cam.start()
time.sleep(2)
print("Camera ready. Point at belt (no bean) first, then place a bean.")
print("Press Ctrl+C to stop.\n")

frame_n = 0
try:
    while True:
        raw = cam.capture_array()
        # Camera RGB swap: actual scene is BGR order in the array
        bgr = raw[:, :, ::-1]   # flip to true BGR for OpenCV
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        h, w = bgr.shape[:2]
        cx, cy = w // 2, h // 2
        margin = min(w, h) // 3

        # Full center crop (same as inference crop)
        roi_bgr = bgr[cy-margin:cy+margin, cx-margin:cx+margin]
        roi_hsv = hsv[cy-margin:cy+margin, cx-margin:cx+margin]

        h_mean  = roi_hsv[:,:,0].mean()
        s_mean  = roi_hsv[:,:,1].mean()
        v_mean  = roi_hsv[:,:,2].mean()
        s_std   = roi_hsv[:,:,1].std()

        r_mean  = roi_bgr[:,:,2].mean()   # true red
        g_mean  = roi_bgr[:,:,1].mean()   # true green
        b_mean  = roi_bgr[:,:,0].mean()   # true blue
        spread  = max(r_mean,g_mean,b_mean) - min(r_mean,g_mean,b_mean)

        print(f"[{frame_n:04d}] "
              f"HSV H={h_mean:5.1f} S={s_mean:5.1f} V={v_mean:5.1f} S_std={s_std:4.1f} | "
              f"RGB R={r_mean:5.1f} G={g_mean:5.1f} B={b_mean:5.1f} spread={spread:4.1f}",
              flush=True)

        if SAVE and frame_n % 5 == 0:
            cv2.imwrite(f"diag_frame_{frame_n:04d}.png", roi_bgr)
            print(f"  -> saved diag_frame_{frame_n:04d}.png")

        frame_n += 1
        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nDone.")
finally:
    cam.stop()
