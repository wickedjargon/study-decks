#!/usr/bin/env python3
"""(Re)generate the world-capitals deck files from the table below.

Country → capital, typed answers, with "=" variants for common alternate
spellings and multi-capital countries. Levels mirror the world-flags pack, so
the two can be studied side by side.

    python3 gen_decks.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Each question shows the country's flag alongside its name, borrowed from
# the sibling world-flags pack (cards still work, just textless, if it's
# absent). Card IDs hash only the question's text lines, so adding or
# removing the image never orphans progress.
FLAGS_DIR = os.path.join(HERE, "..", "study-world-flags.deck", "images")

# Countries whose flag-pack slug isn't the slugified country name.
FLAG_SLUGS = {
    "United Arab Emirates": "uae",
    "Bosnia and Herzegovina": "bosnia",
    "Republic of the Congo": "congo-republic",
    "Democratic Republic of the Congo": "congo-dr",
    "Trinidad and Tobago": "trinidad",
}


def flag_path(country):
    slug = FLAG_SLUGS.get(country)
    if slug is None:
        slug = "".join(c if c.isalnum() else "-" for c in country.lower())
        while "--" in slug:
            slug = slug.replace("--", "-")
    if os.path.exists(os.path.join(FLAGS_DIR, slug + ".png")):
        return f"../study-world-flags.deck/images/{slug}.png"
    print(f"no flag for {country} ({slug})", file=sys.stderr)
    return None

# (level, country, capital, [accepted variants])
CAPITALS = [
    # ── Level 1 — famous ────────────────────────────────────────────────
    (1, "Canada", "Ottawa", []),
    (1, "United States", "Washington, D.C.", ["Washington DC", "Washington D.C.", "Washington"]),
    (1, "Mexico", "Mexico City", []),
    (1, "Brazil", "Brasília", ["Brasilia"]),
    (1, "Argentina", "Buenos Aires", []),
    (1, "United Kingdom", "London", []),
    (1, "France", "Paris", []),
    (1, "Germany", "Berlin", []),
    (1, "Italy", "Rome", []),
    (1, "Spain", "Madrid", []),
    (1, "Portugal", "Lisbon", []),
    (1, "Netherlands", "Amsterdam", []),
    (1, "Belgium", "Brussels", []),
    (1, "Switzerland", "Bern", ["Berne"]),
    (1, "Sweden", "Stockholm", []),
    (1, "Norway", "Oslo", []),
    (1, "Denmark", "Copenhagen", []),
    (1, "Finland", "Helsinki", []),
    (1, "Ireland", "Dublin", []),
    (1, "Greece", "Athens", []),
    (1, "Russia", "Moscow", []),
    (1, "Ukraine", "Kyiv", ["Kiev"]),
    (1, "Poland", "Warsaw", []),
    (1, "Turkey", "Ankara", []),
    (1, "Japan", "Tokyo", []),
    (1, "China", "Beijing", []),
    (1, "South Korea", "Seoul", []),
    (1, "North Korea", "Pyongyang", []),
    (1, "India", "New Delhi", ["Delhi"]),
    (1, "Pakistan", "Islamabad", []),
    (1, "Australia", "Canberra", []),
    (1, "New Zealand", "Wellington", []),
    (1, "Israel", "Jerusalem", []),
    (1, "Egypt", "Cairo", []),
    (1, "South Africa", "Pretoria", ["Cape Town", "Bloemfontein"]),
    (1, "Saudi Arabia", "Riyadh", []),
    (1, "Iran", "Tehran", []),
    (1, "Iraq", "Baghdad", []),
    (1, "Vietnam", "Hanoi", []),
    (1, "Thailand", "Bangkok", ["Krung Thep"]),
    (1, "Indonesia", "Jakarta", ["Nusantara"]),
    (1, "Philippines", "Manila", []),
    (1, "Cuba", "Havana", []),
    (1, "Jamaica", "Kingston", []),
    (1, "Nigeria", "Abuja", []),

    # ── Level 2 — regional ──────────────────────────────────────────────
    (2, "Austria", "Vienna", []),
    (2, "Czechia", "Prague", []),
    (2, "Slovakia", "Bratislava", []),
    (2, "Hungary", "Budapest", []),
    (2, "Romania", "Bucharest", []),
    (2, "Bulgaria", "Sofia", []),
    (2, "Croatia", "Zagreb", []),
    (2, "Serbia", "Belgrade", []),
    (2, "Iceland", "Reykjavík", ["Reykjavik"]),
    (2, "Estonia", "Tallinn", []),
    (2, "Latvia", "Riga", []),
    (2, "Lithuania", "Vilnius", []),
    (2, "Belarus", "Minsk", []),
    (2, "Albania", "Tirana", []),
    (2, "Slovenia", "Ljubljana", []),
    (2, "Georgia", "Tbilisi", []),
    (2, "Armenia", "Yerevan", []),
    (2, "Azerbaijan", "Baku", []),
    (2, "Kazakhstan", "Astana", []),
    (2, "Mongolia", "Ulaanbaatar", ["Ulan Bator"]),
    (2, "Nepal", "Kathmandu", []),
    (2, "Bangladesh", "Dhaka", []),
    (2, "Sri Lanka", "Sri Jayawardenepura Kotte", ["Kotte", "Colombo"]),
    (2, "Myanmar", "Naypyidaw", ["Nay Pyi Taw"]),
    (2, "Malaysia", "Kuala Lumpur", ["KL"]),
    (2, "Singapore", "Singapore", ["Singapore City"]),
    (2, "Cambodia", "Phnom Penh", []),
    (2, "Laos", "Vientiane", []),
    (2, "Taiwan", "Taipei", []),
    (2, "United Arab Emirates", "Abu Dhabi", []),
    (2, "Qatar", "Doha", []),
    (2, "Kuwait", "Kuwait City", ["Kuwait"]),
    (2, "Jordan", "Amman", []),
    (2, "Lebanon", "Beirut", []),
    (2, "Syria", "Damascus", []),
    (2, "Morocco", "Rabat", []),
    (2, "Algeria", "Algiers", []),
    (2, "Tunisia", "Tunis", []),
    (2, "Libya", "Tripoli", []),
    (2, "Kenya", "Nairobi", []),
    (2, "Ethiopia", "Addis Ababa", []),
    (2, "Ghana", "Accra", []),
    (2, "Colombia", "Bogotá", ["Bogota"]),
    (2, "Venezuela", "Caracas", []),
    (2, "Peru", "Lima", []),
    (2, "Chile", "Santiago", []),
    (2, "Ecuador", "Quito", []),
    (2, "Bolivia", "Sucre", ["La Paz"]),
    (2, "Uruguay", "Montevideo", []),
    (2, "Paraguay", "Asunción", ["Asuncion"]),

    # ── Level 3 — expert ────────────────────────────────────────────────
    (3, "Chad", "N'Djamena", ["Ndjamena"]),
    (3, "Moldova", "Chișinău", ["Chisinau"]),
    (3, "Ivory Coast", "Yamoussoukro", ["Abidjan"]),
    (3, "Monaco", "Monaco", []),
    (3, "Luxembourg", "Luxembourg City", ["Luxembourg"]),
    (3, "Liechtenstein", "Vaduz", []),
    (3, "Andorra", "Andorra la Vella", []),
    (3, "San Marino", "San Marino", []),
    (3, "Malta", "Valletta", []),
    (3, "Cyprus", "Nicosia", []),
    (3, "North Macedonia", "Skopje", []),
    (3, "Bosnia and Herzegovina", "Sarajevo", []),
    (3, "Montenegro", "Podgorica", []),
    (3, "Kosovo", "Pristina", ["Prishtina"]),
    (3, "Uzbekistan", "Tashkent", []),
    (3, "Kyrgyzstan", "Bishkek", []),
    (3, "Tajikistan", "Dushanbe", []),
    (3, "Turkmenistan", "Ashgabat", []),
    (3, "Bhutan", "Thimphu", []),
    (3, "Maldives", "Malé", ["Male"]),
    (3, "Brunei", "Bandar Seri Begawan", []),
    (3, "Timor-Leste", "Dili", []),
    (3, "Oman", "Muscat", []),
    (3, "Yemen", "Sana'a", ["Sanaa"]),
    (3, "Bahrain", "Manama", []),
    (3, "Senegal", "Dakar", []),
    (3, "Mali", "Bamako", []),
    (3, "Guinea", "Conakry", []),
    (3, "Cameroon", "Yaoundé", ["Yaounde"]),
    (3, "Gabon", "Libreville", []),
    (3, "Republic of the Congo", "Brazzaville", []),
    (3, "Democratic Republic of the Congo", "Kinshasa", []),
    (3, "Tanzania", "Dodoma", ["Dar es Salaam"]),
    (3, "Uganda", "Kampala", []),
    (3, "Zambia", "Lusaka", []),
    (3, "Zimbabwe", "Harare", []),
    (3, "Botswana", "Gaborone", []),
    (3, "Namibia", "Windhoek", []),
    (3, "Mozambique", "Maputo", []),
    (3, "Angola", "Luanda", []),
    (3, "Rwanda", "Kigali", []),
    (3, "Somalia", "Mogadishu", []),
    (3, "Sudan", "Khartoum", []),
    (3, "Madagascar", "Antananarivo", []),
    (3, "Fiji", "Suva", []),
    (3, "Papua New Guinea", "Port Moresby", []),
    (3, "Guatemala", "Guatemala City", []),
    (3, "Honduras", "Tegucigalpa", []),
    (3, "El Salvador", "San Salvador", []),
    (3, "Nicaragua", "Managua", []),
    (3, "Costa Rica", "San José", ["San Jose"]),
    (3, "Panama", "Panama City", ["Panama"]),
    (3, "Dominican Republic", "Santo Domingo", []),
    (3, "Haiti", "Port-au-Prince", []),
    (3, "Trinidad and Tobago", "Port of Spain", []),
]

LEVELS = {
    1: ("level1-famous", "World Capitals — Level 1 (Famous)"),
    2: ("level2-regional", "World Capitals — Level 2 (Regional)"),
    3: ("level3-expert", "World Capitals — Level 3 (Expert)"),
}


def rebuild():
    for level, (fname, name) in LEVELS.items():
        cards = []
        for lv, country, capital, accepts in CAPITALS:
            if lv != level:
                continue
            card = ""
            if img := flag_path(country):
                card += f"@img {img}\n"
            card += f"{country}\n---\n{capital}\n"
            for a in accepts:
                card += f"= {a}\n"
            cards.append(card)
        path = os.path.join(HERE, fname + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: type\n# answer-case: insensitive\n")
            f.write("# Generated by gen_decks.py — edit that script, not this file.\n\n")
            f.write("\n".join(cards))
        print(f"wrote {fname}.deck ({len(cards)} cards)")


if __name__ == "__main__":
    rebuild()
