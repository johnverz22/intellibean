# iPhone Dataset Collection Guide

## Why iPhone XS Max is Great for This

✅ **Faster** - No SSH/network delays
✅ **Better Camera** - 12MP with excellent optics
✅ **Easier** - Just take photos directly
✅ **Portable** - Can position camera anywhere
✅ **Good Lighting** - Built-in flash if needed
✅ **Quick Transfer** - AirDrop or USB cable

---

## Quick Setup

### Step 1: Camera Settings
1. Open iPhone Camera app
2. Use **Photo mode** (not Portrait)
3. Tap to focus on the beans
4. Make sure HDR is ON for better quality
5. Use grid lines (Settings → Camera → Grid)

### Step 2: Positioning
1. Mount iPhone on a stand or tripod
2. Position 15-20cm above beans (similar to Raspberry Pi)
3. Make sure lighting is even
4. White background is essential
5. Keep camera steady

### Step 3: Taking Photos
1. Arrange 50 beans on white background
2. Tap to focus
3. Take photo
4. Check focus and clarity
5. Retake if needed

---

## Transfer Methods

### Method 1: AirDrop to Laptop (Fastest)
1. Take photos on iPhone
2. Select photos in Photos app
3. Tap Share → AirDrop
4. Send to your laptop
5. Save to `coffee_dataset_final` folder

### Method 2: USB Cable
1. Connect iPhone to laptop with cable
2. Open File Explorer (Windows)
3. Go to iPhone → Internal Storage → DCIM
4. Copy photos to laptop
5. Rename and organize

### Method 3: iCloud Photos
1. Enable iCloud Photos on iPhone
2. Photos sync automatically
3. Download from iCloud.com on laptop
4. Or use iCloud for Windows app

---

## Folder Structure

Organize photos like this:
```
coffee_dataset_final/
├── good_beans/
│   ├── curve/
│   │   ├── good_curve_set01.jpg
│   │   ├── good_curve_set02.jpg
│   │   └── ...
│   └── back/
│       ├── good_back_set01.jpg
│       └── ...
└── bad_beans/
    ├── curve/
    │   ├── bad_curve_set01.jpg
    │   └── ...
    └── back/
        ├── bad_back_set01.jpg
        └── ...
```

---

## Naming Convention

Use this format:
- `good_curve_set01.jpg` to `good_curve_set21.jpg` (21 sets)
- `good_back_set01.jpg` to `good_back_set09.jpg` (9 sets)
- `bad_curve_set01.jpg` to `bad_curve_set21.jpg` (21 sets)
- `bad_back_set01.jpg` to `bad_back_set09.jpg` (9 sets)

---

## Workflow

### Option A: Take All Photos First, Organize Later
1. Take all photos on iPhone (60 total sets)
2. Transfer all to laptop at once
3. Rename and organize into folders
4. Use batch rename tool

### Option B: Organize as You Go
1. Take 1 set of photos (e.g., bad_curve)
2. Transfer to laptop immediately
3. Rename and place in correct folder
4. Update counter manually
5. Repeat for next set

---

## Tips for Best Results

### Lighting
- Use natural daylight if possible
- Or use bright white LED light
- Avoid shadows
- Even illumination across all beans

### Focus
- Tap on beans to focus
- Make sure all beans are sharp
- Check zoom level (1x is best)
- Don't use digital zoom

### Consistency
- Keep same distance for all photos
- Same lighting conditions
- Same white background
- Same camera angle (straight down)

### Quality Check
- Zoom in on photo to check sharpness
- Make sure all 50 beans are visible
- No blurry beans
- Good contrast with background

---

## Batch Renaming Tools

### Windows
**PowerToys PowerRename** (Free)
1. Install PowerToys from Microsoft
2. Select photos in File Explorer
3. Right-click → PowerRename
4. Set pattern: `good_curve_set`
5. Auto-number from 01

**Bulk Rename Utility** (Free)
1. Download from bulkrenameutility.co.uk
2. Load photos
3. Set naming pattern
4. Preview and rename

### Manual Rename Script
Create `rename_photos.py`:
```python
import os
import shutil

# Source folder with iPhone photos
source = "./iphone_photos"

# Destination folders
destinations = {
    'good_curve': './coffee_dataset_final/good_beans/curve',
    'good_back': './coffee_dataset_final/good_beans/back',
    'bad_curve': './coffee_dataset_final/bad_beans/curve',
    'bad_back': './coffee_dataset_final/bad_beans/back'
}

# Organize photos
category = input("Category (good_curve/good_back/bad_curve/bad_back): ")
start_num = int(input("Starting set number: "))

photos = sorted([f for f in os.listdir(source) if f.endswith('.jpg')])

for i, photo in enumerate(photos):
    set_num = start_num + i
    new_name = f"{category}_set{set_num:02d}.jpg"
    
    src = os.path.join(source, photo)
    dst = os.path.join(destinations[category], new_name)
    
    shutil.copy(src, dst)
    print(f"Copied: {photo} → {new_name}")

print(f"\n✓ Organized {len(photos)} photos")
```

