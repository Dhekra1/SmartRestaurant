"""Project-local runtime prerequisite and integrity checks."""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    failures: list[str] = []

    sys.path.insert(0, str(BACKEND_DIR))

    required_dirs = [
        BACKEND_DIR / "configs",
        BACKEND_DIR / "data",
        BACKEND_DIR / "logs",
        BACKEND_DIR / "models",
        PROJECT_ROOT / "fake_camera" / "bin",
        PROJECT_ROOT / "fake_camera" / "videos",
    ]
    for directory in required_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            failures.append(f"Cannot create directory {directory}: {error}")

    try:
        import cv2
        import lap
        import supervision
        import torch
        import torchvision
        import ultralytics

        print("Python:", sys.version.split()[0])
        print("Torch:", torch.__version__)
        print("TorchVision:", torchvision.__version__)
        print("Ultralytics:", ultralytics.__version__)
        print("OpenCV:", cv2.__version__)
        print("LAP:", getattr(lap, "__version__", "installed"))
        print("Supervision:", supervision.__version__)
        print("CUDA available:", torch.cuda.is_available())
    except Exception as error:
        failures.append(f"Python dependency/import failure: {error}")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg:
        print("FFmpeg:", ffmpeg)
    else:
        print("FFmpeg: not found on PATH")
        # FFmpeg is required for fake-camera video streaming, but not for all direct RTSP sources.

    if ffprobe:
        print("FFprobe:", ffprobe)
    else:
        print("FFprobe: not found on PATH")

    mediamtx = PROJECT_ROOT / "fake_camera" / "bin" / ("mediamtx.exe" if os.name == "nt" else "mediamtx")
    if mediamtx.is_file():
        print("MediaMTX:", mediamtx)
        print("MediaMTX SHA-256:", sha256(mediamtx))
    else:
        print("MediaMTX: not found", mediamtx)

    try:
        env_file = BACKEND_DIR / ".env"
        env_example = BACKEND_DIR / ".env.example"
        if not env_file.is_file() and env_example.is_file():
            env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
            print("Created backend/.env from backend/.env.example")

        from app.settings import get_settings
        settings = get_settings()
        print("YOLO model setting:", settings.yolo_model)
        model_path = settings.yolo_model_path
        if model_path.is_file():
            print("YOLO model:", model_path)
            print("YOLO model SHA-256:", sha256(model_path))
        else:
            print("YOLO model: missing (will be downloaded by Ultralytics if network is available):", model_path)
    except Exception as error:
        failures.append(f"Application settings/check failure: {error}")

    db_path = BACKEND_DIR / "data" / "app.db"
    print("SQLite database:", db_path)
    if db_path.is_file():
        print("SQLite database exists; startup will preserve it.")

    if failures:
        print("\nRUNTIME CHECK FAILURES:", file=sys.stderr)
        for failure in failures:
            print("- " + failure, file=sys.stderr)
        return 1

    print("\nRuntime check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
