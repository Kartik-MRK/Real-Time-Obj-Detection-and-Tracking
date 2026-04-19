"""Run object detection on a single image and render demo annotations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import cv2

from src.detector import ObjectDetector
from src.utils import load_config, log_message, setup_output_directory
from src.visualizer import Visualizer


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for single-image inference mode."""
    parser = argparse.ArgumentParser(description="Run detection on one image")
    parser.add_argument("image_path", help="Path to input image file")
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save annotated image output",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output path for saved image",
    )
    return parser.parse_args()


def convert_detections_to_tracked_objects(detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert raw detections into visualizer-ready objects with synthetic track IDs."""
    tracked_objects: List[Dict[str, Any]] = []
    for index, detection in enumerate(detections, start=1):
        tracked = dict(detection)
        tracked["track_id"] = index
        tracked_objects.append(tracked)
    return tracked_objects


def determine_output_path(config: Dict[str, Any], cli_output_path: str) -> Path:
    """Resolve annotated image output path from CLI argument or config defaults."""
    if cli_output_path:
        return Path(cli_output_path)

    configured_video_path = Path(str(config.get("output", {}).get("output_path", "output/tracked_output.mp4")))
    default_name = f"{configured_video_path.stem}_image.jpg"
    return configured_video_path.with_name(default_name)


def main() -> None:
    """Load one image, run detection, draw annotations, display, and optionally save."""
    args = parse_args()
    input_image = Path(args.image_path)

    try:
        if not input_image.exists():
            raise RuntimeError(
                f"Input image not found: {input_image}. See TROUBLESHOOTING.md (ISSUE 1)."
            )

        config = load_config(args.config)
        frame = cv2.imread(str(input_image))
        if frame is None:
            raise RuntimeError(
                f"Unable to read image file: {input_image}. "
                "See TROUBLESHOOTING.md (ISSUE 6)."
            )

        detector = ObjectDetector(config)
        visualizer = Visualizer(config)

        detections = detector.detect(frame)
        tracked_objects = convert_detections_to_tracked_objects(detections)
        visualizer.set_runtime_metrics(fps=0.0, total_unique_objects=len(tracked_objects))

        annotated_frame = visualizer.draw(frame, tracked_objects)

        if args.save:
            output_path = determine_output_path(config, args.output)
            config.setdefault("output", {})["save_video"] = True
            config["output"]["output_path"] = str(output_path)
            setup_output_directory(config)
            cv2.imwrite(str(output_path), annotated_frame)
            log_message("SUCCESS", f"Annotated image saved to {output_path}")

        cv2.imshow("Detection on Image", annotated_frame)
        log_message("INFO", "Press any key to close the image window.")
        cv2.waitKey(0)

    except Exception as exc:
        log_message("ERROR", f"run_on_image failed: {exc}")
        log_message("ERROR", "See TROUBLESHOOTING.md (ISSUE 1, ISSUE 5, ISSUE 6).")
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
