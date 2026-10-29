#!/usr/bin/env python3
"""Generate a simple original CHXCHX-DEV terminal GIF for the GitHub profile.

Usage: python scripts/generate_terminal.py
Dependency: Pillow 11.3.0. No API keys, telemetry or external requests.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "terminal.gif"
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/DejaVuSansMono.ttf",
]
WIDTH, HEIGHT = 1080, 362
BG = "#050d1c"
FG = "#dbefff"
ACCENT = "#39d8ff"
OK = "#69d99b"
MUTED = "#7795b6"

def get_font(size):
    for path in FONT_PATHS:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def render(lines, cursor=False):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((5, 5, WIDTH - 6, HEIGHT - 6), 18, outline="#205373", width=2)
    draw.rounded_rectangle((6, 6, WIDTH - 7, 42), 14, fill="#10253b")
    draw.line((6, 42, WIDTH - 7, 42), fill="#205373", width=2)
    for index, color in enumerate(("#f06e74", "#f2c66a", "#67d596")):
        x = 27 + index * 22
        draw.ellipse((x - 6, 18, x + 6, 30), fill=color)
    mono = get_font(21)
    small = get_font(15)
    draw.text((400, 16), "chxchx@fedora: ~/identity", font=small, fill="#c6def2")
    for i, line in enumerate(lines):
        y = 65 + i * 35
        if y > 325:
            break
        color = ACCENT if line.startswith("$") else (OK if line.startswith("[ OK ]") else (MUTED if line.startswith("...") else FG))
        draw.text((31, y), line, font=mono, fill=color)
    if cursor:
        y = 65 + (len(lines) - 1) * 35
        draw.rectangle((31 + min(len(lines[-1]), 75) * 13, y + 4, 31 + min(len(lines[-1]), 75) * 13 + 12, y + 24), fill=ACCENT)
    return image

def main():
    full = [
        "$ ./init-profile --secure",
        "... loading identity modules",
        "[ OK ] software_architecture",
        "[ OK ] applied_ai / llm_systems",
        "[ OK ] ethical_cybersecurity",
        "[ OK ] linux / open_source",
        "$ build | secure | share",
    ]
    milestones = [
        (full[:1], 650),
        (full[:2], 700),
        (full[:3], 550),
        (full[:4], 550),
        (full[:5], 550),
        (full[:6], 600),
        (full[:7], 1800),
        (full[:7], 900),
    ]
    frames = [render(lines, cursor=(idx == len(milestones) - 2)) for idx, (lines, _) in enumerate(milestones)]
    durations = [duration for _, duration in milestones]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=2)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
