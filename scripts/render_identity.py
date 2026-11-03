#!/usr/bin/env python3
"""Rasterize the CHXCHX-DEV identity panel for reliable GitHub README display.

Source SVG remains editable; generated PNG is the compatible README asset.
Run: python scripts/render_identity.py
Requires: CairoSVG==2.9.1, Pillow==11.3.0.
"""
from pathlib import Path
from xml.etree import ElementTree
from io import BytesIO

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "identity-stack.svg"
OUTPUT = ROOT / "assets" / "identity-stack.png"


def main() -> None:
    source = SOURCE.read_bytes()
    document = ElementTree.fromstring(source)
    if document.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Expected an SVG document")
    if b"<script" in source.lower() or b"foreignobject" in source.lower():
        raise ValueError("Unexpected executable or embedded HTML")
    raster = cairosvg.svg2png(bytestring=source, output_width=2280, output_height=936)
    image = Image.open(BytesIO(raster)).convert("RGB")
    if image.size != (2280, 936):
        raise RuntimeError(f"Unexpected image dimensions: {image.size}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=True)
    print(f"Generated {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
