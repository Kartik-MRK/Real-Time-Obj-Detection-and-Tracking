"""Camera and video source abstraction used by the runtime pipeline."""

from __future__ import annotations

from typing import Any, Tuple

import cv2


class CameraSource:
    """Read frames from a webcam index or a file path using OpenCV."""

    def __init__(self, source: Any, width: int, height: int, fps_target: int) -> None:
        """Initialize the video capture source and apply capture properties."""
        self.source = self._normalize_source(source)
        self.capture = cv2.VideoCapture(self.source)

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Cannot open camera/video source: {source}. "
                "See TROUBLESHOOTING.md (ISSUE 1)."
            )

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
        self.capture.set(cv2.CAP_PROP_FPS, int(fps_target))

    @staticmethod
    def _normalize_source(source: Any) -> Any:
        """Convert string camera indices such as '0' into integers."""
        if isinstance(source, str):
            stripped = source.strip()
            if stripped.isdigit():
                return int(stripped)
            return stripped
        return source

    def read(self) -> Tuple[bool, Any]:
        """Return the next frame tuple as (success_flag, frame)."""
        return self.capture.read()

    def release(self) -> None:
        """Release the underlying OpenCV capture object."""
        if self.capture is not None:
            self.capture.release()
