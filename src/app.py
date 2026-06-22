"""Nazmul Tweaks Tool - main application."""

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import json
import sys
import threading

from paths import get_root, get_assets, get_scripts
from themes import DEFAULT_THEME, THEMES, THEME_ORDER, Theme, FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_MONO, text_for_bg
from resource_bar import ResourceBar
from tweaks import (
    TWEAKS, CATEGORIES, FRESH_SETUP_IDS, SPEED_UP_IDS,
    PRIVACY_BOOST_IDS, GAMING_BOOST_IDS, NETWORK_FIX_IDS,
)
from apps import ESSENTIAL_APPS, APP_CATEGORIES, FRESH_APP_IDS
from executor import (
    run_batch, run_revert_batch, check_winget, is_admin, relaunch_admin, get_activation_status,
    install_pc_manager, is_pc_manager_installed, open_pc_manager,
    is_windows_desktop_refresh_installed, install_windows_desktop_refresh,
    remove_windows_desktop_refresh, get_system_stats, parse_refresh_stats,
)
from session_history import get_last_session, has_last_session
from animations import animate_progress, fade_page, animate_card_hover, pulse_widget, click_bounce
from color_log import ColorLog
from ui_helpers import (
    make_scroll, secondary_btn, primary_btn, category_chips, colored_btn,
    get_install_command, get_install_script_path,
    get_refresh_script_path, setup_global_scroll, apply_theme_live,
    launch_elevated_ps1, launch_mas, launch_mas_action,
    launch_elevated_tweak_scripts,
)

ASSETS = get_assets()
CONFIG_PATH = Path.home() / ".nazmul-tweaks-tool" / "config.json"
CONFIG_PATH.parent.mkdir(exist_ok=True)

class NazmulApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nazmul Tweaks Tool")
        self.geometry("1180x760")
        self.minsize(960, 640)

        saved_theme = self._load_pref("theme", DEFAULT_THEME.name)
        self._theme_name = saved_theme if saved_theme in THEMES else DEFAULT_THEME.name
        self._theme = THEMES[self._theme_name]
        self._checkboxes = {}
        self._nav_btns = {}
        self._pages = {}
        self._page_key = "home"
        self._busy = False
        self._logo_img = None
        self._tweak_filter_val = "All"
        self._toast_label = None
        self._color_log = None
        self._page_scrolls = {}
        self._fresh_checks = {}
        self._resource_bar = None
        self._stats_poll_id = None

        ctk.set_appearance_mode(self._theme.ctk_mode)
        self.configure(fg_color=self._theme.bg)
        self._apply_icon()
        self._build_all()
        self._setup_boost_menu()
        self._show("home", animate=False)

    def _load_pref(self, key, default):
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text()).get(key, default)
        except Exception:
            pass
        return default

    def _save_pref(self, key, value):
        try:
            data = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
            data[key] = value
            CONFIG_PATH.write_text(json.dumps(data))
        except Exception:
            pass

    def _apply_icon(self):
        ico = ASSETS / "logo.ico"
        if ico.exists():
            try:
                self.iconbitmap(str(ico))
            except Exception:
                pass

    def _t(self) -> Theme:
        return self._theme

    def _set_theme(self, name: str):
        if name not in THEMES or name == self._theme_name:
            return
        old = self._theme
        self._theme_name = name
        self._theme = THEMES[name]
        self._save_pref("theme", name)
        ctk.set_appearance_mode(self._theme.ctk_mode)
        self.configure(fg_color=self._theme.bg)
        apply_theme_live(self, old, self._theme)
        if self._color_log:
            self._color_log.update_theme(self._theme)
        if self._resource_bar:
            self._resource_bar.update_theme(self._theme)
        self._refresh_nav_colors()
        if getattr(self, "_theme_menu", None):
            self._theme_menu.set(self._theme.label)
        self._toast(f"Theme: {self._theme.label}", self._theme.primary)

    def _on_theme_pick(self, label: str):
        for key, theme in THEMES.items():
            if theme.label == label:
                self._set_theme(key)
                return

    def _refresh_nav_colors(self):
        t = self._t()
        for key, btn in self._nav_btns.items():
            active = key == self._page_key
            btn.configure(
                fg_color=t.nav_active_bg if active else "transparent",
                text_color=t.nav_active_text if active else t.text,
                hover_color=t.nav_active_bg,
            )

    def _toast(self, msg, color=None):
        if self._toast_label:
            self._toast_label.destroy()
        self._toast_label = ctk.CTkLabel(
            self, text=msg, font=FONT_SMALL,
            fg_color=color or self._t().success, text_color="#FFFFFF",
            corner_radius=8, height=32,
        )
        self._toast_label.place(relx=0.5, rely=0.97, anchor="center")
        self.after(2500, lambda: self._toast_label.destroy() if self._toast_label else None)

    def _build_all(self):
        self._close_boost_popup()
        saved_checks = {k: cb.get() for k, cb in self._checkboxes.items()}
        for w in self.winfo_children():
            w.destroy()
        self._checkboxes.clear()
        self._nav_btns.clear()
        self._pages.clear()
        self._color_log = None
        self._page_scrolls.clear()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._content = ctk.CTkFrame(self, fg_color=self._t().bg, corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        for key, fn in [
            ("home", self._page_home), ("tweaks", self._page_tweaks),
            ("apps", self._page_apps), ("activate", self._page_activate),
            ("fresh", self._page_fresh), ("log", self._page_log),
        ]:
            p = ctk.CTkFrame(self._content, fg_color=self._t().bg)
            p.grid(row=0, column=0, sticky="nsew")
            p.grid_columnconfigure(0, weight=1)
            fn(p)
            self._pages[key] = p

        for k, v in saved_checks.items():
            if k in self._checkboxes:
                if v:
                    self._checkboxes[k].select()
                else:
                    self._checkboxes[k].deselect()

        setup_global_scroll(self, self._active_scroll)
        self._start_resource_poll()

    def _setup_boost_menu(self):
        self._boost_popup = None
        self._boost_outside_bind = None
        self.bind("<Button-3>", self._on_right_click)

    def _close_boost_popup(self):
        if getattr(self, "_boost_outside_bind", None):
            try:
                self.unbind("<Button-1>", self._boost_outside_bind)
            except Exception:
                pass
            self._boost_outside_bind = None
        if getattr(self, "_boost_popup", None):
            try:
                self._boost_popup.destroy()
            except Exception:
                pass
            self._boost_popup = None

    def _boost_run(self, cmd):
        self._close_boost_popup()
        cmd()

    def _on_right_click(self, event):
        if getattr(self, "_boost_popup", None):
            self._close_boost_popup()
            return
        self._show_boost_box(event.x_root, event.y_root)

    def _show_boost_box(self, x_root, y_root):
        t = self._t()
        pop = ctk.CTkToplevel(self)
        pop.overrideredirect(True)
        pop.attributes("-topmost", True)
        pop.configure(fg_color=t.card)

        shell = ctk.CTkFrame(
            pop, fg_color=t.card, corner_radius=14,
            border_width=2, border_color=t.highlight,
        )
        shell.pack(fill="both", expand=True, padx=1, pady=1)

        ctk.CTkLabel(shell, text="⚡ Quick Boost", font=FONT_HEADING,
                     text_color=t.text).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(shell, text="Right-click menu — click to fix",
                     font=FONT_SMALL, text_color=t.text_muted).pack(anchor="w", padx=16, pady=(0, 10))

        refresh_box = ctk.CTkFrame(shell, fg_color=t.primary_light if t.ctk_mode == "light" else t.card_hover,
                                   corner_radius=10, border_width=1, border_color=t.highlight)
        refresh_box.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(refresh_box, text="🚀 System Refresh", font=FONT_HEADING,
                     text_color=t.highlight).pack(anchor="w", padx=12, pady=(10, 0))
        ctk.CTkLabel(refresh_box, text="GPU + RAM + Windows — apps stay open",
                     font=FONT_SMALL, text_color=t.text_muted).pack(anchor="w", padx=12, pady=(0, 6))
        colored_btn(
            refresh_box, "Fix Now", lambda: self._boost_run(self._system_refresh),
            t, t.highlight, width=240, height=36,
        ).pack(padx=12, pady=(0, 12))

        pcm_label = "Open PC Manager" if is_pc_manager_installed() else "Install PC Manager"
        pcm_cmd = self._open_pc_manager if is_pc_manager_installed() else self._install_pc_manager

        extras = [
            ("⚡ Speed Up", self._fix_speed, t.success),
            (f"🛡 {pcm_label}", pcm_cmd, t.primary),
            ("🎮 Razer Cortex", self._install_razer_cortex, t.accent),
        ]
        for label, cmd, color in extras:
            colored_btn(
                shell, label, lambda c=cmd: self._boost_run(c),
                t, color, width=260, height=32,
            ).pack(padx=14, pady=3)

        colored_btn(
            shell, "✕ Close", self._close_boost_popup,
            t, t.btn_secondary, width=260, height=28,
        ).pack(padx=14, pady=(8, 14))

        pop.update_idletasks()
        w, h = 290, pop.winfo_reqheight()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = min(x_root, sw - w - 12)
        y = min(y_root, sh - h - 12)
        pop.geometry(f"{w}x{h}+{max(8, x)}+{max(8, y)}")

        self._boost_popup = pop

        def _outside(event):
            if not self._boost_popup:
                return
            px, py = pop.winfo_rootx(), pop.winfo_rooty()
            pw, ph = pop.winfo_width(), pop.winfo_height()
            if not (px <= event.x_root <= px + pw and py <= event.y_root <= py + ph):
                self._close_boost_popup()

        self._boost_outside_bind = self.bind("<Button-1>", _outside, add="+")

    def _build_sidebar(self):
        t = self._t()
        sb = ctk.CTkFrame(self, width=240, fg_color=t.sidebar, corner_radius=0,
                          border_width=1, border_color=t.card_border)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)

        logo_frame = ctk.CTkFrame(sb, fg_color="transparent")
        logo_frame.pack(fill="x", padx=18, pady=(20, 4))
        png = ASSETS / "logo.png"
        if png.exists():
            try:
                self._logo_img = ctk.CTkImage(light_image=str(png), dark_image=str(png), size=(40, 40))
                ctk.CTkLabel(logo_frame, image=self._logo_img, text="").pack(side="left", padx=(0, 8))
            except Exception:
                pass
        tf = ctk.CTkFrame(logo_frame, fg_color="transparent")
        tf.pack(side="left")
        ctk.CTkLabel(tf, text="Nazmul", font=FONT_TITLE, text_color=t.primary).pack(anchor="w")
        ctk.CTkLabel(tf, text="Tweaks Tool", font=FONT_SMALL, text_color=t.text_muted).pack(anchor="w")
        ctk.CTkFrame(sb, height=1, fg_color=t.card_border).pack(fill="x", padx=16, pady=10)

        for key, label in [
            ("home", "Home"), ("tweaks", "Tweaks"), ("apps", "Apps"),
            ("activate", "Activate"), ("fresh", "Fresh Setup"), ("log", "Log"),
        ]:
            icons = {"home": "🏠", "tweaks": "⚙", "apps": "📦", "activate": "🔑", "fresh": "🚀", "log": "📋"}
            active = key == self._page_key
            btn = ctk.CTkButton(
                sb, text=f"  {icons[key]}  {label}", anchor="w", font=FONT_BODY, height=40,
                corner_radius=10,
                fg_color=t.nav_active_bg if active else "transparent",
                text_color=t.nav_active_text if active else t.text,
                hover_color=t.nav_active_bg,
                command=lambda k=key: self._show(k),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_btns[key] = btn

        ctk.CTkFrame(sb, fg_color="transparent").pack(expand=True)

        self._rocket_btn = colored_btn(
            sb, "🚀 Refresh", self._system_refresh, t, t.highlight,
            width=200, height=46,
        )
        self._rocket_btn.pack(fill="x", padx=12, pady=(0, 10))
        pulse_widget(self._rocket_btn, t.highlight, t.primary, times=2, interval=200)

        self._resource_bar = ResourceBar(sb, t)
        self._resource_bar.pack(fill="x", padx=12, pady=(0, 8))

        theme_box = ctk.CTkFrame(sb, fg_color="transparent")
        theme_box.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(theme_box, text="Theme", font=FONT_SMALL,
                     text_color=t.text_muted).pack(anchor="w", pady=(0, 4))
        labels = [THEMES[k].label for k in THEME_ORDER if k in THEMES]
        self._theme_menu = ctk.CTkOptionMenu(
            theme_box, values=labels, command=self._on_theme_pick,
            font=FONT_SMALL, height=32, corner_radius=8,
            fg_color=t.card, button_color=t.primary, button_hover_color=t.primary_hover,
            dropdown_fg_color=t.card, dropdown_hover_color=t.card_hover,
            text_color=t.text,
        )
        self._theme_menu.pack(fill="x")
        self._theme_menu.set(t.label)

        admin_ok = is_admin()
        mode_txt = "Admin mode" if admin_ok else "Standard — UAC on Apply"
        ctk.CTkLabel(sb, text=mode_txt,
                     font=FONT_SMALL, text_color=t.success if admin_ok else t.warning).pack(padx=16, anchor="w")
        wg = check_winget()
        ctk.CTkLabel(sb, text="winget ready" if wg else "winget missing",
                     font=FONT_SMALL, text_color=t.success if wg else t.error).pack(padx=16, anchor="w", pady=(0, 14))

    def _start_resource_poll(self):
        if self._stats_poll_id:
            try:
                self.after_cancel(self._stats_poll_id)
            except Exception:
                pass
        self._poll_resource_stats()
        self._stats_poll_id = self.after(3000, self._start_resource_poll)

    def _poll_resource_stats(self):
        def worker():
            stats = get_system_stats()
            self.after(0, lambda: self._resource_bar.update_stats(stats) if self._resource_bar else None)
        threading.Thread(target=worker, daemon=True).start()

    def _active_scroll(self):
        return self._page_scrolls.get(self._page_key)

    def _header(self, parent, title, subtitle="", actions=None, show_back=False):
        h = ctk.CTkFrame(parent, fg_color="transparent")
        h.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 6))
        h.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(h, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        if show_back:
            ctk.CTkButton(
                left, text="← Back", width=88, height=32, corner_radius=8,
                font=FONT_SMALL, fg_color=self._t().btn_secondary,
                text_color=self._t().btn_secondary_text,
                hover_color=self._t().card_hover,
                border_width=1, border_color=self._t().card_border,
                command=lambda: self._show("home"),
            ).pack(side="left", padx=(0, 10))

        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text=title, font=FONT_TITLE, text_color=self._t().text).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(title_frame, text=subtitle, font=FONT_SMALL,
                         text_color=self._t().text_muted).pack(anchor="w", pady=(2, 0))

        if actions:
            af = ctk.CTkFrame(h, fg_color="transparent")
            af.grid(row=0, column=2, sticky="e")
            for text, cmd, style in reversed(actions):
                if style == "primary":
                    primary_btn(af, text, cmd, self._t(), self._t().primary).pack(side="right", padx=3)
                elif style == "success":
                    primary_btn(af, text, cmd, self._t(), self._t().success).pack(side="right", padx=3)
                elif style == "warning":
                    colored_btn(af, text, cmd, self._t(), self._t().warning).pack(side="right", padx=3)
                else:
                    secondary_btn(af, text, cmd, self._t()).pack(side="right", padx=3)
        return h

    def _page_home(self, p):
        p.grid_rowconfigure(1, weight=1)
        subtitle = (
            "System Refresh is on your desktop right-click menu."
            if is_windows_desktop_refresh_installed()
            else "Add System Refresh to Windows desktop right-click."
        )
        self._header(p, "Welcome back", subtitle)

        body = make_scroll(p, self._t())
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        self._page_scrolls["home"] = body

        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))
        top_row.grid_columnconfigure(0, weight=1)
        top_row.grid_columnconfigure(1, weight=1)

        refresh_card = ctk.CTkFrame(top_row, fg_color=self._t().card, corner_radius=14,
                                    border_width=2, border_color=self._t().highlight)
        refresh_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(refresh_card, text="🚀", font=("Segoe UI Emoji", 32)).pack(pady=(14, 0))
        ctk.CTkLabel(refresh_card, text="System Refresh", font=FONT_HEADING,
                     text_color=self._t().highlight).pack()
        ctk.CTkLabel(refresh_card, text="GPU + RAM + Windows — apps stay open",
                     font=FONT_SMALL, text_color=self._t().text_muted).pack(pady=(0, 4))
        self._home_refresh_stats = ctk.CTkLabel(
            refresh_card, text="Run refresh to see RAM / CPU / GPU freed",
            font=FONT_SMALL, text_color=self._t().text_muted, wraplength=220,
        )
        self._home_refresh_stats.pack(pady=(0, 6))

        def _do_refresh():
            click_bounce(refresh_card, self._t(), self._t().highlight)
            self._system_refresh()

        colored_btn(refresh_card, "🚀 Refresh Now", _do_refresh, self._t(),
                    self._t().highlight, width=160, height=38).pack(pady=(0, 14))

        hint_card = ctk.CTkFrame(top_row, fg_color=self._t().card, corner_radius=14,
                                 border_width=1, border_color=self._t().card_border)
        hint_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(hint_card, text="💡 Boost Tip", font=FONT_HEADING,
                     text_color=self._t().text).pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkLabel(
            hint_card,
            text="PC slow?\n1. Desktop right-click > System Refresh\n2. Or click Refresh Now here\n3. PC Manager auto install",
            font=FONT_SMALL, text_color=self._t().text_muted, justify="left",
        ).pack(anchor="w", padx=16, pady=(0, 10))
        colored_btn(hint_card, "PC Manager", self._pc_manager_action, self._t(),
                      self._t().primary, width=160, height=34).pack(anchor="w", padx=16, pady=(0, 14))

        self._build_desktop_menu_offer(body)

        cards_data = [
            ("⚙", "Tweaks", f"{len(TWEAKS)} optimizations", "Privacy, speed, debloat", "tweaks", self._t().primary),
            ("📦", "Apps", f"{len(ESSENTIAL_APPS)} apps", "Essential winget installs", "apps", self._t().accent),
            ("🔑", "Activate", "Win 10 + 11", "Windows & Office license", "activate", self._t().accent),
            ("🚀", "Fresh Setup", "One-click", "Full new PC preset", "fresh", self._t().success),
        ]
        cards_grid = ctk.CTkFrame(body, fg_color="transparent")
        cards_grid.pack(fill="x", pady=6)
        cards_grid.grid_columnconfigure(0, weight=1)
        cards_grid.grid_columnconfigure(1, weight=1)
        for i, data in enumerate(cards_data):
            r, c = divmod(i, 2)
            cell = ctk.CTkFrame(cards_grid, fg_color="transparent")
            cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            self._clickable_card(cell, *data).pack(fill="both", expand=True)

        quick = ctk.CTkFrame(body, fg_color=self._t().card, corner_radius=14,
                             border_width=1, border_color=self._t().card_border)
        quick.pack(fill="x", pady=10)
        ctk.CTkLabel(quick, text="Quick Fixes", font=FONT_HEADING,
                     text_color=self._t().text).pack(anchor="w", padx=18, pady=(12, 4))
        ctk.CTkLabel(quick, text="One click each - 2 column layout.",
                     font=FONT_SMALL, text_color=self._t().text_muted).pack(anchor="w", padx=18)
        qf = ctk.CTkFrame(quick, fg_color="transparent")
        qf.pack(fill="x", padx=14, pady=(8, 14))
        qf.grid_columnconfigure(0, weight=1)
        qf.grid_columnconfigure(1, weight=1)

        quick_btns = [
            ("⚡ Speed Up", self._fix_speed, self._t().success),
            ("🚀 Refresh", self._system_refresh, self._t().highlight),
            ("📸 PrtSc Fix", self._fix_prtsc, self._t().accent),
            ("🔒 Privacy Boost", self._fix_privacy, self._t().primary),
            ("🎮 Gaming Boost", self._fix_gaming, self._t().error),
            ("🌐 Network Fix", self._fix_network, self._t().accent),
            ("🧹 Quick Debloat", self._fix_debloat, self._t().primary),
            ("📋 View Log", lambda: self._show("log"), self._t().btn_secondary),
        ]
        for i, (label, cmd, col) in enumerate(quick_btns):
            r, c = divmod(i, 2)
            colored_btn(qf, label, cmd, self._t(), col, width=200, height=36).grid(
                row=r, column=c, sticky="ew", padx=5, pady=5)

        cmd_box = ctk.CTkFrame(body, fg_color=self._t().card, corner_radius=12,
                               border_width=1, border_color=self._t().card_border)
        cmd_box.pack(fill="x", pady=8)
        ctk.CTkLabel(cmd_box, text="One-Line Install", font=FONT_HEADING,
                     text_color=self._t().text).pack(anchor="w", padx=18, pady=(14, 4))
        self._install_cmd = get_install_command()
        self._cmd_entry = ctk.CTkEntry(cmd_box, height=36, font=FONT_MONO,
                                       fg_color=self._t().input_bg, text_color=self._t().text,
                                       border_color=self._t().card_border)
        self._cmd_entry.pack(fill="x", padx=18, pady=4)
        self._cmd_entry.insert(0, self._install_cmd)
        bf = ctk.CTkFrame(cmd_box, fg_color="transparent")
        bf.pack(fill="x", padx=18, pady=(4, 14))
        colored_btn(bf, "Copy", self._copy_install, self._t(), self._t().primary, width=80, height=30).pack(
            side="left", padx=(0, 6))
        colored_btn(bf, "Run Install", self._run_install, self._t(), self._t().success, width=110, height=30).pack(
            side="left")

    def _clickable_card(self, parent, icon, title, badge, desc, nav, color):
        t = self._t()
        c = ctk.CTkFrame(parent, fg_color=t.card, corner_radius=14, border_width=1,
                         border_color=t.card_border, height=140, cursor="hand2")
        c.pack_propagate(False)
        c.bind("<Enter>", lambda e: animate_card_hover(c, t, True))
        c.bind("<Leave>", lambda e: animate_card_hover(c, t, False))

        def go(_=None):
            c.configure(border_color=color)
            self.after(180, lambda: c.configure(border_color=t.card_border))
            self._show(nav)

        for widget in (c,):
            widget.bind("<Button-1>", go)
        inner = ctk.CTkFrame(c, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)
        inner.bind("<Button-1>", go)
        for w in [
            ctk.CTkLabel(inner, text=icon, font=("Segoe UI Emoji", 26)),
            ctk.CTkLabel(inner, text=title, font=FONT_HEADING, text_color=color),
            ctk.CTkLabel(inner, text=badge, font=FONT_BODY, text_color=t.text),
            ctk.CTkLabel(inner, text=desc, font=FONT_SMALL, text_color=t.text_muted),
        ]:
            w.pack(anchor="w")
            w.bind("<Button-1>", go)
        ctk.CTkButton(inner, text="Open", width=70, height=26, corner_radius=6,
                      fg_color=color, text_color=text_for_bg(color), command=go).pack(anchor="w", pady=(6, 0))
        return c

    def _page_tweaks(self, p):
        p.grid_rowconfigure(2, weight=1)
        self._header(p, "Windows Tweaks", "Pick tweaks, then Apply. Revert Last undoes the previous batch.",
                     [("Revert Last", self._revert_last_tweaks, "warning"),
                      ("None", lambda: self._sel("tweak", False), "secondary"),
                      ("All", lambda: self._sel("tweak", True), "secondary"),
                      ("Apply", self._apply_tweaks, "primary")],
                     show_back=True)

        filt_wrap = ctk.CTkFrame(p, fg_color="transparent")
        filt_wrap.grid(row=1, column=0, sticky="ew", padx=28, pady=6)
        self._tweak_filter = ctk.StringVar(value=self._tweak_filter_val)
        chip_frame, self._cat_btns = category_chips(
            filt_wrap, ["All"] + CATEGORIES, self._tweak_filter, self._filter_tweaks, self._t(),
        )
        chip_frame.pack(fill="x")

        self._tweak_scroll = make_scroll(p, self._t())
        self._tweak_scroll.grid(row=2, column=0, sticky="nsew", padx=28, pady=(0, 18))
        self._page_scrolls["tweaks"] = self._tweak_scroll
        self._render_tweaks(self._tweak_filter_val)

    def _render_tweaks(self, cat):
        for k in list(self._checkboxes.keys()):
            if k.startswith("tweak_"):
                del self._checkboxes[k]
        for w in self._tweak_scroll.winfo_children():
            w.destroy()
        items = TWEAKS if cat == "All" else [t for t in TWEAKS if t.category == cat]
        for tweak in items:
            self._item_row(self._tweak_scroll, f"tweak_{tweak.id}",
                           f"{tweak.icon} {tweak.name}", tweak.description, tweak.recommended)

    def _filter_tweaks(self):
        self._tweak_filter_val = self._tweak_filter.get()
        self._render_tweaks(self._tweak_filter_val)

    def _page_apps(self, p):
        p.grid_rowconfigure(1, weight=1)
        self._header(p, "Essential Apps", "Install via winget. Revert Last uninstalls the previous batch.",
                     [("Revert Last", self._revert_last_apps, "warning"),
                      ("None", lambda: self._sel("app", False), "secondary"),
                      ("All", lambda: self._sel("app", True), "secondary"),
                      ("Install", self._install_apps, "success")],
                     show_back=True)
        scroll = make_scroll(p, self._t())
        scroll.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 18))
        self._page_scrolls["apps"] = scroll
        for cat in APP_CATEGORIES:
            items = [a for a in ESSENTIAL_APPS if a.category == cat]
            if not items:
                continue
            ctk.CTkLabel(scroll, text=cat, font=FONT_HEADING, text_color=self._t().accent).pack(anchor="w", pady=(8, 3))
            for app in items:
                self._item_row(scroll, f"app_{app.id}", f"{app.icon} {app.name}", app.description, app.recommended)

    def _page_activate(self, p):
        p.grid_rowconfigure(1, weight=1)
        self._header(p, "Activation Center", "Windows & Office License", show_back=True)
        body = make_scroll(p, self._t())
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        self._page_scrolls["activate"] = body

        sr = ctk.CTkFrame(body, fg_color="transparent")
        sr.pack(fill="x", pady=6)
        sr.grid_columnconfigure(0, weight=1)
        sr.grid_columnconfigure(1, weight=1)
        wc = ctk.CTkFrame(sr, fg_color="transparent")
        wc.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        oc = ctk.CTkFrame(sr, fg_color="transparent")
        oc.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self._win_lines = self._license_status_card(wc, "Windows License", windows=True)
        self._office_lines = self._license_status_card(oc, "Office License", windows=False)

        note_box = ctk.CTkFrame(body, fg_color=self._t().primary_light if self._t().ctk_mode == "light" else self._t().card,
                                corner_radius=12, border_width=1, border_color=self._t().card_border)
        note_box.pack(fill="x", pady=8)
        ctk.CTkLabel(note_box, text="ℹ  Note", font=FONT_HEADING,
                     text_color=self._t().text).pack(anchor="w", padx=18, pady=(12, 4))
        ctk.CTkLabel(
            note_box,
            text="To install Windows or Office, press E in the MAS menu.\n"
                 "Genuine Windows and Office official licenses can be obtained from Microsoft.",
            font=FONT_SMALL, text_color=self._t().text_muted, justify="left",
            wraplength=720,
        ).pack(anchor="w", padx=18, pady=(0, 14))

        mas = ctk.CTkFrame(body, fg_color=self._t().card, corner_radius=12,
                           border_width=1, border_color=self._t().card_border)
        mas.pack(fill="x", pady=10)
        ctk.CTkLabel(mas, text="MAS Activator", font=FONT_HEADING,
                     text_color=self._t().text).pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(
            mas,
            text="Windows 10 + Windows 11 — both supported.\n"
                 "Office install & activate — green option in MAS menu.",
            font=FONT_SMALL, text_color=self._t().text_muted, justify="left",
        ).pack(anchor="w", padx=18, pady=(0, 10))
        mbr = ctk.CTkFrame(mas, fg_color="transparent")
        mbr.pack(fill="x", padx=18, pady=(0, 16))
        colored_btn(mbr, "Install / Activate", self._open_mas, self._t(), self._t().success,
                    width=150, height=38).pack(side="left", padx=(0, 8))
        colored_btn(
            mbr, "Refresh Status",
            lambda: self._refresh_activation_status(show_toast=True),
            self._t(), self._t().btn_secondary, width=130, height=38,
        ).pack(side="left")

        self._status_gen = 0
        self._refresh_activation_status()

    def _license_status_card(self, parent, title, windows=False):
        t = self._t()
        c = ctk.CTkFrame(parent, fg_color=t.card, corner_radius=10, border_width=1,
                         border_color=t.card_border)
        c.pack(fill="x")
        ctk.CTkLabel(c, text=title, font=FONT_HEADING, text_color=t.text).pack(anchor="w", padx=14, pady=(10, 2))
        lines = {}
        for key, label in (("product", "Checking..."), ("install", "Install: ..."), ("activate", "Activate: ...")):
            lbl = ctk.CTkLabel(
                c, text=label,
                font=FONT_BODY if key == "activate" else FONT_SMALL,
                text_color=t.text_muted if key != "activate" else t.text,
                anchor="w",
            )
            lbl.pack(anchor="w", padx=14, pady=1)
            lines[key] = lbl
        btn_row = ctk.CTkFrame(c, fg_color="transparent")
        btn_row.pack(anchor="w", padx=14, pady=(6, 12))
        if windows:
            colored_btn(btn_row, "Install", self._win_install, t, t.primary, width=88, height=30).pack(
                side="left", padx=(0, 6),
            )
            colored_btn(btn_row, "Activate", self._win_activate, t, t.success, width=88, height=30).pack(
                side="left",
            )
        else:
            colored_btn(btn_row, "Install", self._office_install, t, t.primary, width=88, height=30).pack(
                side="left", padx=(0, 6),
            )
            colored_btn(btn_row, "Activate", self._office_activate, t, t.success, width=88, height=30).pack(
                side="left",
            )
        lines["windows"] = windows
        return lines

    def _license_color(self, status: str):
        t = self._t()
        s = status.lower()
        if "not activated" in s or "not licensed" in s or "unlicensed" in s:
            return t.error
        if "not installed" in s:
            return t.text_muted
        if "activated" in s or s == "licensed":
            return t.success
        if "unknown" in s:
            return t.primary
        return t.text_muted

    def _page_fresh(self, p):
        p.grid_rowconfigure(1, weight=1)
        self._header(p, "Fresh Windows Setup", "Choose tweaks and apps, then run setup.", show_back=True)
        body = make_scroll(p, self._t())
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=8)
        self._page_scrolls["fresh"] = body
        self._fresh_checks.clear()

        card = ctk.CTkFrame(body, fg_color=self._t().card, corner_radius=12,
                            border_width=1, border_color=self._t().card_border)
        card.pack(fill="x", pady=(0, 10))
        self._fresh_summary = ctk.CTkLabel(
            card, text="", font=FONT_HEADING, text_color=self._t().text,
        )
        self._fresh_summary.pack(anchor="w", padx=20, pady=(16, 6))
        self._fresh_bar = ctk.CTkProgressBar(card, height=6, progress_color=self._t().success)
        self._fresh_bar.pack(fill="x", padx=20, pady=4)
        self._fresh_bar.set(0)
        bf = ctk.CTkFrame(card, fg_color="transparent")
        bf.pack(fill="x", padx=20, pady=(8, 16))
        colored_btn(bf, "Run Full Setup", self._run_fresh, self._t(), self._t().success,
                    width=140, height=38).pack(side="left", padx=(0, 6))
        colored_btn(bf, "Tweaks Only", self._run_fresh_tweaks, self._t(), self._t().primary,
                    width=110, height=38).pack(side="left", padx=3)
        colored_btn(bf, "Apps Only", self._run_fresh_apps, self._t(), self._t().accent,
                    width=110, height=38).pack(side="left", padx=3)
        colored_btn(bf, "Revert Last", self._revert_last_menu, self._t(), self._t().warning,
                    width=110, height=38).pack(side="left", padx=(12, 0))

        pick = ctk.CTkFrame(body, fg_color="transparent")
        pick.pack(fill="x", pady=4)
        pick.grid_columnconfigure(0, weight=1)
        pick.grid_columnconfigure(1, weight=1)

        def _col(parent, title, prefix, items, column, select_all=True):
            col = ctk.CTkFrame(parent, fg_color=self._t().card, corner_radius=12,
                               border_width=1, border_color=self._t().card_border)
            col.grid(row=0, column=column, sticky="nsew", padx=4, pady=4)
            hdr = ctk.CTkFrame(col, fg_color="transparent")
            hdr.pack(fill="x", padx=12, pady=(12, 4))
            ctk.CTkLabel(hdr, text=title, font=FONT_HEADING, text_color=self._t().text).pack(side="left")
            if select_all:
                secondary_btn(
                    hdr, "All", lambda pr=prefix: self._fresh_select(pr, True), self._t(), width=44,
                ).pack(side="right", padx=2)
                secondary_btn(
                    hdr, "None", lambda pr=prefix: self._fresh_select(pr, False), self._t(), width=48,
                ).pack(side="right")
            inner = ctk.CTkFrame(col, fg_color="transparent")
            inner.pack(fill="x", padx=8, pady=(0, 12))
            for item_id, label, rec in items:
                self._fresh_item_row(inner, f"{prefix}_{item_id}", label, rec)

        tweak_items = [
            (t.id, f"{t.icon} {t.name}", t.recommended)
            for t in TWEAKS if t.id in FRESH_SETUP_IDS
        ]
        app_items = [
            (a.id, f"{a.icon} {a.name}", a.recommended)
            for a in ESSENTIAL_APPS if a.id in FRESH_APP_IDS
        ]
        _col(pick, f"Tweaks ({len(tweak_items)})", "fresh_tweak", tweak_items, 0)
        _col(pick, f"Apps ({len(app_items)})", "fresh_app", app_items, 1)
        self._update_fresh_summary()

    def _fresh_item_row(self, parent, key, name, rec=False):
        t = self._t()
        row = ctk.CTkFrame(parent, fg_color=t.primary_light if t.ctk_mode == "light" else t.card_hover,
                           corner_radius=8)
        row.pack(fill="x", pady=2)
        cb = ctk.CTkCheckBox(
            row, text=name, font=FONT_SMALL, text_color=t.text,
            fg_color=t.primary, hover_color=t.primary_hover,
            command=self._update_fresh_summary,
        )
        cb.pack(anchor="w", padx=10, pady=6)
        if rec:
            cb.select()
        self._fresh_checks[key] = cb

    def _fresh_select(self, prefix, state):
        for k, cb in self._fresh_checks.items():
            if k.startswith(f"{prefix}_"):
                cb.select() if state else cb.deselect()
        self._update_fresh_summary()

    def _fresh_selected(self, prefix):
        return [
            k.replace(f"{prefix}_", "")
            for k, cb in self._fresh_checks.items()
            if k.startswith(f"{prefix}_") and cb.get()
        ]

    def _update_fresh_summary(self):
        if not hasattr(self, "_fresh_summary"):
            return
        nt = len(self._fresh_selected("fresh_tweak"))
        na = len(self._fresh_selected("fresh_app"))
        self._fresh_summary.configure(text=f"Selected: {nt} tweaks + {na} apps")

    def _page_log(self, p):
        p.grid_rowconfigure(1, weight=1)
        self._header(p, "Activity Log", "Color-coded output",
                     [("Clear", self._clear_log, "secondary")], show_back=True)
        self._color_log = ColorLog(p, self._t())
        self._color_log.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 18))
        self._log_msg("Nazmul Tweaks Tool ready")
        if not is_admin():
            self._log_msg("WARNING: Run as Admin for best results")

    def _item_row(self, parent, key, name, desc, rec=False):
        t = self._t()
        row = ctk.CTkFrame(parent, fg_color=t.card, corner_radius=8,
                           border_width=1, border_color=t.card_border)
        row.pack(fill="x", pady=2)
        lbl = f"{name}  *" if rec else name
        cb = ctk.CTkCheckBox(row, text=lbl, font=FONT_BODY, text_color=t.text,
                             fg_color=t.primary, hover_color=t.primary_hover, width=260)
        cb.pack(side="left", padx=12, pady=8)
        if rec:
            cb.select()
        self._checkboxes[key] = cb
        ctk.CTkLabel(row, text=desc, font=FONT_SMALL, text_color=t.text_muted,
                     wraplength=400, justify="left").pack(side="left", padx=6, pady=8)

    def _show(self, key: str, animate: bool = True):
        old_key = self._page_key
        self._page_key = key
        for k, pg in self._pages.items():
            pg.grid() if k == key else pg.grid_remove()
        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color=self._t().nav_active_bg if k == key else "transparent",
                text_color=self._t().nav_active_text if k == key else self._t().text,
            )
        if animate and old_key != key:
            fade_page(self._pages[key], self._t())
        if key == "activate" and hasattr(self, "_win_lines"):
            self._refresh_activation_status()
        if key == "home" and hasattr(self, "_desktop_offer_host"):
            self._refresh_desktop_offer_card()

    def _sel(self, prefix, state):
        for k, cb in self._checkboxes.items():
            if k.startswith(f"{prefix}_"):
                cb.select() if state else cb.deselect()

    def _selected(self, prefix):
        return [k.replace(f"{prefix}_", "") for k, cb in self._checkboxes.items()
                if k.startswith(f"{prefix}_") and cb.get()]

    def _log_msg(self, msg):
        def _do():
            if self._color_log:
                self._color_log.writeln(msg)
        self.after(0, _do)

    def _clear_log(self):
        if self._color_log:
            self._color_log.clear()

    def _copy_install(self):
        cmd = self._cmd_entry.get().strip()
        self.clipboard_clear()
        self.clipboard_append(cmd)
        self.update()
        self._toast("Copied to clipboard!")

    def _one_click_tweaks(self, ids, title, toast_msg):
        if not self._guard():
            return
        tweaks = [t for t in TWEAKS if t.id in ids]
        if not tweaks:
            self._toast("Tweaks not found", self._t().error)
            return
        if not self._confirm_batch(
            f"run {title}",
            [t.name for t in tweaks],
            "Quick tweaks will apply immediately. Use Revert Last on the Tweaks page to undo.",
        ):
            return
        self._busy = True
        self._show("log")
        self._log_msg(f"[INFO] {title}...")
        if not is_admin():
            self._log_msg("[INFO] Allow UAC when prompted")
        run_batch(
            [(t.id, t.name, t.script) for t in tweaks],
            self._log_msg,
            on_done=lambda: (
                setattr(self, "_busy", False),
                self._toast(toast_msg, self._t().success),
            ),
        )

    def _fix_speed(self):
        self._one_click_tweaks(SPEED_UP_IDS, "Speed Up", "PC speed boosted!")

    def _fix_prtsc(self):
        self._one_click_tweaks(["prtsc_snip"], "PrtSc Fix", "PrtSc fix applied!")

    def _fix_privacy(self):
        self._one_click_tweaks(PRIVACY_BOOST_IDS, "Privacy Boost", "Privacy boosted!")

    def _fix_gaming(self):
        self._one_click_tweaks(GAMING_BOOST_IDS, "Gaming Boost", "Gaming boost applied!")

    def _fix_network(self):
        self._one_click_tweaks(NETWORK_FIX_IDS, "Network Fix", "Network fixed!")

    def _fix_debloat(self):
        self._one_click_tweaks(["telemetry", "tips", "cleantemp"], "Quick Debloat", "Debloat done!")

    def _log_refresh_results(self, stats: dict):
        if not stats:
            return
        self._log_msg("─── Refresh Results ───")
        before_pct = stats.get("ram_before_used_pct")
        after_pct = stats.get("ram_after_used_pct")
        drop_pct = stats.get("ram_drop_pct", 0)
        freed = stats.get("ram_freed_mb", 0)
        if before_pct is not None and after_pct is not None:
            line = f"  RAM:  {before_pct}% used → {after_pct}% used"
            if drop_pct > 0:
                line += f"  (-{drop_pct}%)"
            elif freed > 0:
                line += f"  (+{freed} MB available)"
            self._log_msg(line)
        else:
            self._log_msg(
                f"  RAM:  {stats.get('ram_after_free', '?')} MB available"
                + (f"  (+{freed} MB)" if freed > 0 else "")
            )
        self._log_msg(
            f"  CPU:  {stats.get('cpu_after', '?')}%"
            + (f"  (was {stats.get('cpu_before')}%)" if stats.get("cpu_before") is not None else "")
        )
        self._log_msg(
            f"  GPU:  {stats.get('gpu_after', '?')}%"
            + (f"  (was {stats.get('gpu_before')}%)" if stats.get("gpu_before") is not None else "")
        )

    def _apply_refresh_results(self, stats: dict):
        if self._resource_bar and stats:
            self._resource_bar.show_refresh_result(stats)
        if hasattr(self, "_home_refresh_stats") and stats:
            drop = stats.get("ram_drop_pct", 0)
            after = stats.get("ram_after_used_pct", "?")
            freed = stats.get("ram_freed_mb", 0)
            if drop and drop > 0:
                txt = f"Last refresh: RAM -{drop}% (now {after}% used)"
                color = self._t().success
            elif freed > 0:
                txt = f"Last refresh: +{freed} MB available"
                color = self._t().success
            else:
                txt = f"Last refresh: RAM {after}% used — no drop"
                color = self._t().text_muted
            self._home_refresh_stats.configure(text=txt, text_color=color)
        self._poll_resource_stats()

    def _read_refresh_stats_file(self) -> dict:
        import tempfile
        path = Path(tempfile.gettempdir()) / "nazmul_refresh_stats.json"
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}

    def _finish_refresh(self, stats: dict, out: str = ""):
        if out:
            for line in out.splitlines():
                s = line.strip()
                if s and "[STATS]" not in s:
                    self._log_msg(s)
        if not stats:
            stats = self._read_refresh_stats_file()
        self._log_refresh_results(stats)
        self._busy = False
        self._apply_refresh_results(stats)
        drop_pct = stats.get("ram_drop_pct", 0)
        freed = stats.get("ram_freed_mb", 0)
        after_pct = stats.get("ram_after_used_pct")
        if drop_pct and drop_pct > 0:
            self._toast(f"RAM {drop_pct}% lower — now {after_pct}% used", self._t().success)
        elif freed > 0:
            self._toast(f"+{freed} MB available — apps still open", self._t().success)
        elif stats.get("is_admin") is False:
            self._toast("Allow UAC on refresh for RAM purge", self._t().warning)
        else:
            self._toast("Refresh done — close heavy apps for more RAM", self._t().warning)

    def _system_refresh(self):
        if not self._guard():
            return
        script = get_refresh_script_path()
        if not script.exists():
            self._toast("refresh.ps1 missing", self._t().error)
            return
        if getattr(self, "_rocket_btn", None):
            pulse_widget(self._rocket_btn, self._t().highlight, self._t().primary)
        self._busy = True
        self._show("log")
        self._log_msg("[INFO] System Refresh — allow UAC (needed for RAM purge)...")

        def worker():
            from executor import _ps_file
            _, out = _ps_file(str(script))
            stats = parse_refresh_stats(out)
            if not stats:
                stats = self._read_refresh_stats_file()
            self.after(0, lambda: self._finish_refresh(stats, out))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_desktop_offer_card(self):
        if hasattr(self, "_desktop_offer_host") and self._desktop_offer_host.winfo_exists():
            self._build_desktop_menu_offer(self._desktop_offer_host)

    def _desktop_menu_segment(self, parent, t, *, icon, title, desc, note, note_color,
                              btn_text, btn_color, command, enabled):
        seg = ctk.CTkFrame(
            parent, fg_color=t.primary_light if t.ctk_mode == "light" else t.card_hover,
            corner_radius=12, border_width=1, border_color=t.card_border,
        )
        seg.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(seg, text=icon, font=("Segoe UI Emoji", 22)).pack(anchor="w", padx=14, pady=(12, 0))
        ctk.CTkLabel(seg, text=title, font=FONT_HEADING, text_color=t.text).pack(anchor="w", padx=14, pady=(2, 2))
        ctk.CTkLabel(
            seg, text=desc, font=FONT_SMALL, text_color=t.text_muted,
            justify="left", wraplength=240,
        ).pack(anchor="w", padx=14, pady=(0, 6))
        ctk.CTkLabel(seg, text=note, font=FONT_SMALL, text_color=note_color).pack(anchor="w", padx=14, pady=(0, 8))
        btn = colored_btn(seg, btn_text, command, t, btn_color, width=168, height=36)
        btn.pack(anchor="w", padx=14, pady=(0, 14))
        if not enabled:
            btn.configure(
                state="disabled",
                fg_color=t.btn_secondary,
                text_color=t.text_muted,
                hover_color=t.btn_secondary,
            )
        return seg

    def _build_desktop_menu_offer(self, parent):
        self._desktop_offer_host = parent
        if getattr(self, "_desktop_offer_card", None):
            try:
                self._desktop_offer_card.destroy()
            except Exception:
                pass
        t = self._t()
        installed = is_windows_desktop_refresh_installed()
        card = ctk.CTkFrame(parent, fg_color=t.card, corner_radius=16,
                            border_width=2, border_color=t.success if installed else t.card_border)
        card.pack(fill="x", pady=(0, 10))
        self._desktop_offer_card = card

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=18, pady=(16, 4))
        head.grid_columnconfigure(0, weight=1)
        title_box = ctk.CTkFrame(head, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text="🖱 Windows Right-Click Menu", font=FONT_HEADING,
                     text_color=t.text).pack(anchor="w")
        ctk.CTkLabel(
            title_box,
            text="Add or remove System Refresh on the desktop context menu.",
            font=FONT_SMALL, text_color=t.text_muted, justify="left",
        ).pack(anchor="w", pady=(2, 0))

        badge_bg = t.success if installed else t.btn_secondary
        badge_txt = "#FFFFFF" if installed else t.text_muted
        badge_lbl = "● On menu" if installed else "○ Not on menu"
        ctk.CTkLabel(
            head, text=badge_lbl, font=FONT_SMALL,
            fg_color=badge_bg, text_color=badge_txt, corner_radius=14,
            width=108, height=28,
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        split = ctk.CTkFrame(card, fg_color="transparent")
        split.pack(fill="x", padx=14, pady=(8, 10))
        split.grid_columnconfigure(0, weight=1)
        split.grid_columnconfigure(1, weight=1)

        add_seg = self._desktop_menu_segment(
            split, t,
            icon="➕", title="Add to Menu",
            desc="Desktop right-click → System Refresh\nGPU + RAM + Windows — apps stay open.",
            note="Ready to add" if not installed else "Already added to Windows menu",
            note_color=t.highlight if not installed else t.success,
            btn_text="Add to Windows Menu",
            btn_color=t.success,
            command=self._install_windows_desktop_menu,
            enabled=not installed,
        )
        add_seg.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        remove_seg = self._desktop_menu_segment(
            split, t,
            icon="➖", title="Remove from Menu",
            desc="Hide System Refresh from the\ndesktop right-click menu on this PC.",
            note="Click to remove from menu" if installed else "Nothing to remove yet",
            note_color=t.warning if installed else t.text_muted,
            btn_text="Remove from Windows",
            btn_color=t.error,
            command=self._remove_windows_desktop_menu,
            enabled=installed,
        )
        remove_seg.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        foot = ctk.CTkFrame(card, fg_color="transparent")
        foot.pack(fill="x", padx=18, pady=(0, 14))
        colored_btn(foot, "Test Refresh", self._system_refresh, t, t.highlight,
                    width=140, height=34).pack(side="left")
        ctk.CTkLabel(
            foot,
            text="Right-click desktop → System Refresh" if installed else "Add first, then test from desktop",
            font=FONT_SMALL, text_color=t.text_muted,
        ).pack(side="left", padx=(12, 0))
    def _install_windows_desktop_menu(self, silent=False):
        if not self._guard():
            return
        if not silent:
            self._show("log")
        self._busy = True
        self._log_msg("[INFO] Adding System Refresh to Windows right-click menu...")

        def worker():
            ok = install_windows_desktop_refresh(self._log_msg)
            self._busy = False
            if ok:
                self._save_pref("desktop_menu_dismissed", False)
                self.after(0, lambda: self._toast(
                    "Added to Windows menu — right-click the desktop", self._t().success,
                ))
                self.after(100, self._refresh_desktop_offer_card)
            else:
                self.after(0, lambda: self._toast("Could not add — check the log", self._t().error))
        threading.Thread(target=worker, daemon=True).start()

    def _remove_windows_desktop_menu(self):
        if not messagebox.askyesno("Remove", "Remove System Refresh from the Windows right-click menu?"):
            return
        self._show("log")
        self._busy = True
        self._log_msg("[INFO] Removing System Refresh from Windows right-click menu...")

        def worker():
            ok = remove_windows_desktop_refresh(self._log_msg)
            self._busy = False
            if ok:
                self.after(0, lambda: self._toast("Removed from Windows menu", self._t().success))
                self.after(100, self._refresh_desktop_offer_card)
            else:
                self.after(0, lambda: self._toast("Could not remove — check the log", self._t().error))

        threading.Thread(target=worker, daemon=True).start()

    def _pc_manager_action(self):
        if is_pc_manager_installed():
            self._open_pc_manager()
        else:
            self._install_pc_manager()

    def _open_pc_manager(self):
        if not self._guard():
            return
        if open_pc_manager():
            self._toast("PC Manager opened!", self._t().success)
        else:
            self._toast("Search PC Manager in the Start Menu", self._t().accent)

    def _install_pc_manager(self):
        if not self._guard():
            return
        self._show("log")
        self._busy = True

        def worker():
            status = install_pc_manager(self._log_msg)
            self._busy = False
            msgs = {
                "installed": ("PC Manager installed!", self._t().success),
                "already": ("Already installed — open from Start Menu", self._t().primary),
                "store": ("Store opened — click Install", self._t().accent),
                "no_winget": ("Install App Installer, then try again", self._t().accent),
                "failed": ("Install failed — check the log", self._t().error),
            }
            msg, col = msgs.get(status, ("Something went wrong", self._t().error))
            self.after(0, lambda: self._toast(msg, col))

        threading.Thread(target=worker, daemon=True).start()

    def _install_razer_cortex(self):
        if not self._guard():
            return
        self._show("log")
        self._busy = True
        self._log_msg("[INFO] Installing Razer Cortex...")
        run_batch(
            [("cortex", "Razer Cortex", "RazerInc.RazerCortex")],
            self._log_msg,
            on_done=lambda: (setattr(self, "_busy", False), self._toast("Razer Cortex install done", self._t().success)),
            kind="app",
        )

    def _run_install(self):
        script = get_install_script_path()
        if not script.exists():
            self._toast("install.ps1 not found!", self._t().error)
            self._log_msg("[ERR] install.ps1 not found at " + str(script))
            return
        self._show("log")
        self._log_msg("[INFO] Launching one-line installer (Admin)...")
        self._log_msg(f"[INFO] Script: {script}")
        ok = launch_elevated_ps1(script)
        if ok:
            self._toast("Install window opened!", self._t().success)
            self._log_msg("[OK] Admin PowerShell opened - follow installer steps")
        else:
            self._toast("Could not launch (UAC cancelled?)", self._t().error)
            self._log_msg("[ERR] Failed to launch installer - allow UAC prompt")

    def _guard(self):
        if self._busy:
            messagebox.showwarning("Busy", "Wait for current task to finish.")
            return False
        return True

    def _confirm_batch(self, verb: str, names: list[str], warning: str) -> bool:
        n = len(names)
        if n == 0:
            return False
        preview = "\n".join(f"  • {name}" for name in names[:12])
        if n > 12:
            preview += f"\n  ... and {n - 12} more"
        plural = "s" if n != 1 else ""
        msg = (
            f"You are about to {verb} {n} item{plural}:\n\n"
            f"{preview}\n\n"
            f"Warning: {warning}\n\n"
            "Continue?"
        )
        return messagebox.askyesno("Confirm", msg, icon="warning")

    def _revert_confirm(self, kind: str, items: list[dict]) -> bool:
        names = [it.get("name", it.get("id", "?")) for it in items]
        if kind == "tweak":
            warning = (
                "This will try to undo the last tweak batch. "
                "Some tweaks (e.g. temp cleanup) cannot be fully reverted."
            )
        else:
            warning = "This will uninstall apps from the last install batch."
        return self._confirm_batch("revert", names, warning)

    def _revert_last_tweaks(self):
        if not self._guard():
            return
        session = get_last_session("tweak")
        if not session:
            messagebox.showinfo("Revert", "No tweak batch to revert. Apply tweaks first.")
            return
        items = session.get("items", [])
        if not self._revert_confirm("tweak", items):
            return
        self._busy = True
        self._show("log")
        self._log_msg(f"[INFO] Reverting tweak batch from {session.get('timestamp', '?')}...")
        run_revert_batch(
            items, self._log_msg, on_done=lambda: setattr(self, "_busy", False), kind="tweak",
        )

    def _revert_last_apps(self):
        if not self._guard():
            return
        session = get_last_session("app")
        if not session:
            messagebox.showinfo("Revert", "No app install batch to revert. Install apps first.")
            return
        items = session.get("items", [])
        if not self._revert_confirm("app", items):
            return
        if not check_winget():
            messagebox.showerror("winget", "winget required to uninstall apps.")
            return
        self._busy = True
        self._show("log")
        self._log_msg(f"[INFO] Reverting app batch from {session.get('timestamp', '?')}...")
        run_revert_batch(
            items, self._log_msg, on_done=lambda: setattr(self, "_busy", False), kind="app",
        )

    def _revert_last_menu(self):
        has_t = has_last_session("tweak")
        has_a = has_last_session("app")
        if not has_t and not has_a:
            messagebox.showinfo("Revert", "Nothing to revert yet.")
            return
        if has_t and has_a:
            choice = messagebox.askyesnocancel(
                "Revert Last",
                "Revert tweaks, apps, or both?\n\n"
                "Yes = Tweaks only\nNo = Apps only\nCancel = abort",
            )
            if choice is None:
                return
            if choice:
                self._revert_last_tweaks()
            else:
                self._revert_last_apps()
        elif has_t:
            self._revert_last_tweaks()
        else:
            self._revert_last_apps()

    def _apply_tweaks(self):
        if not self._guard():
            return
        ids = self._selected("tweak")
        if not ids:
            messagebox.showinfo("Select", "Select at least one tweak.")
            return
        tweaks = [t for t in TWEAKS if t.id in ids]
        if not self._confirm_batch(
            "apply",
            [t.name for t in tweaks],
            "These change Windows settings. Allow UAC when prompted. Use Revert Last if needed.",
        ):
            return
        self._busy = True
        self._show("log")
        if not is_admin():
            self._log_msg("[INFO] Standard mode — UAC will ask for Admin once")
        run_batch([(t.id, t.name, t.script) for t in tweaks],
                  self._log_msg, on_done=lambda: setattr(self, "_busy", False))

    def _install_apps(self):
        if not self._guard():
            return
        if not check_winget():
            messagebox.showerror("winget", "Install App Installer from Microsoft Store.")
            return
        ids = self._selected("app")
        if not ids:
            messagebox.showinfo("Select", "Select at least one app.")
            return
        apps = [a for a in ESSENTIAL_APPS if a.id in ids]
        if not self._confirm_batch(
            "install",
            [a.name for a in apps],
            "Apps will download and install. Use Revert Last to uninstall the last batch.",
        ):
            return
        self._busy = True
        self._show("log")
        run_batch([(a.id, a.name, a.winget_id) for a in apps],
                  self._log_msg, on_done=lambda: setattr(self, "_busy", False), kind="app")

    def _set_license_checking(self):
        t = self._t()
        checking = "Checking..."
        for lines in (getattr(self, "_win_lines", None), getattr(self, "_office_lines", None)):
            if not lines:
                continue
            lines["product"].configure(text=checking, text_color=t.text_muted)
            lines["install"].configure(text="Install: ...", text_color=t.text_muted)
            lines["activate"].configure(text="Activate: ...", text_color=t.text_muted)

    def _apply_license_status(self, lines, product, install_text, activate_st):
        t = self._t()
        if len(product) > 44:
            product = product[:41] + "..."
        lines["product"].configure(text=product, text_color=t.text)
        lines["install"].configure(text=install_text, text_color=t.text_muted)
        lines["activate"].configure(
            text=f"Activate: {activate_st}",
            text_color=self._license_color(activate_st),
            font=FONT_BODY,
        )

    def _refresh_activation_status(self, show_toast=False):
        self._status_gen = getattr(self, "_status_gen", 0) + 1
        gen = self._status_gen
        self._set_license_checking()

        def worker():
            data = get_activation_status()
            win = data.get("windows", {})
            off = data.get("office", {})
            apps = data.get("apps", [])

            def update():
                if gen != getattr(self, "_status_gen", 0):
                    return
                if hasattr(self, "_win_lines") and self._win_lines.get("windows"):
                    edition = win.get("edition", "Unknown")
                    build = win.get("build", "")
                    license_st = win.get("license", "Unknown")
                    if build:
                        edition = f"{edition} (Build {build})"
                    self._apply_license_status(
                        self._win_lines, edition, "Install: Installed", license_st,
                    )
                if hasattr(self, "_office_lines") and not self._office_lines.get("windows"):
                    product = off.get("product", "Not detected")
                    installed = off.get("installed", "No")
                    license_st = off.get("license", "N/A")
                    if installed.lower() != "yes":
                        license_st = "Not Installed"
                    self._apply_license_status(
                        self._office_lines, product, f"Install: {installed}", license_st,
                    )
                if show_toast:
                    self._toast("Status updated", self._t().success)

            self.after(0, update)

        threading.Thread(target=worker, daemon=True).start()

    def _open_mas(self):
        if not self._guard():
            return
        ok = launch_mas()
        if ok:
            self._toast("MAS opened — pick a green option, then Refresh Status", self._t().success)
        else:
            self._toast("UAC cancelled", self._t().error)

    def _win_install(self):
        if not self._guard():
            return
        ok = launch_mas_action("windows_install")
        if ok:
            self._toast("MAS → Genuine Windows download (E+Enter)", self._t().primary)
        else:
            self._toast("UAC cancelled", self._t().error)

    def _win_activate(self):
        if not self._guard():
            return
        ok = launch_mas_action("windows_activate")
        if ok:
            self._toast("MAS → Windows HWID activate (1+Enter)", self._t().success)
            self.after(12000, lambda: self._refresh_activation_status(show_toast=True))
        else:
            self._toast("UAC cancelled", self._t().error)

    def _office_install(self):
        if not self._guard():
            return
        ok = launch_mas_action("office_install")
        if ok:
            self._toast("MAS → Office install path opened", self._t().primary)
        else:
            self._toast("UAC cancelled", self._t().error)

    def _office_activate(self):
        if not self._guard():
            return
        ok = launch_mas_action("office_activate")
        if ok:
            self._toast("MAS → Office Ohook activate (2+Enter)", self._t().success)
            self.after(12000, lambda: self._refresh_activation_status(show_toast=True))
        else:
            self._toast("UAC cancelled", self._t().error)

    def _run_fresh(self):
        tweak_ids = self._fresh_selected("fresh_tweak")
        app_ids = self._fresh_selected("fresh_app")
        if not tweak_ids and not app_ids:
            messagebox.showinfo("Select items", "Select at least one tweak or app.")
            return
        tweak_names = [t.name for t in TWEAKS if t.id in tweak_ids]
        app_names = [a.name for a in ESSENTIAL_APPS if a.id in app_ids]
        parts = []
        if tweak_names:
            parts.append(f"{len(tweak_names)} tweak(s)")
        if app_names:
            parts.append(f"{len(app_names)} app(s)")
        summary = " + ".join(parts)
        if not self._guard() or not self._confirm_batch(
            f"run full setup ({summary})",
            tweak_names + app_names,
            "Setup will apply tweaks and install apps. Revert Last is available on each page.",
        ):
            return
        self._show("log")
        self._busy = True
        animate_progress(self._fresh_bar, 0.5)

        def after_tweaks():
            animate_progress(self._fresh_bar, 0.85)
            if not app_ids:
                done()
            elif check_winget():
                run_batch(
                    [(a.id, a.name, a.winget_id) for a in ESSENTIAL_APPS if a.id in app_ids],
                    self._log_msg, on_done=done, kind="app",
                )
            else:
                self._log_msg("[ERR] winget missing — apps were not installed")
                self._toast("Install App Installer from Microsoft Store for apps", self._t().error)
                done()

        def done():
            animate_progress(self._fresh_bar, 1.0)
            self._busy = False

        if tweak_ids:
            run_batch(
                [(t.id, t.name, t.script) for t in TWEAKS if t.id in tweak_ids],
                self._log_msg, on_done=after_tweaks if app_ids else done,
            )
        elif app_ids:
            after_tweaks()

    def _run_fresh_tweaks(self):
        tweak_ids = self._fresh_selected("fresh_tweak")
        if not tweak_ids:
            messagebox.showinfo("Select tweaks", "Select at least one tweak.")
            return
        tweaks = [t for t in TWEAKS if t.id in tweak_ids]
        if not self._confirm_batch(
            "apply",
            [t.name for t in tweaks],
            "These change Windows settings. Use Revert Last if you clicked by mistake.",
        ):
            return
        if not self._guard():
            return
        self._busy = True
        self._show("log")
        if not is_admin():
            self._log_msg("[INFO] Standard mode — UAC will ask for Admin once")
        run_batch(
            [(t.id, t.name, t.script) for t in tweaks],
            self._log_msg, on_done=lambda: setattr(self, "_busy", False),
        )

    def _run_fresh_apps(self):
        app_ids = self._fresh_selected("fresh_app")
        if not app_ids:
            messagebox.showinfo("Select apps", "Select at least one app.")
            return
        apps = [a for a in ESSENTIAL_APPS if a.id in app_ids]
        if not self._confirm_batch(
            "install",
            [a.name for a in apps],
            "Apps will download and install. Use Revert Last to uninstall the last batch.",
        ):
            return
        if not self._guard():
            return
        if not check_winget():
            messagebox.showerror("winget", "Install App Installer from Microsoft Store.")
            return
        self._busy = True
        self._show("log")
        run_batch(
            [(a.id, a.name, a.winget_id) for a in apps],
            self._log_msg, on_done=lambda: setattr(self, "_busy", False), kind="app",
        )