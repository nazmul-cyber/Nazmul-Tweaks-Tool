"""Fast PowerShell & winget executor."""

import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Callable

_PS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def _ps_has_error(output: str) -> bool:
    text = (output or "").lower()
    if "[err]" in text or "access is denied" in text or "access denied" in text:
        return True
    if "uac cancelled" in text or "elevation failed" in text:
        return True
    return False


def _tweak_output_ok(output: str) -> bool:
    if _ps_has_error(output):
        return False
    return "[ok]" in (output or "").lower()


def _write_ps1(script: str) -> Path:
    body = "$ErrorActionPreference='Continue'\n" + script.strip() + "\n"
    path = Path(tempfile.gettempdir()) / f"nazmul_{uuid.uuid4().hex}.ps1"
    path.write_text(body, encoding="utf-8")
    return path


def _ps(script: str, admin: bool = False) -> tuple[int, str]:
    """Run PowerShell. Elevates via UAC when admin=True and not already Admin."""
    ps1 = _write_ps1(script)
    log_path = Path(tempfile.gettempdir()) / f"nazmul_out_{uuid.uuid4().hex}.log"
    wrapped = _write_ps1(
        f'$log = "{log_path}"\n'
        "function Log-Line($m) { Write-Host $m; Add-Content -Path $log -Value $m -Encoding UTF8 }\n"
        f'try {{\n{script.strip()}\n}} catch {{\n'
        '    Log-Line "[ERR] $($_.Exception.Message)"\n'
        "    exit 1\n"
        "}\n"
    )
    try:
        need_elevate = admin and sys.platform == "win32" and not is_admin()
        if need_elevate:
            cmd = [
                "powershell", "-NoProfile", "-EP", "Bypass", "-Command",
                (
                    f"Start-Process -FilePath powershell.exe -Verb RunAs -Wait -WindowStyle Hidden "
                    f"-ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"{wrapped}\"'"
                ),
            ]
            r = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, creationflags=_PS_FLAGS,
            )
            if log_path.exists():
                out = log_path.read_text(encoding="utf-8", errors="replace").strip()
            else:
                out = ((r.stdout or "") + (r.stderr or "")).strip()
                if not out:
                    out = "[ERR] UAC cancelled or elevation failed — run Launch Admin.bat"
            code = 1 if _ps_has_error(out) else 0
            return code, out

        r = subprocess.run(
            ["powershell", "-NoProfile", "-EP", "Bypass", "-File", str(wrapped)],
            capture_output=True, text=True, timeout=180, creationflags=_PS_FLAGS,
        )
        if log_path.exists():
            out = log_path.read_text(encoding="utf-8", errors="replace").strip()
        else:
            out = ((r.stdout or "") + (r.stderr or "")).strip()
        code = r.returncode
        if _ps_has_error(out):
            code = 1
        return code, out
    except subprocess.TimeoutExpired:
        return -1, "[ERR] [TIMEOUT]"
    except Exception as e:
        return -1, f"[ERR] {e}"
    finally:
        ps1.unlink(missing_ok=True)
        wrapped.unlink(missing_ok=True)
        log_path.unlink(missing_ok=True)


def _run_elevated_batch_ps1(ps1_path: Path, log_path: Path, log: Callable[[str], None],
                             on_done=None, timeout_sec: int = 600) -> None:
    """Elevate one combined .ps1, stream log file back to UI."""
    log_path.write_text("", encoding="utf-8")
    started = time.time()
    cmd = [
        "powershell", "-NoProfile", "-EP", "Bypass", "-Command",
        (
            f"Start-Process -FilePath powershell.exe -Verb RunAs -Wait -WindowStyle Hidden "
            f"-ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"{ps1_path}\"'"
        ),
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30, creationflags=_PS_FLAGS)
    except Exception as e:
        log(f"[ERR] Could not start elevated PowerShell: {e}")
        if on_done:
            on_done()
        return

    last_size = 0
    while time.time() - started < timeout_sec:
        if log_path.exists():
            try:
                content = log_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                content = ""
            if len(content) > last_size:
                for line in content[last_size:].splitlines():
                    if line.strip():
                        log(line.strip())
                last_size = len(content)
            if "[BATCH_DONE]" in content:
                break
        time.sleep(0.4)

    if not log_path.exists() or log_path.stat().st_size == 0:
        log("[ERR] UAC cancelled or no output — use Launch Admin.bat and try again")
    if on_done:
        on_done()


