"""Check GitHub Releases and download the latest EXE."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Callable

from version import APP_VERSION

GITHUB_API = (
    "https://api.github.com/repos/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest"
)
EXE_URL = (
    "https://github.com/nazmul-cyber/Nazmul-Tweaks-Tool/releases/latest/download/"
    "Nazmul-Tweaks-Tool.exe"
)
UPDATE_SCRIPT_URL = (
    "https://raw.githubusercontent.com/nazmul-cyber/"
    "Nazmul-Tweaks-Tool/main/scripts/update.ps1"
)


def parse_version(tag: str) -> tuple[int, ...]:
    match = re.search(r"(\d+(?:\.\d+)*)", tag or "")
    if not match:
        return (0,)
    return tuple(int(part) for part in match.group(1).split("."))


def check_for_updates(timeout: int = 12) -> dict:
    current = APP_VERSION
    result = {
        "current": current,
        "latest": current,
        "update_available": False,
        "url": EXE_URL,
        "notes": "",
        "error": None,
    }
    try:
        req = urllib.request.Request(
            GITHUB_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": f"Nazmul-Tweaks-Tool/{current}",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        latest = (data.get("tag_name") or "").lstrip("v")
        result["latest"] = latest or current
        result["notes"] = (data.get("body") or "").strip()
        result["update_available"] = parse_version(latest) > parse_version(current)
    except Exception as exc:
        result["error"] = str(exc)
    return result


def download_update(
    dest: Path | None = None,
    log: Callable[[str], None] | None = None,
    timeout: int = 600,
) -> Path | None:
    def _log(msg: str):
        if log:
            log(msg)

    target = dest or (Path(tempfile.gettempdir()) / "Nazmul-Tweaks-Tool-new.exe")
    target.parent.mkdir(parents=True, exist_ok=True)
    _log(f"[INFO] Downloading update to {target}...")
    try:
        req = urllib.request.Request(
            EXE_URL,
            headers={"User-Agent": f"Nazmul-Tweaks-Tool/{APP_VERSION}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        if len(data) < 500_000:
            _log("[ERR] Download too small — update failed")
            return None
        target.write_bytes(data)
        _log(f"[OK] Downloaded {len(data) // (1024 * 1024)} MB")
        return target
    except Exception as exc:
        _log(f"[ERR] Download failed: {exc}")
        return None


def launch_update(exe_path: Path) -> bool:
    import subprocess

    if not exe_path.exists():
        return False
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", f'Unblock-File "{exe_path}" -EA 0'],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        subprocess.Popen([str(exe_path)], cwd=str(exe_path.parent))
        return True
    except Exception:
        return False