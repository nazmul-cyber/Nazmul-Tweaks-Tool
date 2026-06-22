@echo off
title Nazmul Tweaks Tool (Admin)
cd /d "%~dp0"
powershell -Command "Start-Process -FilePath '%~dp0Launch.bat' -Verb RunAs -WorkingDirectory '%~dp0'"