def _ps_file(path: str, args: list[str] | None = None) -> tuple[int, str]:
    try:
        cmd = ["powershell", "-NoProfile", "-EP", "Bypass", "-File", path]
        if args:
            cmd.extend(args)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as e:
        return -1, str(e)


def run_tweak(script: str, name: str, log: Callable[[str], None]) -> bool:
    log(f"  → {name}")
    if not is_admin():
        log("    [INFO] Requesting Admin (UAC)...")
    code, out = _ps(script, admin=True)
    for line in (out or "").splitlines():
        if line.strip():
            log(f"    {line.strip()}")
    ok = _tweak_output_ok(out) and code == 0
    if not ok and "access denied" not in (out or "").lower():
        ok = _tweak_output_ok(out)
    log(f"    {'✓' if ok else '✗ FAILED'} {name}")
    return ok


def _build_tweak_batch_ps1(tasks, log_path: Path, prtsc_safeguard: bool = True) -> Path:
    from tweaks import PRTSC_SAFEGUARD_SCRIPT

    lines = [
        "$ErrorActionPreference='Continue'",
        f'$log = "{log_path}"',
        "function Log-Line($m) { Write-Host $m; Add-Content -Path $log -Value $m -Encoding UTF8 }",
        "Log-Line '[INFO] Elevated tweak batch started'",
    ]
    for i, (tid, name, payload) in enumerate(tasks, 1):
        lines.append(f"Log-Line '[{i}/{len(tasks)}] >> {name}'")
        lines.append(payload.strip())
    if prtsc_safeguard and tasks:
        lines.append("Log-Line '[SAFEGUARD] Print Screen key'")
        lines.append(PRTSC_SAFEGUARD_SCRIPT.strip())
    lines.append("Log-Line '[BATCH_DONE]'")
    ps1 = Path(tempfile.gettempdir()) / f"nazmul_batch_{os.getpid()}_{uuid.uuid4().hex}.ps1"
    ps1.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ps1


def run_elevated_tweak_batch(tasks, log, on_done=None, prtsc_safeguard: bool = True,
                             save_session: bool = True):
    """Run all tweaks in one UAC prompt when app is not Admin."""
    log_path = Path(tempfile.gettempdir()) / "nazmul_tweak_batch.log"
    ps1 = _build_tweak_batch_ps1(tasks, log_path, prtsc_safeguard)

    def worker():
        log(f"\n{'─'*40}\n  Starting {len(tasks)} tweak(s) as Admin...\n{'─'*40}")
        log("[INFO] Allow the UAC prompt to apply tweaks")

        def finished():
            content = ""
            if log_path.exists():
                content = log_path.read_text(encoding="utf-8", errors="replace")
            ok = len([ln for ln in content.splitlines() if "[OK]" in ln])
            fail = len([ln for ln in content.splitlines() if "[ERR]" in ln])
            log(f"\n{'─'*40}\n  Done: {ok} OK, {fail} failed\n{'─'*40}")
            if save_session and ok:
                try:
                    from session_history import save_last_session
                    succeeded = []
                    for tid, name, _ in tasks:
                        marker = f">> {name}"
                        idx = content.find(marker)
                        if idx < 0:
                            continue
                        end = len(content)
                        for _, other_name, _ in tasks:
                            if other_name == name:
                                continue
                            oidx = content.find(f">> {other_name}", idx + len(marker))
                            if 0 <= oidx < end:
                                end = oidx
                        if "[OK]" in content[idx:end]:
                            succeeded.append({"id": tid, "name": name})
                    if succeeded:
                        save_last_session("tweak", succeeded)
                        log("[INFO] Saved last tweak session — use Revert Last to undo")
                except Exception:
                    pass
            if on_done:
                on_done()

        _run_elevated_batch_ps1(ps1, log_path, log, on_done=finished)
        try:
            ps1.unlink(missing_ok=True)
        except OSError:
            pass

    threading.Thread(target=worker, daemon=True).start()


