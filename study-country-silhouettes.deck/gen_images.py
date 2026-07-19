#!/usr/bin/env python3
"""Render country silhouettes from Natural Earth data and (re)generate the
.deck files.

Unlike the flag pack there is no per-country image to download: the public
domain Natural Earth 1:50m country outlines (one ~3 MB GeoJSON, fetched once)
are rendered locally with Pillow, so every silhouette has the same style —
dark shape, white background, mainland centered and filling the frame.

Distant territories are dropped so the shape people recognize fills the
frame: only the largest landmass is kept, plus pieces within KEEP_RADIUS
degrees of it (so Corsica, Tasmania and Baffin Island stay, while French
Guiana, Hawaii and Svalbard go). Antimeridian-straddling countries (Russia,
New Zealand) are unwrapped first so they don't render as two far-apart
halves.

Re-runnable: existing images are skipped, so a second run is cheap. The deck
files are always rebuilt from the list below, skipping any entry whose image
is missing on disk, so the decks and the images never drift apart.

    python3 gen_images.py            # fetch data once, render missing, rebuild decks
    python3 gen_images.py --rebuild  # just rebuild decks
"""

import json
import math
import os
import sys
import urllib.request

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
GEOJSON = os.path.join(HERE, "ne_50m_admin_0_countries.geojson")
GEOJSON_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
               "master/geojson/ne_50m_admin_0_countries.geojson")
UA = "study-country-silhouettes/1.0 (personal flashcard deck)"

SIZE = 480      # canvas, px
MARGIN = 24     # px of whitespace around the shape
SS = 3          # supersampling factor for smooth edges
# The shape is an alpha mask on transparency, drawn in the web light theme's
# --fg; the decks declare "# img-tint: fg" so dark mode recolors it (CSS
# invert on the web, a textColor mask in the GUI).
BG = (0, 0, 0, 0)
FG = (0x21, 0x1d, 0x16, 255)

