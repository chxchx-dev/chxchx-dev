#!/usr/bin/env python3
"""Render the CHXCHX-DEV header animation from the original banner."""
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "header-original.png"
DEST = ROOT / "assets" / "header-glitch.gif"
WIDTH = 1100
PADDING_TOP = 8
PADDING_BOTTOM = 8
MOON_X = 0.521
MOON_Y = 0.15
MOON_RADIUS = 0.023


def build_mask(size):
    """Select only the upper-center mask artwork; leave the person and Maya untouched."""
    scale = size[0] / 2048
    points = [
        (850, 0), (1290, 0), (1280, 55), (1255, 100),
        (1210, 180), (1150, 210), (1040, 210), (945, 168), (860, 85),
    ]
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(
        [(round(x * scale), round(y * scale) + PADDING_TOP) for x, y in points],
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
        x, y = rng.randrange(460, 690), rng.randrange(PADDING_TOP + 4, PADDING_TOP + 112)
        draw_stars.point((x, y), fill=(19, 38, 67))
    sky = Image.composite(stars, base, mask)

    # The moon sits inside the old mask silhouette; all other original artwork stays intact.
    content_height = height - PADDING_TOP - PADDING_BOTTOM
    cx = round(width * MOON_X)
    cy = PADDING_TOP + round(content_height * MOON_Y)
    radius = max(12, round(width * MOON_RADIUS))
    glow = Image.new("RGB", base.size, (0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (cx - radius * 1.25, cy - radius * 1.25, cx + radius * 1.25, cy + radius * 1.25),
        fill=(12, 100, 180),
    )
    sky = ImageChops.screen(sky, glow.filter(ImageFilter.GaussianBlur(radius=radius * 0.42)))

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
    content_height = frame.height - PADDING_TOP - PADDING_BOTTOM
    cx = round(WIDTH * MOON_X)
    cy = PADDING_TOP + round(content_height * MOON_Y)
    radius = max(12, round(WIDTH * MOON_RADIUS))
    left, right = cx - round(radius * 1.45), cx + round(radius * 1.45)
    top = max(PADDING_TOP, cy - round(radius * 1.35))
    bottom = min(frame.height - PADDING_BOTTOM, cy + round(radius * 1.35))
    shift = round(3 + 7 * strength)
    for index in range(10):
        y = rng.randrange(top, bottom)
        band_h = rng.choice((1, 2, 3, 5))
        x1 = rng.randrange(left, right - 15)
        x2 = rng.randrange(x1 + 12, right)
        band = frame.crop((x1, y, x2, min(bottom, y + band_h)))
        offset = rng.choice((-shift, -shift // 2, shift // 2, shift))
        frame.paste(band, (max(left, min(right - band.width, x1 + offset)), y))
    for _ in range(5):
        y = rng.randrange(top, bottom)
        x1 = rng.randrange(left, right - 12)
        x2 = min(right, x1 + rng.randrange(12, 45))
        color = rng.choice(((35, 219, 245), (89, 118, 255), (238, 76, 179)))
        draw.line((x1, y, x2, y), fill=color, width=rng.choice((1, 1, 2)))
    return frame


def main():
    if not SOURCE.is_file():
        print(f"Source missing: {SOURCE.relative_to(ROOT)}. Upload it to render the header.")
        return

    original = Image.open(SOURCE).convert("RGB")
    content_height = round(original.height * WIDTH / original.width)
    artwork = original.resize((WIDTH, content_height), Image.Resampling.LANCZOS)

    # Add a thin extension to the canvas so the title sits slightly lower without
    # cropping or repainting the original characters, dog, city, or lettering.
    base = Image.new("RGB", (WIDTH, content_height + PADDING_TOP + PADDING_BOTTOM))
    base.paste(artwork.crop((0, 0, WIDTH, 1)).resize((WIDTH, PADDING_TOP)), (0, 0))
    base.paste(artwork, (0, PADDING_TOP))
    base.paste(
        artwork.crop((0, content_height - 1, WIDTH, content_height)).resize((WIDTH, PADDING_BOTTOM)),
        (0, PADDING_TOP + content_height),
    )
    moon = make_moon_sky(base, build_mask(base.size))

    # Hold the complete banner, reveal a small crescent in the mask's place,
    # then let tight, localized glitch bands assemble the original mask again.
    sequence = [
        (base, 1650),
        (glitch(Image.blend(base, moon, 0.38), 101, 0.6), 100),
        (moon, 480),
        (glitch(moon, 102, 0.85), 90),
        (moon, 260),
        (glitch(Image.blend(moon, base, 0.30), 103, 1.0), 100),
        (glitch(Image.blend(moon, base, 0.66), 104, 1.0), 100),
        (glitch(Image.blend(moon, base, 0.94), 105, 0.7), 100),
        (glitch(base, 106, 0.55), 90),
        (base, 1800),
        (glitch(base, 107, 0.4), 80),
        (base, 1200),
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