def run_winget(wid: str, name: str, log: Callable[[str], None]) -> bool:
    log(f"  → Installing {name}...")
    try:
        r = subprocess.run(
            ["winget", "install", "--id", wid, "-e",
             "--accept-source-agreements", "--accept-package-agreements",
             "--disable-interactivity", "--silent"],
            capture_output=True, text=True, timeout=600,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        out = (r.stdout or "") + (r.stderr or "")
        for line in out.splitlines()[-4:]:
            if line.strip():
                log(f"    {line.strip()}")
        ok = r.returncode in (0, -1978335189, -1978335212, 2316632107)
        log(f"    {'✓' if ok else '⚠'} {name}")
        return ok
    except FileNotFoundError:
        log("    ✗ winget not found")
        return False


def run_winget_uninstall(wid: str, name: str, log: Callable[[str], None]) -> bool:
    log(f"  → Uninstalling {name}...")
    try:
        r = subprocess.run(
            ["winget", "uninstall", "--id", wid, "-e",
             "--accept-source-agreements", "--disable-interactivity", "--silent"],
            capture_output=True, text=True, timeout=600,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        out = (r.stdout or "") + (r.stderr or "")
        out_l = out.lower()
        for line in out.splitlines()[-4:]:
            if line.strip():
                log(f"    {line.strip()}")
        ok = (
            r.returncode in (0, -1978335189, -1978335212, 2316632107)
            or "not installed" in out_l
            or "no installed package found" in out_l
        )
        log(f"    {'✓' if ok else '⚠'} {name}")
        return ok
    except FileNotFoundError:
        log("    ✗ winget not found")
        return False


def run_activation(action: str, log: Callable[[str], None], key: str = "") -> bool:
    import shutil
    from paths import get_scripts, get_root, get_data

    script = get_scripts() / "activation.ps1"
    keys_dest = get_scripts() / "activation_keys.txt"
    keys_src = get_data() / "activation_keys.txt"
    if keys_src.exists():
        try:
            shutil.copy2(keys_src, keys_dest)
        except Exception:
            pass

    data_src = get_root() / "data"
    if data_src.exists():
        dest = get_scripts().parent / "data"
        if not dest.exists():
            try:
                shutil.copytree(data_src, dest)
            except Exception:
                pass

    if not script.exists():
        log("[ERR] activation.ps1 not found")
        return False

    log(f"[INFO] Running activation ({action})...")
    ps_args = ["-Action", action]
    if key:
        ps_args.extend(["-ProductKey", key])

    if is_admin():
        code, out = _ps_file(str(script), ps_args)
    else:
        log("[WARN] Not running as Admin - activation may fail")
        code, out = _ps_file(str(script), ps_args)

    if not out:
        log("[WARN] No activation output - check Admin rights")
        return False

    for line in out.splitlines():
        if line.strip():
            log(line.strip())
    return code == 0 or "[OK]" in out or "ACTIVATED" in out.upper() or "MAS window" in out


def _apply_prtsc_safeguard(log: Callable[[str], None]) -> bool:
    """Re-enable Print Screen → Snipping Tool after tweak batches."""
    from tweaks import PRTSC_SAFEGUARD_SCRIPT

    log("\n[SAFEGUARD] Protecting Print Screen key...")
    return run_tweak(PRTSC_SAFEGUARD_SCRIPT, "PrtSc Safeguard", log)


def run_batch(tasks, log, on_done=None, kind="tweak", prtsc_safeguard: bool = True,
              save_session: bool = True):
    if kind == "tweak" and tasks and not is_admin():
        run_elevated_tweak_batch(
            tasks, log, on_done=on_done, prtsc_safeguard=prtsc_safeguard, save_session=save_session,
        )
        return

    def worker():
        ok = 0
        succeeded: list[dict] = []
        log(f"\n{'─'*40}\n  Starting {len(tasks)} task(s)...\n{'─'*40}")
        if kind == "tweak":
            log("[INFO] Running as Administrator")
        for i, (tid, name, payload) in enumerate(tasks, 1):
            log(f"\n[{i}/{len(tasks)}]")
            if kind == "tweak":
                success = run_tweak(payload, name, log)
            elif kind == "app":
                success = run_winget(payload, name, log)
            else:
                success = False
            if success:
                ok += 1
                entry = {"id": tid, "name": name}
                if kind == "app":
                    entry["winget_id"] = payload
                succeeded.append(entry)
        extra = 1 if kind == "tweak" and tasks and prtsc_safeguard else 0
        if kind == "tweak" and tasks and prtsc_safeguard:
            if _apply_prtsc_safeguard(log):
                ok += 1
        log(f"\n{'─'*40}\n  Done: {ok}/{len(tasks) + extra} succeeded\n{'─'*40}")
        if save_session and succeeded and kind in ("tweak", "app"):
            try:
                from session_history import save_last_session
                save_last_session(kind, succeeded)
                log(f"[INFO] Saved last {kind} session — use Revert Last to undo")
            except Exception:
                pass
        if on_done:
            on_done()
    threading.Thread(target=worker, daemon=True).start()


def run_revert_batch(items, log, on_done=None, kind="tweak"):
    """Undo last tweak batch or uninstall last installed apps."""
    from tweaks import get_undo_script, NO_UNDO_IDS

    if kind == "tweak" and not is_admin():
        tasks = []
        for item in items:
            tid = item.get("id", "")
            name = item.get("name", tid)
            if tid in NO_UNDO_IDS:
                log(f"[SKIP] {name} — cannot auto-revert")
                continue
            script = get_undo_script(tid)
            if script:
                tasks.append((tid, f"Revert: {name}", script))
        if not tasks:
            log("[INFO] Nothing to revert")
            if on_done:
                on_done()
            return

        def _done():
            try:
                from session_history import clear_last_session
                clear_last_session("tweak")
            except Exception:
                pass
            if on_done:
                on_done()

        run_elevated_tweak_batch(
            tasks, log, on_done=_done, prtsc_safeguard=False, save_session=False,
        )
        return

    def worker():
        ok = 0
        total = len(items)
        log(f"\n{'─'*40}\n  Reverting {total} item(s)...\n{'─'*40}")
        for i, item in enumerate(items, 1):
            tid = item.get("id", "")
            name = item.get("name", tid)
            log(f"\n[{i}/{total}]")
            if kind == "app":
                wid = item.get("winget_id", "")
                if not wid:
                    log(f"    [SKIP] {name} — missing winget id")
                    continue
                if run_winget_uninstall(wid, name, log):
                    ok += 1
            elif kind == "tweak":
                if tid in NO_UNDO_IDS:
                    log(f"    [SKIP] {name} — cannot auto-revert (manual action needed)")
                    continue
                script = get_undo_script(tid)
                if not script:
                    log(f"    [SKIP] {name} — no undo script available")
                    continue
                if run_tweak(script, f"Revert: {name}", log):
                    ok += 1
        log(f"\n{'─'*40}\n  Revert done: {ok}/{total} succeeded\n{'─'*40}")
        if ok and kind in ("tweak", "app"):
            try:
                from session_history import clear_last_session
                clear_last_session(kind)
            except Exception:
                pass
        if on_done:
            on_done()
    threading.Thread(target=worker, daemon=True).start()


def check_winget() -> bool:
    try:
        return subprocess.run(["winget", "-v"], capture_output=True, timeout=8,
                              creationflags=subprocess.CREATE_NO_WINDOW).returncode == 0
    except Exception:
        return False


def is_admin() -> bool:
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_admin():
    import ctypes
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                        " ".join(f'"{a}"' for a in sys.argv), None, 1)


def get_activation_status() -> dict:
    """Return Windows, Office and Microsoft Apps status."""
    import json
    from paths import get_scripts

    default = {
        "windows": {"edition": "Checking...", "build": "", "version": "", "license": "..."},
        "office": {"product": "Checking...", "installed": "...", "license": "..."},
        "apps": [],
    }

    script = get_scripts() / "status.ps1"
    if not script.exists():
        return default

    code, out = _ps_file(str(script))
    if not out:
        err = {
            "windows": {"edition": "Status unavailable", "build": "", "version": "", "license": "Unknown"},
            "office": {"product": "Status unavailable", "installed": "?", "license": "Unknown"},
            "apps": [],
        }
        return err

    try:
        start = out.find("{")
        end = out.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(out[start:end])
            if isinstance(data, dict) and "windows" in data:
                return data
    except json.JSONDecodeError:
        pass

    return {
        "windows": {"edition": "Parse error", "build": "", "version": "", "license": "Unknown"},
        "office": {"product": "Parse error", "installed": "?", "license": "Unknown"},
        "apps": [],
    }


def _winget_ok(returncode: int) -> bool:
    return returncode in (0, -1978335189, -1978335212, 2316632107)


def _winget_install_succeeded(returncode: int, output: str) -> bool:
    out_l = (output or "").lower()
    if "no package found" in out_l or "no applicable" in out_l or "not found matching" in out_l:
        return False
    if "already installed" in out_l:
        return True
    return returncode == 0


def is_pc_manager_installed() -> bool:
    code, out = _ps(
        r"""
        if (Get-AppxPackage -Name '*PCManager*' -EA 0) { Write-Host 'yes'; exit 0 }
        $r = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
            'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*' -EA 0 |
            Where-Object { $_.DisplayName -match 'PC Manager' }
        if ($r) { Write-Host 'yes'; exit 0 }
        exit 1
        """
    )
    return code == 0 or "yes" in (out or "").lower()


_pc_manager_installed = is_pc_manager_installed


def open_pc_manager() -> bool:
    code, _ = _ps(
        r"""
        $app = Get-StartApps | Where-Object { $_.Name -match 'PC Manager' } | Select-Object -First 1
        if ($app) {
            Start-Process explorer.exe "shell:appsFolder\$($app.AppID)"
            exit 0
        }
        exit 1
        """
    )
    return code == 0


def install_pc_manager(log: Callable[[str], None]) -> str:
    """Install PC Manager. Returns: installed | already | store | no_winget | failed."""
    from paths import get_scripts

    if is_pc_manager_installed():
        log("[OK] Microsoft PC Manager already installed on this PC")
        log("[INFO] Open it from the Start Menu (search PC Manager)")
        return "already"

    if not check_winget():
        log("[WARN] winget not found — App Installer required (Microsoft Store)")
        log("[INFO] Step 1: Install App Installer from the Store")
        log("[INFO] Step 2: Then try PC Manager install again")
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command",
             "Start-Process 'ms-windows-store://pdp/?productid=9NBLGGH4NNS1'; "
             "Start-Sleep 2; "
             "Start-Process 'ms-windows-store://pdp/?productid=9PM860492SZD'"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        log("[INFO] Store opened — App Installer + PC Manager page")
        return "no_winget"

    log("[INFO] Installing Microsoft PC Manager (auto try winget + Store)...")
    script = get_scripts() / "install_pcmanager.ps1"
    if script.exists():
        code, out = _ps_file(str(script))
        for line in (out or "").splitlines():
            if line.strip():
                log(f"  {line.strip()}")
        out_l = (out or "").lower()
        if is_pc_manager_installed():
            if "already installed" in out_l:
                return "already"
            return "installed"
        if "store page opened" in out_l or "not installed yet" in out_l:
            log("[INFO] Automatic install failed — click Install in the Store window")
            return "store"

    attempts = [
        (["winget", "install", "-e", "--id", "Microsoft.PCManager",
          "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity"],
         "Microsoft.PCManager"),
        (["winget", "install", "-e", "--id", "9PM860492SZD", "--source", "msstore",
          "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity"],
         "Store 9PM860492SZD"),
        (["winget", "install", "--name", "Microsoft PC Manager",
          "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity"],
         "by name"),
    ]
    try:
        for cmd, label in attempts:
            log(f"  -> Trying {label}...")
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            out = (r.stdout or "") + (r.stderr or "")
            for line in out.splitlines()[-8:]:
                if line.strip():
                    log(f"    {line.strip()}")
            if _winget_install_succeeded(r.returncode, out) and is_pc_manager_installed():
                log("[OK] Microsoft PC Manager installed")
                return "installed"

        log("[WARN] Opening Microsoft Store...")
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command",
             "Start-Process 'ms-windows-store://pdp/?productid=9PM860492SZD'"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        log("[INFO] Store opened — click Install (same steps for all users)")
        return "store"
    except FileNotFoundError:
        log("[ERR] winget not found — install App Installer from the Store")
        return "no_winget"
    except Exception as e:
        log(f"[ERR] {e}")
        return "failed"


def _desktop_refresh_command() -> str:
    import sys
    from paths import get_app_dir

    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}" --system-refresh'
    launcher = get_app_dir() / "SystemRefresh.cmd"
    return f'"{launcher.resolve()}"'


