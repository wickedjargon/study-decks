#!/usr/bin/env python3
"""Download animal track photos from Wikimedia Commons and (re)generate the
.deck file.

Unlike flags, tracks have no systematic file naming on Commons, so each entry
carries the exact file title of a hand-picked, clearly-lit single print. The
set leans North American / British Columbian to sit next to the bc-birds pack.

Files are fetched as PNG renders via Special:FilePath so both frontends can
decode them. Licenses are mixed (public domain, CC0, CC BY, CC BY-SA) — all
free, but the CC ones need credit, so a CREDITS.md is written alongside.

Re-runnable: existing images are skipped, so a second run is cheap. The deck
is always rebuilt from the list below, skipping any entry whose image is
missing on disk, so the deck and the images never drift apart.

    python3 gen_images.py            # download missing images, rebuild deck
    python3 gen_images.py --rebuild  # skip download, just rebuild deck
"""

import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
UA = "study-animal-tracks/1.0 (personal flashcard deck; +https://commons.wikimedia.org/)"
WIDTH = 640

# (slug, animal, commons file title, [accepted variants], author, license)
# NOTE: cards are image-only questions — a shared prompt line would give every
# card the same ID (IDs hash the question's text lines), collapsing the deck.
# Answer-side ID cues: what actually separates this print from the ones
# it's mistaken for. The field skill is the discrimination, so every card
# gets the tell.
NOTES = {
    "black-bear": "Five toes and a wide pad, like a small flat human foot "
                  "with claws. Front and hind prints differ in length.",
    "coyote": "Four toes, claws showing, oval and neat: X-shaped negative "
              "space between pad and toes. Domestic dogs splay wider and "
              "walk sloppier lines.",
    "red-fox": "Like a coyote's but daintier, and the small pad often "
               "shows a chevron-shaped bar. Fur can blur the whole print.",
    "cougar": "Four toes, no claws (retracted), big round print with a "
              "three-lobed heel pad. Claw marks would mean canine.",
    "canada-lynx": "Cat print but huge for the body: furred paws act as "
                   "snowshoes, so edges look soft and undefined.",
    "raccoon": "Five long finger-like toes, like a tiny human hand. Front "
               "and hind often land side by side.",
    "moose": "Two-toed heart shape like a deer's but much larger: over "
             "12 cm long, and dewclaws print in deep snow or mud.",
    "white-tailed-deer": "Two-toed heart shape, points aim in the "
                         "direction of travel. Moose is the same shape "
                         "twice the size.",
    "red-squirrel": "Paired bounding pattern: larger hind feet land ahead "
                    "of the small front feet.",
    "wild-turkey": "Three long forward toes, the middle longest, up to "
                   "10 cm — far bigger than any songbird.",
    "striped-skunk": "Five toes on all feet with long front claw marks "
                     "from digging; flat-footed, unhurried gait.",
    "canada-goose": "Webbing between three thick toes, prints toed "
                    "inward.",
}

TRACKS = [
    ("black-bear", "Black bear",
     "A fresh black bear track in the mud leaves an impression. (6803486491).jpg",
     ["bear"], "U.S. Fish and Wildlife Service", "Public domain"),
    ("coyote", "Coyote",
     "Coyote Tracks - Flickr - treegrow.jpg",
     [], "Katja Schulz", "CC BY 2.0"),
    ("red-fox", "Red fox",
     "Footprint of Vulpes vulpes.jpg",
     ["fox"], "Rasbak", "CC BY-SA 4.0"),
    ("cougar", "Cougar",
     "Mountain Lion Track (8470341949).jpg",
     ["mountain lion", "puma"], "USFWS Mountain-Prairie", "CC BY 2.0"),
    ("canada-lynx", "Canada lynx",
     "Lynx tracks (13436541305).jpg",
     ["lynx"], "USFWS Alaska", "Public domain"),
    ("raccoon", "Raccoon",
     "Raccoon track foot print in mud.jpg",
     [], "Jeepday", "CC BY-SA 3.0"),
    ("moose", "Moose",
     "Moose track (34316145155).jpg",
     [], "Katmai National Park and Preserve", "Public domain"),
    ("white-tailed-deer", "White-tailed deer",
     "2021-01-02 12 39 01 White-tailed deer hoof print in dirt along Tranquility Court in the Franklin Farm section of Oak Hill, Fairfax County, Virginia.jpg",
     ["deer"], "Famartin", "CC BY-SA 4.0"),
    ("red-squirrel", "Red squirrel",
     "Red squirrel tracks (15314171953).jpg",
     ["squirrel"], "Neal Herbert / Yellowstone NP", "Public domain"),
    ("wild-turkey", "Wild turkey",
     "Wild Turkey tracks (8322318922) (2).jpg",
     ["turkey"], "Virginia State Parks staff", "CC BY 2.0"),
    ("striped-skunk", "Striped skunk",
     "Striped skunk tracks.png",
     ["skunk"], "tonyblake", "CC0"),
    ("canada-goose", "Canada goose",
     "Branta canadensis track.jpg",
     ["goose"], "Jomegat", "CC BY-SA 3.0"),
]

DECK_FILE = "tracks"
DECK_NAME = "Animal Tracks"


# Commons serves JPEG originals as JPEG even through the thumbnailer, so the
# stored file's extension is chosen from the bytes, not assumed — the web
# frontend's http.ServeFile sets Content-Type from the extension.
def ext_for(data):
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    return ".img"


def stored_path(slug):
    for ext in (".jpg", ".png", ".img"):
        p = os.path.join(IMG_DIR, slug + ext)
        if os.path.exists(p):
            return p
    return None


def fetch(title):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title) + f"?width={WIDTH}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return r.read()


def download():
    os.makedirs(IMG_DIR, exist_ok=True)
    for slug, _, title, _, _, _ in TRACKS:
        if stored_path(slug):
            continue
        try:
            data = fetch(title)
            dest = os.path.join(IMG_DIR, slug + ext_for(data))
            with open(dest, "wb") as f:
                f.write(data)
            print(f"fetched {os.path.basename(dest)}")
        except Exception as e:
            print(f"FAILED {slug} ({title}): {e}", file=sys.stderr)
        time.sleep(0.5)


def rebuild():
    cards = []
    credits = []
    for slug, animal, title, accepts, author, lic in TRACKS:
        img = stored_path(slug)
        if not img:
            print(f"skipping {slug}: no image", file=sys.stderr)
            continue
        card = f"@img images/{os.path.basename(img)}\n---\n{animal}\n"
        for a in accepts:
            card += f"= {a}\n"
        if note := NOTES.get(slug):
            card += f"---\n{note}\n"
        cards.append(card)
        page = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(title.replace(" ", "_"))
        credits.append(f"- {animal}: {author}, {lic} — {page}")

    path = os.path.join(HERE, DECK_FILE + ".deck")
    with open(path, "w") as f:
        f.write(f"# {DECK_NAME}\n")
        f.write("# answer-mode: type\n# answer-case: insensitive\n")
        f.write("# Generated by gen_images.py — edit that script, not this file.\n\n")
        f.write("\n".join(cards))
    print(f"wrote {DECK_FILE}.deck ({len(cards)} cards)")

    with open(os.path.join(HERE, "CREDITS.md"), "w") as f:
        f.write("# Image credits\n\n")
        f.write("Track photos from Wikimedia Commons, reused under the licenses noted.\n\n")
        f.write("\n".join(credits) + "\n")
    print(f"wrote CREDITS.md ({len(credits)} entries)")


if __name__ == "__main__":
    if "--rebuild" not in sys.argv:
        download()
    rebuild()
