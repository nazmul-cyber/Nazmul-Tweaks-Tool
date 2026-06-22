# Nazmul Tweaks Tool - Chris Titus style: paste once, app opens
# iex (iwr -useb https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/open.ps1)

$ErrorActionPreference = "Stop"
$Url = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$Exe = Join-Path $env:TEMP "Nazmul-Tweaks-Tool.exe"

function Get-Exe {
    if ((Test-Path $Exe) -and (Get-Item $Exe).Length -gt 500000) {
        return $Exe
    }
    Write-Host "  Downloading Nazmul Tweaks Tool..." -ForegroundColor Cyan
    if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
        Start-BitsTransfer -Source $Url -Destination $Exe -Description "Nazmul Tweaks Tool"
    } else {
        Invoke-WebRequest -Uri $Url -OutFile $Exe -UseBasicParsing -TimeoutSec 600
    }
    if (-not (Test-Path $Exe) -or (Get-Item $Exe).Length -lt 500000) {
        throw "Download failed. Get EXE from GitHub Releases."
    }
    return $Exe
}

$path = Get-Exe
Unblock-File $path -ErrorAction SilentlyContinue
Write-Host "  Opening Nazmul Tweaks Tool..." -ForegroundColor Green
Start-Process $path