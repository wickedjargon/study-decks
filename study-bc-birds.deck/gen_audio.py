#!/usr/bin/env python3
"""Download BC bird recordings from Wikimedia Commons and (re)generate the
.deck files.

Commons mirrors many xeno-canto recordings (the XC-numbered files); each
species below is found by searching audio files for its scientific name.
Clips are trimmed to the first 12 seconds and converted to mp3 with ffmpeg so
every browser (Safari included) and the desktop player can decode them.

Re-runnable: existing clips are skipped, so a second run is cheap. The deck
files are always rebuilt from the list below, skipping any entry whose clip
is missing on disk, so the decks and the audio never drift apart.

    python3 gen_audio.py             # download missing clips, rebuild decks
    python3 gen_audio.py --rebuild   # skip download, just rebuild decks

Requires: ffmpeg
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
AUD_DIR = os.path.join(HERE, "audio")
UA = "study-bc-birds/1.0 (personal flashcard deck; +https://commons.wikimedia.org/)"
CLIP_SECONDS = 12

# (deck, slug, common name, scientific name, [accepted variants])
BIRDS = [
    # ── Backyard ────────────────────────────────────────────────────────
    ("backyard", "american-robin",      "American Robin",       "Turdus migratorius", ["robin"]),
    ("backyard", "black-capped-chickadee", "Black-capped Chickadee", "Poecile atricapillus", ["chickadee"]),
    ("backyard", "song-sparrow",        "Song Sparrow",         "Melospiza melodia", []),
    ("backyard", "dark-eyed-junco",     "Dark-eyed Junco",      "Junco hyemalis", ["junco"]),
    ("backyard", "house-finch",         "House Finch",          "Haemorhous mexicanus", []),
    ("backyard", "american-goldfinch",  "American Goldfinch",   "Spinus tristis", ["goldfinch"]),
    ("backyard", "spotted-towhee",      "Spotted Towhee",       "Pipilo maculatus", ["towhee"]),
    ("backyard", "northern-flicker",    "Northern Flicker",     "Colaptes auratus", ["flicker"]),
    ("backyard", "american-crow",       "American Crow",        "Corvus brachyrhynchos", ["crow"]),
    ("backyard", "european-starling",   "European Starling",    "Sturnus vulgaris", ["starling"]),
    ("backyard", "house-sparrow",       "House Sparrow",        "Passer domesticus", []),
    ("backyard", "annas-hummingbird",   "Anna's Hummingbird",   "Calypte anna", []),

    # ── Forest ──────────────────────────────────────────────────────────
    ("forest", "stellers-jay",          "Steller's Jay",        "Cyanocitta stelleri", []),
    # (Varied Thrush would belong here, but Commons has no recording of it.)
    ("forest", "hermit-thrush",         "Hermit Thrush",        "Catharus guttatus", []),
    ("forest", "swainsons-thrush",      "Swainson's Thrush",    "Catharus ustulatus", []),
    ("forest", "pacific-wren",          "Pacific Wren",         "Troglodytes pacificus", []),
    ("forest", "red-breasted-nuthatch", "Red-breasted Nuthatch","Sitta canadensis", ["nuthatch"]),
    ("forest", "ruby-crowned-kinglet",  "Ruby-crowned Kinglet", "Regulus calendula", ["kinglet"]),
    ("forest", "western-tanager",       "Western Tanager",      "Piranga ludoviciana", ["tanager"]),
    ("forest", "chestnut-backed-chickadee", "Chestnut-backed Chickadee", "Poecile rufescens", []),
    ("forest", "pileated-woodpecker",   "Pileated Woodpecker",  "Dryocopus pileatus", []),
    ("forest", "barred-owl",            "Barred Owl",           "Strix varia", []),
    ("forest", "great-horned-owl",      "Great Horned Owl",     "Bubo virginianus", []),
    ("forest", "common-raven",          "Common Raven",         "Corvus corax", ["raven"]),

    # ── Water & raptors ─────────────────────────────────────────────────
    ("water-raptors", "common-loon",    "Common Loon",          "Gavia immer", ["loon"]),
    ("water-raptors", "canada-goose",   "Canada Goose",         "Branta canadensis", ["goose"]),
    ("water-raptors", "mallard",        "Mallard",              "Anas platyrhynchos", ["duck"]),
    ("water-raptors", "killdeer",       "Killdeer",             "Charadrius vociferus", []),
    ("water-raptors", "belted-kingfisher", "Belted Kingfisher", "Megaceryle alcyon", ["kingfisher"]),
    ("water-raptors", "bald-eagle",     "Bald Eagle",           "Haliaeetus leucocephalus", ["eagle"]),
    ("water-raptors", "red-tailed-hawk","Red-tailed Hawk",      "Buteo jamaicensis", []),
    ("water-raptors", "osprey",         "Osprey",               "Pandion haliaetus", []),
    ("water-raptors", "red-winged-blackbird", "Red-winged Blackbird", "Agelaius phoeniceus", []),
    # (Glaucous-winged Gull would be the BC pick, but Commons has no recording.)
    ("water-raptors", "ring-billed-gull", "Ring-billed Gull",   "Larus delawarensis", ["gull", "seagull"]),
]

DECKS = {
    "backyard": "BC Birds — Backyard",
    "forest": "BC Birds — Forest",
    "water-raptors": "BC Birds — Water & Raptors",
}


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req))


def find_recording(scientific):
    """Return the Commons file title of the best audio hit for a species:
    the first search result, preferring titles that mention song/call."""
    d = api({"action": "query", "format": "json", "list": "search", "srnamespace": "6",
             "srlimit": "10", "srsearch": f'"{scientific}" filetype:audio'})
    hits = [r["title"] for r in d["query"]["search"]]
    hits = [t for t in hits if t.lower().endswith((".ogg", ".oga", ".mp3", ".wav", ".flac"))]
    if not hits:
        return None
    for t in hits:
        if "song" in t.lower() or "call" in t.lower():
            return t
    return hits[0]


def fetch_clip(title, dest):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title.removeprefix("File:"))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r, tempfile.NamedTemporaryFile(suffix=os.path.splitext(title)[1], delete=False) as tmp:
        tmp.write(r.read())
        tmpname = tmp.name
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpname,
                        "-t", str(CLIP_SECONDS), "-acodec", "libmp3lame", "-b:a", "96k", dest],
                       check=True)
    finally:
        os.unlink(tmpname)


def download():
    os.makedirs(AUD_DIR, exist_ok=True)
    for _, slug, common, scientific, _ in BIRDS:
        dest = os.path.join(AUD_DIR, slug + ".mp3")
        if os.path.exists(dest):
            continue
        try:
            title = find_recording(scientific)
            if title is None:
                print(f"NO RECORDING for {common} ({scientific})", file=sys.stderr)
                continue
            fetch_clip(title, dest)
            print(f"fetched {slug}.mp3  ({title})")
        except Exception as e:
            print(f"FAILED {slug}: {e}", file=sys.stderr)
        time.sleep(0.6)


def rebuild():
    for deck, name in DECKS.items():
        cards = []
        for d, slug, common, _, accepts in BIRDS:
            if d != deck:
                continue
            clip = os.path.join(AUD_DIR, slug + ".mp3")
            if not os.path.exists(clip):
                print(f"skipping {slug}: no clip", file=sys.stderr)
                continue
            card = f"@audio audio/{slug}.mp3\n---\n{common}\n"
            for a in accepts:
                card += f"= {a}\n"
            cards.append(card)
        path = os.path.join(HERE, deck + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: choice\n# choice-count: 4\n# answer-case: insensitive\n")
            f.write("# Generated by gen_audio.py — edit that script, not this file.\n\n")
            f.write("\n".join(cards))
        print(f"wrote {deck}.deck ({len(cards)} cards)")


if __name__ == "__main__":
    if "--rebuild" not in sys.argv:
        download()
    rebuild()
