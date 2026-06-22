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


def delta_to_pixels(delta: int) -> float:
    """Map wheel delta to pixels — matches Windows trackpad + mouse feel."""
    if delta == 0:
        return 0.0
    if abs(delta) < 120:
        return -delta * 0.55
    return -delta / 2.4


class SmoothScrollEngine:
    """Windows-style smooth scroll with pixel steps and easing."""

    FRAME_MS = 8
    EASE = 0.28
    MIN_STEP = 0.35

    def __init__(self, root: tk.Misc):
        self._root = root
        self._states: dict[int, dict] = {}

    def _key(self, widget) -> int:
        return id(widget)

    def impulse(self, widget, delta: int) -> bool:
        px = delta_to_pixels(delta)
        if abs(px) < 0.01:
            return False
        key = self._key(widget)
        state = self._states.get(key)
        if state is None:
            state = {"widget": widget, "pending": 0.0, "job": None}
            self._states[key] = state
        state["pending"] += px
        if state["job"] is None:
            state["job"] = self._root.after(self.FRAME_MS, lambda k=key: self._tick(k))
        return True

    def _tick(self, key: int):
        state = self._states.get(key)
        if not state:
            return
        state["job"] = None
        pending = state["pending"]
        if abs(pending) < self.MIN_STEP:
            state["pending"] = 0.0
            return

        step = pending * self.EASE
        if abs(step) < 1.0:
            step = pending
            state["pending"] = 0.0
        else:
            state["pending"] = pending - step

        self._scroll_pixels(state["widget"], step)
        state["job"] = self._root.after(self.FRAME_MS, lambda k=key: self._tick(k))

    @staticmethod
    def _scroll_pixels(widget, pixels: float):
        amount = int(round(pixels))
        if amount == 0:
            amount = 1 if pixels > 0 else -1
        try:
            widget.yview_scroll(amount, "pixels")
        except tk.TclError:
            try:
                widget.yview_scroll(amount, "units")
            except Exception:
                pass
        except Exception:
            pass


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
    """Smooth Windows-like scroll for all pages."""
    engine = SmoothScrollEngine(root)
    root._smooth_scroll_engine = engine

    def on_scroll(event):
        target = _scroll_target_from_event(event)
        if target is None:
            scroll_frame = get_scroll_fn()
            if scroll_frame and hasattr(scroll_frame, "_parent_canvas"):
                target = scroll_frame._parent_canvas
        if target:
            engine.impulse(target, event.delta)

    root.bind_all("<MouseWheel>", on_scroll, add="+")
    root.bind_all("<Button-4>", lambda e: on_scroll(type("E", (), {"widget": e.widget, "delta": 120})()), add="+")
    root.bind_all("<Button-5>", lambda e: on_scroll(type("E", (), {"widget": e.widget, "delta": -120})()), add="+")


def smooth_scroll_widget(widget, event, root: tk.Misc | None = None):
    """Smooth-scroll a canvas or text widget (e.g. activity log)."""
    r = root or widget.winfo_toplevel()
    engine = getattr(r, "_smooth_scroll_engine", None)
    if engine is None:
        engine = SmoothScrollEngine(r)
        r._smooth_scroll_engine = engine
    return engine.impulse(widget, event.delta)


def scroll_amount(delta: int) -> int:
    """Legacy helper — prefer smooth_scroll_widget."""
    return int(round(delta_to_pixels(delta)))


def scroll_widget(scroll_frame, event):
    root = scroll_frame.winfo_toplevel()
    canvas = scroll_frame._parent_canvas
    return smooth_scroll_widget(canvas, event, root)


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