def get_system_stats() -> dict:
    import json
    from paths import get_scripts

    default = {
        "cpu_pct": 0,
        "gpu_pct": 0,
        "ram": {"total_mb": 0, "free_mb": 0, "used_mb": 0, "used_pct": 0},
    }
    script = get_scripts() / "sysstats.ps1"
    if not script.exists():
        return default
    _, out = _ps_file(str(script))
    if not out:
        return default
    try:
        start = out.find("{")
        end = out.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(out[start:end])
            if isinstance(data, dict):
                return data
    except json.JSONDecodeError:
        pass
    return default


def parse_refresh_stats(output: str) -> dict:
    import json

    for line in (output or "").splitlines():
        if "[STATS]" in line:
            chunk = line.split("[STATS]", 1)[-1].strip()
            try:
                return json.loads(chunk)
            except json.JSONDecodeError:
                pass
    return {}


def run_system_refresh_cli() -> int:
    """Run from Windows desktop right-click (no GUI)."""
    from paths import get_scripts

    script = get_scripts() / "refresh.ps1"
    if not script.exists():
        _ps("Write-Host 'refresh.ps1 missing'")
        return 1
    code, out = _ps_file(str(script))
    if code != 0:
        code, out = _ps_file(str(script))
    stats = parse_refresh_stats(out)
    freed = stats.get("ram_freed_mb", 0)
    after = stats.get("ram_after_free", "?")
    _ps(
        rf"""
        Add-Type -AssemblyName System.Windows.Forms
        $m = "Refresh complete!`n`nRAM freed: {freed} MB`nFree now: {after} MB`nApps still open."
        [System.Windows.Forms.MessageBox]::Show($m, 'System Refresh') | Out-Null
        """
    )
    return 0 if code == 0 or "[OK]" in (out or "") else code


