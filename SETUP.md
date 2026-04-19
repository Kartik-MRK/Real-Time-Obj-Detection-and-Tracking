# Setup Guide

## System Requirements

- Ubuntu 22.04 (recommended for VM environment)
- Python 3.8+ (Python 3.10 recommended)
- Minimum 4 GB RAM (8 GB preferred for smoother display)
- Internet connection for first-time model download
- Webcam optional (video file mode is supported)

## Manual Setup (Without setup.sh)

1. Open a terminal in the project root.
2. Ensure setup scripts are executable:
   ```bash
   chmod +x setup.sh download_models.sh
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
5. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. Download model files:
   ```bash
   bash download_models.sh
   ```
8. Run the live pipeline:
   ```bash
   python main.py
   ```

## Activate Virtual Environment

```bash
source venv/bin/activate
```

## Verify Installation

Run the following checks:

```bash
python -c "from ultralytics import YOLO; print('ultralytics ok')"
python -c "import cv2; print('opencv ok')"
python -m pytest tests/
```

If all commands complete without errors, setup is successful.

## VM-Specific Notes

### VirtualBox Webcam Passthrough

1. Power off the VM.
2. Open VM Settings -> USB.
3. Enable USB Controller.
4. Add a USB filter for your webcam.
5. Start the VM and verify camera visibility:
   ```bash
   ls /dev/video*
   ```

### VMware Webcam Passthrough

1. Open VM settings while the VM is powered off.
2. Add USB Controller if missing.
3. Connect webcam from VM menu (Removable Devices -> webcam -> Connect).
4. Verify inside Ubuntu:
   ```bash
   ls /dev/video*
   ```

### If Webcam Passthrough Is Unavailable

Use video file mode instead:

```bash
python run_on_video.py /path/to/sample_video.mp4
```

You can also set `camera.source` in `configs/config.yaml` to a video file path.
