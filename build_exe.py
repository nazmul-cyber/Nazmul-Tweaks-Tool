"""Build Nazmul Tweaks Tool as standalone EXE for GitHub Releases."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"


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
        "--collect-all", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
        "--add-data", f"{ASSETS};assets",
        "--add-data", f"{ROOT / 'scripts'};scripts",
        "--add-data", f"{ROOT / 'data'};data",
        "--add-data", f"{ROOT / 'src'};src",
    ]
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
    print("\nEXE ready:")
    lines = []
    for artifact in (icon, exe, release):
        print(f"  {artifact}")
        print(f"    size: {_format_size(artifact)}")
        lines.append(f"{artifact}\t{artifact.stat().st_size}")

    (ROOT / "build-result.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()