"""Check or download the configured YOLO model without replacing an existing file."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="download the configured model if missing")
    args = parser.parse_args()

    try:
        from app.settings import get_settings
        settings = get_settings()
        model_path = settings.yolo_model_path
    except Exception as error:
        print(f"Cannot read application settings: {error}", file=sys.stderr)
        return 1

    model_path.parent.mkdir(parents=True, exist_ok=True)

    if model_path.is_file():
        print(f"Model available: {model_path}")
        print(f"SHA-256: {sha256(model_path)}")
        print("Existing model was not replaced.")
        return 0

    if not args.download:
        print(f"Model missing: {model_path}", file=sys.stderr)
        print("Run with --download to let Ultralytics fetch the configured official weight.", file=sys.stderr)
        return 2

    try:
        from ultralytics import YOLO
        print(f"Downloading/loading configured model: {settings.yolo_model}")
        YOLO(settings.yolo_model)
    except Exception as error:
        print(f"Model download/load failed: {error}", file=sys.stderr)
        return 1

    if model_path.is_file():
        print(f"Model available: {model_path}")
        print(f"SHA-256: {sha256(model_path)}")
        return 0

    print("Ultralytics loaded the model, but the expected project model path was not created:", model_path, file=sys.stderr)
    print("Review Ultralytics cache/location and settings before replacing weights.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
