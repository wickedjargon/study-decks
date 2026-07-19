#!/usr/bin/env python3
"""(Re)generate the borders decks from the table below.

"Which country borders X?" in choice mode: the answer is one real neighbor
(usually the surprising one), the three "~" distractors are hand-picked
plausible non-neighbors, and every other real neighbor is an "=" accepted
answer — so the engine can never auto-fill a true neighbor as a wrong
option, and a typed session accepts any real neighbor.

Adjacency is land borders under the conventional reading (Bahrain is an
island, Chile–Brazil never touch). Disputed borders are left out of both
answers and distractors. The script asserts no distractor collides with an
accepted answer; the adjacency itself is the curator's job.

    python3 gen_decks.py
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (country, answer, [other accepted neighbors], [distractors], note)
CARDS = {
    "europe": ("Borders — Europe", [
        ("Switzerland", "Liechtenstein",
         ["France", "Germany", "Austria", "Italy"],
         ["Belgium", "Netherlands", "Slovenia"],
         "Liechtenstein is doubly landlocked: every route to the sea crosses "
         "two borders."),
        ("Poland", "Russia",
         ["Germany", "Czechia", "Slovakia", "Ukraine", "Belarus", "Lithuania"],
         ["Latvia", "Hungary", "Romania"],
         "Via the Kaliningrad exclave on the Baltic, cut off from the rest "
         "of Russia."),
        ("Norway", "Russia",
         ["Sweden", "Finland"],
         ["Denmark", "Estonia", "Iceland"],
         "A short 198 km Arctic border at Kirkenes."),
        ("Spain", "Morocco",
         ["Portugal", "France", "Andorra"],
         ["Algeria", "Italy", "Tunisia"],
         "Through Ceuta and Melilla, two Spanish cities on the African "
         "coast."),
        ("Croatia", "Montenegro",
         ["Slovenia", "Hungary", "Serbia", "Bosnia and Herzegovina"],
         ["Albania", "North Macedonia", "Austria"],
         None),
        ("Germany", "Denmark",
         ["Netherlands", "Belgium", "Luxembourg", "France", "Switzerland",
          "Austria", "Czechia", "Poland"],
         ["Sweden", "Hungary", "Italy"],
         "Nine neighbors — tied with Russia and China for most in the "
         "world... almost: China and Russia have 14 each."),
        ("Italy", "Slovenia",
         ["France", "Switzerland", "Austria", "San Marino", "Vatican City"],
         ["Croatia", "Germany", "Greece"],
         "Plus two countries entirely inside it: San Marino and Vatican "
         "City."),
        ("Romania", "Moldova",
         ["Hungary", "Serbia", "Bulgaria", "Ukraine"],
         ["Poland", "Slovakia", "Turkey"],
         None),
        ("Ukraine", "Slovakia",
         ["Poland", "Hungary", "Romania", "Moldova", "Belarus", "Russia"],
         ["Lithuania", "Bulgaria", "Latvia"],
         None),
    ]),
    "asia": ("Borders — Asia & Middle East", [
        ("Iran", "Armenia",
         ["Iraq", "Turkey", "Azerbaijan", "Turkmenistan", "Afghanistan",
          "Pakistan"],
         ["Georgia", "Uzbekistan", "Tajikistan"],
         "A 44 km border along the Aras river — one of the shortest of "
         "Iran's seven."),
        ("Turkey", "Azerbaijan",
         ["Greece", "Bulgaria", "Georgia", "Armenia", "Iran", "Iraq",
          "Syria"],
         ["Russia", "Ukraine", "Israel"],
         "Via the Nakhchivan exclave: 17 km, Turkey's shortest border."),
        ("India", "Bhutan",
         ["Pakistan", "China", "Nepal", "Bangladesh", "Myanmar"],
         ["Sri Lanka", "Thailand", "Kazakhstan"],
         None),
        ("China", "Afghanistan",
         ["Russia", "Mongolia", "Kazakhstan", "Kyrgyzstan", "Tajikistan",
          "Pakistan", "India", "Nepal", "Bhutan", "Myanmar", "Laos",
          "Vietnam", "North Korea"],
         ["Thailand", "Bangladesh", "South Korea"],
         "Through the narrow Wakhan Corridor — 76 km of border at the end "
         "of a 350 km panhandle."),
        ("Russia", "North Korea",
         ["Norway", "Finland", "Estonia", "Latvia", "Lithuania", "Poland",
          "Belarus", "Ukraine", "Georgia", "Azerbaijan", "Kazakhstan",
          "Mongolia", "China"],
         ["Sweden", "Japan", "Uzbekistan"],
         "17 km along the Tumen river. Japan is close but the border is "
         "maritime only."),
        ("Afghanistan", "China",
         ["Iran", "Turkmenistan", "Uzbekistan", "Tajikistan", "Pakistan"],
         ["Kyrgyzstan", "Kazakhstan", "Nepal"],
         None),
        ("Thailand", "Malaysia",
         ["Myanmar", "Laos", "Cambodia"],
         ["Vietnam", "China", "Bangladesh"],
         "Vietnam and Thailand never touch — Laos and Cambodia lie "
         "between."),
        ("Vietnam", "Cambodia",
         ["China", "Laos"],
         ["Thailand", "Myanmar", "Malaysia"],
         None),
        ("Saudi Arabia", "Qatar",
         ["Jordan", "Iraq", "Kuwait", "United Arab Emirates", "Oman",
          "Yemen"],
         ["Bahrain", "Egypt", "Syria"],
         "Bahrain is an island — the King Fahd Causeway is a bridge, not a "
         "border."),
        ("Israel", "Lebanon",
         ["Syria", "Jordan", "Egypt"],
         ["Iraq", "Saudi Arabia", "Turkey"],
         None),
    ]),
    "africa": ("Borders — Africa", [
        ("Chad", "Libya",
         ["Niger", "Nigeria", "Cameroon", "Central African Republic",
          "Sudan"],
         ["Ethiopia", "Mali", "Algeria"],
         "Algeria and Chad never touch — Niger and Libya meet between "
         "them."),
        ("Egypt", "Israel",
         ["Libya", "Sudan"],
         ["Chad", "Saudi Arabia", "Ethiopia"],
         "Egypt and Chad nearly meet at Sudan's corner but never touch."),
        ("South Africa", "Lesotho",
         ["Namibia", "Botswana", "Zimbabwe", "Mozambique", "Eswatini"],
         ["Zambia", "Malawi", "Angola"],
         "Lesotho is entirely surrounded by South Africa — one of only "
         "three enclaved countries on Earth."),
        ("Nigeria", "Chad",
         ["Benin", "Niger", "Cameroon"],
         ["Ghana", "Mali", "Sudan"],
         "They meet in Lake Chad. Ghana and Nigeria never touch — Togo and "
         "Benin lie between."),
        ("Morocco", "Spain",
         ["Algeria"],
         ["Portugal", "Tunisia", "Mali"],
         "Ceuta and Melilla, on Morocco's coast, are Spain."),
        ("Kenya", "South Sudan",
         ["Ethiopia", "Somalia", "Uganda", "Tanzania"],
         ["Rwanda", "Sudan", "Eritrea"],
         "Kenya borders South Sudan, not Sudan — true since the 2011 "
         "split."),
        ("Ethiopia", "Djibouti",
         ["Eritrea", "Somalia", "Kenya", "South Sudan", "Sudan"],
         ["Uganda", "Egypt", "Chad"],
         None),
        ("Democratic Republic of the Congo", "Zambia",
         ["Republic of the Congo", "Central African Republic",
          "South Sudan", "Uganda", "Rwanda", "Burundi", "Tanzania",
          "Angola"],
         ["Zimbabwe", "Kenya", "Nigeria"],
         None),
        ("Tanzania", "Malawi",
         ["Kenya", "Uganda", "Rwanda", "Burundi",
          "Democratic Republic of the Congo", "Zambia", "Mozambique"],
         ["Zimbabwe", "Ethiopia", "Somalia"],
         None),
        ("Algeria", "Mauritania",
         ["Morocco", "Tunisia", "Libya", "Niger", "Mali"],
         ["Chad", "Egypt", "Senegal"],
         None),
    ]),
    "americas": ("Borders — The Americas", [
        ("Brazil", "France",
         ["Suriname", "Guyana", "Venezuela", "Colombia", "Peru", "Bolivia",
          "Paraguay", "Argentina", "Uruguay"],
         ["Chile", "Ecuador", "Panama"],
         "Via French Guiana — France's longest land border is with Brazil. "
         "Chile and Ecuador are the only South American countries Brazil "
         "doesn't touch."),
        ("Mexico", "Belize",
         ["United States", "Guatemala"],
         ["Honduras", "El Salvador", "Panama"],
         None),
        ("Panama", "Colombia",
         ["Costa Rica"],
         ["Venezuela", "Nicaragua", "Ecuador"],
         "The Darién Gap: a border with no road across it."),
        ("Argentina", "Bolivia",
         ["Chile", "Paraguay", "Brazil", "Uruguay"],
         ["Peru", "Ecuador", "Colombia"],
         None),
        ("Guatemala", "El Salvador",
         ["Mexico", "Belize", "Honduras"],
         ["Nicaragua", "Costa Rica", "Panama"],
         None),
        ("Colombia", "Panama",
         ["Venezuela", "Brazil", "Peru", "Ecuador"],
         ["Bolivia", "Guyana", "Costa Rica"],
         None),
        ("Peru", "Colombia",
         ["Ecuador", "Brazil", "Bolivia", "Chile"],
         ["Argentina", "Venezuela", "Paraguay"],
         None),
        ("Chile", "Bolivia",
         ["Peru", "Argentina"],
         ["Paraguay", "Uruguay", "Brazil"],
         "Chile and Brazil famously never touch."),
    ]),
}


# Countries for the "name five" set deck: every country in CARDS with at
# least this many neighbors gets a quota-5 enumeration card built from its
# full neighbor list (answer + accepts).
SET_MIN_NEIGHBORS = 7
SET_QUOTA = 5

# Name variants accepted for individual set entries, applied by lookup so
# the adjacency lists above stay canonical.
VARIANTS = {
    "Myanmar": ["Burma"],
    "Czechia": ["Czech Republic"],
    "United Arab Emirates": ["UAE"],
    "Democratic Republic of the Congo": ["DR Congo", "DRC"],
    "Republic of the Congo": ["Congo"],
    "Bosnia and Herzegovina": ["Bosnia"],
    "United States": ["USA", "United States of America", "America"],
    "United Kingdom": ["UK", "Britain", "Great Britain"],
}


def build_sets():
    blocks = []
    for _, (_, cards) in CARDS.items():
        for country, answer, accepts, _, _ in cards:
            neighbors = [answer] + accepts
            if len(neighbors) < SET_MIN_NEIGHBORS:
                continue
            card = f"Name {SET_QUOTA} countries that border {country}\n---\n"
            card += f"quota: {SET_QUOTA}\n"
            for n in neighbors:
                card += f"+ {n}\n"
                for v in VARIANTS.get(n, []):
                    card += f"= {v}\n"
            card += f"---\n{country} has {len(neighbors)} neighbors.\n"
            blocks.append(card)
    path = os.path.join(HERE, "name-five.deck")
    with open(path, "w") as f:
        f.write("# Borders — Name Five\n")
        f.write("# answer-mode: type\n")
        f.write("# Generated by gen_decks.py — edit that script, not this file.\n\n")
        f.write("\n".join(blocks))
    print(f"wrote name-five.deck ({len(blocks)} cards)")


def check():
    for fname, (_, cards) in CARDS.items():
        for country, answer, accepts, distractors, _ in cards:
            correct = {answer, *accepts}
            clash = correct & set(distractors)
            assert not clash, f"{fname}/{country}: distractor is a neighbor: {clash}"
            assert len(distractors) == 3, f"{fname}/{country}: need 3 distractors"
            assert country not in correct, f"{fname}/{country}: self-neighbor"


def rebuild():
    for fname, (name, cards) in CARDS.items():
        blocks = []
        for country, answer, accepts, distractors, note in cards:
            card = f"Which country borders {country}?\n---\n{answer}\n"
            for a in accepts:
                card += f"= {a}\n"
            for d in distractors:
                card += f"~ {d}\n"
            if note:
                card += f"---\n{note}\n"
            blocks.append(card)
        path = os.path.join(HERE, fname + ".deck")
        with open(path, "w") as f:
            f.write(f"# {name}\n")
            f.write("# answer-mode: choice\n")
            f.write("# Generated by gen_decks.py — edit that script, not this file.\n\n")
            f.write("\n".join(blocks))
        print(f"wrote {fname}.deck ({len(blocks)} cards)")


if __name__ == "__main__":
    check()
    rebuild()
    build_sets()
