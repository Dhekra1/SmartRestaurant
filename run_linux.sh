#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

PYTHON="$PROJECT_ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  echo "Setup is missing. Run: ./scripts/setup_linux.sh" >&2
  exit 1
fi
if [[ ! -d frontend/node_modules ]]; then
  echo "Frontend dependencies are missing. Run: ./scripts/setup_linux.sh" >&2
  exit 1
fi

"$PYTHON" scripts/check_runtime.py

(cd backend && exec "../.venv/bin/python" -m app) &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true; wait "$BACKEND_PID" 2>/dev/null || true' EXIT
cd frontend
npm run dev -- --open
