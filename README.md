<p align="center">
  <img src="assets/logo.png" alt="Nazmul Tweaks Tool" width="120">
</p>

<h1 align="center">Nazmul Tweaks Tool</h1>

<p align="center">
  <strong>Free, open-source Windows optimizer for everyone.</strong><br>
  One PowerShell line → app opens. No install wizard. No Python needed.
</p>

<p align="center">
  <a href="https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest">v1.0.15</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe">Download</a>
  &nbsp;·&nbsp;
  ~19 MB
  &nbsp;·&nbsp;
  <a href="https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/blob/main/LICENSE">MIT License</a>
</p>

---

## Project purpose

> Help everyday users **speed up, clean, and fix** Windows 10/11 — one click, no install wizard, 100% free.

Built by **[MD Nazmul Hasan](https://github.com/nazmul-cyber)** so anyone can tweak, refresh, and restore their PC like pro tools — but simpler.

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

### Tweak Back
Every applied tweak is saved on your PC (survives app restarts). Open **Tweak Back** in the sidebar — same list style as Tweaks:

- Shows only tweaks you already applied (icon, name, description)
- Check to **revert** — uncheck to keep
- Category filters, **All** / **None** / **Revert Checked**
- Tweaks without undo scripts show as **(manual only)**

### More
- **PC Manager** — install/open Microsoft PC Manager  
- **Light theme** — clean, fast UI
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