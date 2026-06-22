# Launch MAS and optionally send menu keys (e.g. E+Enter for Genuine Windows download)
param(
    [string]$Keys = "",
    [int]$DelaySec = 7
)

$ErrorActionPreference = "SilentlyContinue"
Add-Type -AssemblyName System.Windows.Forms

$masCmd = "irm https://get.activated.win | iex"
$args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $masCmd)

try {
    $proc = Start-Process -FilePath "powershell.exe" -Verb RunAs -PassThru -ArgumentList $args
} catch {
    Write-Host "[ERR] UAC cancelled"
    exit 1
}

if (-not $Keys) {
    Write-Host "[OK] MAS opened"
    exit 0
}

Start-Sleep -Seconds $DelaySec

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class NazmulWin {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

for ($i = 0; $i -lt 20; $i++) {
    try { $proc.Refresh() } catch {}
    $hwnd = $proc.MainWindowHandle
    if ($hwnd -ne [IntPtr]::Zero) {
        [NazmulWin]::ShowWindow($hwnd, 9) | Out-Null
        [NazmulWin]::SetForegroundWindow($hwnd) | Out-Null
        break
    }
    Start-Sleep -Milliseconds 400
}

Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Write-Host "[OK] MAS opened — sent keys: $Keys"