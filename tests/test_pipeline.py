"""Smoke tests for configuration, detector, and visualization pipeline components."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.detector import ObjectDetector
from src.utils import load_config
from src.visualizer import Visualizer


class FakeTensor:
    """Lightweight tensor stub matching the API used by detector/tracker parsing."""

    def __init__(self, values):
        """Store tensor-like values as a numpy array."""
        self._values = np.array(values)

    def cpu(self):
        """Return self to mimic torch tensor CPU transfer."""
        return self

    def numpy(self):
        """Return the underlying numpy values."""
        return self._values


class FakeBoxes:
    """Mock YOLO boxes output containing one detection with one track ID."""

    def __init__(self):
        """Initialize fake detection tensors."""
        self.xyxy = FakeTensor([[10.0, 20.0, 110.0, 180.0]])
        self.conf = FakeTensor([0.95])
        self.cls = FakeTensor([0])
        self.id = FakeTensor([1])


class FakeResult:
    """Mock YOLO result object with box tensors and COCO-like names map."""

    def __init__(self):
        """Initialize fake result metadata."""
        self.boxes = FakeBoxes()
        self.names = {0: "person"}


class FakeYOLO:
    """Mock Ultralytics YOLO model used to keep tests deterministic and offline."""

    def __init__(self, _model_path: str):
        """Accept model path to match real constructor signature."""
        self.names = {0: "person"}

    def predict(self, **_kwargs):
        """Return one fake prediction result."""
        return [FakeResult()]

    def track(self, **_kwargs):
        """Return one fake tracking result."""
        return [FakeResult()]


class TestPipeline(unittest.TestCase):
    """Unit tests covering baseline pipeline behavior and API stability."""

    def setUp(self):
        """Load standard configuration used across tests."""
        self.config_path = PROJECT_ROOT / "configs" / "config.yaml"

    def test_load_config_success(self):
        """Config YAML should load into a dictionary with expected sections."""
        config = load_config(str(self.config_path))
        self.assertIn("detection", config)
        self.assertIn("tracking", config)
        self.assertIn("camera", config)

    @patch("src.detector.YOLO", new=FakeYOLO)
    def test_detector_initializes(self):
        """ObjectDetector should initialize without raising an exception."""
        config = load_config(str(self.config_path))
        detector = ObjectDetector(config)
        self.assertIsNotNone(detector.model)

    @patch("src.detector.YOLO", new=FakeYOLO)
    def test_detect_dummy_black_frame(self):
        """Detector should process a dummy frame and return normalized detections."""
        config = load_config(str(self.config_path))
        detector = ObjectDetector(config)

        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect(dummy_frame)

        self.assertIsInstance(detections, list)
        self.assertGreaterEqual(len(detections), 1)
        self.assertIn("bbox", detections[0])
        self.assertIn("confidence", detections[0])

    def test_visualizer_draw_on_dummy_frame(self):
        """Visualizer should annotate a dummy frame without crashing."""
        config = load_config(str(self.config_path))
        visualizer = Visualizer(config)

        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracked_objects = [
            {
                "bbox": [10.0, 20.0, 110.0, 180.0],
                "confidence": 0.95,
                "class_id": 0,
                "class_name": "person",
                "track_id": 1,
            }
        ]

        visualizer.set_runtime_metrics(fps=18.0, total_unique_objects=1)
        output = visualizer.draw(dummy_frame, tracked_objects)

        self.assertIsNotNone(output)
        self.assertEqual(output.shape, dummy_frame.shape)


if __name__ == "__main__":
    unittest.main()
