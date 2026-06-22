# Nazmul Tweaks Tool - One-Line Installer
# Usage: Set-ExecutionPolicy Bypass -Scope Process -Force; & "E:\Projects\Nazmul-Tweaks-Tool\scripts\install.ps1"

$ErrorActionPreference = "Stop"

function Write-NT($msg, $color) {
    Write-Host "  [NT] $msg" -ForegroundColor $color
}

Clear-Host
Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "       Nazmul Tweaks Tool Installer       " -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-NT "Relaunching as Administrator..." "Yellow"
    $self = $PSCommandPath
    if (-not $self) { $self = "$PSScriptRoot\install.ps1" }
    Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$self`""
    exit
}

$installDir = "$env:LOCALAPPDATA\NazmulTweaksTool"
$exePath    = "$installDir\Nazmul Tweaks Tool.exe"
$releaseUrl = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$localRoot  = Split-Path $PSScriptRoot -Parent

New-Item -ItemType Directory -Path $installDir -Force | Out-Null

Write-NT "Checking for release EXE..." "Cyan"
$downloaded = $false
try {
    Invoke-WebRequest -Uri $releaseUrl -OutFile $exePath -UseBasicParsing -TimeoutSec 30
    if ((Test-Path $exePath) -and ((Get-Item $exePath).Length -gt 1000000)) {
        $downloaded = $true
        Write-NT "Downloaded EXE successfully!" "Green"
    }
} catch {
    Write-NT "No release EXE - using local source..." "Yellow"
}

if ($downloaded) {
    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Nazmul Tweaks Tool.lnk")
    $lnk.TargetPath = $exePath
    $lnk.WorkingDirectory = $installDir
    $lnk.Save()
    Write-NT "Desktop shortcut created." "Green"
    Start-Process $exePath
} else {
    Write-NT "Setting up from local project..." "Cyan"
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
    if (-not $py) {
        Write-NT "Python not found! Install from python.org" "Red"
        pause
        exit 1
    }

    if (Test-Path "$localRoot\main.py") {
        $srcDir = $localRoot
    } else {
        Write-NT "Project not found at $localRoot" "Red"
        pause
        exit 1
    }

    Set-Location $srcDir
    python -m pip install -r requirements.txt -q
    python generate_logo.py 2>$null

    if (Test-Path "$srcDir\data") {
        New-Item "$installDir\data" -ItemType Directory -Force | Out-Null
        Copy-Item "$srcDir\data\*" "$installDir\data" -Recurse -Force -ErrorAction SilentlyContinue
    }

    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Nazmul Tweaks Tool.lnk")
    $lnk.TargetPath = "$srcDir\Launch.bat"
    $lnk.WorkingDirectory = $srcDir
    $lnk.Save()

    Write-NT "Launching Nazmul Tweaks Tool..." "Green"
    Start-Process "$srcDir\Launch.bat"
}

Write-Host ""
Write-NT "Done!" "Green"
Write-Host ""