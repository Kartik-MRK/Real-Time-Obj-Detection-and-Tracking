"""Visualization helpers using supervision annotators for demo-ready overlays."""

from __future__ import annotations

from typing import Any, Dict, List

import cv2
import numpy as np
import supervision as sv

from src.utils import log_message


class Visualizer:
    """Draw tracked boxes, labels, traces, and runtime statistics on frames."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize drawing options and supervision annotators from config."""
        display_config = config.get("display", {})
        self.show_fps = bool(display_config.get("show_fps", True))
        self.show_labels = bool(display_config.get("show_labels", True))
        self.show_confidence = bool(display_config.get("show_confidence", True))
        self.show_track_id = bool(display_config.get("show_track_id", True))
        self.bbox_thickness = int(display_config.get("bbox_thickness", 2))

        box_annotator_class = self._resolve_supervision_class(
            ["BoundingBoxAnnotator", "BoxAnnotator"]
        )
        label_annotator_class = self._resolve_supervision_class(["LabelAnnotator"])
        trace_annotator_class = self._resolve_supervision_class(["TraceAnnotator"])

        if box_annotator_class is None:
            raise RuntimeError(
                "No compatible bounding box annotator found in supervision package. "
                "Install/upgrade with: pip install -U supervision"
            )

        self.box_annotator = box_annotator_class(thickness=self.bbox_thickness)
        self.label_annotator = (
            label_annotator_class(
                text_scale=0.5,
                text_thickness=1,
                text_padding=6,
            )
            if label_annotator_class is not None
            else None
        )
        self.trace_annotator = (
            trace_annotator_class(thickness=max(1, self.bbox_thickness - 1))
            if trace_annotator_class is not None
            else None
        )

        if self.label_annotator is None:
            log_message(
                "INFO",
                "LabelAnnotator not available in installed supervision version. "
                "Continuing without label-annotator pass.",
            )

        if self.trace_annotator is None:
            log_message(
                "INFO",
                "TraceAnnotator not available in installed supervision version. "
                "Continuing without trajectory traces.",
            )

        self.current_fps = 0.0
        self.current_total_unique = 0

    @staticmethod
    def _resolve_supervision_class(class_names: List[str]) -> Any:
        """Return the first matching supervision class from a list of class names."""
        for class_name in class_names:
            resolved = getattr(sv, class_name, None)
            if resolved is not None:
                return resolved
        return None

    def set_runtime_metrics(self, fps: float, total_unique_objects: int) -> None:
        """Update runtime metrics shown in the top-left overlay."""
        self.current_fps = float(fps)
        self.current_total_unique = int(total_unique_objects)

    def draw(self, frame: Any, tracked_objects: List[Dict[str, Any]]) -> Any:
        """Return a frame annotated with tracks, labels, confidence, and stats."""
        annotated = frame.copy()

        if tracked_objects:
            try:
                detections = self._build_supervision_detections(tracked_objects)
                if self.trace_annotator is not None:
                    annotated = self.trace_annotator.annotate(scene=annotated, detections=detections)
                annotated = self.box_annotator.annotate(scene=annotated, detections=detections)
                labels = self._build_labels(tracked_objects)
                if self.label_annotator is not None:
                    annotated = self.label_annotator.annotate(
                        scene=annotated,
                        detections=detections,
                        labels=labels,
                    )
            except Exception as exc:
                log_message("ERROR", f"Visualizer annotation failed: {exc}")

        self._draw_status_overlay(annotated, len(tracked_objects))
        return annotated

    def _build_supervision_detections(self, tracked_objects: List[Dict[str, Any]]) -> sv.Detections:
        """Convert normalized tracked objects into a supervision Detections object."""
        xyxy = np.array([obj["bbox"] for obj in tracked_objects], dtype=np.float32)
        confidence = np.array([obj["confidence"] for obj in tracked_objects], dtype=np.float32)
        class_id = np.array([obj["class_id"] for obj in tracked_objects], dtype=np.int32)
        tracker_id = np.array([obj.get("track_id", -1) for obj in tracked_objects], dtype=np.int32)

        try:
            return sv.Detections(
                xyxy=xyxy,
                confidence=confidence,
                class_id=class_id,
                tracker_id=tracker_id,
            )
        except TypeError:
            # Some supervision versions do not support tracker_id in the constructor.
            return sv.Detections(
                xyxy=xyxy,
                confidence=confidence,
                class_id=class_id,
            )

    def _build_labels(self, tracked_objects: List[Dict[str, Any]]) -> List[str]:
        """Compose display labels according to config flags for each tracked object."""
        labels: List[str] = []
        for obj in tracked_objects:
            parts: List[str] = []
            track_id = int(obj.get("track_id", -1))

            if self.show_track_id and track_id >= 0:
                parts.append(f"ID {track_id}")
            if self.show_labels:
                parts.append(str(obj.get("class_name", "object")))
            if self.show_confidence:
                parts.append(f"{float(obj.get('confidence', 0.0)):.2f}")

            if not parts:
                parts.append("object")

            labels.append(" | ".join(parts))

        return labels

    def _draw_status_overlay(self, frame: Any, object_count: int) -> None:
        """Draw a semi-transparent panel with FPS and object totals in top-left corner."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (360, 110), (0, 0, 0), thickness=-1)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0.0, frame)

        fps_text = f"FPS: {self.current_fps:.2f}" if self.show_fps else "FPS: hidden"
        frame_count_text = f"Objects (frame): {object_count}"
        unique_count_text = f"Objects (unique): {self.current_total_unique}"

        cv2.putText(frame, fps_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        cv2.putText(
            frame,
            frame_count_text,
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            unique_count_text,
            (20, 98),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