def _desktop_refresh_registry_bases() -> tuple[str, ...]:
    marker = "NazmulSystemRefresh"
    return (
        rf"Software\Classes\DesktopBackground\Shell\{marker}",
        rf"Software\Classes\Directory\Background\shell\{marker}",
    )


def _delete_registry_tree(root, path: str) -> bool:
    import winreg

    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS)
    except OSError:
        return False
    while True:
        try:
            sub = winreg.EnumKey(key, 0)
            _delete_registry_tree(root, f"{path}\\{sub}")
        except OSError:
            break
    winreg.CloseKey(key)
    try:
        winreg.DeleteKey(root, path)
        return True
    except OSError:
        return False


def _refresh_windows_shell() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
    except Exception:
        pass


def is_windows_desktop_refresh_installed() -> bool:
    import winreg

    for base in _desktop_refresh_registry_bases():
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base):
                return True
        except OSError:
            continue
    return False


def _remove_desktop_refresh_registry() -> bool:
    import winreg

    if not is_windows_desktop_refresh_installed():
        return True
    removed_any = False
    for base in _desktop_refresh_registry_bases():
        if _delete_registry_tree(winreg.HKEY_CURRENT_USER, base):
            removed_any = True
    _refresh_windows_shell()
    return removed_any or not is_windows_desktop_refresh_installed()


