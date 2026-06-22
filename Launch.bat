@echo off
title Nazmul Tweaks Tool
cd /d "%~dp0"

:: Find Python
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "C:\Program Files\Python314\python.exe" set "PY=C:\Program Files\Python314\python.exe"
if not defined PY if exist "C:\Program Files\Python313\python.exe" set "PY=C:\Program Files\Python313\python.exe"
if not defined PY if exist "C:\Program Files\Python312\python.exe" set "PY=C:\Program Files\Python312\python.exe"

if not defined PY (
    echo.
    echo  ERROR: Python not found!
    echo  Install Python 3.10+ from https://python.org
    echo  Check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

echo Installing dependencies...
%PY% -m pip install -r requirements.txt -q 2>nul
%PY% generate_logo.py 2>nul

echo Starting Nazmul Tweaks Tool...
if "%PY%"=="py -3" (
    start "Nazmul Tweaks Tool" py -3 "%~dp0main.py"
) else (
    start "Nazmul Tweaks Tool" "%PY%" "%~dp0main.py"
)
timeout /t 2 /nobreak >nul
if exist "%~dp0launch.log" (
    findstr /i "ERROR" "%~dp0launch.log" >nul 2>&1 && (
        echo.
        echo  Something went wrong. Check launch.log
        type "%~dp0launch.log"
        pause
    )
)
exit /b 0