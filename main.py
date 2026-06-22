"""
Nazmul Tweaks Tool — entry point.
"""

import sys
import traceback
from pathlib import Path

if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS)
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parent
    sys.path.insert(0, str(ROOT / "src"))

LOG_FILE = ROOT / "launch.log"


def log(msg: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def show_error(msg: str):
    log(f"ERROR: {msg}")
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Nazmul Tweaks Tool — Error", msg)
        root.destroy()
    except Exception:
        print(msg, file=sys.stderr)


def run_app():
    log("Starting Nazmul Tweaks Tool...")
    try:
        import customtkinter as ctk
        from app import NazmulApp
        app = NazmulApp()
        log("App loaded OK")
        app.mainloop()
    except Exception:
        err = traceback.format_exc()
        log(err)
        show_error(
            "Failed to start Nazmul Tweaks Tool.\n\n"
            f"Log: {LOG_FILE}\n\n"
            "Try running Launch.bat first to install dependencies.\n\n"
            f"{err[-600:]}"
        )


def run_system_refresh():
    try:
        from executor import run_system_refresh_cli
        run_system_refresh_cli()
    except Exception:
        show_error(traceback.format_exc()[-800:])


if __name__ == "__main__":
    try:
        if "--system-refresh" in sys.argv:
            run_system_refresh()
            sys.exit(0)
        LOG_FILE.write_text("", encoding="utf-8")
        run_app()
    except Exception:
        show_error(traceback.format_exc()[-800:])