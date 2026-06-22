# Force-download latest Nazmul Tweaks Tool and open it
# iex (iwr -useb https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/update.ps1)

$ErrorActionPreference = "Stop"
$Url = "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"
$Api = "https://api.github.com/repos/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest"
$Exe = Join-Path $env:TEMP "Nazmul-Tweaks-Tool.exe"
$VerFile = Join-Path $env:TEMP "nazmul-tweaks-version.txt"

Write-Host "  Checking for latest version..." -ForegroundColor Cyan
$latest = $null
try {
    $r = Invoke-RestMethod -Uri $Api -Headers @{"User-Agent" = "Nazmul-Tweaks-Tool-Update"} -TimeoutSec 20
    $latest = ($r.tag_name -replace '^v', '').Trim()
    Write-Host "  Latest release: v$latest" -ForegroundColor Cyan
} catch {
    Write-Host "  Could not read GitHub version (will still download EXE)." -ForegroundColor Yellow
}

Remove-Item $Exe -Force -ErrorAction SilentlyContinue

if (Get-Command Start-BitsTransfer -ErrorAction SilentlyContinue) {
    Start-BitsTransfer -Source $Url -Destination $Exe -Description "Nazmul Tweaks Tool Update"
} else {
    Invoke-WebRequest -Uri $Url -OutFile $Exe -UseBasicParsing -TimeoutSec 600
}

if (-not (Test-Path $Exe) -or (Get-Item $Exe).Length -lt 500000) {
    throw "Update download failed. Try again from GitHub Releases."
}

if ($latest) {
    Set-Content -Path $VerFile -Value $latest -Encoding UTF8 -NoNewline
}

Unblock-File $Exe -ErrorAction SilentlyContinue
Write-Host "  Opening updated Nazmul Tweaks Tool..." -ForegroundColor Green
Start-Process $Exe