def install_windows_desktop_refresh(log: Callable[[str], None]) -> bool:
    from paths import get_assets, get_scripts

    script = get_scripts() / "install_desktop_menu.ps1"
    if not script.exists():
        log("[ERR] install_desktop_menu.ps1 not found")
        return False
    icon = get_assets() / "logo.ico"
    icon_str = str(icon.resolve()) if icon.exists() else "imageres.dll,-1043"
    cmd = _desktop_refresh_command()
    code, out = _ps_file(str(script), ["-Command", cmd, "-Icon", icon_str])
    for line in (out or "").splitlines():
        if line.strip():
            log(f"  {line.strip()}")
    return code == 0 and "[OK]" in (out or "")


def remove_windows_desktop_refresh(log: Callable[[str], None] | None = None) -> bool:
    from paths import get_scripts

    def _log(m):
        if log:
            log(m)

    if not is_windows_desktop_refresh_installed():
        _log("[INFO] System Refresh is not on the Windows menu")
        return True

    if _remove_desktop_refresh_registry():
        _log("[OK] System Refresh removed from Windows right-click")
        return True

    script = get_scripts() / "install_desktop_menu.ps1"
    if script.exists():
        code, out = _ps_file(str(script), ["-Remove"])
        for line in (out or "").splitlines():
            if line.strip():
                _log(f"  {line.strip()}")
        if code == 0 and not is_windows_desktop_refresh_installed():
            _refresh_windows_shell()
            return True

    if not is_windows_desktop_refresh_installed():
        _log("[OK] System Refresh removed from Windows right-click")
        return True

    _log("[ERR] Could not remove System Refresh from Windows menu")
    return False