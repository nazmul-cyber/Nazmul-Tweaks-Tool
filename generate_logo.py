"""Generate Nazmul Tweaks Tool logo (PNG + ICO) — teal bolt + gear mark."""

from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("pip install Pillow")
    raise

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

BG_TOP = (15, 118, 110)      # teal-700
BG_BOTTOM = (13, 148, 136)    # teal-600
ACCENT = (45, 212, 191)       # teal-300
BOLT = (255, 255, 255)
GEAR = (204, 251, 241)        # teal-100


def _lerp(a, b, t):
    return int(a + (b - a) * t)


def create_logo(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = size // 12
    radius = size // 4
    for y in range(margin, size - margin):
        t = (y - margin) / max(1, size - 2 * margin - 1)
        r = _lerp(BG_TOP[0], BG_BOTTOM[0], t)
        g = _lerp(BG_TOP[1], BG_BOTTOM[1], t)
        b = _lerp(BG_TOP[2], BG_BOTTOM[2], t)
        draw.rounded_rectangle(
            [margin, y, size - margin, y + 1],
            radius=radius,
            fill=(r, g, b, 255),
        )

    # Subtle inner ring
    ring = size // 5
    draw.ellipse(
        [ring, ring, size - ring, size - ring],
        outline=(*ACCENT, 90),
        width=max(2, size // 64),
    )

    cx, cy = size // 2, size // 2
    scale = size / 256.0

    # Gear (top-right accent)
    gx, gy = cx + int(42 * scale), cy - int(46 * scale)
    gr = int(18 * scale)
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(*GEAR, 230))
    for i in range(8):
        import math
        ang = math.radians(i * 45)
        x1 = gx + math.cos(ang) * gr * 0.75
        y1 = gy + math.sin(ang) * gr * 0.75
        x2 = gx + math.cos(ang) * gr * 1.35
        y2 = gy + math.sin(ang) * gr * 1.35
        draw.line([x1, y1, x2, y2], fill=(*GEAR, 230), width=max(3, int(4 * scale)))

    # Lightning bolt (center)
    bolt = [
        (cx + int(8 * scale), cy - int(62 * scale)),
        (cx - int(18 * scale), cy + int(4 * scale)),
        (cx + int(2 * scale), cy + int(4 * scale)),
        (cx - int(10 * scale), cy + int(62 * scale)),
        (cx + int(26 * scale), cy - int(8 * scale)),
        (cx + int(4 * scale), cy - int(8 * scale)),
    ]
    draw.polygon(bolt, fill=(*BOLT, 245))

    # Small refresh arc under bolt
    arc_box = [cx - int(34 * scale), cy + int(18 * scale), cx + int(34 * scale), cy + int(70 * scale)]
    draw.arc(arc_box, start=200, end=340, fill=(*ACCENT, 220), width=max(3, int(5 * scale)))

    return img


if __name__ == "__main__":
    logo = create_logo(256)
    logo.save(ASSETS / "logo.png")
    logo.save(
        ASSETS / "logo.ico",
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )
    print(f"Logo saved to {ASSETS}")