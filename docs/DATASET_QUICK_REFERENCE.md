# Dataset Collection - Quick Reference

## Setup (One-time)

```bash
# 1. Deploy code to Pi
python scripts/deploy_to_pi.py

# 2. SSH to Pi
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197

# 3. Setup OpenCV
cd ~/coffee-sorter
./scripts/setup_dataset_collection.sh
```

## Daily Workflow

### 1. Prepare Physical Setup
- [ ] Clean white background
- [ ] Set up consistent lighting
- [ ] Prepare beans (sorted by quality and side)

### 2. Test Detection (First time each day)
```bash
# Arrange 240 test beans on grid
python3 scripts/test_opencv_detection.py

# Check results in ~/test_results/
# Adjust parameters if needed
```

### 3. Start Collection
```bash
python3 src/ml/dataset_collector.py
```

### 4. For Each Batch
1. Select category (good/bad, curve/back)
2. Arrange 240 beans on grid
3. Click "CAPTURE & PROCESS"
4. Wait for processing (~10-30 seconds)
5. Verify count in GUI
6. Repeat

## Target Progress

| Category | Target | Batches |
|----------|--------|---------|
| Good Curve | 1,050 | 5 batches (4×240 + 1×90) |
| Good Back | 450 | 2 batches (1×240 + 1×210) |
| Bad Curve | 1,050 | 5 batches (4×240 + 1×90) |
| Bad Back | 450 | 2 batches (1×240 + 1×210) |
| **TOTAL** | **3,000** | **~13 batches** |

## Tips

### Bean Arrangement
- Use 16×15 grid template
- 1-2cm spacing between beans
- All beans same orientation
- No overlapping

### Lighting
- Diffused LED panel above
- No direct sunlight
- Consistent brightness
- Avoid shadows

### Quality Check
After each batch:
```bash
# Count images
ls ~/coffee_dataset/good_beans/curve/ | wc -l

# View samples
eog ~/coffee_dataset/good_beans/curve/good_curve_*.jpg
```

## Troubleshooting

### Low Detection (<200 beans)
- Improve lighting
- Increase contrast
- Check bean spacing
- Lower `min_area` parameter

### Too Many Detections (>250)
- Clean background
- Increase `min_area` parameter
- Better lighting
- Remove artifacts

### GUI Won't Start
```bash
# Check X11 forwarding
ssh -X -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197

# Or use VNC
```

## Backup

```bash
# Compress dataset
cd ~
tar -czf coffee_dataset_$(date +%Y%m%d).tar.gz coffee_dataset/

# Copy to PC
scp coffee_dataset_*.tar.gz user@pc:/backup/
```

## File Locations

- Dataset: `~/coffee_dataset/`
- Temp captures: `~/temp_captures/`
- Test results: `~/test_results/`
- Progress file: `~/dataset_counts.json`

## Commands Cheat Sheet

```bash
# Deploy from PC
python scripts/deploy_to_pi.py

# SSH to Pi
ssh -i ~/.ssh/id_ed25519_rpi beans@192.168.100.197

# Test detection
python3 scripts/test_opencv_detection.py

# Launch GUI
python3 src/ml/dataset_collector.py

# Check progress
cat ~/dataset_counts.json

# Count images
find ~/coffee_dataset -name "*.jpg" | wc -l

# Backup dataset
tar -czf dataset_backup.tar.gz ~/coffee_dataset/
```
