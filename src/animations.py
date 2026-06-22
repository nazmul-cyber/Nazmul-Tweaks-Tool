"""Lightweight UI animation helpers."""

import customtkinter as ctk


def fade_page(page_frame, theme, steps=5, interval=30, on_done=None):
    """Instant page switch — no fade animation (reduces lag)."""
    try:
        page_frame.configure(fg_color=theme.bg)
    except Exception:
        pass
    if on_done:
        on_done()


def animate_card_hover(card, theme, entering=True):
    try:
        card.configure(border_color=theme.primary if entering else theme.card_border)
    except Exception:
        pass


def animate_progress(bar, target=1.0, steps=20, interval=25, on_done=None):
    current = bar.get()

    def step(i=0):
        val = current + (target - current) * (i / steps)
        bar.set(min(val, target))
        if i < steps:
            bar.after(interval, lambda: step(i + 1))
        elif on_done:
            on_done()

    step()


def pulse_widget(widget, color_a, color_b, times=3, interval=140):
    def tick(i=0, flip=False):
        if i >= times * 2:
            try:
                widget.configure(fg_color=color_a)
            except Exception:
                pass
            return
        try:
            widget.configure(fg_color=color_b if flip else color_a)
        except Exception:
            pass
        widget.after(interval, lambda: tick(i + 1, not flip))

    tick()


def stagger_fade_in(widgets, theme, delay=55):
    """Reveal widgets with a quick fade-in effect."""
    for w in widgets:
        try:
            w.configure(fg_color=theme.bg)
        except Exception:
            pass

    def reveal(i=0):
        if i < len(widgets):
            try:
                widgets[i].configure(fg_color=theme.card if hasattr(widgets[i], "cget") else theme.bg)
            except Exception:
                try:
                    widgets[i].grid()
                except Exception:
                    pass
            if widgets[i].winfo_manager() == "grid":
                pass
            widgets[i].after(delay, lambda: reveal(i + 1))
        else:
            for w in widgets:
                try:
                    if "CTkFrame" in str(type(w)):
                        w.configure(fg_color=theme.card)
                except Exception:
                    pass

    reveal()


def click_bounce(widget, theme, original_border=None):
    """Quick press feedback on click."""
    try:
        widget.configure(border_width=2, border_color=theme.primary)
        widget.after(160, lambda: widget.configure(
            border_width=1,
            border_color=original_border or theme.card_border,
        ))
    except Exception:
        pass