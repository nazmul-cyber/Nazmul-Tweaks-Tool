@echo off
title System Refresh - Nazmul Tweaks Tool
cd /d "%~dp0"

set "SCRIPT=%~dp0scripts\refresh.ps1"
if not exist "%SCRIPT%" (
    mshta "javascript:alert('refresh.ps1 not found.\nReinstall Nazmul Tweaks Tool.');close()"
    exit /b 1
)

:: refresh.ps1 self-elevates with -Wait when Admin is needed
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%SCRIPT%"
if %ERRORLEVEL% NEQ 0 (
    mshta "javascript:alert('System Refresh could not complete.\nAllow UAC when prompted and try again.');close()"
    exit /b 1
)

powershell -NoProfile -WindowStyle Hidden -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('GPU, RAM, and Windows refreshed! Your apps are still open.','System Refresh',[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null"

exit /b 0