"""Syntax-colored activity log widget."""

import re
import tkinter as tk
import customtkinter as ctk
from themes import Theme, FONT_LOG, get_log_colors



class ColorLog(ctk.CTkFrame):
    KEYWORDS = {
        "ok": "bold", "err": "bold", "warn": "bold", "info": "",
        "header": "bold", "cmd": "", "path": "", "num": "",
        "str": "", "kw": "bold", "sym": "", "default": "",
    }

    RE_PARTS = re.compile(
        r'(\[OK\]|\[ERR\]|\[WARN\]|\[INFO\]|'
        r'---|===|'
        r'"[^"]*"|\'[^\']*\'|'
        r'\b\d+\b|'
        r'[A-Za-z]:\\[^\s]+|'
        r'\.ps1|\.vbs|slmgr|cscript|winget|powershell|'
        r'✓|✗|⚠|→)'
    )

    def __init__(self, parent, theme: Theme):
        super().__init__(parent, fg_color=theme.log_bg, corner_radius=8,
                         border_width=1, border_color=theme.card_border)
        self._theme = theme
        self._text = tk.Text(
            self, font=FONT_LOG, wrap="word", bd=0, padx=14, pady=12,
            bg=theme.log_bg, fg=theme.text, insertbackground=theme.text,
            selectbackground=theme.primary, highlightthickness=0,
            spacing1=2, spacing3=2,
        )
        sb = ctk.CTkScrollbar(self, command=self._text.yview)
        self._text.configure(yscrollcommand=sb.set)
        self._text.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=4)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=4)
        self._apply_tags()

    def _apply_tags(self):
        colors = get_log_colors(self._theme)
        for tag, weight in self.KEYWORDS.items():
            self._text.tag_configure(
                tag,
                foreground=colors.get(tag, colors["default"]),
                font=(FONT_LOG[0], FONT_LOG[1], weight) if weight else FONT_LOG,
            )

    def update_theme(self, theme: Theme):
        self._theme = theme
        self.configure(fg_color=theme.log_bg, border_color=theme.card_border)
        self._text.configure(bg=theme.log_bg, fg=theme.text, insertbackground=theme.text)
        self._apply_tags()

    def _token_tag(self, token: str) -> str:
        if token in ("[OK]", "✓") or "ACTIVATED" in token.upper():
            return "ok"
        if token in ("[ERR]", "✗") or "error" in token.lower() or "failed" in token.lower():
            return "err"
        if token in ("[WARN]", "⚠") or "warning" in token.lower():
            return "warn"
        if token in ("[INFO]", "→") or "installing" in token.lower():
            return "info"
        if token.startswith("---") or token.startswith("==="):
            return "header"
        if token.startswith('"') or token.startswith("'"):
            return "str"
        if token.isdigit():
            return "num"
        if ":\\" in token or token.endswith(".ps1") or token.endswith(".vbs"):
            return "path"
        if token.lower() in ("slmgr", "cscript", "winget", "powershell"):
            return "cmd"
        if token in ("→", "✓", "✗", "⚠"):
            return "sym"
        return "default"

    def _detect_line_tag(self, line: str) -> str | None:
        low = line.lower()
        if "[ok]" in low or line.strip().startswith("+"):
            return "ok"
        if "[err]" in low or "parsererror" in low or "no package found" in low:
            return "err"
        if "[warn]" in low or low.startswith("warning") or "warning:" in low:
            return "warn"
        if "[info]" in low:
            return "info"
        if line.startswith("---") or line.startswith("==="):
            return "header"
        return None

    def write(self, msg: str):
        for line in msg.splitlines(keepends=True):
            line_tag = self._detect_line_tag(line)
            if line_tag:
                self._text.insert("end", line, line_tag)
                continue

            pos = 0
            for m in self.RE_PARTS.finditer(line):
                if m.start() > pos:
                    self._text.insert("end", line[pos:m.start()], "default")
                token = m.group(0)
                self._text.insert("end", token, self._token_tag(token))
                pos = m.end()
            if pos < len(line):
                self._text.insert("end", line[pos:], "default")
        self._text.see("end")

    def writeln(self, msg: str):
        self.write(msg + "\n")

    def clear(self):
        self._text.delete("1.0", "end")