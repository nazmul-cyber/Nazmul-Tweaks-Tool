# Force-download latest Nazmul Tweaks Tool and open it
# iex (iwr -useb https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/update.ps1)

$ErrorActionPreference = "Stop"
$Url = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$Exe = Join-Path $env:TEMP "Nazmul-Tweaks-Tool.exe"

Write-Host "  Checking for latest version..." -ForegroundColor Cyan
Remove-Item $Exe -Force -ErrorAction SilentlyContinue

if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
    Start-BitsTransfer -Source $Url -Destination $Exe -Description "Nazmul Tweaks Tool Update"
} else {
    Invoke-WebRequest -Uri $Url -OutFile $Exe -UseBasicParsing -TimeoutSec 600
}

if (-not (Test-Path $Exe) -or (Get-Item $Exe).Length -lt 500000) {
    throw "Update download failed. Try again from GitHub Releases."
}

Unblock-File $Exe -ErrorAction SilentlyContinue
Write-Host "  Opening updated Nazmul Tweaks Tool..." -ForegroundColor Green
Start-Process $Exe