#!/usr/bin/env python3
"""Download country locator maps from Wikimedia Commons and (re)generate the
.deck files: a world map with one country highlighted, you type the country.

Commons keeps a uniformly styled set under the systematic name
"<Country> (orthographic projection).svg"; OVERRIDES carries the exceptions.
The country table (levels, slugs, names, accepted variants) is borrowed from
../study-world-flags.deck so the packs stay in lockstep — a country added
there just works here once its map downloads.

Files are fetched as PNG renders via Special:FilePath so both frontends can
decode them, and each download is verified to actually be a PNG. Re-runnable:
existing images are skipped, and the deck files are always rebuilt from the
table, skipping entries whose image is missing, so decks and images never
drift apart.

    python3 gen_images.py            # download missing maps, rebuild decks
    python3 gen_images.py --rebuild  # skip download, just rebuild decks
"""

import importlib.util
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
UA = "study-locator-maps/1.0 (personal flashcard deck; +https://commons.wikimedia.org/)"
WIDTH = 600

# The sibling pack's curated FLAGS table: (level, slug, country, title, accepts).
WF = os.path.join(HERE, "..", "study-world-flags.deck")
spec = importlib.util.spec_from_file_location("wf_gen", os.path.join(WF, "gen_images.py"))
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

# Countries whose Commons map title isn't "<Country> (orthographic projection).svg".
# Two sister series fill the gaps: "EU-<X> (orthographic projection).svg" for
# a couple of EU members, and "<X> on the globe (<region> centered).svg",
# whose micro-state maps carry a zoom inset that a plain orthographic
# projection lacks.
OVERRIDES = {
    "China": "People's Republic of China (orthographic projection).svg",
    "Czechia": "Czech Republic (orthographic projection).svg",
    "Ivory Coast": "Côte d'Ivoire (orthographic projection).svg",
    "Timor-Leste": "East Timor (orthographic projection).svg",
    "Ireland": "EU-Ireland (orthographic projection).svg",
    "Greece": "EU-Greece (orthographic projection).svg",
    "Slovakia": "Slovakia on the globe (Europe centered).svg",
    "Hungary": "Hungary on the globe (Europe centered).svg",
    "Croatia": "Croatia on the globe (Europe centered).svg",
    "Estonia": "Estonia on the globe (Europe centered).svg",
    "Latvia": "Latvia on the globe (Europe centered).svg",
    "Lithuania": "Lithuania on the globe (Europe centered).svg",
    "Slovenia": "Slovenia on the globe (Europe centered).svg",
    "Luxembourg": "Luxembourg on the globe (Europe centered).svg",
    "Malta": "Malta on the globe (Europe centered).svg",
    "Moldova": "Moldova on the globe (Europe centered).svg",
    "Monaco": "Monaco on the globe (Europe centered).svg",
    "Liechtenstein": "Liechtenstein on the globe (Europe centered).svg",
    "Andorra": "Andorra on the globe (Europe centered).svg",
    "San Marino": "San Marino on the globe (Europe centered).svg",
    "Singapore": "Singapore on the globe (Southeast Asia centered).svg",
    "Qatar": "Qatar on the globe (Afro-Eurasia centered).svg",
    "Kuwait": "Kuwait on the globe (Afro-Eurasia centered).svg",
    "Bahrain": "Bahrain on the globe (Afro-Eurasia centered).svg",
}

# Countries with no usable locator map on Commons in any of the series.
SKIP = set()


def map_title(country):
    return OVERRIDES.get(country, f"{country} (orthographic projection).svg")


def fetch(title, dest):
    url = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
           + urllib.parse.quote(title) + f"?width={WIDTH}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        data = r.read()
    if not data.startswith(b"\x89PNG"):
        raise ValueError(f"not a PNG ({len(data)} bytes)")
    with open(dest, "wb") as f:
        f.write(data)


def download():
    os.makedirs(IMG_DIR, exist_ok=True)
    failed = []
    for _, slug, country, _, _ in wf.FLAGS:
        if country in SKIP:
            continue
        dest = os.path.join(IMG_DIR, slug + ".png")
        if os.path.exists(dest):
            continue
        try:
            fetch(map_title(country), dest)
            print(f"fetched {slug}.png")
        except Exception as e:
            failed.append(country)
            print(f"FAILED {slug} ({map_title(country)}): {e}", file=sys.stderr)
        time.sleep(0.4)
    if failed:
        print(f"\n{len(failed)} failures: {failed}", file=sys.stderr)


LEVELS = {
    1: ("level1-famous", "Locator Maps — Level 1 (Famous)"),
    2: ("level2-regional", "Locator Maps — Level 2 (Regional)"),
    3: ("level3-expert", "Locator Maps — Level 3 (Expert)"),
}


def rebuild():
    for level, (fname, name) in LEVELS.items():
        cards = []
        for lv, slug, country, _, accepts in wf.FLAGS:
            if lv != level or country in SKIP:
                continue
            img = os.path.join(IMG_DIR, slug + ".png")
            if not os.path.exists(img):
                print(f"skipping {slug}: no image", file=sys.stderr)
                continue
            card = f"@img images/{slug}.png\n---\n{country}\n"
            for a in accepts:
                card += f"= {a}\n"
            cards.append(card)
        path = os.path.join(HERE, fname + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: type\n# answer-case: insensitive\n")
            f.write("# Generated by gen_images.py — edit that script, not this file.\n\n")
            f.write("\n".join(cards))
        print(f"wrote {fname}.deck ({len(cards)} cards)")


if __name__ == "__main__":
    if "--rebuild" not in sys.argv:
        download()
    rebuild()
