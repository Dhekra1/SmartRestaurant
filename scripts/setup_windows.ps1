[CmdletBinding()]
param(
    [switch]$SkipPythonPackages,
    [switch]$SkipFrontend,
    [switch]$SkipMediaMtx,
    [switch]$ForceVenv
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ProjectRoot

function Assert-Command([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is not available on PATH. Install it and open a new terminal."
    }
}

Write-Host "Project: $ProjectRoot"

$candidates = @(
    'py -3.11',
    'python3.11',
    'python'
)
$python = $null
foreach ($candidate in $candidates) {
    try {
        $parts = $candidate.Split(' ')
        $exe = $parts[0]
        $arguments = if ($parts.Count -gt 1) { $parts[1..($parts.Count - 1)] } else { @() }
        $probe = & $exe @arguments -c "import sys; print(sys.version_info.major); print(sys.version_info.minor)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $probe.Count -ge 2 -and $probe[0] -eq '3') {
            $pythonExe = $exe
            $pythonArgs = $arguments
            $python = @{ Exe = $exe; Args = $arguments }
            break
        }
    } catch {}
}

if (-not $python) {
    throw 'A compatible Python 3 interpreter was not found. Install Python 3.11 or a validated compatible version.'
}

$venv = Join-Path $ProjectRoot '.venv'
$venvPython = Join-Path $venv 'Scripts\python.exe'
if ($ForceVenv -and (Test-Path $venv)) {
    Remove-Item -Recurse -Force $venv
}
if (-not (Test-Path $venvPython)) {
    Write-Host 'Creating project-local Python environment...'
    & $python.Exe @($python.Args) '-m' 'venv' $venv
    if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' }
}

@(
    'backend\configs',
    'backend\data',
    'backend\logs',
    'backend\models',
    'fake_camera\bin',
    'fake_camera\videos',
    'backend\data\thumbnails'
) | ForEach-Object {
    $path = Join-Path $ProjectRoot $_
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

if (-not $SkipPythonPackages) {
    Write-Host 'Installing locked Python dependencies...'
    & $venvPython '-m' 'pip' 'install' '--upgrade' 'pip' 'setuptools' 'wheel'
    if ($LASTEXITCODE -ne 0) { throw 'pip bootstrap failed.' }
    & $venvPython '-m' 'pip' 'install' '--requirement' (Join-Path $ProjectRoot 'backend\requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
}

if (-not $SkipFrontend) {
    Assert-Command 'node'
    Assert-Command 'npm'
    Write-Host 'Installing frontend dependencies from package-lock.json...'
    Push-Location (Join-Path $ProjectRoot 'frontend')
    try {
        npm ci
        if ($LASTEXITCODE -ne 0) { throw 'npm ci failed.' }
    } finally { Pop-Location }
}

if (-not (Test-Path (Join-Path $ProjectRoot 'backend\.env'))) {
    Copy-Item (Join-Path $ProjectRoot 'backend\.env.example') (Join-Path $ProjectRoot 'backend\.env')
}
if (-not (Test-Path (Join-Path $ProjectRoot 'frontend\.env'))) {
    Copy-Item (Join-Path $ProjectRoot 'frontend\.env.example') (Join-Path $ProjectRoot 'frontend\.env')
}

if (-not $SkipMediaMtx) {
    $mediaMtx = Join-Path $ProjectRoot 'fake_camera\bin\mediamtx.exe'
    if (-not (Test-Path $mediaMtx)) {
        Write-Host 'Downloading MediaMTX...'
        & $venvPython (Join-Path $ProjectRoot 'fake_camera\download_mediamtx.py')
        if ($LASTEXITCODE -ne 0) { throw 'MediaMTX download failed.' }
    }
}

Write-Host 'Running startup prerequisite checks...'
& $venvPython (Join-Path $ProjectRoot 'scripts\check_runtime.py')
if ($LASTEXITCODE -ne 0) { throw 'Runtime prerequisite checks failed. Review the output above.' }

Write-Host 'Setup complete.'
Write-Host 'Start with: run_windows.bat (or run_windows.ps1)'
