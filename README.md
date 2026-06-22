# Nazmul Tweaks Tool

Free Windows optimizer — 38 tweaks, System Refresh, winget apps, MAS activation.

![Release](https://img.shields.io/github/v/release/nazmul-cyber/Nazmul-Tweaks-Tool?label=release)
![Platform](https://img.shields.io/badge/Windows-10%2F11-0078D6)
![Size](https://img.shields.io/badge/EXE-~19%20MB-teal)

---

## Open the app (copy all lines → PowerShell → paste → Enter)

Open **PowerShell** (normal is fine), select **all 5 lines** below, copy, paste, Enter.
The app will **download and open automatically**.

```powershell
$d="$env:LOCALAPPDATA\NazmulTweaksTool"
ni $d -ItemType Directory -Force | Out-Null
$e="$d\Nazmul Tweaks Tool.exe"
iwr "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe" -OutFile $e -UseBasicParsing
Unblock-File $e -ErrorAction SilentlyContinue
Start-Process $e
```

No `iex`. No pipe. No Admin needed just to open the app.

---

## Or: 1-line version

```powershell
$d="$env:LOCALAPPDATA\NazmulTweaksTool";ni $d -Force|Out-Null;$e="$d\Nazmul Tweaks Tool.exe";iwr "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe" -OutFile $e -UseBasicParsing;Unblock-File $e -EA 0;Start-Process $e
```

> **Security popup?** Click **Run**. Unsigned free software shows "Unknown Publisher" — that is normal. `Unblock-File` above reduces the warning.

---

## Or: download in browser

https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe

Double-click the downloaded file.

[![Download EXE](https://img.shields.io/badge/Download-EXE-0D9488?style=for-the-badge)](https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/Nazmul-Tweaks-Tool.exe)

---

## Features

- 38+ Windows tweaks (privacy, speed, debloat, gaming)
- System Refresh on desktop right-click
- 23 essential apps via winget
- MAS activation center
- 6 themes

**Tweaks need Run as Administrator** inside the app (UAC prompt).

## Author

**MD Nazmul Hasan** — [GitHub](https://github.com/nazmul-cyber)

MIT License