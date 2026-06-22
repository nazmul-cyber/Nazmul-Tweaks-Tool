# Nazmul Tweaks Tool - Public One-Line Installer
# Public install (paste in PowerShell Admin - ONE line, copy from GitHub README):
# powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/install.ps1').Content)"

$ErrorActionPreference = "Stop"

function Write-NT($msg, $color) {
    Write-Host "  [NT] $msg" -ForegroundColor $color
}

function Test-WindowsSupported {
    $os = Get-CimInstance Win32_OperatingSystem
    $ver = [version]$os.Version
    if ($os.Caption -notmatch "Windows 10|Windows 11|Windows Server") {
        return $false
    }
    return $ver.Major -ge 10
}

function Get-DownloadSizeText($bytes) {
    if ($bytes -ge 1MB) { return "{0:N1} MB" -f ($bytes / 1MB) }
    if ($bytes -ge 1KB) { return "{0:N0} KB" -f ($bytes / 1KB) }
    return "$bytes bytes"
}

Clear-Host
Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "       Nazmul Tweaks Tool Installer       " -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-WindowsSupported)) {
    Write-NT "Windows 10 or 11 is required." "Red"
    pause
    exit 1
}

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
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

Write-NT "Downloading latest EXE (faster BITS transfer)..." "Cyan"
$downloaded = $false
$tmpExe = Join-Path $env:TEMP "Nazmul-Tweaks-Tool-download.exe"

try {
    if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
        Start-BitsTransfer -Source $releaseUrl -Destination $tmpExe -Description "Nazmul Tweaks Tool" -DisplayName "Nazmul Tweaks Tool"
    } else {
        Invoke-WebRequest -Uri $releaseUrl -OutFile $tmpExe -UseBasicParsing -TimeoutSec 300
    }
    if ((Test-Path $tmpExe) -and ((Get-Item $tmpExe).Length -gt 500000)) {
        Move-Item -Path $tmpExe -Destination $exePath -Force
        $downloaded = $true
        $sz = Get-DownloadSizeText (Get-Item $exePath).Length
        Write-NT "Downloaded $sz successfully!" "Green"
    }
} catch {
    Write-NT "Download failed: $($_.Exception.Message)" "Yellow"
    Write-NT "Check internet or download manually from GitHub Releases." "Yellow"
}

if ($downloaded) {
    $iconPath = Join-Path $installDir "logo.ico"
    try {
        $iconUrl = "https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/assets/logo.ico"
        Invoke-WebRequest -Uri $iconUrl -OutFile $iconPath -UseBasicParsing -TimeoutSec 30
    } catch { $iconPath = $exePath }

    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Nazmul Tweaks Tool.lnk")
    $lnk.TargetPath = $exePath
    $lnk.WorkingDirectory = $installDir
    if (Test-Path $iconPath) { $lnk.IconLocation = "$iconPath,0" }
    $lnk.Description = "Nazmul Tweaks Tool - Windows optimizer"
    $lnk.Save()
    Write-NT "Desktop shortcut created." "Green"
    Write-NT "Works on any Windows 10/11 PC - no Python needed." "Cyan"
    Start-Process $exePath
} else {
    Write-NT "Falling back to local source (dev mode)..." "Yellow"
    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
    if (-not $py) {
        Write-NT "Python not found. Download EXE manually:" "Red"
        Write-NT $releaseUrl "White"
        Start-Process "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest"
        pause
        exit 1
    }

    if (-not (Test-Path "$localRoot\main.py")) {
        Write-NT "Local project not found. Use GitHub download link above." "Red"
        pause
        exit 1
    }

    Set-Location $localRoot
    python -m pip install -r requirements.txt -q
    python generate_logo.py 2>$null

    $shell = New-Object -ComObject WScript.Shell
    $lnk = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Nazmul Tweaks Tool.lnk")
    $lnk.TargetPath = "$localRoot\Launch.bat"
    $lnk.WorkingDirectory = $localRoot
    $lnk.Save()

    Write-NT "Launching from source..." "Green"
    Start-Process "$localRoot\Launch.bat"
}

Write-Host ""
Write-NT "Done! Right-click desktop for System Refresh after you add it in the app." "Green"
Write-Host ""