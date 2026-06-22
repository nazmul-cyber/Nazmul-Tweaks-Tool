"""UI helpers - scroll, buttons, themes."""

import time
import tkinter as tk
import customtkinter as ctk
from themes import Theme, FONT_SMALL, btn_text_color

_THEME_COLOR_FIELDS = (
    "bg", "sidebar", "card", "card_hover", "card_border", "primary", "primary_hover",
    "primary_light", "accent", "accent_hover", "text", "text_muted", "success", "warning",
    "error", "log_bg", "input_bg", "btn_secondary", "btn_secondary_text", "shadow",
    "nav_active_bg", "nav_active_text", "highlight",
)

_WIDGET_COLOR_PROPS = (
    "fg_color", "text_color", "hover_color", "border_color", "button_color",
    "button_hover_color", "scrollbar_button_color", "scrollbar_button_hover_color",
    "progress_color", "checkmark_color", "text_color_disabled",
)


def _theme_color_map(old: Theme, new: Theme) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for field in _THEME_COLOR_FIELDS:
        ov = getattr(old, field, "")
        nv = getattr(new, field, "")
        if isinstance(ov, str) and ov.startswith("#") and ov.lower() != nv.lower():
            mapping[ov.lower()] = nv
    mapping["#ffffff"] = "#FFFFFF"
    mapping["#0f172a"] = "#0F172A"
    return mapping


def _remap_color(value, cmap: dict[str, str]):
    if value in (None, "", "transparent"):
        return value
    if isinstance(value, (list, tuple)):
        return type(value)(_remap_color(v, cmap) for v in value)
    if isinstance(value, str) and value.startswith("#"):
        return cmap.get(value.lower(), value)
    return value


def apply_theme_live(root: tk.Misc, old: Theme, new: Theme) -> None:
    """Recolor widgets in place — no UI rebuild."""
    cmap = _theme_color_map(old, new)

    def walk(widget):
        for prop in _WIDGET_COLOR_PROPS:
            try:
                current = widget.cget(prop)
            except Exception:
                continue
            updated = _remap_color(current, cmap)
            if updated != current:
                try:
                    widget.configure(**{prop: updated})
                except Exception:
                    pass
        if isinstance(widget, tk.Text):
            try:
                widget.configure(
                    bg=_remap_color(widget.cget("bg"), cmap),
                    fg=_remap_color(widget.cget("fg"), cmap),
                    insertbackground=_remap_color(widget.cget("insertbackground"), cmap),
                    selectbackground=_remap_color(widget.cget("selectbackground"), cmap),
                )
            except Exception:
                pass
        for child in widget.winfo_children():
            walk(child)

    walk(root)


def delta_to_scroll_units(delta: int) -> int:
    """Map wheel delta to scroll units — one clean step per tick."""
    if delta == 0:
        return 0
    if abs(delta) < 120:
        return -1 if delta > 0 else 1
    return int(round(-delta / 36))


def native_scroll_widget(widget, delta: int) -> bool:
    """Immediate unit scroll (no chunked pixel animation)."""
    units = delta_to_scroll_units(delta)
    if units == 0:
        return False
    try:
        widget.yview_scroll(units, "units")
        return True
    except tk.TclError:
        return False
    except Exception:
        return False


def _scroll_target_from_event(event):
    w = event.widget
    while w:
        if isinstance(w, ctk.CTkScrollableFrame):
            return w._parent_canvas
        if isinstance(w, tk.Text):
            return w
        nested = getattr(w, "_text", None)
        if isinstance(nested, tk.Text):
            return nested
        try:
            w = w.master
        except Exception:
            break
    return None


def setup_global_scroll(root, get_scroll_fn):
    """Native wheel scroll — one motion per tick, no stutter."""

    def on_scroll(event):
        target = _scroll_target_from_event(event)
        if target is None:
            scroll_frame = get_scroll_fn()
            if scroll_frame and hasattr(scroll_frame, "_parent_canvas"):
                target = scroll_frame._parent_canvas
        if target and native_scroll_widget(target, event.delta):
            return "break"

    root.bind_all("<MouseWheel>", on_scroll, add="+")
    root.bind_all(
        "<Button-4>",
        lambda e: on_scroll(type("E", (), {"widget": e.widget, "delta": 120})()),
        add="+",
    )
    root.bind_all(
        "<Button-5>",
        lambda e: on_scroll(type("E", (), {"widget": e.widget, "delta": -120})()),
        add="+",
    )


def scroll_widget(scroll_frame, event):
    return native_scroll_widget(scroll_frame._parent_canvas, event.delta)


def sync_scroll_frame_width(scroll_frame) -> None:
    """Keep CTkScrollableFrame canvas width in sync after window resize/maximize."""
    try:
        w = scroll_frame.winfo_width()
        if w > 40:
            scroll_frame._parent_canvas.configure(width=w)
            scroll_frame._parent_frame.update_idletasks()
    except Exception:
        pass


def make_scroll(parent, theme: Theme, **kw) -> ctk.CTkScrollableFrame:
    return ctk.CTkScrollableFrame(
        parent,
        fg_color="transparent",
        scrollbar_button_color=theme.primary,
        scrollbar_button_hover_color=theme.primary_hover,
        **kw,
    )


def two_column_grid(parent, pairs):
    """Place (widget_factory) items in a 2-column grid."""
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)
    for i, build_fn in enumerate(pairs):
        r, c = divmod(i, 2)
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
        build_fn(cell)


def colored_btn(parent, text, command, theme: Theme, bg_color, width=120, height=34):
    return ctk.CTkButton(
        parent, text=text, width=width, height=height, corner_radius=10,
        font=FONT_SMALL, command=command,
        fg_color=bg_color, hover_color=theme.primary_hover,
        text_color=btn_text_color(bg_color, theme),
    )


