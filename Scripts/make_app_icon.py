#!/usr/bin/env python3
"""Builds Frost's app icon from Resources/Icon-source.webp.

The source is a 1024x1024 rounded square on a white background. This cuts it
out, places it on the macOS icon grid with a drop shadow, and writes
Resources/Icon.png, every size in AppIcon.appiconset, and website/icon.png.

Usage: Scripts/make_app_icon.py   (requires Pillow)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parents[1]
art = Image.open(root / "Resources/Icon-source.webp").convert("RGB")
assert art.size == (1024, 1024), art.size

# Cut the rounded square out of its white background. The source corners are
# circular with r ~ 200; inset slightly so no white fringe survives.
ss = 4
mask = Image.new("L", (1024 * ss, 1024 * ss), 0)
ImageDraw.Draw(mask).rounded_rectangle(
    (2 * ss, 2 * ss, (1024 - 2) * ss - 1, (1024 - 2) * ss - 1), radius=198 * ss, fill=255
)
mask = mask.resize((1024, 1024), Image.LANCZOS)
square = art.convert("RGBA")
square.putalpha(mask)

# macOS icon grid: an 824x824 shape centered on a 1024x1024 canvas, with a
# soft drop shadow.
size, origin = 824, 100
square = square.resize((size, size), Image.LANCZOS)
canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
shadow_alpha = Image.new("L", (1024, 1024), 0)
shadow_alpha.paste(square.getchannel("A").point(lambda a: a * 0.35), (origin, origin + 10))
shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(12))
shadow = Image.new("RGBA", (1024, 1024), (0, 0, 0, 255))
shadow.putalpha(shadow_alpha)
canvas = Image.alpha_composite(canvas, shadow)
canvas.alpha_composite(square, (origin, origin))
canvas.save(root / "Resources/Icon.png", optimize=True)

iconset = root / "Ice/Resources/Assets.xcassets/AppIcon.appiconset"
for points in [16, 32, 128, 256, 512]:
    for scale in [1, 2]:
        pixels = points * scale
        suffix = "@2x" if scale == 2 else ""
        image = canvas if pixels == 1024 else canvas.resize((pixels, pixels), Image.LANCZOS)
        image.save(iconset / f"icon_{points}x{points}{suffix}.png", optimize=True)

canvas.resize((512, 512), Image.LANCZOS).save(root / "website/icon.png", optimize=True)
print("Wrote Resources/Icon.png, AppIcon.appiconset, and website/icon.png")
