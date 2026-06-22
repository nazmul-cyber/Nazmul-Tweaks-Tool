# Add/remove "System Refresh" on Windows desktop right-click menu
param(
    [switch]$Remove,
    [string]$Command = "",
    [string]$Icon = ""
)

$ErrorActionPreference = "Stop"

$menuName = "NazmulSystemRefresh"
$regBases = @(
    "HKCU:\Software\Classes\DesktopBackground\Shell\$menuName",
    "HKCU:\Software\Classes\Directory\Background\Shell\$menuName"
)

function Remove-Menu {
    foreach ($base in $regBases) {
        Remove-Item -Path $base -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] System Refresh removed from Windows right-click"
}

if ($Remove) {
    Remove-Menu
    exit 0
}

if (-not $Command) {
    Write-Host "[ERR] Launcher command missing"
    exit 1
}

if (-not $Icon) { $Icon = "imageres.dll,-1043" }

Remove-Menu

foreach ($base in $regBases) {
    New-Item -Path $base -Force | Out-Null
    Set-ItemProperty -Path $base -Name "(Default)" -Value "System Refresh"
    Set-ItemProperty -Path $base -Name "Icon" -Value $Icon
    Set-ItemProperty -Path $base -Name "Position" -Value "Top"
    New-Item -Path "$base\command" -Force | Out-Null
    Set-ItemProperty -Path "$base\command" -Name "(Default)" -Value $Command
}

Write-Host "[OK] System Refresh added to Windows right-click menu"
Write-Host "[INFO] Right-click desktop - System Refresh is on the menu"
exit 0