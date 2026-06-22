"""Build Nazmul Tweaks Tool as standalone EXE for GitHub Releases."""

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
SRC = ROOT / "src"

# Bundle as Python modules (NOT --add-data) so stdlib imports work in frozen EXE.
HIDDEN_IMPORTS = [
    "app", "executor", "themes", "tweaks", "apps", "paths", "version", "updater",
    "ui_helpers", "animations", "color_log", "resource_bar", "session_history",
    "customtkinter", "PIL", "PIL._tkinter_finder", "PIL.Image", "PIL.ImageTk",
    "darkdetect", "uuid", "winreg", "ctypes", "json", "threading", "tempfile",
    "dataclasses", "pathlib", "typing", "re", "datetime",
]

EXCLUDES = [
    "numpy", "matplotlib", "pandas", "scipy", "pytest",
    "setuptools", "distutils", "tkinter.test",
]


def ensure_logo():
    if not (ASSETS / "logo.ico").exists():
        print("Generating logo...")
        subprocess.run([sys.executable, str(ROOT / "generate_logo.py")], check=True)


def _format_size(path: Path) -> str:
    size = path.stat().st_size
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB ({size:,} bytes)"
    if size >= 1024:
        return f"{size / 1024:.2f} KB ({size:,} bytes)"
    return f"{size:,} bytes"


def verify_exe(exe: Path) -> bool:
    """Smoke-test: EXE must stay alive 5s without error dialog."""
    print("Verifying EXE launches...")
    proc = subprocess.Popen([str(exe)], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
    time.sleep(5)
    code = proc.poll()
    if code is not None and code != 0:
        print(f"  FAIL: EXE exited immediately with code {code}")
        log = ROOT / "launch.log"
        if log.exists():
            print(log.read_text(encoding="utf-8", errors="replace")[-800:])
        return False
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("  OK: EXE launched and ran 5 seconds")
    return True


def build():
    ensure_logo()
    icon = ASSETS / "logo.ico"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Nazmul Tweaks Tool",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--noupx",
        "--paths", str(SRC),
        "--collect-all", "customtkinter",
        "--add-data", f"{ASSETS};assets",
        "--add-data", f"{ROOT / 'scripts'};scripts",
        "--add-data", f"{ROOT / 'data'};data",
    ]
    for mod in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", mod]
    for mod in EXCLUDES:
        cmd += ["--exclude-module", mod]
    if icon.exists():
        cmd += ["--icon", str(icon)]
    cmd.append(str(ROOT / "main.py"))

    print("Building EXE...")
    subprocess.run(cmd, cwd=str(ROOT), check=True)

    exe = ROOT / "dist" / "Nazmul Tweaks Tool.exe"
    release = ROOT / "release" / "Nazmul-Tweaks-Tool.exe"
    release.parent.mkdir(exist_ok=True)
    if not exe.exists():
        raise FileNotFoundError(f"Build finished but EXE not found: {exe}")

    shutil.copy2(exe, release)

    if not verify_exe(release):
        raise RuntimeError("EXE verification failed — fix build before publishing")

    print("\nEXE ready:")
    for artifact in (icon, exe, release):
        print(f"  {artifact}")
        print(f"    size: {_format_size(artifact)}")

    (ROOT / "build-result.txt").write_text(
        "\n".join(f"{p}\t{p.stat().st_size}" for p in (icon, exe, release)) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()