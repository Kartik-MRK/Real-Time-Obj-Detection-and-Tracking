# Real-Time Object Detection and Tracking

A VM-friendly, end-to-end YOLOv8 + ByteTrack/BoT-SORT pipeline for live object detection and tracking.

## Features

- Real-time object detection using Ultralytics YOLOv8
- Multi-object tracking with persistent IDs (ByteTrack or BoT-SORT)
- Live FPS and object statistics overlay
- Fully config-driven behavior via `configs/config.yaml`
- CPU-friendly defaults for Ubuntu 22.04 virtual machines
- Modular architecture for easy extension and maintenance

## Quick Start

```bash
cd real_time_object_tracking
bash setup.sh
source venv/bin/activate && python main.py
```

## Project Structure

```text
real_time_object_tracking/
├── README.md
├── SETUP.md
├── TROUBLESHOOTING.md
├── DEMO.md
├── requirements.txt
├── setup.sh
├── download_models.sh
├── configs/
│   └── config.yaml
├── src/
│   ├── detector.py
│   ├── tracker.py
│   ├── visualizer.py
│   ├── camera.py
│   └── utils.py
├── main.py
├── run_on_video.py
├── run_on_image.py
├── tests/
│   └── test_pipeline.py
└── assets/
    └── sample_video_instructions.txt
```

## Screenshot Placeholder

Add your demo screenshots here after running the project:

- `assets/screenshots/live_webcam_demo.png`
- `assets/screenshots/video_tracking_demo.png`
- `assets/screenshots/image_detection_demo.png`

## Documentation

- Setup Guide: [SETUP.md](SETUP.md)
- Demo Guide: [DEMO.md](DEMO.md)
- Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Full Architecture Guide: [PROJECT_ARCHITECTURE_GUIDE.md](PROJECT_ARCHITECTURE_GUIDE.md)