# (level, slug, Natural Earth ADMIN name, display name, [accepted variants])
# Levels: 1 = iconic shapes, 2 = regional, 3 = expert/confusable.
# NOTE: cards are image-only questions — prompt text would give every card in
# a deck the same ID (IDs hash the question's text lines).
COUNTRIES = [
    # ── Level 1 — iconic ────────────────────────────────────────────────
    (1, "italy",          "Italy",          "Italy",          []),
    (1, "france",         "France",         "France",         []),
    (1, "spain",          "Spain",          "Spain",          []),
    (1, "portugal",       "Portugal",       "Portugal",       []),
    (1, "united-kingdom", "United Kingdom", "United Kingdom", ["UK", "Great Britain", "Britain"]),
    (1, "ireland",        "Ireland",        "Ireland",        []),
    (1, "germany",        "Germany",        "Germany",        []),
    (1, "norway",         "Norway",         "Norway",         []),
    (1, "sweden",         "Sweden",         "Sweden",         []),
    (1, "finland",        "Finland",        "Finland",        []),
    (1, "iceland",        "Iceland",        "Iceland",        []),
    (1, "greece",         "Greece",         "Greece",         []),
    (1, "turkey",         "Turkey",         "Turkey",         ["Türkiye"]),
    (1, "russia",         "Russia",         "Russia",         []),
    (1, "india",          "India",          "India",          []),
    (1, "china",          "China",          "China",          []),
    (1, "japan",          "Japan",          "Japan",          []),
    (1, "australia",      "Australia",      "Australia",      []),
    (1, "new-zealand",    "New Zealand",    "New Zealand",    []),
    (1, "brazil",         "Brazil",         "Brazil",         []),
    (1, "argentina",      "Argentina",      "Argentina",      []),
    (1, "chile",          "Chile",          "Chile",          []),
    (1, "mexico",         "Mexico",         "Mexico",         []),
    (1, "united-states",  "United States of America", "United States", ["USA", "United States of America", "America"]),
    (1, "canada",         "Canada",         "Canada",         []),
    (1, "egypt",          "Egypt",          "Egypt",          []),
    (1, "south-africa",   "South Africa",   "South Africa",   []),
    (1, "madagascar",     "Madagascar",     "Madagascar",     []),

    # ── Level 2 — regional ──────────────────────────────────────────────
    (2, "poland",         "Poland",         "Poland",         []),
    (2, "ukraine",        "Ukraine",        "Ukraine",        []),
    (2, "netherlands",    "Netherlands",    "Netherlands",    ["Holland"]),
    (2, "belgium",        "Belgium",        "Belgium",        []),
    (2, "switzerland",    "Switzerland",    "Switzerland",    []),
    (2, "austria",        "Austria",        "Austria",        []),
    (2, "denmark",        "Denmark",        "Denmark",        []),
    (2, "croatia",        "Croatia",        "Croatia",        []),
    (2, "cuba",           "Cuba",           "Cuba",           []),
    (2, "indonesia",      "Indonesia",      "Indonesia",      []),
    (2, "philippines",    "Philippines",    "Philippines",    []),
    (2, "thailand",       "Thailand",       "Thailand",       []),
    (2, "vietnam",        "Vietnam",        "Vietnam",        []),
    (2, "south-korea",    "South Korea",    "South Korea",    ["Korea"]),
    (2, "north-korea",    "North Korea",    "North Korea",    []),
    (2, "sri-lanka",      "Sri Lanka",      "Sri Lanka",      []),
    (2, "israel",         "Israel",         "Israel",         []),
    (2, "saudi-arabia",   "Saudi Arabia",   "Saudi Arabia",   []),
    (2, "iran",           "Iran",           "Iran",           []),
    (2, "iraq",           "Iraq",           "Iraq",           []),
    (2, "pakistan",       "Pakistan",       "Pakistan",       []),
    (2, "afghanistan",    "Afghanistan",    "Afghanistan",    []),
    (2, "kazakhstan",     "Kazakhstan",     "Kazakhstan",     []),
    (2, "mongolia",       "Mongolia",       "Mongolia",       []),
    (2, "peru",           "Peru",           "Peru",           []),
    (2, "colombia",       "Colombia",       "Colombia",       []),
    (2, "venezuela",      "Venezuela",      "Venezuela",      []),
    (2, "bolivia",        "Bolivia",        "Bolivia",        []),
    (2, "ecuador",        "Ecuador",        "Ecuador",        []),
    (2, "uruguay",        "Uruguay",        "Uruguay",        []),
    (2, "paraguay",       "Paraguay",       "Paraguay",       []),
    (2, "nigeria",        "Nigeria",        "Nigeria",        []),
    (2, "kenya",          "Kenya",          "Kenya",          []),
    (2, "morocco",        "Morocco",        "Morocco",        []),

    # ── Level 3 — expert & confusable ───────────────────────────────────
    (3, "algeria",        "Algeria",        "Algeria",        []),
    (3, "libya",          "Libya",          "Libya",          []),
    (3, "ethiopia",       "Ethiopia",       "Ethiopia",       []),
    (3, "somalia",        "Somalia",        "Somalia",        []),
    (3, "chad",           "Chad",           "Chad",           []),
    (3, "niger",          "Niger",          "Niger",          []),
    (3, "mali",           "Mali",           "Mali",           []),
    (3, "mauritania",     "Mauritania",     "Mauritania",     []),
    (3, "sudan",          "Sudan",          "Sudan",          []),
    (3, "angola",         "Angola",         "Angola",         []),
    (3, "mozambique",     "Mozambique",     "Mozambique",     []),
    (3, "tanzania",       "United Republic of Tanzania", "Tanzania", []),
    (3, "zambia",         "Zambia",         "Zambia",         []),
    (3, "zimbabwe",       "Zimbabwe",       "Zimbabwe",       []),
    (3, "botswana",       "Botswana",       "Botswana",       []),
    (3, "namibia",        "Namibia",        "Namibia",        []),
    (3, "senegal",        "Senegal",        "Senegal",        []),
    (3, "ghana",          "Ghana",          "Ghana",          []),
    (3, "ivory-coast",    "Ivory Coast",    "Ivory Coast",    ["Côte d'Ivoire", "Cote d'Ivoire"]),
    (3, "cameroon",       "Cameroon",       "Cameroon",       []),
    (3, "tunisia",        "Tunisia",        "Tunisia",        []),
    (3, "uzbekistan",     "Uzbekistan",     "Uzbekistan",     []),
    (3, "turkmenistan",   "Turkmenistan",   "Turkmenistan",   []),
    (3, "kyrgyzstan",     "Kyrgyzstan",     "Kyrgyzstan",     []),
    (3, "nepal",          "Nepal",          "Nepal",          []),
    (3, "bangladesh",     "Bangladesh",     "Bangladesh",     []),
    (3, "myanmar",        "Myanmar",        "Myanmar",        ["Burma"]),
    (3, "laos",           "Laos",           "Laos",           []),
    (3, "cambodia",       "Cambodia",       "Cambodia",       []),
    (3, "malaysia",       "Malaysia",       "Malaysia",       []),
    (3, "romania",        "Romania",        "Romania",        []),
    (3, "bulgaria",       "Bulgaria",       "Bulgaria",       []),
    (3, "hungary",        "Hungary",        "Hungary",        []),
    (3, "czechia",        "Czechia",        "Czechia",        ["Czech Republic"]),
    (3, "slovakia",       "Slovakia",       "Slovakia",       []),
    (3, "serbia",         "Republic of Serbia", "Serbia",     []),
]

LEVELS = {
    1: ("level1-iconic", "Country Silhouettes — Level 1 (Iconic)"),
    2: ("level2-regional", "Country Silhouettes — Level 2 (Regional)"),
    3: ("level3-expert", "Country Silhouettes — Level 3 (Expert)"),
}

