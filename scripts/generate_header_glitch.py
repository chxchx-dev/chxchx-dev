#!/usr/bin/env python3
"""Animate the lunar eclipse and signature mask in the original profile art."""

from math import hypot, pi, sin, sqrt
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH = 1100
TOP = 8
# These coordinates refer to the 2048 × 682 source illustration.
MOON_CENTER = (278, 241)
MOON_RADIUS = 200
SKY_BOX = (68, 32, 493, 381)
MASK_BOX = (824, 0, 1294, 200)


def clear_center(art):
    """Fill the upper-center emblem with nearby sky, above the lettering."""
    patch = Image.new("L", art.size)
    ImageDraw.Draw(patch).polygon(
        [(805, 0), (1310, 0), (1395, 127), (1342, 154),
         (1230, 188), (1170, 195), (926, 195), (834, 184), (741, 131)],
        fill=255,
    )
    patch = patch.filter(ImageFilter.GaussianBlur(14))
    # Keep the blend out of the first row of letters.
    ImageDraw.Draw(patch).rectangle((0, 200, art.width, art.height), fill=0)
    clean_sky = art.crop((1336, 0, 1746, 200)).resize((706, 200), Image.Resampling.LANCZOS)
    replacement = art.copy()
    replacement.paste(clean_sky, (713, 0))
    return Image.composite(replacement, art, patch)


def lunar_light(art, texture):
    """Light the existing crescent from the right, behind the foreground."""
    left, top, right, bottom = SKY_BOX
    diameter = 2 * MOON_RADIUS
    surface = texture.resize((diameter, diameter), Image.Resampling.LANCZOS)
    light = Image.new("RGB", (right - left, bottom - top))
    cx, cy = MOON_CENTER
    for y in range(top, bottom):
        for x in range(left, right):
            u = (x - cx) / MOON_RADIUS
            v = (y - cy) / MOON_RADIUS
            if u * u + v * v >= 1:
                continue
            depth = sqrt(1 - u * u - v * v)
            # A lit sphere produces a curved terminator, with faint earthshine.
            sun = max(0, min(1, (0.83 * u + 0.18 * v - 0.56 * depth) * 2.4))
            terrain = surface.getpixel((x - cx + MOON_RADIUS, y - cy + MOON_RADIUS)) / 255
            level = (terrain ** 1.24) * (0.023 + 0.91 * sun ** 0.8)
            light.putpixel((x - left, y - top), tuple(round(level * c) for c in (164, 191, 219)))

    foreground = Image.new("L", light.size, 255)
    contour = [
        (68, 160), (117, 170), (152, 193), (188, 216), (223, 238),
        (250, 236), (272, 222), (310, 204), (351, 214), (381, 229),
        (400, 249), (410, 271), (401, 301), (397, 330), (429, 350),
        (452, 357), (478, 374), (493, 378), (493, 381), (68, 381),
    ]
    ImageDraw.Draw(foreground).polygon([(x - left, y - top) for x, y in contour], fill=0)
    sky = art.crop(SKY_BOX)
    # The brighter wisps of the original clouds also occlude the lunar surface.
    clouds = sky.getchannel("B").point(lambda value: round(255 * max(0.12, 1 - (value / 137) ** 2)))
    visibility = ImageChops.multiply(foreground.filter(ImageFilter.GaussianBlur(4)), clouds)
    return Image.composite(ImageChops.screen(sky, light), sky, visibility)


def signature_patch(art, sky):
    """Project the original mask into the same area of the sky as the moon."""
    left, top, _, _ = SKY_BOX
    emblem = art.crop(MASK_BOX).resize((286, 122), Image.Resampling.LANCZOS)
    emblem = ImageOps.colorize(
        emblem.getchannel("B").point(lambda value: min(255, round(value * 2.55))),
        black=(0, 0, 0),
        white=(123, 202, 245),
    )
    matte = Image.new("L", emblem.size)
    ImageDraw.Draw(matte).ellipse((-9, -20, 295, 127), fill=255)
    matte = matte.filter(ImageFilter.GaussianBlur(14))
    # Feather the extracted edges, including the top edge cut by the artwork.
    for y in range(15):
        row = matte.crop((0, y, matte.width, y + 1))
        matte.paste(row.point(lambda value: round(value * y / 15)), (0, y))
    layer = Image.new("RGB", sky.size)
    layer.paste(emblem, (146 - left, 61 - top), matte)
    return ImageChops.screen(sky, layer)


