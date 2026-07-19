#!/usr/bin/env python3
"""Download country flags from Wikimedia Commons and (re)generate the .deck
files.

Flags on Commons follow the systematic "Flag of <country>.svg" naming; each
entry below carries its exact file title. Files are fetched as PNG renders
via Special:FilePath so both frontends can decode them.

Re-runnable: existing images are skipped, so a second run is cheap. The deck
files are always rebuilt from the list below, skipping any entry whose image
is missing on disk, so the decks and the images never drift apart.

    python3 gen_images.py            # download missing flags, rebuild decks
    python3 gen_images.py --rebuild  # skip download, just rebuild decks
"""

import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "images")
UA = "study-world-flags/1.0 (personal flashcard deck; +https://commons.wikimedia.org/)"
WIDTH = 480

# (level, slug, country, commons file title, [accepted variants])
# Levels: 1 = famous/iconic, 2 = regional, 3 = expert/confusable.
# NOTE: cards are image-only questions — prompt text would give every card in
# a deck the same ID (IDs hash the question's text lines).
FLAGS = [
    # ── Level 1 — famous ────────────────────────────────────────────────
    (1, "canada",         "Canada",         "Flag of Canada (Pantone).svg", []),
    (1, "united-states",  "United States",  "Flag of the United States.svg", ["USA", "United States of America", "America"]),
    (1, "mexico",         "Mexico",         "Flag of Mexico.svg", []),
    (1, "brazil",         "Brazil",         "Flag of Brazil.svg", []),
    (1, "argentina",      "Argentina",      "Flag of Argentina.svg", []),
    (1, "united-kingdom", "United Kingdom", "Flag of the United Kingdom.svg", ["UK", "Great Britain", "Britain"]),
    (1, "france",         "France",         "Flag of France.svg", []),
    (1, "germany",        "Germany",        "Flag of Germany.svg", []),
    (1, "italy",          "Italy",          "Flag of Italy.svg", []),
    (1, "spain",          "Spain",          "Flag of Spain.svg", []),
    (1, "portugal",       "Portugal",       "Flag of Portugal.svg", []),
    (1, "netherlands",    "Netherlands",    "Flag of the Netherlands.svg", ["Holland"]),
    (1, "belgium",        "Belgium",        "Flag of Belgium (civil).svg", []),
    (1, "switzerland",    "Switzerland",    "Flag of Switzerland (Pantone).svg", []),
    (1, "sweden",         "Sweden",         "Flag of Sweden.svg", []),
    (1, "norway",         "Norway",         "Flag of Norway.svg", []),
    (1, "denmark",        "Denmark",        "Flag of Denmark.svg", []),
    (1, "finland",        "Finland",        "Flag of Finland.svg", []),
    (1, "ireland",        "Ireland",        "Flag of Ireland.svg", []),
    (1, "greece",         "Greece",         "Flag of Greece.svg", []),
    (1, "russia",         "Russia",         "Flag of Russia.svg", []),
    (1, "ukraine",        "Ukraine",        "Flag of Ukraine.svg", []),
    (1, "poland",         "Poland",         "Flag of Poland.svg", []),
    (1, "turkey",         "Turkey",         "Flag of Turkey.svg", ["Türkiye"]),
    (1, "japan",          "Japan",          "Flag of Japan.svg", []),
    (1, "china",          "China",          "Flag of the People's Republic of China.svg", ["People's Republic of China", "PRC"]),
    (1, "south-korea",    "South Korea",    "Flag of South Korea.svg", ["Korea"]),
    (1, "north-korea",    "North Korea",    "Flag of North Korea.svg", []),
    (1, "india",          "India",          "Flag of India.svg", []),
    (1, "pakistan",       "Pakistan",       "Flag of Pakistan.svg", []),
    (1, "australia",      "Australia",      "Flag of Australia (converted).svg", []),
    (1, "new-zealand",    "New Zealand",    "Flag of New Zealand.svg", []),
    (1, "israel",         "Israel",         "Flag of Israel.svg", []),
    (1, "egypt",          "Egypt",          "Flag of Egypt.svg", []),
    (1, "south-africa",   "South Africa",   "Flag of South Africa.svg", []),
    (1, "saudi-arabia",   "Saudi Arabia",   "Flag of Saudi Arabia.svg", []),
    (1, "iran",           "Iran",           "Flag of Iran.svg", []),
    (1, "iraq",           "Iraq",           "Flag of Iraq.svg", []),
    (1, "vietnam",        "Vietnam",        "Flag of Vietnam.svg", []),
    (1, "thailand",       "Thailand",       "Flag of Thailand.svg", []),
    (1, "indonesia",      "Indonesia",      "Flag of Indonesia.svg", []),
    (1, "philippines",    "Philippines",    "Flag of the Philippines.svg", []),
    (1, "cuba",           "Cuba",           "Flag of Cuba.svg", []),
    (1, "jamaica",        "Jamaica",        "Flag of Jamaica.svg", []),
    (1, "nigeria",        "Nigeria",        "Flag of Nigeria.svg", []),

    # ── Level 2 — regional ──────────────────────────────────────────────
    (2, "austria",        "Austria",        "Flag of Austria.svg", []),
    (2, "czechia",        "Czechia",        "Flag of the Czech Republic.svg", ["Czech Republic"]),
    (2, "slovakia",       "Slovakia",       "Flag of Slovakia.svg", []),
    (2, "hungary",        "Hungary",        "Flag of Hungary.svg", []),
    (2, "romania",        "Romania",        "Flag of Romania.svg", []),
    (2, "bulgaria",       "Bulgaria",       "Flag of Bulgaria.svg", []),
    (2, "croatia",        "Croatia",        "Flag of Croatia.svg", []),
    (2, "serbia",         "Serbia",         "Flag of Serbia.svg", []),
    (2, "iceland",        "Iceland",        "Flag of Iceland.svg", []),
    (2, "estonia",        "Estonia",        "Flag of Estonia.svg", []),
    (2, "latvia",         "Latvia",         "Flag of Latvia.svg", []),
    (2, "lithuania",      "Lithuania",      "Flag of Lithuania.svg", []),
    (2, "belarus",        "Belarus",        "Flag of Belarus.svg", []),
    (2, "albania",        "Albania",        "Flag of Albania.svg", []),
    (2, "slovenia",       "Slovenia",       "Flag of Slovenia.svg", []),
    (2, "georgia",        "Georgia",        "Flag of Georgia.svg", []),
    (2, "armenia",        "Armenia",        "Flag of Armenia.svg", []),
    (2, "azerbaijan",     "Azerbaijan",     "Flag of Azerbaijan.svg", []),
    (2, "kazakhstan",     "Kazakhstan",     "Flag of Kazakhstan.svg", []),
    (2, "mongolia",       "Mongolia",       "Flag of Mongolia.svg", []),
    (2, "nepal",          "Nepal",          "Flag of Nepal.svg", []),
    (2, "bangladesh",     "Bangladesh",     "Flag of Bangladesh.svg", []),
    (2, "sri-lanka",      "Sri Lanka",      "Flag of Sri Lanka.svg", []),
    (2, "myanmar",        "Myanmar",        "Flag of Myanmar.svg", ["Burma"]),
    (2, "malaysia",       "Malaysia",       "Flag of Malaysia.svg", []),
    (2, "singapore",      "Singapore",      "Flag of Singapore.svg", []),
    (2, "cambodia",       "Cambodia",       "Flag of Cambodia.svg", []),
    (2, "laos",           "Laos",           "Flag of Laos.svg", []),
    (2, "taiwan",         "Taiwan",         "Flag of the Republic of China.svg", ["Republic of China"]),
    (2, "uae",            "United Arab Emirates", "Flag of the United Arab Emirates.svg", ["UAE"]),
    (2, "qatar",          "Qatar",          "Flag of Qatar.svg", []),
    (2, "kuwait",         "Kuwait",         "Flag of Kuwait.svg", []),
    (2, "jordan",         "Jordan",         "Flag of Jordan.svg", []),
    (2, "lebanon",        "Lebanon",        "Flag of Lebanon.svg", []),
    (2, "syria",          "Syria",          "Flag of Syria.svg", []),
    (2, "morocco",        "Morocco",        "Flag of Morocco.svg", []),
    (2, "algeria",        "Algeria",        "Flag of Algeria.svg", []),
    (2, "tunisia",        "Tunisia",        "Flag of Tunisia.svg", []),
    (2, "libya",          "Libya",          "Flag of Libya.svg", []),
    (2, "kenya",          "Kenya",          "Flag of Kenya.svg", []),
    (2, "ethiopia",       "Ethiopia",       "Flag of Ethiopia.svg", []),
    (2, "ghana",          "Ghana",          "Flag of Ghana.svg", []),
    (2, "colombia",       "Colombia",       "Flag of Colombia.svg", []),
    (2, "venezuela",      "Venezuela",      "Flag of Venezuela.svg", []),
    (2, "peru",           "Peru",           "Flag of Peru.svg", []),
    (2, "chile",          "Chile",          "Flag of Chile.svg", []),
    (2, "ecuador",        "Ecuador",        "Flag of Ecuador.svg", []),
    (2, "bolivia",        "Bolivia",        "Flag of Bolivia.svg", []),
    (2, "uruguay",        "Uruguay",        "Flag of Uruguay.svg", []),
    (2, "paraguay",       "Paraguay",       "Flag of Paraguay.svg", []),

    # ── Level 3 — expert & confusable ───────────────────────────────────
    (3, "chad",           "Chad",           "Flag of Chad.svg", []),
    (3, "moldova",        "Moldova",        "Flag of Moldova.svg", []),
    (3, "ivory-coast",    "Ivory Coast",    "Flag of Côte d'Ivoire.svg", ["Côte d'Ivoire", "Cote d'Ivoire"]),
    (3, "monaco",         "Monaco",         "Flag of Monaco.svg", []),
    (3, "luxembourg",     "Luxembourg",     "Flag of Luxembourg.svg", []),
    (3, "liechtenstein",  "Liechtenstein",  "Flag of Liechtenstein.svg", []),
    (3, "andorra",        "Andorra",        "Flag of Andorra.svg", []),
    (3, "san-marino",     "San Marino",     "Flag of San Marino.svg", []),
    (3, "malta",          "Malta",          "Flag of Malta.svg", []),
    (3, "cyprus",         "Cyprus",         "Flag of Cyprus.svg", []),
    (3, "north-macedonia","North Macedonia","Flag of North Macedonia.svg", ["Macedonia"]),
    (3, "bosnia",         "Bosnia and Herzegovina", "Flag of Bosnia and Herzegovina.svg", ["Bosnia"]),
    (3, "montenegro",     "Montenegro",     "Flag of Montenegro.svg", []),
    (3, "kosovo",         "Kosovo",         "Flag of Kosovo.svg", []),
    (3, "uzbekistan",     "Uzbekistan",     "Flag of Uzbekistan.svg", []),
    (3, "kyrgyzstan",     "Kyrgyzstan",     "Flag of Kyrgyzstan.svg", []),
    (3, "tajikistan",     "Tajikistan",     "Flag of Tajikistan.svg", []),
    (3, "turkmenistan",   "Turkmenistan",   "Flag of Turkmenistan.svg", []),
    (3, "bhutan",         "Bhutan",         "Flag of Bhutan.svg", []),
    (3, "maldives",       "Maldives",       "Flag of Maldives.svg", []),
    (3, "brunei",         "Brunei",         "Flag of Brunei.svg", []),
    (3, "timor-leste",    "Timor-Leste",    "Flag of East Timor.svg", ["East Timor"]),
    (3, "oman",           "Oman",           "Flag of Oman.svg", []),
    (3, "yemen",          "Yemen",          "Flag of Yemen.svg", []),
    (3, "bahrain",        "Bahrain",        "Flag of Bahrain.svg", []),
    (3, "senegal",        "Senegal",        "Flag of Senegal.svg", []),
    (3, "mali",           "Mali",           "Flag of Mali.svg", []),
    (3, "guinea",         "Guinea",         "Flag of Guinea.svg", []),
    (3, "cameroon",       "Cameroon",       "Flag of Cameroon.svg", []),
    (3, "gabon",          "Gabon",          "Flag of Gabon.svg", []),
    (3, "congo-republic", "Republic of the Congo", "Flag of the Republic of the Congo.svg", ["Congo"]),
    (3, "congo-dr",       "Democratic Republic of the Congo", "Flag of the Democratic Republic of the Congo.svg", ["DR Congo", "DRC"]),
    (3, "tanzania",       "Tanzania",       "Flag of Tanzania.svg", []),
    (3, "uganda",         "Uganda",         "Flag of Uganda.svg", []),
    (3, "zambia",         "Zambia",         "Flag of Zambia.svg", []),
    (3, "zimbabwe",       "Zimbabwe",       "Flag of Zimbabwe.svg", []),
    (3, "botswana",       "Botswana",       "Flag of Botswana.svg", []),
    (3, "namibia",        "Namibia",        "Flag of Namibia.svg", []),
    (3, "mozambique",     "Mozambique",     "Flag of Mozambique.svg", []),
    (3, "angola",         "Angola",         "Flag of Angola.svg", []),
    (3, "rwanda",         "Rwanda",         "Flag of Rwanda.svg", []),
    (3, "somalia",        "Somalia",        "Flag of Somalia.svg", []),
    (3, "sudan",          "Sudan",          "Flag of Sudan.svg", []),
    (3, "madagascar",     "Madagascar",     "Flag of Madagascar.svg", []),
    (3, "fiji",           "Fiji",           "Flag of Fiji.svg", []),
    (3, "papua-new-guinea","Papua New Guinea","Flag of Papua New Guinea.svg", []),
    (3, "guatemala",      "Guatemala",      "Flag of Guatemala.svg", []),
    (3, "honduras",       "Honduras",       "Flag of Honduras.svg", []),
    (3, "el-salvador",    "El Salvador",    "Flag of El Salvador.svg", []),
    (3, "nicaragua",      "Nicaragua",      "Flag of Nicaragua.svg", []),
    (3, "costa-rica",     "Costa Rica",     "Flag of Costa Rica.svg", []),
    (3, "panama",         "Panama",         "Flag of Panama.svg", []),
    (3, "dominican-republic", "Dominican Republic", "Flag of the Dominican Republic.svg", []),
    (3, "haiti",          "Haiti",          "Flag of Haiti.svg", []),
    (3, "trinidad",       "Trinidad and Tobago", "Flag of Trinidad and Tobago.svg", ["Trinidad"]),
]

