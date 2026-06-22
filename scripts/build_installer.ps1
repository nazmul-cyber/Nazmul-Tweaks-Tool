# Build EXE + Inno Setup installer (run from repo root)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

& "$PSScriptRoot\build.ps1"

$version = (Select-String -Path "src\version.py" -Pattern 'APP_VERSION = "([^"]+)"').Matches[0].Groups[1].Value
Write-Host "Building Inno Setup installer v$version..."

$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    $iscc = "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
}
if (-not (Test-Path $iscc)) {
    throw "Inno Setup not found. Install from https://jrsoftware.org/isinfo.php"
}

New-Item -ItemType Directory -Path "installer" -Force | Out-Null
& $iscc "/DMyAppVersion=$version" "installer.iss"

$setup = Get-ChildItem "installer\Nazmul-Tweaks-Tool-Setup-v$version.exe" -ErrorAction Stop
Write-Host "`nInstaller ready:"
Write-Host "  $($setup.FullName)"
Write-Host "  size: $([math]::Round($setup.Length / 1MB, 2)) MB ($($setup.Length) bytes)"