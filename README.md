# Nazmul Tweaks Tool

Free Windows optimizer for everyone — 38 tweaks, System Refresh, winget apps, MAS activation.

![Release](https://img.shields.io/github/v/release/nazmul-cyber/Nazmul-Tweaks-Tool?label=release)
![Downloads](https://img.shields.io/github/downloads/nazmul-cyber/Nazmul-Tweaks-Tool/total?label=downloads)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6)
![Size](https://img.shields.io/badge/EXE-~19%20MB-teal)

---

## Install (copy this — 1 line)

**PowerShell → Run as Administrator** → paste → Enter:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/install.ps1').Content)"
```

Click the **copy button** (top-right of the code box on GitHub).

| Also works | |
|------------|--|
| **Download EXE** | https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe |
| **Releases page** | https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest |

[![Download EXE](https://img.shields.io/badge/Download-EXE%20(~19%20MB)-0D9488?style=for-the-badge)](https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe)

> **Never use** `irm ... | iex` — broken on Windows (*empty string* error).

---

## Features

- **38+ Windows Tweaks** — Privacy, Performance, Explorer, Debloat, Updates, Network, Gaming
- **23 Essential Apps** — One-click winget installs
- **System Refresh** — GPU + RAM + Windows; desktop right-click menu
- **Activation Center** — Windows 10/11 + Office via MAS
- **Fresh Setup** — Recommended tweaks + apps in one click
- **6 Themes** — Light, Slate, Ocean, Midnight, Emerald, and more

## Requirements

- Windows 10 / 11 (64-bit)
- Administrator for tweaks (UAC prompt)
- winget for Apps page (free App Installer from Microsoft Store)

## Public use — works on most PCs?

| Feature | Works? | Notes |
|---------|--------|-------|
| EXE | Yes | No Python needed |
| Tweaks | Yes* | *Needs Admin |
| System Refresh | Yes | Built-in PowerShell |
| Apps | If winget installed | Microsoft Store |
| Activation | Internet required | MAS menu |

Create a **restore point** before applying tweaks.

## Build EXE (developers)

```bash
pip install -r requirements.txt
python generate_logo.py
python build_exe.py
```

Output: `release/Nazmul-Tweaks-Tool.exe`

## Author

**MD Nazmul Hasan** — [GitHub](https://github.com/nazmul-cyber)

## License

MIT