def secondary_btn(parent, text, command, theme: Theme, width=100):
    bg = theme.btn_secondary
    return ctk.CTkButton(
        parent, text=text, width=width, height=34, corner_radius=8,
        font=FONT_SMALL, command=command,
        fg_color=bg, text_color=theme.btn_secondary_text,
        hover_color=theme.card_hover, border_width=1, border_color=theme.card_border,
    )


def primary_btn(parent, text, command, theme: Theme, color, width=120):
    return colored_btn(parent, text, command, theme, color, width=width)


def category_chips(parent, categories, variable, command, theme: Theme):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    buttons = {}

    def select(cat):
        variable.set(cat)
        for name, btn in buttons.items():
            active = name == cat
            bg = theme.primary if active else theme.btn_secondary
            btn.configure(
                fg_color=bg,
                text_color="#FFFFFF" if active else theme.btn_secondary_text,
                hover_color=theme.primary_hover if active else theme.card_hover,
            )
        command()

    for cat in categories:
        active = cat == variable.get()
        bg = theme.primary if active else theme.btn_secondary
        btn = ctk.CTkButton(
            frame, text=cat, height=30, corner_radius=15,
            font=FONT_SMALL, width=max(72, len(cat) * 9),
            fg_color=bg,
            text_color="#FFFFFF" if active else theme.btn_secondary_text,
            hover_color=theme.primary_hover if active else theme.card_hover,
            command=lambda c=cat: select(c),
        )
        btn.pack(side="left", padx=3, pady=2)
        buttons[cat] = btn

    return frame, buttons


def get_install_script_path():
    from paths import get_scripts
    return get_scripts() / "install.ps1"


def get_activation_script_path():
    from paths import get_scripts
    return get_scripts() / "activation.ps1"


def get_refresh_script_path():
    from paths import get_scripts
    return get_scripts() / "refresh.ps1"


OPEN_SCRIPT_URL = (
    "https://raw.githubusercontent.com/nazmul-cyber/"
    "Nazmul-Tweaks-Tool/main/scripts/open.ps1"
)

UPDATE_SCRIPT_URL = (
    "https://raw.githubusercontent.com/nazmul-cyber/"
    "Nazmul-Tweaks-Tool/main/scripts/update.ps1"
)


def get_install_command() -> str:
    return f"iex (iwr -useb {OPEN_SCRIPT_URL})"


def launch_public_install() -> bool:
    """Chris Titus style: run open.ps1, app window opens."""
    import subprocess
    import sys

    inner = f"iex (iwr -useb '{OPEN_SCRIPT_URL}')"
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", inner],
            creationflags=flags,
        )
        return True
    except Exception:
        return False


def launch_update_script() -> bool:
    """Force-download latest EXE via update.ps1."""
    import subprocess
    import sys

    inner = f"iex (iwr -useb '{UPDATE_SCRIPT_URL}')"
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", inner],
            creationflags=flags,
        )
        return True
    except Exception:
        return False


def _shell_elevate(executable: str, params: str) -> bool:
    import ctypes
    ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
    return ret > 32


def launch_elevated_ps1(script_path) -> bool:
    script = str(script_path)
    params = f'-NoProfile -ExecutionPolicy Bypass -File "{script}"'
    return _shell_elevate("powershell.exe", params)


def launch_elevated_activation(action: str, key: str = "") -> bool:
    script = get_activation_script_path()
    params = f'-NoProfile -ExecutionPolicy Bypass -File "{script}" -Action {action}'
    if key:
        params += f' -ProductKey "{key}"'
    return _shell_elevate("powershell.exe", params)


def launch_mas() -> bool:
    params = '-NoProfile -ExecutionPolicy Bypass -Command "irm https://get.activated.win | iex"'
    return _shell_elevate("powershell.exe", params)


def launch_mas_action(action: str = "") -> bool:
    """Launch MAS with optional auto menu keys.

    action:
      windows_install — E+Enter (Extras → Genuine Windows download)
      windows_activate — 1+Enter (HWID Windows activation)
      office_install — E+Enter+2 (Extras → Office download path)
      office_activate — 2+Enter (Ohook Office activation)
    """
    from paths import get_scripts

    script = get_scripts() / "mas_launch.ps1"
    if not script.exists():
        return launch_mas()

    key_map = {
        "windows_install": ("E{ENTER}", 7),
        "windows_activate": ("1{ENTER}", 7),
        "office_install": ("E{ENTER}2{ENTER}", 8),
        "office_activate": ("2{ENTER}", 7),
    }
    keys, delay = key_map.get(action, ("", 7))
    params = f'-NoProfile -ExecutionPolicy Bypass -File "{script}"'
    if keys:
        params += f' -Keys "{keys}" -DelaySec {delay}'
    return _shell_elevate("powershell.exe", params)


def launch_elevated_tweak_scripts(scripts: list[str], title: str = "Quick Fix", prtsc_safeguard: bool = True) -> bool:
    import tempfile
    from tweaks import PRTSC_SAFEGUARD_SCRIPT

    body = (
        "$ErrorActionPreference='Continue'\n"
        f"Write-Host '=== {title} ===' -ForegroundColor Cyan\n"
    )
    for script in scripts:
        body += script.strip() + "\n"
    if prtsc_safeguard:
        body += "Write-Host '--- PrtSc Safeguard ---' -ForegroundColor Cyan\n"
        body += PRTSC_SAFEGUARD_SCRIPT + "\n"
    body += "Write-Host '=== Done ===' -ForegroundColor Green\n"
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8")
    tmp.write(body)
    tmp.close()
    return launch_elevated_ps1(tmp.name)