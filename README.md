<p align="center">
  <img src="assets/logo.png" alt="Nazmul Tweaks Tool" width="120">
</p>

<h1 align="center">Nazmul Tweaks Tool</h1>

<p align="center">
  <strong>Free, open-source Windows optimizer for everyone.</strong><br>
  One PowerShell line → app opens. No install wizard. No Python needed.
</p>

<p align="center">
  <a href="https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest"><img src="https://img.shields.io/github/v/release/nazmul-cyber/Nazmul-Tweaks-Tool?label=release&style=for-the-badge" alt="Release"></a>
  <a href="https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe"><img src="https://img.shields.io/badge/Download-EXE-0D9488?style=for-the-badge" alt="Download"></a>
  <img src="https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge" alt="Windows">
  <img src="https://img.shields.io/badge/Size-~19%20MB-teal?style=for-the-badge" alt="Size">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="MIT">
</p>

---

## Project purpose | উদ্দেশ্য

> **সংক্ষেপে:** সাধারণ মানুষের Windows PC **দ্রুত, পরিষ্কার ও সহজ** রাখা — এক ক্লিকে, বিনা ইনস্টল, ১০০% ফ্রি।  
> **In short:** Help everyday users **speed up, clean, and fix** Windows 10/11 — no tech skills needed.

Built by **MD Nazmul Hasan** so anyone can tweak, refresh, and restore their PC like pro tools — but simpler.

---

## What is Nazmul Tweaks Tool?

**Nazmul Tweaks Tool** is a portable Windows desktop app that helps everyday users **speed up, clean, and customize** Windows 10/11 — without editing the registry manually or running random scripts.

Inspired by **Chris Titus WinUtil**: copy one line in PowerShell, the app window opens. Built by **MD Nazmul Hasan** to be simple, safe, and actually usable for non-technical people.

| | |
|---|---|
| **Type** | Portable `.exe` (~19 MB) — no installer |
| **Works on** | Windows 10 & 11 |
| **Admin** | Some tweaks need UAC (one prompt per batch) |
| **Cost** | 100% free · MIT License |

---

## Open the app (1 line — like WinUtil)

Open **PowerShell**, paste, press **Enter**:

```powershell
iex (iwr -useb https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/open.ps1)
```

- **First time:** downloads ~19 MB to `%TEMP%`, then opens  
- **Next times:** opens faster from cache  
- **Security popup** *Unknown Publisher*? Click **Run** — normal for free unsigned software  

> Do **not** use old 5-line `LOCALAPPDATA` install commands — they fail with `PermissionDenied` on many PCs.

---

## Or download EXE once

<p align="center">
  <a href="https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe">
    <img src="assets/nazmul-tweaks-tool.png" alt="Nazmul Tweaks Tool preview" width="300">
  </a>
</p>

**Direct link:** https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe

Double-click. No install wizard.

---

## Features

### Windows Tweaks (38+)
Privacy, performance, Explorer, debloat, updates, network, and gaming — organized by category with checkboxes. Apply selected tweaks in one batch. **Revert Last** undoes the previous batch.

| Category | Examples |
|----------|----------|
| Privacy | Disable telemetry, ads ID, activity history |
| Performance | Disable animations, SysMain tweak, power plan |
| Explorer | Show extensions, classic menu, compact view |
| Debloat | Copilot, widgets, consumer features |
| Network | DNS, IPv6, Nagle, Print Screen fix |
| Gaming | Game Mode, mouse accel, fullscreen opt |

### System Refresh
**Graphics + Windows shell + RAM refresh** — feels closer to a fresh boot. Apps stay open.

- Restarts Explorer, Start menu, DWM (GPU compositor), Themes service  
- Clears temp, flushes DNS, optimizes RAM  
- Click **Refresh Now** or add to **desktop right-click** menu

### Essential Apps (23)
Install popular apps via **winget** — browsers, 7-Zip, VLC, VS Code, and more. Revert Last uninstalls the previous batch.

### Activation Center
Windows & Office license status. MAS activator shortcuts (Windows 10 + 11).

### Fresh Windows Setup
One-click preset for a new PC — pick recommended tweaks + apps, run full setup.

### Restore Previous Settings
Tweak history is saved on your PC (survives app restarts):

| Button | What it does |
|--------|----------------|
| **Undo Last Batch** | Revert the most recent tweak apply |
| **Restore All Recorded** | Undo every tweak this app ever applied on this PC |
| **Reset Services & Defaults** | Turn SysMain, Windows Search, etc. back on — even without history |

### More
- **PC Manager** — install/open Microsoft PC Manager  
- **6 themes** — Light, Slate, Ocean, and more  
- **Live CPU / RAM / GPU** bars in sidebar  
- **Check for updates** — built-in GitHub release checker  
- **Activity log** — color-coded output  

---

## Update to latest version

**Inside the app:** Sidebar → **Check for updates**

**Or force download:**
```powershell
iex (iwr -useb https://raw.githubusercontent.com/nazmul-cyber/Nazmul-Tweaks-Tool/main/scripts/update.ps1)
```

---

## Quick fixes (Home page)

One-click presets: **Speed Up**, **Privacy Boost**, **Gaming Boost**, **Network Fix**, **Quick Debloat**, **Print Screen Fix**.

---

## Project structure

```
Nazmul-Tweaks-Tool/
├── main.py              # Entry point
├── src/                 # App UI + logic
├── scripts/             # PowerShell (open, update, refresh, tweaks)
├── assets/              # Logo & icons
└── release/             # Built EXE (local)
```

---

## Build from source

```bat
pip install -r requirements.txt
python main.py
```

Build EXE:
```bat
python build_exe.py
```

---

## Author

**MD Nazmul Hasan** — Entrepreneur & Web Developer · KUET

- GitHub: [@nazmul-cyber](https://github.com/nazmul-cyber)
- Portfolio: [portfolio-eight-red-48.vercel.app](https://portfolio-eight-red-48.vercel.app/projects.html)

MIT License — use freely, star the repo if it helps you.

---

<p align="center">
  <sub>Made with care for Windows users who just want their PC to work better.</sub>
</p>