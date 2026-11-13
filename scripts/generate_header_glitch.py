#!/usr/bin/env python3
"""Render the CHXCHX-DEV header animation from the original banner."""
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "header-original.png"
DEST = ROOT / "assets" / "header-glitch.gif"
WIDTH = 1100


def build_mask(size):
    """Select only the upper-center mask artwork; leave the person and Maya untouched."""
    scale = size[0] / 2048
    points = [
        (850, 0), (1290, 0), (1280, 55), (1255, 100),
        (1210, 180), (1150, 210), (1040, 210), (945, 168), (860, 85),
    ]
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(
        [(round(x * scale), round(y * scale)) for x, y in points],
        fill=255,
    )
    return mask.filter(ImageFilter.GaussianBlur(radius=8))


def make_moon_sky(base, mask):
    """Replace the mask with a luminous moon instead of an empty patch of sky."""
    width, height = base.size
    rng = Random(431)
    stars = Image.new("RGB", base.size, (3, 9, 20))
    draw_stars = ImageDraw.Draw(stars)
    for _ in range(48):
        x, y = rng.randrange(460, 690), rng.randrange(4, 112)
        draw_stars.point((x, y), fill=(19, 38, 67))
    sky = Image.composite(stars, base, mask)

    # The moon sits inside the old mask silhouette; all other original artwork stays intact.
    cx, cy, radius = round(width * 0.521), round(height * 0.15), round(width * 0.034)
    glow = Image.new("RGB", base.size, (0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (cx - radius * 1.35, cy - radius * 1.35, cx + radius * 1.35, cy + radius * 1.35),
        fill=(8, 72, 128),
    )
    sky = ImageChops.screen(sky, glow.filter(ImageFilter.GaussianBlur(radius=radius * 0.38)))

    # Cut an offset shadow out of the moon disc to create a clean crescent silhouette.
    moon_mask = Image.new("L", base.size, 0)
    mask_draw = ImageDraw.Draw(moon_mask)
    mask_draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=255)
    mask_draw.ellipse(
        (cx + radius * 0.43, cy - radius * 1.15,
         cx + radius * 2.43, cy + radius * 1.15),
        fill=0,
    )
    moon = Image.new("RGBA", base.size, (0, 0, 0, 0))
    moon_color = Image.new("RGBA", base.size, (177, 224, 248, 255))
    moon_color.putalpha(moon_mask)
    moon = Image.alpha_composite(moon, moon_color)

    # Fine craters add texture while keeping the crescent clean at profile scale.
    details = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(details)
    for ox, oy, crater in [(-0.40, -0.22, 0.095), (-0.20, 0.28, 0.075), (-0.10, -0.52, 0.05)]:
        r = max(1, round(radius * crater))
        x, y = round(cx + radius * ox), round(cy + radius * oy)
        d.ellipse((x-r, y-r, x+r, y+r), fill=(89, 151, 192, 170))
    details.putalpha(ImageChops.multiply(details.getchannel("A"), moon_mask))
    moon = Image.alpha_composite(moon, details)
    return Image.alpha_composite(sky.convert("RGBA"), moon).convert("RGB")


def glitch(image, seed, strength=1):
    """Apply short horizontal data tears around the moon/mask transition."""
    frame = image.copy()
    draw = ImageDraw.Draw(frame)
    rng = Random(seed)
    left, right = round(WIDTH * 0.405), round(WIDTH * 0.635)
    top, bottom = 2, min(frame.height - 1, round(frame.height * 0.31))
    shift = round(5 + 13 * strength)
    for index in range(10):
        y = rng.randrange(top, bottom)
        band_h = rng.choice((1, 2, 3, 5))
        x1 = rng.randrange(left, right - 30)
        x2 = rng.randrange(x1 + 25, right)
        band = frame.crop((x1, y, x2, min(bottom, y + band_h)))
        offset = rng.choice((-shift, -shift // 2, shift // 2, shift))
        frame.paste(band, (max(left, min(right - band.width, x1 + offset)), y))
    for _ in range(5):
        y = rng.randrange(top, bottom)
        x1 = rng.randrange(left, right - 20)
        x2 = min(right, x1 + rng.randrange(18, 85))
        color = rng.choice(((35, 219, 245), (89, 118, 255), (238, 76, 179)))
        draw.line((x1, y, x2, y), fill=color, width=rng.choice((1, 1, 2)))
    return frame


def main():
    if not SOURCE.is_file():
        print(f"Source missing: {SOURCE.relative_to(ROOT)}. Upload it to render the header.")
        return

    original = Image.open(SOURCE).convert("RGB")
    height = round(original.height * WIDTH / original.width)
    base = original.resize((WIDTH, height), Image.Resampling.LANCZOS)
    moon = make_moon_sky(base, build_mask(base.size))

    # Move from the original artwork to the moon, let the glitch assemble the mask,
    # then hold the finished banner. No empty-sky frame is used.
    sequence = [
        (base, 1500),
        (glitch(Image.blend(base, moon, 0.32), 101, 0.55), 110),
        (glitch(Image.blend(base, moon, 0.68), 102, 0.85), 110),
        (moon, 760),
        (glitch(moon, 103, 1.0), 100),
        (glitch(Image.blend(moon, base, 0.28), 104, 1.0), 100),
        (glitch(Image.blend(moon, base, 0.58), 105, 1.0), 90),
        (glitch(Image.blend(moon, base, 0.84), 106, 0.85), 90),
        (glitch(base, 107, 0.7), 100),
        (base, 1650),
        (glitch(base, 108, 0.45), 90),
        (base, 1100),
    ]

    frames = [frame.quantize(colors=96, dither=Image.Dither.NONE) for frame, _ in sequence]
    DEST.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        DEST,
        save_all=True,
        append_images=frames[1:],
        duration=[duration for _, duration in sequence],
        loop=0,
        disposal=2,
        optimize=True,
    )
    print(f"Generated {DEST.relative_to(ROOT)} ({DEST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