---

## Progress Tracking

Create a simple checklist:

**Good Beans - Curve (21 sets)**
- [ ] Set 01-05
- [ ] Set 06-10
- [ ] Set 11-15
- [ ] Set 16-21

**Good Beans - Back (9 sets)**
- [ ] Set 01-05
- [ ] Set 06-09

**Bad Beans - Curve (21 sets)**
- [ ] Set 01-05
- [ ] Set 06-10
- [ ] Set 11-15
- [ ] Set 16-21

**Bad Beans - Back (9 sets)**
- [ ] Set 01-05
- [ ] Set 06-09

---

## Advantages of iPhone Method

### Speed
- No network delays
- No SSH connection issues
- Instant photo capture
- Quick transfer via AirDrop

### Quality
- 12MP camera (4032x3024)
- Better than Raspberry Pi Camera Module 3
- Excellent color accuracy
- Great low-light performance

### Convenience
- No Raspberry Pi setup needed
- No LED light control needed
- Can work anywhere
- Portable setup

### Flexibility
- Easy to adjust position
- Quick to retake photos
- Can use flash if needed
- Preview immediately

---

## Disadvantages to Consider

### Manual Work
- Need to transfer photos manually
- Need to rename files
- Need to organize folders
- Need to track progress manually

### Consistency
- Need to maintain same distance
- Need consistent lighting
- Need steady hand or tripod
- Camera angle must be consistent

### No Automation
- Can't integrate with sorting system later
- No automatic LED control
- No live preview on laptop
- Manual process throughout

---

## Hybrid Approach (Best of Both)

Use iPhone for dataset collection, then:
1. Collect all 3,000 images with iPhone (faster)
2. Transfer and organize on laptop
3. Use OpenCV to crop individual beans
4. Train ML model with iPhone images
5. Deploy model on Raspberry Pi for sorting

This way:
- ✅ Fast dataset collection (iPhone)
- ✅ Automated sorting (Raspberry Pi)
- ✅ Best of both worlds

---

## Recommended Workflow

### Phase 1: Collection (iPhone)
1. Set up white background and lighting
2. Mount iPhone on tripod/stand
3. Take all 60 sets of photos (1-2 hours)
4. Transfer to laptop via AirDrop

### Phase 2: Organization (Laptop)
1. Create folder structure
2. Batch rename photos
3. Organize into categories
4. Verify all photos are good quality

### Phase 3: Processing (Laptop)
1. Run OpenCV cropping on all images
2. Extract individual beans
3. Verify detection rate (should be 98%+)
4. Ready for ML training

### Phase 4: Training (Laptop)
1. Train model with iPhone dataset
2. Test accuracy
3. Export model for Raspberry Pi

### Phase 5: Deployment (Raspberry Pi)
1. Deploy trained model to Raspberry Pi
2. Use Raspberry Pi camera for sorting
3. Real-time bean classification
4. Automated sorting with servos

---

## Time Comparison

### Raspberry Pi Method
- Setup: 10 min
- Per capture: 30 sec (network + SSH)
- 60 captures: 30 minutes
- Total: ~40 minutes

### iPhone Method
- Setup: 5 min
- Per capture: 5 sec (just tap)
- 60 captures: 5 minutes
- Transfer: 5 minutes
- Organize: 10 minutes
- Total: ~25 minutes

**iPhone is 37% faster!**

---

## Recommendation

**For Dataset Collection: Use iPhone XS Max**
- Much faster
- Better quality
- More convenient
- Less technical issues

**For Production Sorting: Use Raspberry Pi**
- Automated system
- Integrated with servos
- LED control
- Continuous operation

**Best Approach:**
1. Use iPhone to collect dataset quickly
2. Train ML model with iPhone images
3. Deploy model to Raspberry Pi for sorting
4. Raspberry Pi handles automated sorting

This gives you the best of both worlds!

---

## Getting Started with iPhone

1. Clean your white background
2. Set up good lighting
3. Mount iPhone on stand/tripod
4. Open Camera app
5. Start taking photos!
6. Transfer to laptop when done
7. Organize and rename
8. Run OpenCV cropping
9. Ready for ML training!

Much simpler and faster than the Raspberry Pi setup for data collection!
