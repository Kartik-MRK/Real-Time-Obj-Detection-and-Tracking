"""YOLOv8-based object detector module with config-driven inference settings."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ultralytics import YOLO

from src.utils import get_device, log_message


class ObjectDetector:
    """Load and run YOLO detections on incoming frames."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize YOLO model and detection thresholds from configuration."""
        detection_config = config.get("detection", {})
        self.model_path = str(detection_config.get("model_path", "models/yolov8n.pt"))
        self.confidence_threshold = float(detection_config.get("confidence_threshold", 0.4))
        self.iou_threshold = float(detection_config.get("iou_threshold", 0.45))
        self.device = get_device(str(detection_config.get("device", "auto")))

        try:
            self.model = YOLO(self.model_path)
            self.class_filter_ids = self._resolve_classes(
                detection_config.get("classes_to_track", [])
            )
            log_message(
                "SUCCESS",
                f"Detector initialized with model={self.model_path}, device={self.device}",
            )
        except Exception as exc:
            log_message("ERROR", f"Failed to initialize YOLO model: {exc}")
            raise RuntimeError(
                "Detector initialization failed. See TROUBLESHOOTING.md (ISSUE 4, ISSUE 6)."
            ) from exc

    def _resolve_classes(self, classes_to_track: Any) -> Optional[List[int]]:
        """Resolve class filters from names or IDs to integer class IDs."""
        if not classes_to_track:
            return None

        model_names = self.model.names
        if isinstance(model_names, dict):
            id_to_name = {int(class_id): str(name) for class_id, name in model_names.items()}
        else:
            id_to_name = {idx: str(name) for idx, name in enumerate(model_names)}

        name_to_id = {name.lower(): class_id for class_id, name in id_to_name.items()}
        resolved_ids: List[int] = []

        for class_item in classes_to_track:
            if isinstance(class_item, int):
                resolved_ids.append(class_item)
                continue

            if isinstance(class_item, str):
                cleaned = class_item.strip().lower()
                if cleaned.isdigit():
                    resolved_ids.append(int(cleaned))
                elif cleaned in name_to_id:
                    resolved_ids.append(name_to_id[cleaned])
                else:
                    log_message("INFO", f"Unknown class filter ignored: {class_item}")

        unique_ids = sorted(set(resolved_ids))
        return unique_ids or None

    def detect(self, frame: Any) -> List[Dict[str, Any]]:
        """Run detection on a frame and return normalized detection dictionaries."""
        try:
            results = self.model.predict(
                source=frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                classes=self.class_filter_ids,
                device=self.device,
                verbose=False,
            )

            if not results:
                return []

            result = results[0]
            if result.boxes is None:
                return []

            names = result.names if isinstance(result.names, dict) else dict(enumerate(result.names))
            boxes = result.boxes

            xyxy = boxes.xyxy.cpu().numpy()
            confidences = boxes.conf.cpu().numpy()
            class_ids = boxes.cls.cpu().numpy().astype(int)

            detections: List[Dict[str, Any]] = []
            for index in range(len(xyxy)):
                class_id = int(class_ids[index])
                class_name = str(names.get(class_id, str(class_id)))
                x1, y1, x2, y2 = [float(value) for value in xyxy[index]]
                confidence = float(confidences[index])

                detections.append(
                    {
                        "bbox": [x1, y1, x2, y2],
                        "confidence": confidence,
                        "class_id": class_id,
                        "class_name": class_name,
                    }
                )

            return detections
        except Exception as exc:
            log_message("ERROR", f"Detection failed: {exc}")
            return []
