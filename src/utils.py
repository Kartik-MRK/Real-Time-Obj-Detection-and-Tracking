"""Utility helpers for configuration, logging, device selection, and runtime metrics."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml


def log_message(level: str, message: str) -> None:
    """Print a timestamped log line with a consistent severity tag."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} [{level}] {message}")


def load_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration from disk and return it as a dictionary."""
    config_path = Path(path)
    if not config_path.exists():
        log_message("ERROR", f"Config file not found: {config_path}")
        raise RuntimeError(
            "Configuration file is missing. See TROUBLESHOOTING.md (ISSUE 6)."
        )

    try:
        with config_path.open("r", encoding="utf-8") as file_handle:
            config = yaml.safe_load(file_handle)
    except Exception as exc:
        log_message("ERROR", f"Failed to read config file: {exc}")
        raise RuntimeError(
            "Failed to parse config.yaml. See TROUBLESHOOTING.md (ISSUE 6)."
        ) from exc

    if not isinstance(config, dict):
        log_message("ERROR", "Config file format is invalid; expected a mapping.")
        raise RuntimeError(
            "Invalid config format. See TROUBLESHOOTING.md (ISSUE 6)."
        )

    log_message("SUCCESS", f"Loaded configuration from {config_path}")
    return config


def get_device(preferred: str = "auto") -> str:
    """Return the execution device, automatically falling back to CPU when needed."""
    preference = str(preferred).strip().lower()

    try:
        import torch

        cuda_available = torch.cuda.is_available()
    except Exception:
        cuda_available = False

    if preference == "auto":
        return "cuda:0" if cuda_available else "cpu"

    if preference.startswith("cuda"):
        if cuda_available:
            return preference
        log_message("INFO", "CUDA requested but unavailable. Falling back to CPU.")
        return "cpu"

    if preference == "cpu":
        return "cpu"

    log_message("INFO", f"Unknown device '{preferred}', using auto selection.")
    return "cuda:0" if cuda_available else "cpu"


def calculate_fps(prev_time: float) -> Tuple[float, float]:
    """Compute FPS from the previous timestamp and return FPS with updated time."""
    current_time = time.time()
    elapsed = max(current_time - prev_time, 1e-6)
    fps = 1.0 / elapsed
    return fps, current_time


def setup_output_directory(config: Dict[str, Any]) -> Optional[Path]:
    """Create output directory when video saving is enabled and return the directory path."""
    output_config = config.get("output", {})
    save_video = bool(output_config.get("save_video", False))

    if not save_video:
        return None

    output_path = Path(str(output_config.get("output_path", "output/tracked_output.mp4")))
    output_dir = output_path.parent if output_path.parent.as_posix() != "." else Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    log_message("INFO", f"Output directory ready: {output_dir}")
    return output_dir
