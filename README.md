# Nazmul Tweaks Tool

A beautiful, fast Windows optimization tool inspired by [Chris Titus WinUtil](https://github.com/ChrisTitusTech/winutil). Apply tweaks, install essential apps, and activate Windows/Office — all from one clean UI.

![Theme](https://img.shields.io/badge/Theme-Light%20%26%20Dark-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6)
![Python](https://img.shields.io/badge/Python-3.10+-green)

## Features

- **38+ Windows Tweaks** — Privacy, Performance, Explorer, Debloat, Updates, Network, Gaming
- **23 Essential Apps** — One-click winget installs for fresh Windows setups
- **System Refresh** — GPU + RAM + Windows refresh; add to desktop right-click menu
- **Activation Center** — Windows 10/11 + Office via MAS activator
- **Fresh Setup Preset** — Apply all recommended tweaks + apps automatically
- **6 Themes** — Light, Slate, Ocean, Midnight, Emerald, and more
- **Fast Splash Screen** — Opens instantly, loads UI in background
- **One-Line Install** — PowerShell command like WinUtil

## Quick Install (PowerShell Admin)

```powershell
irm https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/install.ps1 | iex
```

Copy → paste in **PowerShell (Admin)** → hit Enter → done.

## Manual Run

```bash
cd E:\Projects\Nazmul-Tweaks-Tool
pip install -r requirements.txt
python generate_logo.py
python main.py
```

**As Admin:** Right-click `run_admin.bat` → Run as administrator

## Build EXE (for GitHub Releases)

```bash
pip install -r requirements.txt
python generate_logo.py
python build_exe.py
```

Output:
- `dist/Nazmul Tweaks Tool.exe`
- `release/Nazmul-Tweaks-Tool.exe` ← upload this to GitHub Releases

## GitHub Release Setup

1. Build EXE: `python build_exe.py`
2. Create a new Release on GitHub
3. Upload `release/Nazmul-Tweaks-Tool.exe`
4. Users can install with the one-liner above

## Project Structure

```
Nazmul-Tweaks-Tool/
├── main.py              # Fast splash + entry
├── src/
│   ├── app.py           # Main GUI
│   ├── themes.py        # Light/Dark themes
│   ├── tweaks.py        # 38 tweak definitions
│   ├── apps.py          # Essential apps (winget)
│   ├── executor.py      # PowerShell/winget runner
│   └── animations.py    # UI animations
├── scripts/
│   ├── install.ps1      # One-line installer
│   └── activation.ps1   # Windows/Office activation
├── assets/
│   ├── logo.png
│   └── logo.ico
├── build_exe.py
└── requirements.txt
```

## Pages

| Page | Description |
|------|-------------|
| Home | Dashboard + one-line install command |
| Tweaks | Category-filtered Windows optimizations |
| Apps | Essential app installer via winget |
| Activate | Windows 10/11 + Office 1-click activation |
| Fresh Setup | Full preset for new Windows installs |
| Log | Real-time activity log |

## Requirements

- Windows 10 / 11
- Python 3.10+ (for dev) or use the EXE
- winget (Microsoft App Installer)
- Administrator privileges for tweaks & activation

## Disclaimer

- Create a system restore point before applying tweaks
- Activation module is for personal/educational use — comply with Microsoft licensing
- Use at your own risk

## Author

**MD Nazmul Hasan** — [GitHub](https://github.com/nazmul-cyber)

## License

MIT