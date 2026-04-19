# Demo Guide

## 1. Run Live Webcam Demo

```bash
source venv/bin/activate
python main.py
```

- Press `Q` or `ESC` to exit.
- This uses `camera.source` from `configs/config.yaml`.

## 2. Run on a Sample Video File

```bash
source venv/bin/activate
python run_on_video.py /path/to/sample_video.mp4
```

- Output video is saved to `output.output_path` from `configs/config.yaml`.
- Press `Q` or `ESC` to stop early.

## 3. Run on a Single Image

```bash
source venv/bin/activate
python run_on_image.py /path/to/sample_image.jpg --save
```

- Displays annotated image.
- `--save` writes the output image.
- Optional custom output path:
  ```bash
  python run_on_image.py /path/to/sample_image.jpg --save --output output/custom_result.jpg
  ```

## 4. Change YOLO Model (Speed vs Accuracy)

Edit `configs/config.yaml`:

```yaml
detection:
  model_path: models/yolov8s.pt
```

- `yolov8n.pt`: fastest on CPU (recommended for VM)
- `yolov8s.pt`: better accuracy with lower FPS

## 5. Filter Detection to Specific Classes

Edit `configs/config.yaml` and set `classes_to_track`.

Example: only persons and cars using COCO IDs (`person=0`, `car=2`):

```yaml
detection:
  classes_to_track: [0, 2]
```

You can also use names if preferred:

```yaml
detection:
  classes_to_track: [person, car]
```

## 6. Save Output Video

Enable output saving in `configs/config.yaml`:

```yaml
output:
  save_video: true
  output_path: output/tracked_output.mp4
```

Then run:

```bash
python main.py
```

## 7. Expected Output on Screen

You will see:

- Bounding boxes around detected objects
- Track IDs that persist across frames
- Class labels and confidence values
- Top-left transparent overlay with FPS and object counts
- Console logs with `[INFO]`, `[SUCCESS]`, `[ERROR]` status tags

## 8. VM Performance Tips

- Keep default model as `yolov8n.pt`
- Reduce resolution in `configs/config.yaml` (for example 640x480)
- Reduce target FPS if CPU is saturated
- Close unused applications in the VM
- Prefer video-file demo when webcam passthrough is unstable

## 9. Optional ROS2 Integration Path (Future Extension)

This project is standalone by design, but can be extended to ROS2:

- Use a ROS2 node to subscribe to `/camera/image_raw`
- Convert ROS image messages to OpenCV frames
- Feed frames into `ObjectDetector`, `ObjectTracker`, and `Visualizer`
- Publish annotated frames to a new topic (for example `/tracking/image_annotated`)

This keeps the current modular structure unchanged while allowing ROS-based demos.
