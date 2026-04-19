"""Run the full detection and tracking pipeline on a video file."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any, Dict, Optional

import cv2

from src.camera import CameraSource
from src.detector import ObjectDetector
from src.tracker import ObjectTracker
from src.utils import calculate_fps, load_config, log_message, setup_output_directory
from src.visualizer import Visualizer


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for video tracking mode."""
    parser = argparse.ArgumentParser(description="Run object tracking on a video file")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to YAML configuration file",
    )
    return parser.parse_args()


def create_video_writer(config: Dict[str, Any], width: int, height: int) -> cv2.VideoWriter:
    """Create a video writer using output settings from config."""
    setup_output_directory(config)
    output_path = str(config.get("output", {}).get("output_path", "output/tracked_output.mp4"))
    target_fps = float(config.get("camera", {}).get("fps_target", 30))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, target_fps, (int(width), int(height)))

    if not writer.isOpened():
        raise RuntimeError(
            "Failed to initialize output writer. See TROUBLESHOOTING.md (ISSUE 6)."
        )

    log_message("SUCCESS", f"Video output will be saved to {output_path}")
    return writer


def main() -> None:
    """Execute tracking on a file-based video source and save output."""
    args = parse_args()
    input_video = Path(args.video_path)

    camera: Optional[CameraSource] = None
    writer: Optional[cv2.VideoWriter] = None

    total_frames = 0
    fps_sum = 0.0
    prev_time = time.time()

    try:
        if not input_video.exists():
            raise RuntimeError(
                f"Input video does not exist: {input_video}. "
                "See TROUBLESHOOTING.md (ISSUE 1)."
            )

        config = load_config(args.config)
        config.setdefault("output", {})["save_video"] = True

        camera_config = config.get("camera", {})
        camera = CameraSource(
            source=str(input_video),
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

        writer = create_video_writer(config, width=width, height=height)

        log_message("SUCCESS", "Video pipeline started. Press Q or ESC to stop early.")

        while True:
            success, frame = camera.read()
            if not success:
                break

            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections, frame)

            fps, prev_time = calculate_fps(prev_time)
            total_frames += 1
            fps_sum += fps

            visualizer.set_runtime_metrics(fps=fps, total_unique_objects=tracker.get_total_unique_objects())
            annotated_frame = visualizer.draw(frame, tracked_objects)

            writer.write(annotated_frame)
            cv2.imshow("Tracking on Video", annotated_frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                log_message("INFO", "Early stop requested by user.")
                break

        average_fps = fps_sum / total_frames if total_frames else 0.0
        log_message("SUCCESS", f"Frames processed: {total_frames}")
        log_message("SUCCESS", f"Average FPS: {average_fps:.2f}")
        log_message("SUCCESS", "Video processing completed.")

    except Exception as exc:
        log_message("ERROR", f"run_on_video failed: {exc}")
        log_message("ERROR", "See TROUBLESHOOTING.md (ISSUE 1, ISSUE 4, ISSUE 5, ISSUE 6).")
    finally:
        if writer is not None:
            writer.release()
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
