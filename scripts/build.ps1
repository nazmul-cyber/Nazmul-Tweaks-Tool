# Build Nazmul Tweaks Tool EXE (run from repo root)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Installing requirements..."
python -m pip install -r requirements.txt

Write-Host "Generating logo..."
python generate_logo.py

Write-Host "Building EXE..."
python build_exe.py

$artifacts = @(
    "assets\logo.ico",
    "dist\Nazmul Tweaks Tool.exe",
    "release\Nazmul-Tweaks-Tool.exe"
)

Write-Host "`nVerification:"
foreach ($rel in $artifacts) {
    $path = Join-Path (Get-Location) $rel
    if (Test-Path $path) {
        $size = (Get-Item $path).Length
        Write-Host "  OK  $path  ($size bytes)"
    } else {
        Write-Host "  MISSING  $path"
        exit 1
    }
}