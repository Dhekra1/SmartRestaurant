# Portable Installation and Transfer

## Supported targets

- Windows 10/11 on x64. The setup script prefers Python 3.11; the dependency manifest reports testing with Python 3.14 on Windows 11. Verify a clean setup on the target machine.
- Linux setup is provided where Bash and standard package tools are available, but has not been validated across all distributions.
- macOS is not a primary target; the Bash scripts may work if all prerequisites are installed.

Do not copy `.venv/`, `node_modules/`, `backend/data/`, `backend/logs/`, uploaded recordings, or user `.env` files between computers.

## Windows setup

1. Install Python 3.11 (preferred by the setup script) or a version validated for the pinned requirements. The dependency manifest reports testing with Python 3.14 on Windows 11.
2. Install Node.js 22.12+ and npm.
3. Install FFmpeg/FFprobe and ensure `ffmpeg.exe` and `ffprobe.exe` are on `PATH`, or configure absolute paths in `backend/.env`.
4. Open PowerShell in the project root.
5. Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup_windows.ps1
```

The setup script:

- creates `.venv/` inside the project;
- installs `backend/requirements.txt`;
- runs `npm ci` in `frontend/`;
- copies example `.env` files only when actual files do not exist;
- creates runtime directories;
- downloads MediaMTX if missing;
- runs `scripts/check_runtime.py`.

The setup script prefers Python 3.11. The requirements file reports testing with Python 3.14 on Windows 11; compatibility with other versions should be verified on a clean environment.

## Windows startup

```powershell
.\run_windows.bat
```

or:

```powershell
.\run_windows.ps1
```

- Backend: `http://127.0.0.1:8000`
- Dashboard: `http://127.0.0.1:5173`

## Linux setup and startup

```bash
./scripts/setup_linux.sh
./run_linux.sh
```

You can choose the interpreter with `PYTHON=python3.12 ./scripts/setup_linux.sh`, but only after proving it compatible with the complete pinned dependency set.

## External artifacts

The project ZIP should not normally include:

- virtual environments;
- `node_modules/`;
- SQLite database or journals;
- local `.env` secrets;
- uploaded recordings;
- caches/logs.

The following may need to be downloaded or separately approved:

- **MediaMTX:** `fake_camera/download_mediamtx.py` downloads a checksum-verified release for the current platform.
- **FFmpeg/FFprobe:** system-installed or included in a separately approved binary bundle.
- **YOLO weight:** `yolo26s.pt` is configured in `backend/.env.example` and is not bundled. The project may download official weights when network access is available.

To inspect without changing a model:

```powershell
.\.venv\Scripts\python.exe scripts\check_model.py
```

To allow a missing configured weight to be downloaded:

```powershell
.\.venv\Scripts\python.exe scripts\check_model.py --download
```

Existing weight files are never replaced by the check script.

## Package a portable ZIP

```powershell
.\.venv\Scripts\python.exe scripts\package_project.py
```

Optional approved inclusions:

```powershell
.\.venv\Scripts\python.exe scripts\package_project.py --include-model backend\models\yolo26s.pt --include-binary fake_camera\bin\mediamtx.exe
```

Do not include model weights or binaries until their source and redistribution terms have been approved.

## Transfer steps

1. Package or extract the project without `.venv`, `node_modules`, database, secrets, and recordings.
2. Copy approved external binaries and explicitly approved model weights if they should travel with the ZIP.
3. Extract to a destination path without spaces if a tool is known to fail with spaces, although scripts resolve paths relatively.
4. Copy or recreate `backend/.env` and `frontend/.env` from the examples.
5. Run the setup script once.
6. Run `run_windows.bat` or `run_windows.ps1`.
7. Open `http://127.0.0.1:5173`.

Do not run setup by copying a virtual environment from one computer to another.

## Troubleshooting

- **PowerShell execution policy:** use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current shell.
- **Python packages fail:** record `python --version`, `pip --version`, and the wheel error. Do not downgrade dependencies until the complete set is tested.
- **FFmpeg missing:** install FFmpeg and ensure `ffmpeg -version` and `ffprobe -version` work.
- **MediaMTX missing:** rerun setup or `python fake_camera/download_mediamtx.py`.
- **No model:** run the model check; network access may be required for first download.
- **Port occupied:** change API, frontend, or RTSP ports in `.env` and align CORS/frontend settings.
- **Existing database:** setup and startup create missing schema objects but do not replace `backend/data/app.db`.
- **CUDA:** CPU setup is supported. CUDA requires matching Torch/TorchVision wheels and NVIDIA driver compatibility.
