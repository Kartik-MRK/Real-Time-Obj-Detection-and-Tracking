#!/usr/bin/env bash
set -euo pipefail

log() {
  local level="$1"
  shift
  printf "%s [%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$level" "$*"
}

handle_error() {
  log "ERROR" "Model download failed. See TROUBLESHOOTING.md (ISSUE 4)."
  exit 1
}

trap handle_error ERR

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

mkdir -p models

download_model() {
  local model_name="$1"
  local required="$2"

  log "INFO" "Downloading ${model_name} via Ultralytics API"

  if (cd models && python - "$model_name" <<'PY'
import sys
from ultralytics import YOLO

model_name = sys.argv[1]
YOLO(model_name)
print(model_name)
PY
); then
    log "SUCCESS" "Downloaded ${model_name}"
  else
    if [ "$required" = "true" ]; then
      log "ERROR" "Failed to download required model: ${model_name}"
      exit 1
    else
      log "INFO" "Optional model download skipped: ${model_name}"
    fi
  fi
}

download_model "yolov8n.pt" "true"
download_model "yolov8s.pt" "false"

if [ ! -f "models/yolov8n.pt" ]; then
  log "ERROR" "Required model not found: models/yolov8n.pt"
  exit 1
fi

for model_file in models/yolov8n.pt models/yolov8s.pt; do
  if [ -f "$model_file" ]; then
    model_size="$(du -h "$model_file" | awk '{print $1}')"
    log "INFO" "${model_file} size: ${model_size}"
  fi
done

log "SUCCESS" "Model download check completed"
log "INFO" "To switch models, edit configs/config.yaml"
log "INFO" "Set detection.model_path to models/yolov8s.pt for better accuracy"
