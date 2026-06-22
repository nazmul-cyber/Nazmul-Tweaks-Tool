"""Theme system - Light, Slate, Ocean. No yellow - orange/cyan accents only."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    label: str
    bg: str
    sidebar: str
    card: str
    card_hover: str
    card_border: str
    primary: str
    primary_hover: str
    primary_light: str
    accent: str
    accent_hover: str
    text: str
    text_muted: str
    success: str
    warning: str
    error: str
    log_bg: str
    input_bg: str
    btn_secondary: str
    btn_secondary_text: str
    shadow: str
    ctk_mode: str
    nav_active_bg: str
    nav_active_text: str
    highlight: str


LIGHT = Theme(
    name="light", label="Light",
    bg="#F1F5F9", sidebar="#FFFFFF", card="#FFFFFF", card_hover="#F8FAFC",
    card_border="#CBD5E1", primary="#2563EB", primary_hover="#1D4ED8",
    primary_light="#DBEAFE", accent="#0891B2", accent_hover="#0E7490",
    text="#0F172A", text_muted="#64748B", success="#15803D", warning="#EA580C",
    error="#DC2626", log_bg="#FFFFFF", input_bg="#F8FAFC",
    btn_secondary="#E2E8F0", btn_secondary_text="#334155",
    shadow="#94A3B8", ctk_mode="light",
    nav_active_bg="#DBEAFE", nav_active_text="#1D4ED8",
    highlight="#0891B2",
)

SLATE = Theme(
    name="slate", label="Slate",
    bg="#1C1C1E", sidebar="#2C2C2E", card="#3A3A3C", card_hover="#48484A",
    card_border="#545456", primary="#6E8EFB", primary_hover="#5B7CFA",
    primary_light="#3D4F7C", accent="#5AC8FA", accent_hover="#47B8EA",
    text="#F5F5F7", text_muted="#AEAEB2", success="#30D158", warning="#FF9F5A",
    error="#FF6961", log_bg="#2C2C2E", input_bg="#3A3A3C",
    btn_secondary="#48484A", btn_secondary_text="#F5F5F7",
    shadow="#000000", ctk_mode="dark",
    nav_active_bg="#3D4F7C", nav_active_text="#9BB4FF",
    highlight="#5AC8FA",
)

OCEAN = Theme(
    name="ocean", label="Ocean",
    bg="#0F172A", sidebar="#1E293B", card="#1E293B", card_hover="#334155",
    card_border="#475569", primary="#38BDF8", primary_hover="#0EA5E9",
    primary_light="#164E63", accent="#22D3EE", accent_hover="#06B6D4",
    text="#F1F5F9", text_muted="#94A3B8", success="#4ADE80", warning="#FB923C",
    error="#F87171", log_bg="#1E293B", input_bg="#334155",
    btn_secondary="#334155", btn_secondary_text="#E2E8F0",
    shadow="#020617", ctk_mode="dark",
    nav_active_bg="#164E63", nav_active_text="#7DD3FC",
    highlight="#22D3EE",
)

MIDNIGHT = Theme(
    name="midnight", label="Midnight",
    bg="#09090F", sidebar="#12121C", card="#1C1C28", card_hover="#28283A",
    card_border="#36364D", primary="#A78BFA", primary_hover="#8B5CF6",
    primary_light="#3F2F6B", accent="#F472B6", accent_hover="#EC4899",
    text="#F4F4F8", text_muted="#9CA3AF", success="#34D399", warning="#FBBF24",
    error="#FB7185", log_bg="#12121C", input_bg="#1C1C28",
    btn_secondary="#28283A", btn_secondary_text="#E5E7EB",
    shadow="#000000", ctk_mode="dark",
    nav_active_bg="#3F2F6B", nav_active_text="#DDD6FE",
    highlight="#F472B6",
)

EMERALD = Theme(
    name="emerald", label="Emerald",
    bg="#071210", sidebar="#0F1A17", card="#152420", card_hover="#1F332D",
    card_border="#2A4A40", primary="#2DD4BF", primary_hover="#14B8A6",
    primary_light="#134E4A", accent="#6EE7B7", accent_hover="#34D399",
    text="#ECFDF5", text_muted="#86EFAC", success="#4ADE80", warning="#FCD34D",
    error="#F87171", log_bg="#0F1A17", input_bg="#152420",
    btn_secondary="#1F332D", btn_secondary_text="#D1FAE5",
    shadow="#020617", ctk_mode="dark",
    nav_active_bg="#134E4A", nav_active_text="#99F6E4",
    highlight="#6EE7B7",
)

THEMES = {
    "midnight": MIDNIGHT,
    "emerald": EMERALD,
    "ocean": OCEAN,
    "slate": SLATE,
    "light": LIGHT,
}
THEME_ORDER = ["midnight", "emerald", "ocean", "slate", "light"]
DEFAULT_THEME = LIGHT

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 11)
FONT_MONO = ("Consolas", 10)
FONT_LOG = ("Consolas", 13)

LOG_PALETTES = {
    "light": {
        "ok": "#15803D", "err": "#DC2626", "warn": "#EA580C", "info": "#1D4ED8",
        "header": "#6D28D9", "cmd": "#0891B2", "path": "#BE185D", "num": "#C2410C",
        "str": "#166534", "sym": "#64748B", "default": "#334155",
    },
    "slate": {
        "ok": "#30D158", "err": "#FF6961", "warn": "#FF9F5A", "info": "#6E8EFB",
        "header": "#BF5AF2", "cmd": "#5AC8FA", "path": "#FF6482", "num": "#FF9F5A",
        "str": "#32D74B", "sym": "#AEAEB2", "default": "#F5F5F7",
    },
    "ocean": {
        "ok": "#4ADE80", "err": "#FCA5A5", "warn": "#FB923C", "info": "#7DD3FC",
        "header": "#C4B5FD", "cmd": "#67E8F9", "path": "#F9A8D4", "num": "#FB923C",
        "str": "#86EFAC", "sym": "#94A3B8", "default": "#E2E8F0",
    },
    "midnight": {
        "ok": "#34D399", "err": "#FB7185", "warn": "#FBBF24", "info": "#A78BFA",
        "header": "#E9D5FF", "cmd": "#F472B6", "path": "#FDA4AF", "num": "#FBBF24",
        "str": "#6EE7B7", "sym": "#9CA3AF", "default": "#F4F4F8",
    },
    "emerald": {
        "ok": "#4ADE80", "err": "#F87171", "warn": "#FCD34D", "info": "#2DD4BF",
        "header": "#A7F3D0", "cmd": "#6EE7B7", "path": "#F9A8D4", "num": "#FCD34D",
        "str": "#86EFAC", "sym": "#86EFAC", "default": "#ECFDF5",
    },
}


def get_log_colors(theme: Theme) -> dict:
    return LOG_PALETTES.get(theme.name, LOG_PALETTES["light"])


def text_for_bg(hex_color: str) -> str:
    c = hex_color.lstrip("#")
    if len(c) != 6:
        return "#FFFFFF"
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0F172A" if lum > 0.52 else "#FFFFFF"


def btn_text_color(bg_color: str, theme: Theme) -> str:
    if bg_color in (theme.warning, theme.highlight) and theme.ctk_mode == "light":
        return "#FFFFFF"
    if bg_color == theme.btn_secondary:
        return theme.btn_secondary_text
    return text_for_bg(bg_color)