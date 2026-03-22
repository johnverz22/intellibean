# Camera Settings — DO NOT CHANGE

Camera: Raspberry Pi Camera Module 3 (IMX708)
Status: WORKING — confirmed correct colors and sharpness

---

## Working Configuration

```python
from picamera2 import Picamera2
from PIL import Image, ImageTk, ImageEnhance

cam = Picamera2()
cfg = cam.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"},
    controls={
        "AfMode":    2,    # Continuous AF
        "AfRange":   2,    # Macro range (close objects on conveyor)
        "AfSpeed":   1,    # Fast AF
        "Sharpness": 3.0,  # Max camera-level sharpness
    }
)
cam.configure(cfg)
cam.start()
time.sleep(2)  # wait for AF to lock
```

## Working Frame Capture + Display

```python
frame = cam.capture_array()

# IMPORTANT: picamera2 returns BGR channel order despite RGB888 label
# Must swap R and B or the image appears blue
img = Image.fromarray(frame).convert("RGB")
r, g, b = img.split()
img = Image.merge("RGB", (b, g, r))  # fix blue tint — DO NOT REMOVE

img = img.resize((500, 375), Image.LANCZOS)
img = ImageEnhance.Sharpness(img).enhance(3.0)   # software sharpness boost
img = ImageEnhance.Contrast(img).enhance(1.2)    # slight contrast boost

tk_img = ImageTk.PhotoImage(img)
label.image = tk_img       # keep reference on widget — prevents GC blank screen
label.config(image=tk_img)
```

## Key Notes

- `(b, g, r)` channel swap is REQUIRED — removing it makes beans appear blue
- Do NOT add `ExposureTime` or `AnalogueGain` overrides — causes white/overexposed frames
- Do NOT use `[:, :, ::-1]` numpy flip — same blue problem
- `label.image = tk_img` second reference is REQUIRED — without it Tkinter GC kills the image and shows white
- `time.sleep(2)` after `cam.start()` is needed for AF to lock on first frame
- Camera outputs RGBA (4 channels) in some modes — always `.convert("RGB")` before processing
