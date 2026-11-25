$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path $PSScriptRoot).Path
Set-Location $ProjectRoot

$python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw 'Setup is missing. Run: scripts\setup_windows.ps1'
}
if (-not (Test-Path (Join-Path $ProjectRoot 'frontend\node_modules'))) {
    throw 'Frontend dependencies are missing. Run: scripts\setup_windows.ps1'
}

& $python (Join-Path $ProjectRoot 'scripts\check_runtime.py')
if ($LASTEXITCODE -ne 0) { throw 'Runtime prerequisite checks failed.' }

Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', 'cd /d "{0}" && "{1}" -m app' -WorkingDirectory (Join-Path $ProjectRoot 'backend') -f (Join-Path $ProjectRoot 'backend'), $python
Start-Process -FilePath 'cmd.exe' -ArgumentList '/k', 'npm run dev -- --open' -WorkingDirectory (Join-Path $ProjectRoot 'frontend')
