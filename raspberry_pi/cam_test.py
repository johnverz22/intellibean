#!/usr/bin/env python3
from picamera2 import Picamera2
from PIL import Image
import time

cam = Picamera2()
cfg = cam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
cam.configure(cfg)
cam.start()
time.sleep(2)
frame = cam.capture_array()
print("shape:", frame.shape, "dtype:", frame.dtype)
print("min:", frame.min(), "max:", frame.max(), "mean:", round(float(frame.mean()), 1))
img = Image.fromarray(frame)
img.save("/tmp/cam_test.jpg")
cam.stop()
print("saved /tmp/cam_test.jpg")
