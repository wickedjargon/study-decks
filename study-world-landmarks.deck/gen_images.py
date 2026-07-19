#!/usr/bin/env python3
"""Download landmark photos and (re)generate the world-landmarks decks.

Two decks from one table: cities.deck shows a landmark and asks for its
city, countries.deck holds the natural and remote sites where a country is
the honest answer. Photos come from each landmark's English Wikipedia
infobox image via the REST summary API (Commons file titles follow no
pattern), re-thumbed to ~560px and verified to be real JPEG/PNG bytes.

Cards are image-only questions: naming the landmark in the prompt would
give the answer away for the famous ones — the photo is the question.
The landmark's name appears in the note, visible only with the answer.

Re-runnable: existing images are skipped; decks are always rebuilt,
skipping entries whose image is missing.

    python3 gen_images.py            # download missing photos, rebuild decks
    python3 gen_images.py --rebuild  # skip download, just rebuild decks
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
UA = "study-world-landmarks/1.0 (personal flashcard deck; +https://en.wikipedia.org/)"
# upload.wikimedia.org only serves thumbnails at fixed bucket widths
# (400 "Use thumbnail sizes listed" otherwise); 500 is a bucket.
WIDTH = 500

# (slug, wiki page title, landmark display name, answer, [accepts], note)
CITIES = [
    ("eiffel-tower", "Eiffel Tower", "The Eiffel Tower",
     "Paris", [], None),
    ("statue-of-liberty", "Statue of Liberty", "The Statue of Liberty",
     "New York City", ["New York", "NYC"], None),
    ("big-ben", "Big Ben", "Big Ben",
     "London", [],
     "Strictly the name of the bell — the tower is the Elizabeth Tower."),
    ("tower-bridge", "Tower Bridge", "Tower Bridge",
     "London", [],
     "Often misnamed London Bridge — that one is the plain bridge just "
     "upstream."),
    ("colosseum", "Colosseum", "The Colosseum",
     "Rome", [], None),
    ("leaning-tower", "Leaning Tower of Pisa", "The Leaning Tower",
     "Pisa", [], None),
    ("sagrada-familia", "Sagrada Família", "The Sagrada Família",
     "Barcelona", [],
     "Under construction since 1882."),
    ("brandenburg-gate", "Brandenburg Gate", "The Brandenburg Gate",
     "Berlin", [], None),
    ("charles-bridge", "Charles Bridge", "Charles Bridge",
     "Prague", [], None),
    ("saint-basils", "Saint Basil's Cathedral", "Saint Basil's Cathedral",
     "Moscow", [],
     "On Red Square, beside the Kremlin."),
    ("hagia-sophia", "Hagia Sophia", "Hagia Sophia",
     "Istanbul", [],
     "Cathedral, then mosque, then museum, then mosque again — 1,500 "
     "years of it."),
    ("acropolis", "Acropolis of Athens", "The Acropolis (Parthenon)",
     "Athens", [], None),
    ("opera-house", "Sydney Opera House", "The Sydney Opera House",
     "Sydney", [], None),
    ("golden-gate", "Golden Gate Bridge", "The Golden Gate Bridge",
     "San Francisco", [], None),
    ("hollywood-sign", "Hollywood Sign", "The Hollywood Sign",
     "Los Angeles", ["LA", "Hollywood"], None),
    ("cn-tower", "CN Tower", "The CN Tower",
     "Toronto", [], None),
    ("space-needle", "Space Needle", "The Space Needle",
     "Seattle", [], None),
    ("gateway-arch", "Gateway Arch", "The Gateway Arch",
     "St. Louis", ["Saint Louis"], None),
    ("christ-redeemer", "Christ the Redeemer (statue)", "Christ the Redeemer",
     "Rio de Janeiro", ["Rio"], None),
    ("burj-khalifa", "Burj Khalifa", "The Burj Khalifa",
     "Dubai", [],
     "Tallest building in the world since 2009."),
    ("taj-mahal", "Taj Mahal", "The Taj Mahal",
     "Agra", [],
     "Not in Delhi — Agra is 200 km south, on the Yamuna."),
    ("forbidden-city", "Forbidden City", "The Forbidden City",
     "Beijing", [], None),
    ("tokyo-tower", "Tokyo Tower", "Tokyo Tower",
     "Tokyo", [],
     "The Eiffel-styled one. The taller white-and-blue one is the "
     "Skytree."),
    ("fushimi-inari", "Fushimi Inari-taisha", "Fushimi Inari's torii gates",
     "Kyoto", [], None),
    ("marina-bay-sands", "Marina Bay Sands", "Marina Bay Sands",
     "Singapore", [], None),
    ("petronas-towers", "Petronas Towers", "The Petronas Towers",
     "Kuala Lumpur", ["KL"], None),
    ("wat-arun", "Wat Arun", "Wat Arun",
     "Bangkok", [], None),
    ("azadi-tower", "Azadi Tower", "The Azadi Tower",
     "Tehran", [],
     "Built 1971 for 2,500 years of the Persian monarchy; renamed "
     "Freedom Tower after the revolution."),
    ("naqsh-e-jahan", "Naqsh-e Jahan Square", "Naqsh-e Jahan Square",
     "Isfahan", ["Esfahan"],
     "\"Image of the World\" — the centrepiece of Safavid Isfahan."),
    ("giza-pyramids", "Great Pyramid of Giza", "The Pyramids of Giza",
     "Giza", ["Cairo"], None),
    ("alhambra", "Alhambra", "The Alhambra",
     "Granada", [], None),
    ("st-peters", "St. Peter's Basilica", "St. Peter's Basilica",
     "Vatican City", ["Vatican", "Rome"],
     "Technically its own country, surrounded by Rome."),
    ("table-mountain", "Table Mountain", "Table Mountain",
     "Cape Town", [], None),
    ("little-mermaid", "The Little Mermaid (statue)", "The Little Mermaid",
     "Copenhagen", [], None),
    ("atomium", "Atomium", "The Atomium",
     "Brussels", [],
     "An iron crystal magnified 165 billion times, from the 1958 World's "
     "Fair."),
    ("hallgrimskirkja", "Hallgrímskirkja", "Hallgrímskirkja",
     "Reykjavík", [], None),
]

COUNTRIES = [
    ("machu-picchu", "Machu Picchu", "Machu Picchu",
     "Peru", [], None),
    ("petra", "Petra", "Petra",
     "Jordan", [],
     "The Treasury facade, carved into the rock face."),
    ("angkor-wat", "Angkor Wat", "Angkor Wat",
     "Cambodia", [],
     "The largest religious monument on Earth — it's on the flag."),
    ("great-wall", "Great Wall of China", "The Great Wall",
     "China", [], None),
    ("stonehenge", "Stonehenge", "Stonehenge",
     "United Kingdom", ["England", "UK", "Britain"], None),
    ("uluru", "Uluru", "Uluru",
     "Australia", [],
     "Formerly Ayers Rock."),
    ("moai", "Moai", "The moai statues",
     "Chile", ["Easter Island"],
     "Easter Island, 3,500 km off the Chilean coast."),
    ("salar-de-uyuni", "Salar de Uyuni", "Salar de Uyuni",
     "Bolivia", [],
     "The world's largest salt flat — a mirror in the wet season."),
    ("ha-long-bay", "Hạ Long Bay", "Hạ Long Bay",
     "Vietnam", [], None),
    ("mount-fuji", "Mount Fuji", "Mount Fuji",
     "Japan", [], None),
    ("matterhorn", "Matterhorn", "The Matterhorn",
     "Switzerland", ["Italy"],
     "The border runs across the summit; the classic pyramid view is "
     "from Zermatt, Switzerland."),
    ("santorini", "Santorini", "Santorini",
     "Greece", [], None),
    ("cappadocia", "Cappadocia", "Cappadocia",
     "Turkey", ["Türkiye"], None),
    ("victoria-falls", "Victoria Falls", "Victoria Falls",
     "Zimbabwe", ["Zambia"],
     "On the Zambezi, shared by both countries."),
    ("persepolis", "Persepolis", "Persepolis",
     "Iran", [],
     "Ceremonial capital of the Achaemenid Empire, burned by Alexander."),
    ("giants-causeway", "Giant's Causeway", "The Giant's Causeway",
     "United Kingdom", ["Northern Ireland", "UK"], None),
    ("cliffs-of-moher", "Cliffs of Moher", "The Cliffs of Moher",
     "Ireland", [], None),
    ("neuschwanstein", "Neuschwanstein Castle", "Neuschwanstein Castle",
     "Germany", [],
     "Ludwig II's Bavarian castle — the Disney castle's model."),
    ("mount-rushmore", "Mount Rushmore", "Mount Rushmore",
     "United States", ["USA", "America", "United States of America"],
     "Washington, Jefferson, Theodore Roosevelt, Lincoln."),
    ("grand-canyon", "Grand Canyon", "The Grand Canyon",
     "United States", ["USA", "America", "United States of America"], None),
    ("chichen-itza", "Chichen Itza", "Chichen Itza",
     "Mexico", [],
     "El Castillo, the Temple of Kukulcán."),
    ("blue-lagoon", "Blue Lagoon (geothermal spa)", "The Blue Lagoon",
     "Iceland", [], None),
    ("borobudur", "Borobudur", "Borobudur",
     "Indonesia", [],
     "The world's largest Buddhist temple, on Java."),
    ("mont-saint-michel", "Mont-Saint-Michel", "Mont-Saint-Michel",
     "France", [], None),
    ("timbuktu", "Timbuktu", "Timbuktu",
     "Mali", [],
     "The Sankore mosque, in mud-brick Sudano-Sahelian style."),
    ("banff", "Banff National Park", "Banff National Park",
     "Canada", [], None),
    ("niagara-falls", "Niagara Falls", "Niagara Falls",
     "Canada", ["United States", "USA"],
     "The Horseshoe Falls are mostly on the Canadian side."),
]

DECKS = {
    "cities": ("World Landmarks — Name the City", CITIES),
    "countries": ("World Landmarks — Name the Country", COUNTRIES),
}


# Landmarks whose Wikipedia article has no lead image: fetched straight from
# Commons by file title instead (rendered through Special:FilePath).
COMMONS_OVERRIDES = {
    "persepolis": "Persépolis, Irán, 2016-09-24, DD 56.jpg",
}


def summary_image(page):
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + urllib.parse.quote(page.replace(" ", "_")))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        s = json.load(r)
    thumb = s.get("thumbnail", {}).get("source")
    if not thumb:
        raise ValueError("no thumbnail in page summary")
    return re.sub(r"/\d+px-", f"/{WIDTH}px-", thumb)


def fetch(page, slug):
    if title := COMMONS_OVERRIDES.get(slug):
        url = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
               + urllib.parse.quote(title) + f"?width={WIDTH}")
    else:
        url = summary_image(page)
    ext = ".png" if url.lower().endswith(".png") else ".jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as r:
            data = r.read()
    except urllib.error.HTTPError:
        # The source image is smaller than WIDTH (or the bucket moved):
        # take the summary's own thumbnail untouched.
        url = re.sub(r"/\d+px-", "/330px-", url)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as r:
            data = r.read()
    if not (data.startswith(b"\xff\xd8\xff") or data.startswith(b"\x89PNG")):
        raise ValueError(f"not a JPEG/PNG ({len(data)} bytes)")
    with open(os.path.join(IMG_DIR, slug + ext), "wb") as f:
        f.write(data)


def image_for(slug):
    for ext in (".jpg", ".png"):
        if os.path.exists(os.path.join(IMG_DIR, slug + ext)):
            return slug + ext
    return None


def download():
    os.makedirs(IMG_DIR, exist_ok=True)
    failed = []
    for _, entries in DECKS.values():
        for slug, page, _, _, _, _ in entries:
            if image_for(slug):
                continue
            try:
                fetch(page, slug)
                print(f"fetched {slug}")
            except Exception as e:
                failed.append(page)
                print(f"FAILED {page}: {e}", file=sys.stderr)
            time.sleep(0.4)
    if failed:
        print(f"\n{len(failed)} failures: {failed}", file=sys.stderr)


def rebuild():
    for fname, (name, entries) in DECKS.items():
        cards = []
        for slug, _, landmark, answer, accepts, note in entries:
            img = image_for(slug)
            if not img:
                print(f"skipping {slug}: no image", file=sys.stderr)
                continue
            card = f"@img images/{img}\n---\n{answer}\n"
            for a in accepts:
                card += f"= {a}\n"
            card += f"---\n{landmark}."
            if note:
                card += f" {note}"
            card += "\n"
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
