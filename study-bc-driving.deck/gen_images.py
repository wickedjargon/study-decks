#!/usr/bin/env python3
"""Download BC road-sign diagrams from Wikimedia Commons and (re)generate the
sign .deck files.

The sign list below is hand-curated for the ICBC learner's knowledge test.
Diagrams come from the official-style sign sets on Commons: the BC MoTI
catalog (CA-BC road sign …) where available, otherwise the national MUTCDC
or Ontario sets (visually identical for these signs). Files are fetched as
PNG renders via Special:FilePath so both frontends can decode them.

Re-runnable: existing images are skipped, so a second run is cheap. The sign
deck files are always rebuilt from the list below, skipping any entry whose
image is missing on disk, so the decks and the images never drift apart.

    python3 gen_images.py            # download missing images, rebuild decks
    python3 gen_images.py --rebuild  # skip download, just rebuild decks

The rules-*.deck files are hand-written and never touched by this script.
"""

import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
UA = "study-bc-driving/1.0 (personal flashcard deck; +https://commons.wikimedia.org/)"
WIDTH = 480

# (deck, slug, commons file title, meaning)
# deck: regulatory | warning | school-construction
SIGNS = [
    # ── Regulatory ──────────────────────────────────────────────────────
    ("regulatory", "stop",                "CA-BC road sign R-001.svg",          "Stop"),
    ("regulatory", "yield",               "CA-BC road sign R-002.svg",          "Yield"),
    ("regulatory", "speed-50",            "CA-BC road sign R-004-050.svg",      "Speed limit 50 km/h"),
    ("regulatory", "no-right-turn",       "CA-ON road sign Rb-011.svg",         "No right turn"),
    ("regulatory", "no-left-turn",        "CA-ON road sign Rb-012.svg",         "No left turn"),
    ("regulatory", "no-u-turn",           "CA-MUTCDC RB-016.svg",               "No U-turn"),
    ("regulatory", "do-not-enter",        "CA-MUTCDC RB-023.svg",               "Do not enter"),
    ("regulatory", "wrong-way",           "CA-MUTCDC RB-022-EN.svg",            "Wrong way"),
    ("regulatory", "one-way",             "CA-MUTCDC RB-021-R.svg",             "One-way traffic"),
    ("regulatory", "two-way",             "CA-BC road sign R-010.svg",          "Two-way traffic"),
    ("regulatory", "keep-right",          "CA-MUTCDC RB-025-R.svg",             "Keep right of the divider"),
    ("regulatory", "do-not-pass",         "CA-MUTCDC RB-031.svg",               "Do not pass"),
    ("regulatory", "no-parking",          "CA-BC road sign P-001-D.svg",        "No parking"),
    ("regulatory", "no-stopping",         "CA-BC road sign P-058-D.svg",        "No stopping"),
    ("regulatory", "two-way-left-turn",   "CA-BC road sign R-090.svg",          "Two-way left turn lane"),
    ("regulatory", "no-block-intersection", "CA-BC road sign R-106.svg",        "Do not block the intersection"),
    ("regulatory", "left-on-red",         "CA-BC road sign R-110-4.svg",        "Left turn permitted on red after stopping"),
    ("regulatory", "no-pedestrians",      "CA-BC road sign PS-012-R.svg",       "No pedestrians"),
    ("regulatory", "school-bus-no-pass",  "CA-BC road sign PS-009.svg",         "Do not pass a stopped school bus with flashing red lights"),

    # ── Warning ─────────────────────────────────────────────────────────
    ("warning", "curve",                  "CA-BC road sign W-001-R.svg",        "Curve ahead"),
    ("warning", "sharp-curve",            "CA-BC road sign W-002-R.svg",        "Sharp curve ahead"),
    ("warning", "reverse-curve",          "CA-BC road sign W-003-R.svg",        "Reverse curve ahead"),
    ("warning", "hairpin-curve",          "CA-BC road sign W-004-R.svg",        "Hairpin curve ahead"),
    ("warning", "winding-road",           "CA-BC road sign W-005-R.svg",        "Winding road ahead"),
    ("warning", "crossroads",             "CA-BC road sign W-006.svg",          "Crossroads ahead"),
    ("warning", "t-junction",             "CA-BC road sign W-008.svg",          "T-intersection ahead"),
    ("warning", "railway-crossing",       "CA-BC road sign W-010-1.svg",        "Railway crossing ahead"),
    ("warning", "stop-ahead",             "CA-BC road sign W-011.svg",          "Stop sign ahead"),
    ("warning", "signals-ahead",          "CA-BC road sign W-012.svg",          "Traffic signals ahead"),
    ("warning", "yield-ahead",            "CA-BC road sign W-013.svg",          "Yield sign ahead"),
    ("warning", "dead-end",               "CA-BC road sign W-014.svg",          "Dead end"),
    ("warning", "two-way-ahead",          "CA-BC road sign W-020.svg",          "Two-way traffic ahead"),
    ("warning", "road-narrows",           "CA-BC road sign W-026.svg",          "Road narrows ahead"),
    ("warning", "steep-descent",          "CA-BC road sign W-029-1.svg",        "Steep hill downhill ahead"),
    ("warning", "added-lane",             "CA-BC road sign W-035-R.svg",        "Added lane ahead"),
    ("warning", "merging-traffic",        "CA-BC road sign W-037-L.svg",        "Merging traffic"),
    ("warning", "congestion",             "CA-BC road sign W-036.svg",          "Traffic congestion ahead"),
    ("warning", "slide-area",             "CA-BC road sign W-032.svg",          "Slide area"),
    ("warning", "slippery",               "CA-MUTCDC WC-023.svg",               "Slippery when wet"),
    ("warning", "speed-zone-ahead",       "CA-BC road sign W-028-60.svg",       "Speed limit ahead"),

    # ── School, pedestrian & construction ───────────────────────────────
    ("school-construction", "school-zone",      "CA-BC road sign PS-001.svg",    "School zone"),
    ("school-construction", "school-zone-30",   "CA-BC road sign PS-001-TA.svg", "30 km/h school zone speed limit"),
    ("school-construction", "school-crossing",  "CA-BC road sign PS-004.svg",    "School crossing ahead"),
    ("school-construction", "ped-crossing",     "CA-BC road sign PS-002.svg",    "Pedestrian crossing ahead"),
    ("school-construction", "playground",       "CA-BC road sign PS-006.svg",    "Playground area"),
    ("school-construction", "school-bus-stop",  "CA-BC road sign PS-008.svg",    "School bus stop ahead"),
    ("school-construction", "flagger",          "CA-BC road sign C-001-1.svg",   "Traffic control person ahead"),
    ("school-construction", "construction",     "CA-BC road sign C-018-1A.svg",  "Construction ahead"),
    ("school-construction", "soft-shoulder",    "CA-BC road sign C-012.svg",     "Soft shoulder"),
    ("school-construction", "blasting",         "CA-BC road sign C-033.svg",     "Blasting zone — turn off radio transmitters"),
    ("school-construction", "lane-ends",        "CA-BC road sign C-130-R.svg",   "Right lane ends"),
    ("school-construction", "zipper-merge",     "CA-BC road sign C-138-TF.svg",  "Merge like a zipper — take turns"),
    ("school-construction", "end-construction", "CA-MUTCDC TC-004-EN.svg",       "End of construction zone"),
]

