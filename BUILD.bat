@echo off
title Nazmul Tweaks Tool - BUILD
color 0B
cd /d "%~dp0"
set "LOG=%~dp0build.log"

echo. > "%LOG%"
echo ============================================>> "%LOG%"
echo   Nazmul Tweaks Tool - EXE Builder>> "%LOG%"
echo ============================================>> "%LOG%"
echo.>> "%LOG%"

echo [1/4] Installing dependencies...
echo [1/4] Installing dependencies...>> "%LOG%"
python -m pip install -r requirements.txt -q >> "%LOG%" 2>&1
if errorlevel 1 (
    echo FAILED: pip install>> "%LOG%"
    type "%LOG%"
    exit /b 1
)

echo [2/4] Generating logo...
echo [2/4] Generating logo...>> "%LOG%"
python generate_logo.py >> "%LOG%" 2>&1
if errorlevel 1 (
    echo FAILED: logo>> "%LOG%"
    type "%LOG%"
    exit /b 1
)

echo [3/4] Building EXE (may take 2-3 min)...
echo [3/4] Building EXE (may take 2-3 min)...>> "%LOG%"
python build_exe.py >> "%LOG%" 2>&1
if errorlevel 1 (
    echo FAILED: build>> "%LOG%"
    type "%LOG%"
    exit /b 1
)

echo.>> "%LOG%"
echo [4/4] Done!>> "%LOG%"
echo.>> "%LOG%"
echo EXE files:>> "%LOG%"
echo   dist\Nazmul Tweaks Tool.exe>> "%LOG%"
echo   release\Nazmul-Tweaks-Tool.exe  ^<-- upload to GitHub Releases>> "%LOG%"
echo.>> "%LOG%"

if exist "release\Nazmul-Tweaks-Tool.exe" (
    for %%F in ("release\Nazmul-Tweaks-Tool.exe") do (
        echo release\Nazmul-Tweaks-Tool.exe  ^(%%~zF bytes^)>> "%LOG%"
        echo.
        echo SUCCESS: release\Nazmul-Tweaks-Tool.exe  ^(%%~zF bytes^)
    )
    if exist "build-result.txt" type "build-result.txt" >> "%LOG%"
    if not defined BUILD_NO_UI explorer "release"
    type "%LOG%"
    exit /b 0
)

echo FAILED - release\Nazmul-Tweaks-Tool.exe not found>> "%LOG%"
type "%LOG%"
exit /b 1