LEVELS = {
    1: ("level1-famous", "World Flags — Level 1 (Famous)"),
    2: ("level2-regional", "World Flags — Level 2 (Regional)"),
    3: ("level3-expert", "World Flags — Level 3 (Expert)"),
}

# Answer-side notes for the confusable flags: each names its lookalikes and
# the tell that separates them. Only pairs genuinely mistaken for each other
# get one — a flag nobody confuses stays bare. Kept out of the FLAGS tuples
# so importing packs (flags-by-region, capitals) don't break; they can apply
# the same notes via this dict.
NOTES = {
    "chad": "Nearly identical to Romania. Chad's blue is officially darker "
            "(indigo), but at a glance the two are the same flag.",
    "romania": "Chad flies almost exactly this flag — Romania's blue is "
               "slightly brighter. Moldova adds a coat of arms.",
    "moldova": "Romania's tricolor with the aurochs-and-eagle arms in the "
               "center — the arms are the only difference.",
    "monaco": "Same red-over-white as Indonesia — Monaco's flag is squarer. "
              "Upside down it's Poland.",
    "indonesia": "Red over white. Monaco is the same pair but squarer; "
                 "Poland is the reverse.",
    "poland": "White over red. Flipped, it becomes Indonesia (or Monaco).",
    "ivory-coast": "Ireland mirrored: orange at the hoist instead of green.",
    "ireland": "Green at the hoist. The mirror image, orange first, is "
               "Ivory Coast.",
    "netherlands": "Luxembourg's is nearly the same — the Dutch blue is "
                   "darker and the flag slightly stubbier.",
    "luxembourg": "The Netherlands with lighter blue and a longer shape.",
    "iceland": "Norway with the colors swapped: blue field, red cross "
               "outlined in white.",
    "norway": "Iceland reverses it: blue field with a red-and-white cross.",
    "senegal": "Mali's tricolor plus a green star in the center band.",
    "mali": "Green-gold-red. Senegal adds a star; Guinea runs the same "
            "colors in reverse.",
    "guinea": "Mali reversed: red at the hoist instead of green.",
    "venezuela": "Yellow-blue-red with an arc of eight stars. Colombia and "
                 "Ecuador share the tricolor; only Venezuela has stars.",
    "colombia": "The top half is all yellow. Ecuador flies the same bands "
                "with a coat of arms; Venezuela adds stars.",
    "ecuador": "Colombia's tricolor with the condor coat of arms in the "
               "middle.",
    "slovenia": "White-blue-red like Russia and Slovakia. The shield at the "
                "hoist shows Triglav's three peaks.",
    "slovakia": "Russia's tricolor with the double-cross shield.",
    "russia": "Plain white-blue-red. Slovakia and Slovenia fly the same "
              "bands with shields added.",
    "australia": "Six white stars plus the big Commonwealth Star under the "
                 "Union Jack. New Zealand's four stars are red.",
    "new-zealand": "Four red five-pointed stars. Australia's stars are "
                   "white, six, and include the large Commonwealth Star.",
    "qatar": "Maroon with nine serration points. Bahrain is brighter red "
             "with five.",
    "bahrain": "Red with five white serration points. Qatar is maroon, "
               "longer, with nine.",
}


def fetch(title, dest):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title) + f"?width={WIDTH}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())


def download():
    os.makedirs(IMG_DIR, exist_ok=True)
    for _, slug, _, title, _ in FLAGS:
        dest = os.path.join(IMG_DIR, slug + ".png")
        if os.path.exists(dest):
            continue
        try:
            fetch(title, dest)
            print(f"fetched {slug}.png")
        except Exception as e:
            print(f"FAILED {slug} ({title}): {e}", file=sys.stderr)
        time.sleep(0.4)


def rebuild():
    for level, (fname, name) in LEVELS.items():
        cards = []
        for lv, slug, country, _, accepts in FLAGS:
            if lv != level:
                continue
            img = os.path.join(IMG_DIR, slug + ".png")
            if not os.path.exists(img):
                print(f"skipping {slug}: no image", file=sys.stderr)
                continue
            card = f"@img images/{slug}.png\n---\n{country}\n"
            for a in accepts:
                card += f"= {a}\n"
            if note := NOTES.get(slug):
                card += f"---\n{note}\n"
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
