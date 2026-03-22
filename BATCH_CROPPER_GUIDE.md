# Batch Bean Cropper Guide

Simple command-line tool to crop multiple coffee beans from images to 224x224 pixels.

## Quick Start

```bash
python scripts/crop_beans_batch.py <input_directory> <output_directory>
```

Example:
```bash
py -3.12 scripts/crop_beans_batch.py ./raw_images/bad/ ./cropped_images/bad/

py -3.12 scripts/crop_beans_batch.py ./raw_images/bad/curve ./cropped_images/bad/curve

py -3.12 scripts/crop_beans_batch.py ./raw_images/good ./cropped_images/good

py -3.12 scripts/crop_beans_batch.py ./raw_images/good/curve ./cropped_images/good/curve

```

## What It Does

- Detects all beans in each image
- Crops each bean to 224x224 (preserves aspect ratio with white padding)
- Saves with incremental names: `bean_000000.jpg`, `bean_000001.jpg`, etc.
- Logs processed files to avoid duplicates
- Can resume if interrupted

## Usage Examples

### Basic Usage
```bash
python scripts/crop_beans_batch.py ./my_photos ./cropped_beans
```

### Process iPhone Photos
```bash
python scripts/crop_beans_batch.py ./iphone_captures ./dataset_good
```

Note: iPhone HEIC files are automatically supported. Make sure pillow-heif is installed.

### Continue Previous Run
Just run the same command again - it will skip already processed images:
```bash
python scripts/crop_beans_batch.py ./raw_images ./dataset_224
```

## Output Structure

```
output_directory/
├── bean_000000.jpg    # First bean (224x224)
├── bean_000001.jpg    # Second bean (224x224)
├── bean_000002.jpg    # Third bean (224x224)
├── ...
└── processing_log.json # Tracking file
```

## Processing Log

The script creates `processing_log.json` in the output directory:

```json
{
  "processed_files": ["image1.jpg", "image2.jpg"],
  "total_beans": 150,
  "last_index": 150
}
```

This ensures:
- No duplicate processing
- Resume capability
- Continuous incremental naming

## Tips for Best Results

### Image Preparation
- Use white background (poster board)
- Even lighting, no shadows
- Space beans 5-10mm apart
- 100 beans per image works well

### Detection Settings
Default settings work for most cases:
- Min bean area: 800 pixels
- Max bean area: 20,000 pixels
- Target image: 4608x2592 (iPhone 12 Pro)

### If Detection is Poor
Check your images:
- Background contrast too low
- Beans touching each other
- Shadows or uneven lighting
- Dirty background

## Output Format

Each cropped bean:
- Size: 224x224 pixels
- Format: JPEG (95% quality)
- Aspect ratio: Preserved (centered with white padding)
- Background: White

## Command-Line Help

```bash
python scripts/crop_beans_batch.py --help
```

## Workflow

1. Capture images with 100 beans each
2. Put all images in one directory
3. Run the cropper script
4. Check output directory
5. Manually remove bad crops
6. Run report to see final counts
7. Add more images and run again (continues numbering)

## Dataset Report

After manually removing bad crops, check your dataset:

```bash
python scripts/report_dataset.py ./cropped_images/bad
```

This shows:
- Images processed vs actual count
- How many images were manually removed
- Quality control metrics
- File statistics
- Dataset readiness for training

## Example Session

```bash
$ python scripts/crop_beans_batch.py ./photos ./dataset

Found 3 images in ./photos
Output directory: ./dataset
Starting from index: 0
------------------------------------------------------------

[PROCESSING] IMG_0001.jpg
  Image size: 4608x2592
  Detected: 98 beans
  Saved: 98 beans (bean_000000 to bean_000097)

[PROCESSING] IMG_0002.jpg
  Image size: 4608x2592
  Detected: 102 beans
  Saved: 102 beans (bean_000098 to bean_000199)

[PROCESSING] IMG_0003.jpg
  Image size: 4608x2592
  Detected: 95 beans
  Saved: 95 beans (bean_000200 to bean_000294)

============================================================
BATCH PROCESSING COMPLETE
============================================================
Images processed: 3
Total beans cropped: 295
Beans in this run: 295
Output directory: ./dataset
Log file: ./dataset/processing_log.json
------------------------------------------------------------
ACTUAL IMAGE COUNT IN FOLDER
------------------------------------------------------------
Images in folder: 280
Expected (from log): 295
Manually removed: 15 images (5.1%)
Remaining: 280 images
============================================================
```

After manually cleaning up bad crops, run the report:

```bash
$ python scripts/report_dataset.py ./dataset

======================================================================
DATASET REPORT
======================================================================
Directory: ./dataset
Log file: ./dataset/processing_log.json

----------------------------------------------------------------------
PROCESSING HISTORY
----------------------------------------------------------------------
Source images processed: 3
Total beans cropped: 295
Last index used: 295

----------------------------------------------------------------------
CURRENT STATE
----------------------------------------------------------------------
Images in folder: 280
Expected (from log): 295

Status: 15 images manually removed (5.1%)
Remaining: 280 images (94.9%)

Quality Control:
  ✓ Excellent - Very few bad crops (<5%)

----------------------------------------------------------------------
FILE STATISTICS
----------------------------------------------------------------------
Total size: 12.45 MB
Average file size: 45.52 KB
Smallest file: 38.21 KB
Largest file: 62.18 KB

======================================================================
SUMMARY
======================================================================
Dataset ready: 280 images
⚠ Minimal dataset (200-500 images) - more data recommended
======================================================================
```

## Troubleshooting

### HEIC files not working
Install HEIC support:
```bash
pip install pillow-heif
```

### No beans detected
- Check image quality
- Verify background contrast
- Ensure beans are visible

### Too many/few beans detected
- Adjust lighting
- Clean background
- Check bean spacing

### Script crashes
- Check disk space
- Verify image files are valid
- Ensure output directory is writable

## Requirements

- Python 3.6+
- OpenCV (cv2)
- NumPy
- Pillow & pillow-heif (for HEIC support)

Install dependencies:
```bash
pip install opencv-python numpy pillow pillow-heif
```

Or use the project requirements:
```bash
pip install -r requirements.txt
```

## Supported Formats

- HEIC (iPhone photos)
- JPG/JPEG
- PNG
- BMP

The script automatically detects and handles HEIC files from iPhone.
