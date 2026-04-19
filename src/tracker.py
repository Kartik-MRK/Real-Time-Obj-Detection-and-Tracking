"""Object tracking wrapper based on Ultralytics ByteTrack/BoT-SORT."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

import numpy as np

from src.utils import log_message


class ObjectTracker:
    """Track objects across frames and maintain per-class unique counts."""

    def __init__(self, config: Dict[str, Any], detector: Any) -> None:
        """Initialize tracker settings and bind to the detector model."""
        detection_config = config.get("detection", {})
        tracking_config = config.get("tracking", {})

        self.model = detector.model
        self.device = detector.device
        self.class_filter_ids = detector.class_filter_ids
        self.confidence_threshold = float(detection_config.get("confidence_threshold", 0.4))
        self.iou_threshold = float(detection_config.get("iou_threshold", 0.45))

        tracker_name = str(tracking_config.get("tracker", "bytetrack")).strip().lower()
        tracker_map = {
            "bytetrack": "bytetrack.yaml",
            "botsort": "botsort.yaml",
        }

        if tracker_name not in tracker_map:
            log_message("INFO", f"Unknown tracker '{tracker_name}', using bytetrack.")
            tracker_name = "bytetrack"

        self.tracker_name = tracker_name
        self.tracker_config_file = tracker_map[tracker_name]
        self.max_disappeared = int(tracking_config.get("max_disappeared", 30))

        # max_disappeared is kept for compatibility with config-driven behavior.
        self.unique_ids_by_class: Dict[str, set[int]] = defaultdict(set)

        log_message(
            "SUCCESS",
            f"Tracker initialized with tracker={self.tracker_name}, device={self.device}",
        )

    def update(self, detections: List[Dict[str, Any]], frame: Any) -> List[Dict[str, Any]]:
        """Update tracking state for a frame and return objects with persistent IDs."""
        try:
            results = self.model.track(
                source=frame,
                persist=True,
                tracker=self.tracker_config_file,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                classes=self.class_filter_ids,
                device=self.device,
                verbose=False,
            )
            tracked_objects = self._parse_track_results(results)
            if tracked_objects:
                return tracked_objects

            return self._fallback_from_detections(detections)
        except Exception as exc:
            log_message("ERROR", f"Tracking failed: {exc}")
            return self._fallback_from_detections(detections)

    def _parse_track_results(self, results: Any) -> List[Dict[str, Any]]:
        """Convert Ultralytics tracking output into normalized object dictionaries."""
        tracked_objects: List[Dict[str, Any]] = []
        if not results:
            return tracked_objects

        result = results[0]
        if result.boxes is None:
            return tracked_objects

        names = result.names if isinstance(result.names, dict) else dict(enumerate(result.names))
        boxes = result.boxes

        xyxy = boxes.xyxy.cpu().numpy()
        confidences = boxes.conf.cpu().numpy()
        class_ids = boxes.cls.cpu().numpy().astype(int)

        if boxes.id is not None:
            track_ids = boxes.id.cpu().numpy().astype(int)
        else:
            track_ids = np.full(shape=(len(xyxy),), fill_value=-1, dtype=int)

        for index in range(len(xyxy)):
            class_id = int(class_ids[index])
            class_name = str(names.get(class_id, str(class_id)))
            x1, y1, x2, y2 = [float(value) for value in xyxy[index]]
            confidence = float(confidences[index])
            track_id = int(track_ids[index])

            tracked_object = {
                "bbox": [x1, y1, x2, y2],
                "confidence": confidence,
                "class_id": class_id,
                "class_name": class_name,
                "track_id": track_id,
            }
            tracked_objects.append(tracked_object)

            if track_id >= 0:
                self.unique_ids_by_class[class_name].add(track_id)

        return tracked_objects

    def _fallback_from_detections(
        self, detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fallback path when tracker output is unavailable; keeps pipeline alive."""
        fallback_objects: List[Dict[str, Any]] = []
        for index, detection in enumerate(detections):
            fallback = dict(detection)
            fallback["track_id"] = -1 * (index + 1)
            fallback_objects.append(fallback)
        return fallback_objects

    def get_unique_object_counts(self) -> Dict[str, int]:
        """Return the number of unique tracked IDs observed for each class."""
        return {
            class_name: len(track_ids)
            for class_name, track_ids in sorted(self.unique_ids_by_class.items())
        }

    def get_total_unique_objects(self) -> int:
        """Return total number of unique tracked objects across all classes."""
        return sum(len(track_ids) for track_ids in self.unique_ids_by_class.values())
