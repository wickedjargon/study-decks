#!/usr/bin/env python3
"""(Re)generate the by-region flag decks from the world-flags pack.

The country table (names, Commons titles, accepted variants) and the images
both live in ../study-world-flags.deck — this pack only adds the region
assignment, so a country added over there just needs a REGION entry here.
Images are referenced across the pack boundary (@img ../study-world-flags.deck/
images/...), the same borrowing world-capitals does; nothing is downloaded or
copied.

    python3 gen_decks.py    # rebuild the region decks
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, "..", "study-world-flags.deck")

# The sibling pack's curated FLAGS table: (level, slug, country, title, accepts).
spec = importlib.util.spec_from_file_location("wf_gen", os.path.join(WF, "gen_images.py"))
wf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wf)

# Region per slug. The big continents are subdivided (Europe, Asia, Africa);
# regions that are already a decent session size stay whole (Middle East,
# the Americas, Oceania). Conventional judgment calls: the Caucasus is its
# own tiny deck rather than lumped with Central Asia; Turkey and the Gulf
# are the Middle East; Egypt goes with North Africa; Russia with Eastern
# Europe; Sudan with North Africa; Madagascar with East Africa.
REGION = {
    # ── North America (incl. Central America & Caribbean) ──────────────
    "canada": "north-america", "united-states": "north-america",
    "mexico": "north-america", "cuba": "north-america",
    "jamaica": "north-america", "guatemala": "north-america",
    "honduras": "north-america", "el-salvador": "north-america",
    "nicaragua": "north-america", "costa-rica": "north-america",
    "panama": "north-america", "dominican-republic": "north-america",
    "haiti": "north-america", "trinidad": "north-america",
    # ── South America ───────────────────────────────────────────────────
    "brazil": "south-america", "argentina": "south-america",
    "colombia": "south-america", "venezuela": "south-america",
    "peru": "south-america", "chile": "south-america",
    "ecuador": "south-america", "bolivia": "south-america",
    "uruguay": "south-america", "paraguay": "south-america",
    # ── Northern Europe ─────────────────────────────────────────────────
    "sweden": "northern-europe", "norway": "northern-europe",
    "denmark": "northern-europe", "finland": "northern-europe",
    "iceland": "northern-europe", "estonia": "northern-europe",
    "latvia": "northern-europe", "lithuania": "northern-europe",
    # ── Western Europe ──────────────────────────────────────────────────
    "united-kingdom": "western-europe", "ireland": "western-europe",
    "france": "western-europe", "germany": "western-europe",
    "netherlands": "western-europe", "belgium": "western-europe",
    "switzerland": "western-europe", "austria": "western-europe",
    "luxembourg": "western-europe", "monaco": "western-europe",
    "liechtenstein": "western-europe",
    # ── Southern Europe ─────────────────────────────────────────────────
    "italy": "southern-europe", "spain": "southern-europe",
    "portugal": "southern-europe", "greece": "southern-europe",
    "malta": "southern-europe", "cyprus": "southern-europe",
    "andorra": "southern-europe", "san-marino": "southern-europe",
    # ── Eastern Europe ──────────────────────────────────────────────────
    "russia": "eastern-europe", "ukraine": "eastern-europe",
    "poland": "eastern-europe", "czechia": "eastern-europe",
    "slovakia": "eastern-europe", "hungary": "eastern-europe",
    "romania": "eastern-europe", "bulgaria": "eastern-europe",
    "belarus": "eastern-europe", "moldova": "eastern-europe",
    # ── Balkans ─────────────────────────────────────────────────────────
    "croatia": "balkans", "serbia": "balkans", "albania": "balkans",
    "slovenia": "balkans", "north-macedonia": "balkans",
    "bosnia": "balkans", "montenegro": "balkans", "kosovo": "balkans",
    # ── East Asia ───────────────────────────────────────────────────────
    "japan": "east-asia", "china": "east-asia", "south-korea": "east-asia",
    "north-korea": "east-asia", "mongolia": "east-asia",
    "taiwan": "east-asia",
    # ── South Asia ──────────────────────────────────────────────────────
    "india": "south-asia", "pakistan": "south-asia", "nepal": "south-asia",
    "bangladesh": "south-asia", "sri-lanka": "south-asia",
    "bhutan": "south-asia", "maldives": "south-asia",
    # ── Southeast Asia ──────────────────────────────────────────────────
    "vietnam": "southeast-asia", "thailand": "southeast-asia",
    "indonesia": "southeast-asia", "philippines": "southeast-asia",
    "myanmar": "southeast-asia", "malaysia": "southeast-asia",
    "singapore": "southeast-asia", "cambodia": "southeast-asia",
    "laos": "southeast-asia", "brunei": "southeast-asia",
    "timor-leste": "southeast-asia",
    # ── Central Asia ────────────────────────────────────────────────────
    "kazakhstan": "central-asia", "uzbekistan": "central-asia",
    "kyrgyzstan": "central-asia", "tajikistan": "central-asia",
    "turkmenistan": "central-asia",
    # ── Caucasus ────────────────────────────────────────────────────────
    "georgia": "caucasus", "armenia": "caucasus", "azerbaijan": "caucasus",
    # ── Middle East ─────────────────────────────────────────────────────
    "turkey": "middle-east", "israel": "middle-east",
    "saudi-arabia": "middle-east", "iran": "middle-east",
    "iraq": "middle-east", "uae": "middle-east", "qatar": "middle-east",
    "kuwait": "middle-east", "jordan": "middle-east",
    "lebanon": "middle-east", "syria": "middle-east", "oman": "middle-east",
    "yemen": "middle-east", "bahrain": "middle-east",
    # ── North Africa ────────────────────────────────────────────────────
    "egypt": "north-africa", "morocco": "north-africa",
    "algeria": "north-africa", "tunisia": "north-africa",
    "libya": "north-africa", "sudan": "north-africa",
    # ── West Africa ─────────────────────────────────────────────────────
    "nigeria": "west-africa", "ghana": "west-africa",
    "ivory-coast": "west-africa", "senegal": "west-africa",
    "mali": "west-africa", "guinea": "west-africa",
    # ── Central Africa ──────────────────────────────────────────────────
    "chad": "central-africa", "cameroon": "central-africa",
    "gabon": "central-africa", "congo-republic": "central-africa",
    "congo-dr": "central-africa",
    # ── East Africa ─────────────────────────────────────────────────────
    "kenya": "east-africa", "ethiopia": "east-africa",
    "tanzania": "east-africa", "uganda": "east-africa",
    "rwanda": "east-africa", "somalia": "east-africa",
    "madagascar": "east-africa",
    # ── Southern Africa ─────────────────────────────────────────────────
    "south-africa": "southern-africa", "zambia": "southern-africa",
    "zimbabwe": "southern-africa", "botswana": "southern-africa",
    "namibia": "southern-africa", "mozambique": "southern-africa",
    "angola": "southern-africa",
    # ── Oceania ─────────────────────────────────────────────────────────
    "australia": "oceania", "new-zealand": "oceania", "fiji": "oceania",
    "papua-new-guinea": "oceania",
}

# File name and deck title per region, in shelf order.
REGIONS = [
    ("balkans", "Flags by Region — Balkans"),
    ("caucasus", "Flags by Region — Caucasus"),
    ("central-africa", "Flags by Region — Central Africa"),
    ("central-asia", "Flags by Region — Central Asia"),
    ("east-africa", "Flags by Region — East Africa"),
    ("east-asia", "Flags by Region — East Asia"),
    ("eastern-europe", "Flags by Region — Eastern Europe"),
    ("middle-east", "Flags by Region — Middle East"),
    ("north-africa", "Flags by Region — North Africa"),
    ("north-america", "Flags by Region — North America"),
    ("northern-europe", "Flags by Region — Northern Europe"),
    ("oceania", "Flags by Region — Oceania"),
    ("south-america", "Flags by Region — South America"),
    ("south-asia", "Flags by Region — South Asia"),
    ("southeast-asia", "Flags by Region — Southeast Asia"),
    ("southern-africa", "Flags by Region — Southern Africa"),
    ("southern-europe", "Flags by Region — Southern Europe"),
    ("west-africa", "Flags by Region — West Africa"),
    ("western-europe", "Flags by Region — Western Europe"),
]


def rebuild():
    by_region = {key: [] for key, _ in REGIONS}
    for _, slug, country, _, accepts in wf.FLAGS:
        region = REGION.get(slug)
        if region is None:
            print(f"UNASSIGNED {slug}: add it to REGION", file=sys.stderr)
            continue
        img = os.path.join(WF, "images", slug + ".png")
        if not os.path.exists(img):
            print(f"skipping {slug}: no image", file=sys.stderr)
            continue
        # NOTE: image-only questions on purpose — a shared prompt line would
        # give every card the same ID (IDs hash the question's text lines).
        card = f"@img ../study-world-flags.deck/images/{slug}.png\n---\n{country}\n"
        for a in accepts:
            card += f"= {a}\n"
        # The sibling pack's confusable-pair notes apply to the same flags.
        if note := wf.NOTES.get(slug):
            card += f"---\n{note}\n"
        by_region[region].append(card)

    for stale in set(REGION) - {slug for _, slug, *_ in wf.FLAGS}:
        print(f"STALE {stale}: in REGION but not in the flags table", file=sys.stderr)

    # A renamed or re-split region must not leave its old deck file behind —
    # a stale file would keep showing up in packs and the library.
    import glob
    keep = {key + ".deck" for key, _ in REGIONS}
    for path in glob.glob(os.path.join(HERE, "*.deck")):
        if os.path.basename(path) not in keep:
            os.remove(path)
            print(f"removed stale {os.path.basename(path)}")

    for key, name in REGIONS:
        path = os.path.join(HERE, key + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: type\n# answer-case: insensitive\n")
            f.write("# Generated by gen_decks.py — edit that script, not this file.\n\n")
            f.write("\n".join(by_region[key]))
        print(f"wrote {key}.deck ({len(by_region[key])} cards)")


if __name__ == "__main__":
    rebuild()
