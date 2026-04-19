# Team Presentation Script: High-Level Codebase Walkthrough

## Total Duration
- Recommended: 10 to 12 minutes
- 4 speakers, approximately 2 to 3 minutes each

## Presentation Goal
Explain the whole codebase at a high level, covering:
- What the system does
- How the architecture is organized
- What each key file is responsible for
- How the system runs in real scenarios
- Why design choices make it robust for demo and evaluation

---

## Speaker 1 Script: System Flow, Core Wiring, and Configuration
### Files Covered
- main.py
- src/camera.py
- src/utils.py
- configs/config.yaml

### What to Say
Hello everyone. I will explain the project flow and the core orchestration.

This project is a real-time object detection and tracking pipeline. At the highest level, each frame follows one fixed path: read frame, detect objects, track IDs, visualize results, then display or save output.

The orchestration happens in main.py. It loads configuration, initializes the camera source, detector, tracker, and visualizer, and then runs the main frame loop.

The camera input abstraction is in src/camera.py. This file handles either webcam index or video path and provides consistent frame reading behavior.

Utility behaviors are centralized in src/utils.py. This includes configuration loading, device selection logic for CUDA or CPU fallback, FPS calculation, output directory setup, and standardized logging.

All runtime behavior is configuration-driven from configs/config.yaml. That file controls model path, thresholds, tracker selection, camera source, display options, and output settings.

The architectural advantage is maintainability and quick tuning. Instead of editing code for every demo change, we can update config values.

### Handoff Line
Now that the pipeline orchestration is clear, the next part covers how detection works and why the model setup is chosen.

---

## Speaker 2 Script: Detection Engine and Inference Design
### Files Covered
- src/detector.py
- download_models.sh
- requirements.txt

### What to Say
I will explain the detection layer.

Object detection is implemented in src/detector.py using Ultralytics YOLO. The detector class loads the model path from config and runs frame inference with configurable confidence and IOU thresholds.

The detector also supports class filtering. That means we can detect all classes, or only specific ones such as person and car, based on config values.

A key design point is device flexibility. The detector uses utility logic to select CUDA when available and otherwise safely fall back to CPU. This is important for virtual machine demos where GPU may not be available.

Model setup is automated through download_models.sh. It creates the models folder, downloads yolov8n as default and optionally yolov8s, verifies files, and prints guidance for switching models in config.

Dependency boundaries are defined in requirements.txt, ensuring the same package ecosystem across environments.

### Handoff Line
With detection completed per frame, the next layer is tracking identity over time and rendering the final annotated output.

---

## Speaker 3 Script: Tracking Logic and Visualization Layer
### Files Covered
- src/tracker.py
- src/visualizer.py

### What to Say
I will explain tracking and visualization.

Detection tells us what is in one frame, but tracking tells us whether an object in this frame is the same object from previous frames. That is implemented in src/tracker.py.

The tracker supports ByteTrack and BoT-SORT through config selection. For each frame, it produces tracked objects with persistent track IDs. It also maintains unique object counts per class using track ID sets.

If tracking fails in a frame, the system uses a fallback from detections so the pipeline keeps running instead of crashing.

Rendering is handled by src/visualizer.py using annotation components. It draws bounding boxes, labels, confidence scores, and trace history. It also draws a semi-transparent status panel in the top-left with FPS and object counts.

The result is a demo-friendly view that is easy to interpret during live presentation.

### Handoff Line
Now I will hand over to the final part, which explains execution modes, setup automation, testing, and operational reliability.

---

## Speaker 4 Script: Execution Modes, Setup, Testing, and Documentation
### Files Covered
- run_on_video.py
- run_on_image.py
- setup.sh
- tests/test_pipeline.py
- README.md
- SETUP.md
- DEMO.md
- TROUBLESHOOTING.md
- PROJECT_ARCHITECTURE_GUIDE.md

### What to Say
I will explain how the project is run and how reliability is handled.

The codebase supports three execution modes: live pipeline through main.py, batch video processing through run_on_video.py, and single-image mode through run_on_image.py. This gives flexibility for webcam demos, recorded demos, and quick static checks.

Environment setup is automated with setup.sh, which checks Python version, creates virtual environment, installs requirements, and triggers model download.

Quality checks are in tests/test_pipeline.py. The tests validate config loading, detector initialization, dummy-frame detection, and visualizer output behavior.

Operational guidance is fully documented: README for overview, SETUP for installation, DEMO for usage scenarios, TROUBLESHOOTING for common failures, and PROJECT_ARCHITECTURE_GUIDE for deep technical explanation.

This combination of modular code and strong documentation makes the project presentation-ready and reproducible.

### Closing Line
That completes the high-level walkthrough of the full codebase.

---

## Optional 30-Second Team Summary (If Asked at the End)
This project is a modular, config-driven real-time detection and tracking system. It separates camera input, detection, tracking, visualization, and runtime orchestration into clean components. It is designed to be robust on Ubuntu virtual machines with CPU fallback, automated setup, and clear documentation, making it reliable for both technical evaluation and live demonstration.

---

## Rapid Q and A Roles
- System flow and config questions: Speaker 1
- Model and inference questions: Speaker 2
- Tracking and overlay questions: Speaker 3
- Setup, testing, and deployment questions: Speaker 4
