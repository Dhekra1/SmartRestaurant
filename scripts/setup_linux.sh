#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
  for candidate in python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON="$candidate"
      break
    fi
  done
fi
if [[ -z "$PYTHON" ]]; then
  echo "Python 3 was not found. Install Python 3.11 or a validated compatible version." >&2
  exit 1
fi

mkdir -p backend/configs backend/data backend/logs backend/models fake_camera/bin fake_camera/videos

VENV="$PROJECT_ROOT/.venv"
VENV_PYTHON="$VENV/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Creating project-local Python environment..."
  "$PYTHON" -m venv "$VENV"
fi

"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel
"$VENV_PYTHON" -m pip install -r backend/requirements.txt

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js 20.19+ or 22.12+ and npm are required." >&2
  exit 1
fi
(cd frontend && npm ci)

if [[ ! -f backend/.env ]]; then
  cp backend/.env.example backend/.env
fi
if [[ ! -f frontend/.env ]]; then
  cp frontend/.env.example frontend/.env
fi

if [[ "$(uname -s)" == "Linux" || "$(uname -s)" == "Darwin" ]]; then
  if [[ ! -x fake_camera/bin/mediamtx ]]; then
    echo "Downloading MediaMTX..."
    "$VENV_PYTHON" fake_camera/download_mediamtx.py
  fi
fi

"$VENV_PYTHON" scripts/check_runtime.py

echo "Setup complete."
echo "Start with: ./run_linux.sh"
