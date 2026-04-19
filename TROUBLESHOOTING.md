# Troubleshooting Guide

## ISSUE 1: Cannot open camera / camera index 0 not working

### Cause

- VM webcam passthrough is not enabled
- Wrong camera index
- Device is already in use by another app

### Fix

- Enable webcam passthrough in VirtualBox or VMware
- Change `camera.source` in `configs/config.yaml` (try `1`, `2`, or video file path)
- Close apps using the camera and rerun
- Use video mode:
  ```bash
  python run_on_video.py /path/to/sample_video.mp4
  ```

## ISSUE 2: ModuleNotFoundError for ultralytics or cv2

### Cause

- Virtual environment is not activated
- Dependencies were not installed in the current environment

### Fix

```bash
source venv/bin/activate
pip install -r requirements.txt
```

If `venv` does not exist:

```bash
bash setup.sh
source venv/bin/activate
```

## ISSUE 3: Very low FPS (below 5)

### Cause

- Model is too heavy for VM CPU
- Input resolution is too high
- VM has limited resources

### Fix

- Use `models/yolov8n.pt`
- Reduce camera resolution in `configs/config.yaml` (for example 640x480)
- Close unnecessary apps in host and VM
- Lower `camera.fps_target`

## ISSUE 4: Model file not found

### Cause

- `models/yolov8n.pt` was not downloaded
- Incorrect model path in config

### Fix

```bash
bash download_models.sh
```

Or run the pipeline once after dependency install to trigger auto-download.

Then verify `detection.model_path` in `configs/config.yaml`.

## ISSUE 5: cv2.imshow not working in VM (no display)

### Cause

- GUI display not available in VM session
- DISPLAY variable not set

### Fix

```bash
export DISPLAY=:0
```

If GUI is still unavailable, run in headless style and save output only:

- Set `output.save_video: true`
- Process with `python run_on_video.py /path/to/video.mp4`

## ISSUE 6: ImportError or version conflict

### Cause

- Stale virtual environment
- Mixed system and virtualenv packages
- Incompatible package versions

### Fix

```bash
rm -rf venv
bash setup.sh
source venv/bin/activate
python --version
```

Ensure Python is 3.8+.

## ISSUE 7: Segmentation fault on startup

### Cause

- OpenCV binary conflict in VM environment

### Fix

```bash
source venv/bin/activate
pip uninstall -y opencv-python
pip install opencv-python-headless
```

If you switch to headless OpenCV, avoid GUI display and save output to files.

## ISSUE 8: Tracker producing duplicate IDs

### Cause

- Detections include unstable low-confidence boxes
- Frequent occlusion and re-entry events

### Fix

- Increase `detection.confidence_threshold` (for example from `0.4` to `0.55`)
- Keep tracker as `bytetrack` for CPU-friendly stability
- Improve camera angle and lighting where possible
