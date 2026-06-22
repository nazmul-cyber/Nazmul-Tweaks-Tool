"""Generate Nazmul Tweaks Tool logo (PNG + ICO) — modern N + bolt + refresh ring."""

from pathlib import Path
import math

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("pip install Pillow")
    raise

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

# Matches app Light theme: blue primary + cyan highlight
BG_TOP = (30, 64, 175)       # blue-800
BG_BOTTOM = (8, 145, 178)    # cyan-600
RING = (56, 189, 248)        # sky-400
RING_DIM = (14, 116, 144)    # cyan-700
BOLT = (255, 255, 255)
ACCENT = (125, 211, 252)     # sky-300


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def _rounded_gradient(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = size // 14
    radius = size // 5
    for y in range(margin, size - margin):
        t = (y - margin) / max(1, size - 2 * margin - 1)
        color = (
            _lerp(BG_TOP[0], BG_BOTTOM[0], t),
            _lerp(BG_TOP[1], BG_BOTTOM[1], t),
            _lerp(BG_TOP[2], BG_BOTTOM[2], t),
            255,
        )
        draw.rounded_rectangle(
            [margin, y, size - margin, y + 1],
            radius=radius,
            fill=color,
        )
    return img


def create_logo(size=256):
    img = _rounded_gradient(size)
    draw = ImageDraw.Draw(img)
    scale = size / 256.0
    cx, cy = size // 2, size // 2

    # Outer refresh ring
    ring_pad = int(34 * scale)
    draw.ellipse(
        [ring_pad, ring_pad, size - ring_pad, size - ring_pad],
        outline=(*RING, 200),
        width=max(3, int(6 * scale)),
    )
    # Ring arrow ticks (refresh hint)
    rr = (size - 2 * ring_pad) / 2
    for deg in (35, 145, 215, 325):
        ang = math.radians(deg)
        x1 = cx + math.cos(ang) * (rr - 4 * scale)
        y1 = cy + math.sin(ang) * (rr - 4 * scale)
        x2 = cx + math.cos(ang + 0.35) * (rr + 8 * scale)
        y2 = cy + math.sin(ang + 0.35) * (rr + 8 * scale)
        draw.polygon(
            [(x1, y1), (x2, y2), (x1 + math.cos(ang - 0.5) * 10 * scale, y1 + math.sin(ang - 0.5) * 10 * scale)],
            fill=(*ACCENT, 220),
        )

    # Inner glow disc
    inner = int(52 * scale)
    draw.ellipse(
        [cx - inner, cy - inner, cx + inner, cy + inner],
        fill=(*RING_DIM, 120),
        outline=(*RING, 80),
        width=max(2, int(3 * scale)),
    )

    # Lightning bolt
    bolt = [
        (cx + int(10 * scale), cy - int(58 * scale)),
        (cx - int(20 * scale), cy + int(2 * scale)),
        (cx + int(4 * scale), cy + int(2 * scale)),
        (cx - int(8 * scale), cy + int(58 * scale)),
        (cx + int(28 * scale), cy - int(10 * scale)),
        (cx + int(6 * scale), cy - int(10 * scale)),
    ]
    draw.polygon(bolt, fill=(*BOLT, 250))

    # Small "N" lettermark bottom-left
    try:
        font = ImageFont.truetype("arialbd.ttf", max(14, int(22 * scale)))
    except OSError:
        font = ImageFont.load_default()
    draw.text(
        (int(28 * scale), size - int(42 * scale)),
        "N",
        font=font,
        fill=(*ACCENT, 230),
    )

    return img


if __name__ == "__main__":
    logo = create_logo(512)
    logo_large = logo.resize((256, 256), Image.Resampling.LANCZOS)
    logo_large.save(ASSETS / "logo.png")
    logo_large.save(ASSETS / "nazmul-tweaks-tool.png")
    logo_large.save(
        ASSETS / "logo.ico",
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"Logo saved to {ASSETS}")