def smoothstep(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def transition(base, moon, mask, progress, seed):
    """Fade through the original dark sky and distort the reveal in thin bands."""
    frame = Image.blend(base, moon, 1 - smoothstep(progress / 0.59))
    frame = Image.blend(frame, mask, smoothstep((progress - 0.36) / 0.64))

    strength = sin(pi * progress) ** 2
    rng = Random(seed)
    draw = ImageDraw.Draw(frame)
    width, height = frame.size
    for _ in range(round(9 * strength)):
        y = rng.randrange(round(height * 0.12), round(height * 0.51))
        x = rng.randrange(round(width * 0.21), round(width * 0.74))
        span = rng.randrange(12, round(width * 0.21))
        offset = rng.choice((-1, 1)) * max(1, round(rng.uniform(2, 10) * strength))
        band = frame.crop((x, y, x + span, y + rng.randint(1, 3)))
        frame.paste(band, (x + offset, y))
        if rng.random() < 0.48:
            tone = rng.choice(((86, 162, 197), (63, 107, 166), (127, 150, 194)))
            draw.line((x, y, x + span // 2, y), fill=tone)
    return frame


def main():
    with Image.open(ASSETS / "header-original.png") as original:
        art = original.convert("RGB").resize((2048, 682), Image.Resampling.LANCZOS)
    with Image.open(ASSETS / "header-lunar-texture.jpg") as source_texture:
        texture = source_texture.convert("L")

    background = clear_center(art)
    content_height = round(art.height * WIDTH / art.width)
    base = Image.new("RGB", (WIDTH, content_height + TOP * 2))
    backdrop = background.resize((WIDTH, content_height), Image.Resampling.LANCZOS)
    base.paste(backdrop, (0, TOP))
    base.paste(backdrop.crop((0, 0, WIDTH, 1)).resize((WIDTH, TOP)), (0, 0))
    base.paste(backdrop.crop((0, content_height - 1, WIDTH, content_height)).resize((WIDTH, TOP)),
               (0, TOP + content_height))

    scale = WIDTH / art.width
    left, top, right, bottom = (round(value * scale) for value in SKY_BOX)
    position = left, top + TOP
    size = right - left, bottom - top
    sky = background.crop(SKY_BOX)
    calm = sky.resize(size, Image.Resampling.LANCZOS)
    moon = lunar_light(background, texture).resize(size, Image.Resampling.LANCZOS)
    mask = signature_patch(art, sky).resize(size, Image.Resampling.LANCZOS)

    forward = [(transition(calm, moon, mask, step / 17, 100 + step), 50) for step in range(1, 17)]
    backward = [(transition(calm, moon, mask, step / 17, 200 + step), 50) for step in range(16, 0, -1)]
    sequence = [(moon, 2600), *forward, (mask, 1480), *backward]

    # One palette across the loop keeps the city, lettering and characters still
    # and allows the GIF encoder to store only the changing part of the frame.
    samples = Image.new("RGB", (WIDTH, base.height + 2 * size[1]))
    samples.paste(base)
    samples.paste(moon, (0, base.height))
    samples.paste(mask, (size[0], base.height))
    palette = samples.quantize(colors=256)
    frames = []
    for patch, _ in sequence:
        frame = base.copy()
        frame.paste(patch, position)
        frames.append(frame.quantize(palette=palette, dither=Image.Dither.NONE))

    frames[0].save(
        ASSETS / "header-glitch.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[duration for _, duration in sequence],
        loop=0,
        disposal=1,
        optimize=True,
    )


if __name__ == "__main__":
    main()
