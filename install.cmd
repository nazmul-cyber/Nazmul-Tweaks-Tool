@echo off
title Nazmul Tweaks Tool - Install
:: Double-click this file (or run as Admin) to install from GitHub
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/install.ps1').Content)"
pause