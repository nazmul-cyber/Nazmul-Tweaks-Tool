"""Compact CPU / RAM / GPU usage bars."""

import customtkinter as ctk
from themes import Theme, FONT_SMALL


class ResourceBar(ctk.CTkFrame):
    def __init__(self, parent, theme: Theme):
        super().__init__(
            parent, fg_color=theme.card, corner_radius=10,
            border_width=1, border_color=theme.card_border,
        )
        self._theme = theme
        self._rows: dict[str, dict] = {}
        ctk.CTkLabel(
            self, text="System", font=FONT_SMALL, text_color=theme.text_muted,
        ).pack(anchor="w", padx=10, pady=(8, 4))

        for key, label, color in (
            ("cpu", "CPU", theme.primary),
            ("ram", "RAM", theme.highlight),
            ("gpu", "GPU", theme.accent),
        ):
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=label, font=FONT_SMALL, text_color=theme.text_muted,
                         width=34, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, height=8, width=120, progress_color=color,
                                     fg_color=theme.btn_secondary)
            bar.pack(side="left", padx=(4, 6))
            bar.set(0)
            val = ctk.CTkLabel(row, text="—%", font=FONT_SMALL, text_color=theme.text, width=72, anchor="e")
            val.pack(side="right")
            self._rows[key] = {"bar": bar, "val": val, "color": color}

        self._freed = ctk.CTkLabel(
            self, text="", font=FONT_SMALL, text_color=theme.success, wraplength=200,
        )
        self._freed.pack(anchor="w", padx=10, pady=(4, 10))

    def update_theme(self, theme: Theme):
        self._theme = theme
        self.configure(fg_color=theme.card, border_color=theme.card_border)
        colors = {"cpu": theme.primary, "ram": theme.highlight, "gpu": theme.accent}
        for key, row in self._rows.items():
            row["color"] = colors[key]
            row["bar"].configure(progress_color=colors[key], fg_color=theme.btn_secondary)

    def update_stats(self, stats: dict | None):
        if not stats:
            return
        ram = stats.get("ram", {})
        mapping = {
            "cpu": stats.get("cpu_pct", 0),
            "ram": ram.get("used_pct", 0),
            "gpu": stats.get("gpu_pct", 0),
        }
        detail = {
            "cpu": f"{mapping['cpu']}%",
            "ram": f"{mapping['ram']}% ({ram.get('available_mb', ram.get('free_mb', 0))} MB avail)",
            "gpu": f"{mapping['gpu']}%",
        }
        t = self._theme
        for key, pct in mapping.items():
            row = self._rows[key]
            pct = max(0, min(100, int(pct)))
            row["bar"].set(pct / 100.0)
            color = row["color"]
            if pct >= 85:
                color = t.error
            elif pct >= 65:
                color = t.warning
            row["bar"].configure(progress_color=color)
            row["val"].configure(text=detail[key])

    def show_refresh_result(self, result: dict):
        drop_pct = result.get("ram_drop_pct", 0)
        before_pct = result.get("ram_before_used_pct")
        after_pct = result.get("ram_after_used_pct")
        freed = result.get("ram_freed_mb", 0)
        cpu = result.get("cpu_freed_pct", 0)
        gpu = result.get("gpu_freed_pct", 0)
        parts = []
        if drop_pct and drop_pct > 0 and before_pct is not None and after_pct is not None:
            parts.append(f"RAM {before_pct}%→{after_pct}% (-{drop_pct}%)")
        elif freed > 0:
            parts.append(f"+{freed} MB avail")
        elif freed < 0:
            parts.append(f"{freed} MB avail")
        if cpu > 0:
            parts.append(f"CPU -{cpu}%")
        if gpu > 0:
            parts.append(f"GPU -{gpu}%")
        if parts:
            color = self._theme.success if (drop_pct or 0) > 0 or freed > 0 else self._theme.warning
            self._freed.configure(text=f"Refresh: {', '.join(parts)}", text_color=color)
        else:
            after_pct = after_pct if after_pct is not None else "?"
            self._freed.configure(
                text=f"Refresh done — RAM still {after_pct}% used",
                text_color=self._theme.text_muted,
            )
        if after_pct is not None and self._rows.get("ram"):
            pct = max(0, min(100, int(after_pct)))
            self._rows["ram"]["bar"].set(pct / 100.0)
            avail = result.get("ram_after_available", result.get("ram_after_free", 0))
            self._rows["ram"]["val"].configure(text=f"{pct}% ({avail} MB avail)")