#!/usr/bin/env python3
"""Render the blue moon and crimson mask phases of the profile banner."""

from math import hypot, pi, sin, sqrt
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WIDTH = 1100
TOP = 8
# Coordinates are measured on the 2048 × 682 source illustration.
MOON_CENTER = (1092, 100)
MOON_RADIUS = 89
ORIGINAL_MOON = (278, 241, 200)


def smoothstep(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def remove_left_rim(art):
    """Restore the sky around the old eclipse without touching the foreground."""
    box = (170, 0, 550, 365)
    left, top, right, bottom = box
    size = right - left, bottom - top
    stars = art.crop((1392, 0, 1762, 195)).resize(size, Image.Resampling.LANCZOS)
    sky = art.crop(box)
    matte = Image.new("L", size)
    cx, cy, radius = ORIGINAL_MOON
    for y in range(top, bottom):
        for x in range(left, right):
            distance = hypot(x - cx, y - cy)
            weight = 1 - smoothstep((abs(distance - radius) - 22) / 37)
            weight *= smoothstep((x - 181) / 58)
            weight *= 1 - smoothstep((y - 348) / 14)
            # Fade behind the hair and the cloud bank around the ridge.
            weight *= 1 - smoothstep((y - 166) / 53) * (1 - smoothstep((x - 375) / 52))
            matte.putpixel((x - left, y - top), round(255 * weight))
    clean = art.copy()
    clean.paste(Image.composite(stars, sky, matte), (left, top))
    return clean


def clear_center(art):
    """Replace the central emblem with stars for the blue phase."""
    matte = Image.new("L", art.size)
    ImageDraw.Draw(matte).polygon(
        [(755, 0), (1364, 0), (1420, 117), (1352, 166), (1218, 193),
         (960, 194), (848, 179), (738, 132)],
        fill=255,
    )
    matte = matte.filter(ImageFilter.GaussianBlur(18))
    ImageDraw.Draw(matte).rectangle((0, 200, art.width, art.height), fill=0)
    sky = art.crop((1390, 0, 1750, 200)).resize((750, 200), Image.Resampling.LANCZOS)
    replacement = art.copy()
    replacement.paste(sky, (700, 0))
    return Image.composite(replacement, art, matte)


def add_crescent(art, texture):
    """Apply directional lighting to the same crater texture used in the previous banner."""
    radius = MOON_RADIUS
    diameter = 2 * radius
    texture = texture.resize((diameter, diameter), Image.Resampling.LANCZOS)
    light = Image.new("RGB", texture.size)
    for y in range(diameter):
        for x in range(diameter):
            u, v = (x + 0.5 - radius) / radius, (y + 0.5 - radius) / radius
            distance = hypot(u, v)
            if distance >= 1:
                continue
            depth = sqrt(1 - distance * distance)
            sun = max(0, min(1, (0.83 * u + 0.18 * v - 0.56 * depth) * 2.4))
            edge = smoothstep((1 - distance) * radius / 1.7)
            rim = smoothstep((distance - 0.967) / 0.030) * max(0, u)
            terrain = texture.getpixel((x, y)) / 255
            level = edge * (terrain ** 1.24 * (0.018 + 1.18 * sun ** 0.8) + 0.28 * rim)
            light.putpixel((x, y), tuple(min(255, round(level * channel)) for channel in (174, 208, 247)))
    cx, cy = MOON_CENTER
    position = (cx - radius, cy - radius)
    layer = Image.new("RGB", art.size)
    layer.paste(light, position)
    glow = layer.filter(ImageFilter.GaussianBlur(13)).point(lambda value: value * 0.44)
    return ImageChops.screen(ImageChops.screen(art, glow), layer)


def mask_phase(art):
    """Warm the sky and bring out the face while preserving the original blue outlines."""
    red_light = Image.new("L", art.size)
    draw = ImageDraw.Draw(red_light)
    draw.ellipse((60, -290, 1890, 295), fill=46)
    draw.ellipse((405, -155, 1655, 248), fill=75)
    draw.ellipse((736, -58, 1410, 196), fill=99)
    red_light = red_light.filter(ImageFilter.GaussianBlur(82))
    draw = ImageDraw.Draw(red_light)
    # Keep the lettering and foreground silhouettes out of the sky grade.
    for y in range(158, 259):
        band = red_light.crop((540, y, 1650, y + 1))
        fade = 1 - smoothstep((y - 158) / 101)
        red_light.paste(band.point(lambda value: round(value * fade)), (540, y))
    draw.rectangle((540, 259, 1650, 378), fill=0)
    draw.rectangle((0, 202, 530, art.height), fill=0)
    draw.rectangle((1755, 0, art.width, art.height), fill=0)
    draw.rectangle((0, 420, art.width, art.height), fill=0)
    red_light = red_light.filter(ImageFilter.GaussianBlur(12))
    warm = ImageChops.screen(art, Image.new("RGB", art.size, (170, 31, 79)))
    tinted = Image.composite(warm, art, red_light)

    face_box = (828, 0, 1316, 197)
    face = art.crop(face_box)
    blue = face.getchannel("B")
    highlights = Image.merge("RGB", (
        blue.point(lambda value: min(255, value * 1.36)),
        blue.point(lambda value: min(255, value * 0.71)),
        blue.point(lambda value: min(255, value * 0.91)),
    ))
    matte = Image.new("L", face.size)
    ImageDraw.Draw(matte).ellipse((-10, -110, face.width + 10, face.height - 4), fill=255)
    matte = matte.filter(ImageFilter.GaussianBlur(22))
    tinted.paste(ImageChops.screen(tinted.crop(face_box), highlights), face_box, matte)

    # A small red catchlight picks out the original mark at the center of the face.
    ember = Image.new("RGB", art.size)
    ImageDraw.Draw(ember).ellipse((1051, 111, 1064, 124), fill=(240, 54, 94))
    return ImageChops.screen(tinted, ember.filter(ImageFilter.GaussianBlur(3)))


def banner_frame(art):
    height = round(art.height * WIDTH / art.width)
    resized = art.resize((WIDTH, height), Image.Resampling.LANCZOS)
    frame = Image.new("RGB", (WIDTH, height + TOP * 2))
    frame.paste(resized, (0, TOP))
    frame.paste(resized.crop((0, 0, WIDTH, 1)).resize((WIDTH, TOP)), (0, 0))
    frame.paste(resized.crop((0, height - 1, WIDTH, height)).resize((WIDTH, TOP)), (0, TOP + height))
    return frame


def glitch(frame, progress, seed, reverse):
    """Tear wide strips across the banner while the signal moves down or up."""
    power = sin(pi * progress) ** 2 * (0.66 if reverse else 1.0)
    rng = Random(seed)
    width, height = frame.size
    source = frame.copy()
    draw = ImageDraw.Draw(frame)
    sweep = 0.13 + 0.74 * progress
    for index in range(round(18 * power)):
        y = round(height * (sweep + rng.uniform(-0.29, 0.29)))
        y = max(5, min(height - 12, y))
        band_height = rng.randint(1, 7)
        left = rng.randint(16, width // 4)
        right = rng.randint(3 * width // 4, width - 16)
        offset = rng.choice((-1, 1)) * round(rng.uniform(3, 24) * power)
        band = source.crop((left, y, right, y + band_height))
        if index % 3 == 0:
            red, green, blue = band.split()
            red = ImageChops.offset(red, max(1, round(6 * power)), 0)
            blue = ImageChops.offset(blue, -max(1, round(5 * power)), 0)
            band = Image.merge("RGB", (red, green, blue))
        frame.paste(band, (left + offset, y))
        if index % 3 == 1:
            start = rng.randint(left, right - 110)
            color = rng.choice(((148, 55, 107), (61, 129, 178), (155, 100, 155)))
            draw.line((start, y, start + rng.randint(40, 110), y), fill=color)
    return frame


def transition(blue, calm, red, progress, seed, reverse=False):
    # Let the lunar disk go dark before the signature mask settles in.
    frame = Image.blend(blue, calm, smoothstep((progress - 0.09) / 0.45))
    frame = Image.blend(frame, red, smoothstep((progress - 0.38) / 0.52))
    return glitch(frame, 1 - progress if reverse else progress, seed, reverse)


def main():
    with Image.open(ASSETS / "header-original.png") as original:
        art = original.convert("RGB").resize((2048, 682), Image.Resampling.LANCZOS)
    with Image.open(ASSETS / "header-lunar-texture.jpg") as source_texture:
        texture = source_texture.convert("L")

    art = remove_left_rim(art)
    sky = clear_center(art)
    blue = banner_frame(add_crescent(sky, texture))
    calm = banner_frame(sky)
    red = banner_frame(mask_phase(art))

    forward = [(transition(blue, calm, red, step / 15, 100 + step), 50) for step in range(1, 15)]
    backward = [(transition(blue, calm, red, step / 15, 200 + step, reverse=True), 50)
                for step in range(14, 0, -1)]
    sequence = [(blue, 2350), *forward, (red, 1750), *backward]

    samples = Image.new("RGB", (WIDTH, blue.height * 3))
    for index, frame in enumerate((blue, calm, red)):
        samples.paste(frame, (0, blue.height * index))
    palette = samples.quantize(colors=256)
    frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame, _ in sequence]
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
