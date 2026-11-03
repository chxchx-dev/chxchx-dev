#!/usr/bin/env python3
"""CHXCHX / SIGNAL: original telemetry based on GitHub contribution records.

Generate assets/activity-signal.svg and assets/activity-signal.png.
The default GITHUB_TOKEN reads visible GitHub activity; no personal token required.
"""
import base64
import json
import os
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

import cairosvg
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
LOGIN = os.environ.get("PROFILE_USER", "chxchx-dev")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
QUERY = """query($login:String!, $start:DateTime!, $end:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$start, to:$end) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def contributions():
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required to render verified activity")
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=364)
    records = {}
    a = start
    while a <= end:
        b = min(a + timedelta(days=89), end)
        payload = json.dumps({"query": QUERY, "variables": {
            "login": LOGIN,
            "start": a.isoformat() + "T00:00:00Z",
            "end": b.isoformat() + "T23:59:59Z",
        }}).encode()
        request = Request("https://api.github.com/graphql", data=payload, headers={
            "Authorization": "Bearer " + TOKEN,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "chxchx-dev-activity-signal",
        }, method="POST")
        with urlopen(request, timeout=30) as handle:
            result = json.load(handle)
        if result.get("errors"):
            raise RuntimeError("GraphQL returned errors: " + json.dumps(result["errors"]))
        account = (result.get("data") or {}).get("user")
        if not account:
            raise RuntimeError("User contribution data is not available")
        weeks = account["contributionsCollection"]["contributionCalendar"]["weeks"]
        for week in weeks:
            for day in week["contributionDays"]:
                if a.isoformat() <= day["date"] <= b.isoformat():
                    records[day["date"]] = int(day["contributionCount"])
        a = b + timedelta(days=1)
    if len(records) < 350:
        raise RuntimeError("Incomplete GitHub calendar: " + str(len(records)) + " days")
    return start, end, records


def portrait():
    source = ASSETS / "header-original.png"
    if not source.exists():
        return ""
    with Image.open(source) as original:
        w, h = original.size
        face = original.convert("RGB").crop((int(w * .394), 0, int(w * .635), int(h * .277)))
        face = ImageEnhance.Brightness(face).enhance(1.5)
        face = ImageEnhance.Contrast(face).enhance(1.4)
        face = ImageOps.colorize(ImageOps.grayscale(face), "#031325", "#2eb8ec")
        memory = BytesIO()
        face.save(memory, "JPEG", quality=82, optimize=True)
    return base64.b64encode(memory.getvalue()).decode("ascii")


def color(value):
    if value == 0:
        return "#102236"
    if value <= 2:
        return "#124566"
    if value <= 5:
        return "#156f98"
    if value <= 10:
        return "#1ba7c5"
    return "#5ae6ef"


def build_svg(start, end, records):
    total = sum(records.values())
    active = sum(value > 0 for value in records.values())
    longest, current = 0, 0
    for delta in range(365):
        day = (start + timedelta(days=delta)).isoformat()
        if records.get(day, 0):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    graph_start = start - timedelta(days=(start.weekday() + 1) % 7)
    width_weeks = ((end - graph_start).days // 7) + 1
    if width_weeks > 54:
        raise RuntimeError("Unexpected activity grid width")
    segs = [f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="470" viewBox="0 0 1200 470" role="img" aria-labelledby="title desc">
<title id="title">CHXCHX-DEV / Signal Log</title>
<desc id="desc">Actividad verificada: {total} contribuciones visibles en 365 días, {active} días activos y una racha máxima de {longest} días.</desc>
<defs>
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#030813"/><stop offset=".56" stop-color="#07182c"/><stop offset="1" stop-color="#020916"/></linearGradient>
<linearGradient id="neon" x2="1"><stop stop-color="#11d5e9"/><stop offset=".5" stop-color="#19578e"/><stop offset="1" stop-color="#11d5e9"/></linearGradient>
<clipPath id="face"><rect x="850" y="111" width="294" height="154" rx="12"/></clipPath>
</defs>
<rect width="1200" height="470" fill="url(#bg)" rx="18"/>
<rect x="4" y="4" width="1192" height="462" fill="none" stroke="url(#neon)" stroke-width="2" rx="16"/>
<path d="M21 4h66m1026 0h66M21 466h66m1026 0h66" stroke="#58ecff" stroke-width="2.5"/>
<path d="M814 30v414" stroke="#1d678b" stroke-width="1.4"/>
<text x="53" y="62" fill="#eff8ff" font-size="31" font-weight="800" font-family="DejaVu Sans,Arial,sans-serif">CHXCHX / SIGNAL</text>
<text x="54" y="89" fill="#3cd5ee" font-size="14" font-family="DejaVu Sans Mono,monospace">~/activity --source github --window 365d</text>
<path d="M53 106H780" stroke="#1b5077" stroke-width="1"/>
<text x="843" y="62" fill="#64e8f7" font-size="15" font-family="DejaVu Sans Mono,monospace">NODE // CHXCHX-DEV</text>
<text x="843" y="86" fill="#a6c1d5" font-size="13" font-family="DejaVu Sans Mono,monospace">STATUS: VERIFIED • UTC</text>
<circle cx="1130" cy="80" r="5" fill="#36e5c8"/>
<rect x="842" y="104" width="310" height="169" rx="12" fill="#06192c" stroke="#16618d" stroke-width="1.4"/>
"""]
    art = portrait()
    if art:
        segs.append('<g clip-path="url(#face)"><image x="850" y="111" width="294" height="154" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,' + art + '" opacity=".85"/></g>')
    segs.append('<rect x="987" y="184" width="7" height="7" fill="#f1493a"/>')
    for x, label, value in [
        (54, "CONTRIBUCIONES VISIBLES", total),
        (319, "DÍAS ACTIVOS", active),
        (575, "RACHA MÁXIMA", longest),
    ]:
        segs.append(f'<text x="{x}" y="139" fill="#91aec7" font-size="14" font-family="DejaVu Sans Mono,monospace">{escape(label)}</text>')
        segs.append(f'<text x="{x}" y="191" fill="#f0faff" font-size="48" font-weight="800" font-family="DejaVu Sans,Arial,sans-serif">{value}</text>')
    segs.extend([
        '<path d="M296 127v71M553 127v71" stroke="#1a4d70" stroke-width="1"/>',
        '<text x="53" y="236" fill="#4de3f4" font-size="14" font-family="DejaVu Sans Mono,monospace">/ CONTRIBUTION PACKETS</text>',
    ])
    first = date(start.year, start.month, 1)
    if first < start:
        first = date(start.year + (start.month == 12), (start.month % 12) + 1, 1)
    months = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
    while first <= end:
        col = (first - graph_start).days // 7
        segs.append(f'<text x="{53 + col * 12.8:.1f}" y="262" fill="#7d9bb5" font-size="11" font-family="DejaVu Sans Mono,monospace">{months[first.month - 1]}</text>')
        first = date(first.year + (first.month == 12), (first.month % 12) + 1, 1)
    for delta in range(365):
        day = start + timedelta(days=delta)
        col = (day - graph_start).days // 7
        row = (day.weekday() + 1) % 7
        x = 54 + col * 12.8
        y = 281 + row * 15
        value = records.get(day.isoformat(), 0)
        segs.append(f'<path d="M{x:.1f} {y:.1f}h7l2 2v7h-9z" fill="{color(value)}" stroke="#20415b" stroke-width=".6"/>')
        if value >= 11:
            segs.append(f'<rect x="{x + 2:.1f}" y="{y + 2:.1f}" width="3" height="1" fill="#e7ffff"/>')
    segs.extend([
        '<path d="M53 406h727" stroke="#20506e" stroke-width="1"/>',
        f'<text x="53" y="435" fill="#b0cadc" font-size="14" font-family="DejaVu Sans Mono,monospace">{start.isoformat()} → {end.isoformat()}</text>',
        '<text x="845" y="307" fill="#e7f8ff" font-size="24" font-weight="800" font-family="DejaVu Sans,Arial,sans-serif">BUILD // SECURE</text>',
        '<text x="845" y="336" fill="#4bdbea" font-size="15" font-family="DejaVu Sans Mono,monospace">LINUX · AI · OPEN SOURCE</text>',
        '<path d="M845 356h304" stroke="#215b78" stroke-width="1"/>',
        '<text x="845" y="385" fill="#a9c0d3" font-size="13" font-family="DejaVu Sans Mono,monospace">SOURCE: GITHUB GRAPHQL</text>',
        '<text x="845" y="407" fill="#a9c0d3" font-size="13" font-family="DejaVu Sans Mono,monospace">PUBLICLY VISIBLE DATA</text>',
        '<text x="845" y="437" fill="#4fe4f0" font-size="13" font-family="DejaVu Sans Mono,monospace">&gt; build --ethical --open</text>',
        '</svg>',
    ])
    return "\n".join(segs)


def main():
    start, end, records = contributions()
    ASSETS.mkdir(parents=True, exist_ok=True)
    svg = build_svg(start, end, records)
    (ASSETS / "activity-signal.svg").write_text(svg, encoding="utf-8")
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=1800, output_height=705)
    with Image.open(BytesIO(png)) as im:
        if im.size != (1800, 705):
            raise RuntimeError("Bad PNG dimensions")
    (ASSETS / "activity-signal.png").write_bytes(png)
    print(f"Verified activity: {len(records)} days, {start} to {end}; rendered PNG")


if __name__ == "__main__":
    main()
