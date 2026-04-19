"""Main entry point for real-time object detection and tracking."""

from __future__ import annotations

import argparse
import time
from typing import Any, Dict, Optional

import cv2

from src.camera import CameraSource
from src.detector import ObjectDetector
from src.tracker import ObjectTracker
from src.utils import calculate_fps, load_config, log_message, setup_output_directory
from src.visualizer import Visualizer


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the live tracking application."""
    parser = argparse.ArgumentParser(description="Real-time object detection and tracking")
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to YAML configuration file.",
    )
    return parser.parse_args()


def create_video_writer(config: Dict[str, Any], width: int, height: int) -> Optional[cv2.VideoWriter]:
    """Create and return an OpenCV video writer when output saving is enabled."""
    output_config = config.get("output", {})
    if not bool(output_config.get("save_video", False)):
        return None

    setup_output_directory(config)
    output_path = str(output_config.get("output_path", "output/tracked_output.mp4"))
    target_fps = float(config.get("camera", {}).get("fps_target", 30))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, target_fps, (int(width), int(height)))

    if not writer.isOpened():
        raise RuntimeError(
            "Failed to initialize video writer. See TROUBLESHOOTING.md (ISSUE 6)."
        )

    log_message("SUCCESS", f"Saving output video to {output_path}")
    return writer


def main() -> None:
    """Run the detection-tracking-visualization loop until user exits."""
    args = parse_args()

    camera: Optional[CameraSource] = None
    writer: Optional[cv2.VideoWriter] = None

    total_frames = 0
    fps_sum = 0.0
    prev_time = time.time()

    try:
        config = load_config(args.config)

        camera_config = config.get("camera", {})
        camera = CameraSource(
            source=camera_config.get("source", 0),
            width=int(camera_config.get("width", 1280)),
            height=int(camera_config.get("height", 720)),
            fps_target=int(camera_config.get("fps_target", 30)),
        )
        detector = ObjectDetector(config)
        tracker = ObjectTracker(config, detector)
        visualizer = Visualizer(config)

        width = int(camera.capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or int(
            camera_config.get("width", 1280)
        )
        height = int(camera.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or int(
            camera_config.get("height", 720)
        )
        writer = create_video_writer(config, width, height)

        log_message("SUCCESS", "Pipeline initialized. Press Q or ESC to exit.")

        while True:
            success, frame = camera.read()
            if not success:
                log_message("INFO", "No more frames available. Stopping pipeline.")
                break

            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections, frame)

            fps, prev_time = calculate_fps(prev_time)
            total_frames += 1
            fps_sum += fps

            visualizer.set_runtime_metrics(fps=fps, total_unique_objects=tracker.get_total_unique_objects())
            annotated_frame = visualizer.draw(frame, tracked_objects)

            if writer is not None:
                writer.write(annotated_frame)

            cv2.imshow("Real-Time Object Detection and Tracking", annotated_frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                log_message("INFO", "Exit key pressed. Shutting down pipeline.")
                break

        average_fps = fps_sum / total_frames if total_frames else 0.0
        log_message("SUCCESS", f"Total frames processed: {total_frames}")
        log_message("SUCCESS", f"Average FPS: {average_fps:.2f}")

        unique_counts = tracker.get_unique_object_counts()
        if unique_counts:
            for class_name, class_count in unique_counts.items():
                log_message("INFO", f"Unique objects detected - {class_name}: {class_count}")
        else:
            log_message("INFO", "No uniquely tracked objects were recorded.")

    except Exception as exc:
        log_message("ERROR", f"Pipeline failed: {exc}")
        log_message(
            "ERROR",
            "See TROUBLESHOOTING.md for fixes (ISSUE 1, ISSUE 4, ISSUE 5, ISSUE 6).",
        )
    finally:
        if writer is not None:
            writer.release()
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
