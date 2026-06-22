# Nazmul Tweaks Tool - paste once, always opens latest version
# iex (iwr -useb https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/open.ps1)

$ErrorActionPreference = "Stop"
$Url = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$Api = "https://api.github.com/repos/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest"
$Exe = Join-Path $env:TEMP "Nazmul-Tweaks-Tool.exe"
$VerFile = Join-Path $env:TEMP "nazmul-tweaks-version.txt"

function Get-LatestVersion {
    try {
        $r = Invoke-RestMethod -Uri $Api -Headers @{"User-Agent" = "Nazmul-Tweaks-Tool-Open"} -TimeoutSec 20
        return ($r.tag_name -replace '^v', '').Trim()
    } catch {
        return $null
    }
}

function Test-NeedsDownload([string]$Latest) {
    if (-not (Test-Path $Exe) -or (Get-Item $Exe).Length -lt 500000) { return $true }
    if (-not $Latest) { return $false }
    if (-not (Test-Path $VerFile)) { return $true }
    $cached = (Get-Content $VerFile -Raw -ErrorAction SilentlyContinue).Trim()
    return ($cached -ne $Latest)
}

function Save-Exe([string]$Latest) {
    Remove-Item $Exe -Force -ErrorAction SilentlyContinue
    Write-Host "  Downloading Nazmul Tweaks Tool v$Latest..." -ForegroundColor Cyan
    if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
        Start-BitsTransfer -Source $Url -Destination $Exe -Description "Nazmul Tweaks Tool v$Latest"
    } else {
        Invoke-WebRequest -Uri $Url -OutFile $Exe -UseBasicParsing -TimeoutSec 600
    }
    if (-not (Test-Path $Exe) -or (Get-Item $Exe).Length -lt 500000) {
        throw "Download failed. Get EXE from GitHub Releases."
    }
    if ($Latest) {
        Set-Content -Path $VerFile -Value $Latest -Encoding UTF8 -NoNewline
    }
}

$latest = Get-LatestVersion
if (Test-NeedsDownload -Latest $latest) {
    Save-Exe -Latest $latest
} else {
    Write-Host "  Already on latest (v$latest)." -ForegroundColor Green
}

Unblock-File $Exe -ErrorAction SilentlyContinue
Write-Host "  Opening Nazmul Tweaks Tool..." -ForegroundColor Green
Start-Process $Exe