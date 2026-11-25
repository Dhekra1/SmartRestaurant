"""Create a portable project archive excluding caches, secrets, databases and recordings."""

from __future__ import annotations

import argparse
import fnmatch
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_NAMES = {
    ".git", ".venv", "venv", "node_modules", "dist", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".vite", "htmlcov", "logs", "data", ".env",
}
EXCLUDED_SUFFIXES = {
    ".pyc", ".pyo", ".db", ".db-journal", ".sqlite", ".sqlite3", ".log", ".coverage",
}
EXCLUDED_PATTERNS = (
    "*.mp4", "*.avi", "*.mov", "*.mkv", "*.webm", "*.m4v", "*.db-wal", "*.db-shm",
    "*.env.*", "!*.env.example", "npm-debug.log*", "Thumbs.db", "*.tsbuildinfo",
)


def should_exclude(relative: Path) -> bool:
    if any(part in EXCLUDED_NAMES for part in relative.parts):
        return True
    if relative.suffix.lower() in EXCLUDED_SUFFIXES:
        return True

    name = relative.name
    if name in {".env"}:
        return True

    for pattern in EXCLUDED_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            if name.endswith(".env.example"):
                return False
            return True

    # Keep approved MediaMTX binaries/config/license if explicitly present.
    # Keep project source and user package lock. Model .pt files are intentionally excluded
    # below unless explicitly included to avoid silently copying unverified weights.
    if relative.suffix.lower() in {".pt", ".pth", ".onnx", ".engine", ".torchscript"}:
        return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a portable source ZIP.")
    parser.add_argument("--include-model", action="append", default=[], help="relative model path to include; may be repeated")
    parser.add_argument("--include-media", action="append", default=[], help="relative media file to include; may be repeated")
    parser.add_argument("--include-binary", action="append", default=[], help="relative external binary to include; may be repeated")
    parser.add_argument("--output", default=None, help="output ZIP path")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output = Path(args.output) if args.output else (PROJECT_ROOT.parent / f"SmartRestaurant-portable-{timestamp}.zip")
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    explicit = set()
    for option in (args.include_model, args.include_media, args.include_binary):
        for item in option:
            path = (PROJECT_ROOT / item).resolve()
            try:
                path.relative_to(PROJECT_ROOT)
            except ValueError:
                print(f"Refusing path outside project: {item}", file=sys.stderr)
                return 2
            if not path.is_file():
                print(f"Requested package file does not exist: {item}", file=sys.stderr)
                return 2
            explicit.add(path.relative_to(PROJECT_ROOT))

    count = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in PROJECT_ROOT.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(PROJECT_ROOT)
            if relative not in explicit and should_exclude(relative):
                continue
            archive.write(path, relative.as_posix())
            count += 1

    print(f"Portable ZIP: {output}")
    print(f"Files included: {count}")
    print("Excluded: virtual environments, node_modules, caches, secrets, databases, SQLite journals, recordings, and unapproved model weights.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
