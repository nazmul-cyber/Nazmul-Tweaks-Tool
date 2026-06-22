# Nazmul Tweaks Tool - Download EXE, shortcut, open app
$ErrorActionPreference = "Stop"

$ReleaseUrl = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$InstallDir = "$env:LOCALAPPDATA\NazmulTweaksTool"
$ExePath    = "$InstallDir\Nazmul Tweaks Tool.exe"

function Write-NT($msg, $color) {
    Write-Host "  [NT] $msg" -ForegroundColor $color
}

Clear-Host
Write-Host ""
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host "       Nazmul Tweaks Tool Installer       " -ForegroundColor Cyan
Write-Host "  ========================================" -ForegroundColor Cyan
Write-Host ""

$os = Get-CimInstance Win32_OperatingSystem
if ([version]$os.Version -lt [version]"10.0") {
    Write-NT "Windows 10 or 11 required." "Red"
    pause
    exit 1
}

New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

Write-NT "Downloading Nazmul Tweaks Tool..." "Cyan"
try {
    if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
        Start-BitsTransfer -Source $ReleaseUrl -Destination $ExePath -Description "Nazmul Tweaks Tool"
    } else {
        Invoke-WebRequest -Uri $ReleaseUrl -OutFile $ExePath -UseBasicParsing -TimeoutSec 600
    }
} catch {
    Write-NT "Download failed: $($_.Exception.Message)" "Red"
    Write-NT "Open in browser: $ReleaseUrl" "Yellow"
    Start-Process "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest"
    pause
    exit 1
}

if (-not (Test-Path $ExePath) -or (Get-Item $ExePath).Length -lt 500000) {
    Write-NT "Download incomplete. Try again or use browser download." "Red"
    pause
    exit 1
}

$mb = [math]::Round((Get-Item $ExePath).Length / 1MB, 1)
Write-NT "Downloaded $mb MB" "Green"

try {
    $icon = Join-Path $InstallDir "logo.ico"
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/assets/logo.ico" `
        -OutFile $icon -UseBasicParsing -TimeoutSec 30
} catch {
    $icon = $ExePath
}

$lnkPath = "$env:USERPROFILE\Desktop\Nazmul Tweaks Tool.lnk"
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($lnkPath)
$lnk.TargetPath = $ExePath
$lnk.WorkingDirectory = $InstallDir
if (Test-Path $icon) { $lnk.IconLocation = "$icon,0" }
$lnk.Description = "Nazmul Tweaks Tool"
$lnk.Save()
Write-NT "Desktop shortcut created." "Green"

Write-NT "Opening Nazmul Tweaks Tool..." "Cyan"
Start-Process $ExePath

Write-Host ""
Write-NT "Done!" "Green"
Write-Host ""