# How far (degrees) a detached piece may sit from the largest landmass and
# still be drawn. The default keeps near-shore islands; overrides trim cases
# where the default keeps too much (Alaska, Svalbard, the Chathams, the
# Galápagos) and Indonesia keeps its whole archipelago.
KEEP_RADIUS = 8.0
KEEP_RADIUS_OVERRIDE = {
    "united-states": 5.0,
    "norway": 4.0,
    "new-zealand": 4.0,
    "ecuador": 5.0,
    "indonesia": 1e9,
}


def polygons(geom):
    """Geometry -> list of polygons, each a list of rings (outer first)."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return list(geom["coordinates"])
    raise ValueError(f"unsupported geometry {geom['type']}")


def unwrap(polys):
    """Shift longitudes so an antimeridian-straddling country is contiguous."""
    lons = [p[0] for poly in polys for p in poly[0]]
    if max(lons) - min(lons) <= 180:
        return polys
    return [[[[x + 360 if x < 0 else x, y] for x, y in ring] for ring in poly]
            for poly in polys]


def ring_area(ring, k):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        a += x1 * k * y2 - x2 * k * y1
    return abs(a) / 2


def centroid(ring):
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def keep_mainland(polys, radius):
    """Largest polygon plus pieces whose centroid is near its coastline."""
    lat0 = centroid(max((poly[0] for poly in polys), key=len))[1]
    k = math.cos(math.radians(lat0))
    main = max(polys, key=lambda poly: ring_area(poly[0], k))
    if radius >= 1e9:
        return polys
    kept = []
    for poly in polys:
        if poly is main:
            kept.append(poly)
            continue
        cx, cy = centroid(poly[0])
        d = min(math.hypot((cx - x) * k, cy - y) for x, y in main[0])
        if d <= radius:
            kept.append(poly)
    return kept


def render(polys, dest):
    pts = [p for poly in polys for ring in poly for p in ring]
    lat0 = sum(p[1] for p in pts) / len(pts)
    k = math.cos(math.radians(lat0))
    xs = [p[0] * k for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    span = max(maxx - minx, maxy - miny) or 1.0
    scale = (SIZE - 2 * MARGIN) * SS / span
    # center the shape on the supersampled canvas
    ox = (SIZE * SS - (maxx - minx) * scale) / 2
    oy = (SIZE * SS - (maxy - miny) * scale) / 2

    def screen(ring):
        return [((x * k - minx) * scale + ox, (maxy - y) * scale + oy)
                for x, y in ring]

    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), BG)
    draw = ImageDraw.Draw(img)
    for poly in polys:
        draw.polygon(screen(poly[0]), fill=FG)
        for hole in poly[1:]:  # e.g. Lesotho inside South Africa
            draw.polygon(screen(hole), fill=BG)
    img.resize((SIZE, SIZE), Image.LANCZOS).save(dest)


def load_features():
    if not os.path.exists(GEOJSON):
        print("fetching Natural Earth data …")
        req = urllib.request.Request(GEOJSON_URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as r, open(GEOJSON, "wb") as f:
            f.write(r.read())
    with open(GEOJSON) as f:
        data = json.load(f)
    return {f["properties"]["ADMIN"]: f["geometry"] for f in data["features"]}


def generate():
    admin = load_features()
    os.makedirs(IMG_DIR, exist_ok=True)
    for _, slug, name, _, _ in COUNTRIES:
        dest = os.path.join(IMG_DIR, slug + ".png")
        if os.path.exists(dest):
            continue
        if name not in admin:
            print(f"FAILED {slug}: no such ADMIN name {name!r}", file=sys.stderr)
            continue
        polys = unwrap(polygons(admin[name]))
        polys = keep_mainland(polys, KEEP_RADIUS_OVERRIDE.get(slug, KEEP_RADIUS))
        render(polys, dest)
        print(f"rendered {slug}.png")


def rebuild():
    for level, (fname, name) in LEVELS.items():
        cards = []
        for lv, slug, _, display, accepts in COUNTRIES:
            if lv != level:
                continue
            if not os.path.exists(os.path.join(IMG_DIR, slug + ".png")):
                print(f"skipping {slug}: no image", file=sys.stderr)
                continue
            card = f"@img images/{slug}.png\n---\n{display}\n"
            for a in accepts:
                card += f"= {a}\n"
            cards.append(card)
        path = os.path.join(HERE, fname + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: type\n# answer-case: insensitive\n# img-tint: fg\n")
            f.write("# Generated by gen_images.py — edit that script, not this file.\n\n")
            f.write("\n".join(cards))
        print(f"wrote {fname}.deck ({len(cards)} cards)")


if __name__ == "__main__":
    if "--rebuild" not in sys.argv:
        generate()
    rebuild()
