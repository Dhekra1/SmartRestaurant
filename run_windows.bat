@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Setup is missing. Run: scripts\setup_windows.ps1
  exit /b 1
)

if not exist "frontend\node_modules" (
  echo Frontend dependencies are missing. Run: scripts\setup_windows.ps1
  exit /b 1
)

".venv\Scripts\python.exe" scripts\check_runtime.py
if errorlevel 1 exit /b 1

start "Table Occupancy - backend" /D "%~dp0backend" cmd /k "..\.venv\Scripts\python.exe -m app"
start "Table Occupancy - dashboard" /D "%~dp0frontend" cmd /k "npm run dev -- --open"
