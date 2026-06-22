@echo off
title Nazmul Tweaks Tool
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d='%LOCALAPPDATA%\NazmulTweaksTool';ni $d -Force|Out-Null;$e='$d\Nazmul Tweaks Tool.exe';iwr 'https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe' -OutFile $e -UseBasicParsing;Start-Process $e"