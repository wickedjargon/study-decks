#!/usr/bin/env python3
"""(Re)generate the waters decks from the tables below.

Straits, rivers, and seas as typed answers, cued by what they connect,
flow through, or lie between. Text-only — the locator-maps pack covers
the visual side of geography.

    python3 gen_decks.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (question, answer, [accepted variants], note)
DECKS = {
    "straits": ("Waters — Straits", [
        ("The strait between Spain and Morocco",
         "Strait of Gibraltar", ["Gibraltar"],
         "14 km wide — Africa and Europe at their closest."),
        ("The strait between the Persian Gulf and the Gulf of Oman",
         "Strait of Hormuz", ["Hormuz"],
         "About a fifth of the world's oil passes through it."),
        ("The strait through Istanbul",
         "Bosporus", ["Bosphorus", "Bosporus Strait", "Strait of Istanbul"],
         "Splits the city between Europe and Asia."),
        ("The other Turkish strait, joining the Sea of Marmara to the Aegean",
         "Dardanelles", ["Hellespont", "Strait of Gallipoli"],
         "Ancient name: the Hellespont. Gallipoli sits on its European "
         "shore."),
        ("The strait between Russia and Alaska",
         "Bering Strait", ["Bering"],
         "82 km wide, with the International Date Line down the middle."),
        ("The strait between Malaysia and the Indonesian island of Sumatra",
         "Strait of Malacca", ["Malacca"],
         "The world's busiest shipping lane, and Singapore sits at its "
         "mouth."),
        ("The strait between England and France",
         "Strait of Dover", ["Dover"],
         "The Channel's narrowest point: 33 km."),
        ("The strait at the southern tip of mainland South America",
         "Strait of Magellan", ["Magellan"],
         "North of Tierra del Fuego; the open-ocean alternative around "
         "Cape Horn is the Drake Passage."),
        ("The strait between the Red Sea and the Gulf of Aden",
         "Bab-el-Mandeb", ["Bab el Mandeb", "Bab al-Mandab"],
         "Arabic for \"gate of tears\". Yemen on one side, Djibouti and "
         "Eritrea on the other."),
        ("The strait between China and Taiwan",
         "Taiwan Strait", ["Formosa Strait"], None),
        ("The strait between New Zealand's North and South Islands",
         "Cook Strait", ["Cook"], None),
        ("The strait between Australia and Papua New Guinea",
         "Torres Strait", ["Torres"], None),
        ("The strait between Australia and Tasmania",
         "Bass Strait", ["Bass"], None),
        ("The strait between Sicily and mainland Italy",
         "Strait of Messina", ["Messina"], None),
        ("The strait between Denmark and Sweden",
         "Øresund", ["Oresund", "The Sound"],
         "Crossed by the Øresund Bridge between Copenhagen and Malmö."),
    ]),
    "rivers": ("Waters — Rivers", [
        ("The river through Baghdad",
         "Tigris", [],
         "The Euphrates runs west of it; the two meet to form the Shatt "
         "al-Arab."),
        ("The river through Cairo",
         "Nile", [], None),
        ("The river through Paris",
         "Seine", [], None),
        ("The river through London",
         "Thames", [], None),
        ("The river through Rome",
         "Tiber", [], None),
        ("The river through Vienna and Budapest",
         "Danube", [],
         "Ten countries touch it — more than any other river."),
        ("The river through Cologne, ending in the Netherlands",
         "Rhine", [], None),
        ("The river through Lisbon",
         "Tagus", ["Tejo"], None),
        ("The river through Varanasi, sacred in Hinduism",
         "Ganges", ["Ganga"], None),
        ("The river through Wuhan and Shanghai's delta, Asia's longest",
         "Yangtze", ["Chang Jiang"], None),
        ("The river forming much of the US–Mexico border",
         "Rio Grande", [],
         "Called the Río Bravo in Mexico."),
        ("The river through Khartoum, where its two branches meet",
         "Nile", ["Blue Nile", "White Nile"],
         "The Blue Nile (from Ethiopia) and White Nile (from Lake "
         "Victoria) join at Khartoum."),
        ("The river of the world's largest drainage basin",
         "Amazon", [],
         "Carries more water than the next seven rivers combined."),
        ("The river through Saint Petersburg",
         "Neva", [], None),
        ("The river through Kyiv",
         "Dnieper", ["Dnipro"], None),
    ]),
    "seas": ("Waters — Seas & Lakes", [
        ("The gulf between Iran and the Arabian Peninsula",
         "Persian Gulf", [], None),
        ("The sea between Italy and the Balkans",
         "Adriatic Sea", ["Adriatic"], None),
        ("The sea between Greece and Turkey",
         "Aegean Sea", ["Aegean"], None),
        ("The sea north of Turkey",
         "Black Sea", [], None),
        ("The small sea between the Bosporus and the Dardanelles",
         "Sea of Marmara", ["Marmara"], None),
        ("The lake between Israel and Jordan, saltiest open water on Earth",
         "Dead Sea", [],
         "Its shore is the lowest dry land on Earth, about 430 m below "
         "sea level."),
        ("The world's largest lake, between Iran and Russia",
         "Caspian Sea", ["Caspian"],
         "Called a sea, but landlocked — larger than all the Great Lakes "
         "combined."),
        ("The sea between Egypt and Saudi Arabia",
         "Red Sea", [], None),
        ("The sea between Scandinavia and the Baltic states",
         "Baltic Sea", ["Baltic"], None),
        ("The sea between Britain and Scandinavia",
         "North Sea", [], None),
        ("The sea between Australia and New Zealand",
         "Tasman Sea", ["Tasman"], None),
        ("The sea between Korea and Japan",
         "Sea of Japan", ["East Sea"], None),
        ("The deepest lake on Earth, in Siberia",
         "Lake Baikal", ["Baikal"],
         "1,642 m deep — about a fifth of the world's unfrozen fresh "
         "water."),
        ("The largest freshwater lake by area, on the US–Canada border",
         "Lake Superior", ["Superior"], None),
        ("The only sea with no coastline",
         "Sargasso Sea", ["Sargasso"],
         "Bounded by Atlantic currents instead of land."),
    ]),
}


def rebuild():
    for fname, (name, cards) in DECKS.items():
        blocks = []
        for question, answer, accepts, note in cards:
            card = f"{question}?\n---\n{answer}\n"
            for a in accepts:
                card += f"= {a}\n"
            if note:
                card += f"---\n{note}\n"
            blocks.append(card)
        path = os.path.join(HERE, fname + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: type\n# answer-case: insensitive\n")
            f.write("# Generated by gen_decks.py — edit that script, not this file.\n\n")
            f.write("\n".join(blocks))
        print(f"wrote {fname}.deck ({len(blocks)} cards)")


if __name__ == "__main__":
    rebuild()
