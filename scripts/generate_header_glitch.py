#!/usr/bin/env python3
"""Render CHXCHX-DEV header GIF from the owner's original PNG, without API calls."""
from pathlib import Path
from random import Random
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "header-original.png"
DEST = ROOT / "assets" / "header-glitch.gif"
README = ROOT / "README.md"
WIDTH = 1100


def main():
    if not SOURCE.is_file():
        print(f"Source missing: {SOURCE.relative_to(ROOT)}. Upload it to render the header.")
        return
    original = Image.open(SOURCE).convert("RGB")
    height = round(original.height * WIDTH / original.width)
    base = original.resize((WIDTH, height), Image.Resampling.LANCZOS)

    # Mask only the upper-central figure. Keep the title and city untouched.
    scale = WIDTH / 2048
    coords = [(850, 0), (1290, 0), (1280, 55), (1255, 100),
              (1210, 180), (1150, 210), (1040, 210), (945, 168), (860, 85)]
    mask = Image.new("L", base.size, 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.polygon([(round(x * scale), round(y * scale)) for x, y in coords], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=8))
    stars = Image.new("RGB", base.size, (3, 9, 20))
    sdraw = ImageDraw.Draw(stars)
    rng = Random(431)
    for _ in range(42):
        x, y = rng.randrange(460, 690), rng.randrange(4, 112)
        sdraw.point((x, y), fill=(19, 38, 67))
    empty_sky = Image.composite(stars, base, mask)
    timeline = [
        (0.00, 0, 2100), (0.25, 1, 100), (0.90, 6, 100),
        (1.00, 0, 700), (0.70, 8, 90), (0.10, 4, 120),
        (1.00, 0, 300), (0.20, 8, 110), (0.00, 0, 2200),
    ]
    frames = []
    for index, (fade, jitter, duration) in enumerate(timeline):
        frame = Image.blend(base, empty_sky, fade)
        if jitter:
            local = Random(912 + index)
            for j in range(7):
                y = local.randrange(4, 109)
                x1 = local.randrange(450, 525)
                x2 = local.randrange(570, 687)
                band = frame.crop((x1, y, x2, y + 2))
                frame.paste(band, (x1 + (jitter if j % 2 else -jitter), y))
            draw = ImageDraw.Draw(frame)
            for _ in range(3):
                y = local.randrange(8, 107)
                draw.line((local.randrange(455, 530), y, local.randrange(580, 680), y),
                          fill=(7, 81, 120), width=1)
        frames.append(frame.quantize(colors=96, dither=Image.Dither.NONE))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        DEST, save_all=True, append_images=frames[1:],
        duration=[duration for _, _, duration in timeline], loop=0,
        disposal=2, optimize=True,
    )
    print(f"Generated {DEST.relative_to(ROOT)} ({DEST.stat().st_size} bytes)")

    if README.exists():
        content = README.read_text(encoding="utf-8")
        old = '<img alt="CHXCHX-DEV — banner personal, máscara y ciudad nocturna" width="100%" src="./assets/brand-banner.svg" />'
        new = """<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/header-original.png" />
  <img alt="CHXCHX-DEV: ciudad nocturna con máscara que desaparece y reaparece mediante glitch" width="100%" src="./assets/header-glitch.gif" />
</picture>"""
        if old in content:
            README.write_text(content.replace(old, new, 1), encoding="utf-8")
            print("README now references animated header and reduced-motion fallback")


if __name__ == "__main__":
    main()