# NOTE: sign cards are image-only questions — shared prompt text would give
# every card in a deck the same ID (IDs hash the question's text lines) and
# collapse the deck to one card.
DECK_HEADERS = {
    "regulatory": "Signs: Regulatory",
    "warning": "Signs: Warning",
    "school-construction": "Signs: School & Construction",
}


def fetch(title, dest):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title) + f"?width={WIDTH}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())


def download():
    os.makedirs(IMG_DIR, exist_ok=True)
    for _, slug, title, _ in SIGNS:
        dest = os.path.join(IMG_DIR, slug + ".png")
        if os.path.exists(dest):
            continue
        try:
            fetch(title, dest)
            print(f"fetched {slug}.png  ({title})")
        except Exception as e:
            print(f"FAILED {slug}: {e}", file=sys.stderr)
        time.sleep(0.5)


def rebuild():
    for deck, name in DECK_HEADERS.items():
        cards = []
        for d, slug, _, meaning in SIGNS:
            if d != deck:
                continue
            img = os.path.join(IMG_DIR, slug + ".png")
            if not os.path.exists(img):
                print(f"skipping {slug}: no image", file=sys.stderr)
                continue
            cards.append(f"@img images/{slug}.png\n---\n{meaning}\n")
        path = os.path.join(HERE, f"signs-{deck}.deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: choice\n# choice-count: 4\n")
            f.write("# Generated by gen_images.py — edit that script, not this file.\n\n")
            f.write("\n".join(cards))
        print(f"wrote signs-{deck}.deck ({len(cards)} cards)")


if __name__ == "__main__":
    if "--rebuild" not in sys.argv:
        download()
    rebuild()
