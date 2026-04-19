#!/usr/bin/env bash
set -euo pipefail

log() {
  local level="$1"
  shift
  printf "%s [%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$level" "$*"
}

handle_error() {
  log "ERROR" "Setup failed. See TROUBLESHOOTING.md (ISSUE 2, ISSUE 6)."
  exit 1
}

trap handle_error ERR

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

log "INFO" "Project root: $PROJECT_ROOT"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  log "ERROR" "Python executable not found: $PYTHON_BIN"
  log "ERROR" "Install Python 3.8+ and rerun setup.sh"
  exit 1
fi

python_major="$($PYTHON_BIN -c 'import sys; print(sys.version_info.major)')"
python_minor="$($PYTHON_BIN -c 'import sys; print(sys.version_info.minor)')"
python_version="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"

log "INFO" "Detected Python version: $python_version"

if [ "$python_major" -lt 3 ] || { [ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]; }; then
  log "INFO" "Python version is below 3.8. Setup may fail; upgrade Python if possible."
fi

if [ ! -d "venv" ]; then
  log "INFO" "Creating virtual environment in ./venv"
  "$PYTHON_BIN" -m venv venv
else
  log "INFO" "Using existing virtual environment in ./venv"
fi

# shellcheck disable=SC1091
source venv/bin/activate

log "INFO" "Upgrading pip"
python -m pip install --upgrade pip

log "INFO" "Installing dependencies from requirements.txt"
pip install -r requirements.txt

log "INFO" "Downloading model weights"
bash download_models.sh

log "SUCCESS" "Setup complete"
log "SUCCESS" "Next commands:"
log "SUCCESS" "source venv/bin/activate"
log "SUCCESS" "python main.py"
