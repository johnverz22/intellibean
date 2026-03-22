# Recapture Feature

## Overview
The GUI now includes a "Recapture Last" button that allows you to retake the most recent image without incrementing the counter or having to manually delete files.

## How It Works

### Normal Capture Flow
1. Click "📷 CAPTURE IMAGE"
2. Confirm the capture
3. Image is saved as the next set number
4. Counter increments
5. "🔄 RECAPTURE LAST" button becomes enabled

### Recapture Flow
1. Click "🔄 RECAPTURE LAST"
2. Confirm the recapture
3. Image is captured again
4. **Replaces** the previous image file
5. **Counter does NOT increment**
6. Same set number is maintained

## Use Cases

### When to Use Recapture
- Beans were blurry in the last capture
- Beans were not arranged properly
- Lighting was wrong
- Camera focus was off
- You want to improve the quality of the last set
- Made a mistake with bean arrangement

### Benefits
- ✅ No need to manually delete images
- ✅ No need to edit JSON counter file
- ✅ Counter stays accurate
- ✅ Quick and easy to fix mistakes
- ✅ Maintains proper set numbering

## Example Scenario

### Without Recapture (Old Way)
1. Capture Set 5 → Image is blurry
2. Stop GUI
3. Navigate to folder and delete `bad_curve_set05.jpg`
4. Edit `dataset_counts_final.json` to decrement counter
5. Restart GUI
6. Capture Set 5 again

### With Recapture (New Way)
1. Capture Set 5 → Image is blurry
2. Click "🔄 RECAPTURE LAST"
3. Rearrange beans
4. Confirm → Set 5 is replaced
5. Continue with Set 6

## Button States

### "🔄 RECAPTURE LAST" Button
- **Disabled (Gray)**: No previous capture yet
- **Enabled (Orange)**: Ready to recapture last image

The button becomes enabled after your first capture and remains enabled throughout the session.

## Technical Details

### What Gets Tracked
```python
self.last_capture = {
    'category': 'bad_curve',      # Category of last capture
    'set_number': 5,               # Set number
    'filepath': 'path/to/file',   # Full path to image file
    'quality': 'bad',              # Quality (good/bad)
    'side': 'curve'                # Side (curve/back)
}
```

### What Happens During Recapture
1. Captures new image from Raspberry Pi
2. Downloads to temporary location
3. **Replaces** the file at `last_capture['filepath']`
4. Counter remains unchanged
5. Progress bars remain unchanged
6. JSON file remains unchanged

### File Replacement
The recapture uses `shutil.copy()` to overwrite the existing file:
```python
shutil.copy(local_file, self.last_capture['filepath'])
```

This ensures:
- Same filename
- Same location
- Same set number
- No orphaned files

## GUI Layout

```
┌─────────────────────────────────────────────────┐
│  💡 LED Light Control                           │
│  [Brightness Slider] [Presets]                  │
└─────────────────────────────────────────────────┘

┌──────────────────┐  ┌──────────────────┐
│  📷 CAPTURE      │  │  🔄 RECAPTURE    │
│     IMAGE        │  │     LAST         │
│  (Green, Large)  │  │  (Orange, Med)   │
└──────────────────┘  └──────────────────┘
         ↓                     ↓
    New capture          Replace last
    Counter +1           Counter same
```

## Confirmation Dialogs

### Capture Confirmation
```
Category: Bad Beans - Curve Side
Current: Set 4/21
This will be: Set 5/21
Beans: 200 → 250 (of 1050 target)

Arrange 50 beans and click OK to capture
```

### Recapture Confirmation
```
Recapture Set 5?

Category: Bad Beans - Curve Side
Set: 5/21

This will REPLACE the existing image.
Counter will NOT increment.

Arrange 50 beans and click OK
```

## Success Messages

### Capture Success
```
Set 5 captured and saved!

File: bad_curve_set05.jpg
Sets: 5/21
Beans collected: 250/1050
Sets remaining: 16

Next: Arrange 50 beans for next set
```

### Recapture Success
```
Set 5 recaptured!

File: bad_curve_set05.jpg
Category: Bad - Curve
Counter unchanged: 5/21

Image has been replaced.
```

## Important Notes

### Session-Based
- Last capture is tracked per GUI session
- If you close and reopen GUI, recapture button will be disabled
- First capture in new session enables the button

### Category Independent
- Recapture always replaces the LAST captured image
- Even if you switch categories, it will recapture the previous category
- Example: Capture bad_curve_set05 → Switch to good_back → Recapture still replaces bad_curve_set05

### File Safety
- Original file is overwritten (not backed up)
- Make sure you want to replace before confirming
- No undo function (but you can recapture again)

## Workflow Tips

### Best Practice
1. Capture image
2. Check image quality immediately (open file)
3. If not satisfied, click "🔄 RECAPTURE LAST" right away
4. If satisfied, continue to next capture

### Quality Check
After each capture, you can:
- Open the image file to verify quality
- Check focus and clarity
- Verify all beans are visible
- Check lighting and exposure
- Use recapture if needed

### Multiple Recaptures
You can recapture the same set multiple times:
1. Capture Set 5
2. Recapture Set 5 (first attempt)
3. Recapture Set 5 (second attempt)
4. Recapture Set 5 (third attempt)
5. When satisfied, continue to Set 6

Each recapture replaces the previous file.

## Troubleshooting

### Button is Disabled
- **Cause**: No previous capture in this session
- **Solution**: Capture at least one image first

### Wrong Image Replaced
- **Cause**: Recapture replaces the LAST captured image
- **Solution**: Check which set was last captured before recapturing

### Counter Incremented by Mistake
- **Cause**: Used "CAPTURE IMAGE" instead of "RECAPTURE LAST"
- **Solution**: 
  1. Manually delete the extra image file
  2. Edit `dataset_counts_final.json` to decrement counter
  3. Restart GUI

### File Not Found Error
- **Cause**: Original file was manually deleted
- **Solution**: Use "CAPTURE IMAGE" to create new set

## Summary

The recapture feature makes dataset collection much more efficient by:
- Eliminating manual file deletion
- Maintaining accurate counters automatically
- Allowing quick quality improvements
- Reducing workflow interruptions
- Preventing counter synchronization issues

Just capture, check quality, and recapture if needed!
