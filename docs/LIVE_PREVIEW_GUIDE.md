# Live Camera Preview Guide

## Overview
The GUI now includes a live camera preview feature that lets you see exactly where to position your beans before capturing.

## How to Use

### Starting Live Preview
1. Click the **📹 LIVE PREVIEW** button (blue button on the left)
2. A new window will open showing the live camera feed
3. The preview updates every 2 seconds
4. Position your 50 beans while watching the preview

### Positioning Beans
1. Open live preview
2. Arrange beans on the white background
3. Watch the preview to ensure:
   - All beans are visible in frame
   - Beans are well-spaced (not touching)
   - Lighting is even
   - Focus is sharp
   - No shadows or glare

### Capturing After Preview
1. Once beans are positioned correctly
2. Close the preview window (or leave it open)
3. Click **📷 CAPTURE IMAGE** to take the high-resolution photo
4. The capture uses full resolution (4608x2592) for best quality

### Stopping Preview
- Click "Close Preview" button in preview window
- Or click the X to close the preview window
- Or click **📹 LIVE PREVIEW** again to toggle off

## Button Layout

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  📹 LIVE     │  │  📷 CAPTURE  │  │  🔄 RECAPTURE│
│   PREVIEW    │  │    IMAGE     │  │     LAST     │
│  (Blue)      │  │  (Green)     │  │  (Orange)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Preview Window Features

### Window Title
"Live Camera Preview - Position Your Beans"

### Instructions Bar (Blue)
"Position your 50 beans in the frame. Preview updates every 2 seconds."

### Live Image Display
- Shows camera feed in real-time
- Automatically scaled to fit window
- Updates every 2 seconds
- Lower resolution (1920x1080) for speed

### Status Bar
Shows current frame number and status:
- "Capturing frame 1..."
- "Frame 5 - Live"
- "Frame 10 - Download failed" (if error)

### Close Button (Red)
"Close Preview" - Stops preview and closes window

## Technical Details

### Preview Settings
- **Resolution**: 1920x1080 (lower than capture for speed)
- **Update Rate**: Every 2 seconds
- **Quality**: 85% JPEG (lower than capture for speed)
- **Timeout**: 1 second per frame
- **Autofocus**: Macro mode (15-16cm distance)

### Capture Settings (Full Quality)
- **Resolution**: 4608x2592 (maximum)
- **Quality**: 95% JPEG (high quality)
- **Timeout**: 5 seconds (allows autofocus)
- **All optimizations**: Sharpness, contrast, etc.

### Why Different Settings?
- **Preview**: Fast updates, lower quality for positioning
- **Capture**: Slow, high quality for dataset

## Workflow Examples

### Recommended Workflow
1. Click **📹 LIVE PREVIEW**
2. Arrange 50 beans while watching preview
3. Adjust spacing and positioning
4. When satisfied, leave preview open
5. Click **📷 CAPTURE IMAGE**
6. High-resolution image is captured
7. Check captured image quality
8. If not satisfied, click **🔄 RECAPTURE LAST**
9. Close preview when done

### Quick Workflow
1. Arrange beans (no preview)
2. Click **📷 CAPTURE IMAGE**
3. If positioning was wrong, click **🔄 RECAPTURE LAST**
4. Use **📹 LIVE PREVIEW** to reposition
5. Click **🔄 RECAPTURE LAST** again

### First-Time Setup Workflow
1. Click **📹 LIVE PREVIEW**
2. Mark the visible area on your white background
3. Use tape or markers to show bean placement zone
4. Close preview
5. Now you can position beans without preview
6. Use preview occasionally to verify

## Tips for Best Results

### Lighting
- Use live preview to check lighting
- Adjust LED brightness if needed
- Look for shadows or glare
- Ensure even illumination

### Bean Spacing
- Beans should not touch each other
- Leave small gaps between beans
- Use preview to verify spacing
- Aim for even distribution

### Focus Check
- Preview shows if focus is sharp
- If blurry, adjust camera height
- Optimal distance: 15-16cm
- Use preview to verify focus

### Frame Coverage
- Use preview to see full capture area
- Don't place beans too close to edges
- Leave margin around bean area
- Ensure all 50 beans fit in frame

## Troubleshooting

### Preview window is black
- **Cause**: Camera capture failed
- **Solution**: Check Raspberry Pi connection
- **Check**: SSH connection is active
- **Try**: Close and reopen preview

### Preview is very slow
- **Normal**: Updates every 2 seconds
- **Reason**: Network transfer takes time
- **Note**: Capture is slower but higher quality

### Preview shows "Capture failed"
- **Cause**: Camera busy or error
- **Solution**: Wait a few seconds
- **Try**: Close preview and reopen
- **Check**: Camera is not being used elsewhere

### Preview shows "Download failed"
- **Cause**: Network issue
- **Solution**: Check WiFi connection
- **Check**: Raspberry Pi is on network
- **Try**: Test connection in main window

### Preview window won't close
- **Solution**: Click X on window
- **Or**: Click "Close Preview" button
- **Or**: Close main GUI window

### Image in preview is rotated/flipped
- **Normal**: Camera orientation
- **Note**: Capture will have same orientation
- **Solution**: Rotate camera physically if needed

## Performance Notes

### Network Usage
- Preview uses ~1-2 MB per frame
- Updates every 2 seconds
- ~30-60 MB per minute
- Ensure stable WiFi connection

### Raspberry Pi Load
- Preview is lightweight
- Uses quick capture mode
- Doesn't interfere with main captures
- Can run continuously

### Laptop Performance
- Preview uses minimal CPU
- Image display is efficient
- Threading prevents GUI freeze
- Safe to run for extended periods

## Advanced Usage

### Multiple Preview Sessions
- You can open/close preview multiple times
- Each session starts fresh
- No limit on preview duration
- Safe to leave open while capturing

### Preview + Capture
- Preview can stay open during capture
- Capture uses different settings
- No interference between them
- Useful for continuous positioning

### Preview for Different Categories
- Use preview for each category
- Check positioning for curve vs back
- Verify good vs bad bean arrangement
- Adjust lighting per category

## Keyboard Shortcuts

Currently no keyboard shortcuts, but you can:
- Click buttons with mouse
- Use Tab to navigate between buttons
- Use Enter to activate focused button
- Use Alt+F4 to close preview window

## Future Enhancements

Possible future features:
- Faster preview (1 second updates)
- Grid overlay for bean positioning
- Bean count detection in preview
- Zoom in/out controls
- Brightness adjustment in preview
- Snapshot button in preview
- Side-by-side comparison

## Summary

The live preview feature makes dataset collection much easier by:
- ✅ Showing exact camera view
- ✅ Helping position beans accurately
- ✅ Verifying lighting and focus
- ✅ Reducing bad captures
- ✅ Improving dataset quality
- ✅ Saving time on recaptures

Use it whenever you need to verify bean positioning!
