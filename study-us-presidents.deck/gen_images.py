#!/usr/bin/env python3
"""Download US president portraits and (re)generate the deck: a portrait,
you type the president.

Images come from each president's English Wikipedia infobox portrait via the
REST summary API — the one place all 45 are curated under one naming scheme
(Commons portrait file titles follow no pattern). Downloads are re-rendered
as ~480px thumbnails and verified to be real JPEG/PNG bytes.

Surnames are accepted where unique. The five ambiguous families (Adams,
Harrison, Johnson, Roosevelt, Bush) require a distinguishing form, so bare
"Bush" or "Roosevelt" is never accepted for anyone.

Re-runnable: existing images are skipped; the deck is always rebuilt,
skipping entries whose image is missing.

    python3 gen_images.py            # download missing portraits, rebuild deck
    python3 gen_images.py --rebuild  # skip download, just rebuild deck
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
UA = "study-us-presidents/1.0 (personal flashcard deck; +https://en.wikipedia.org/)"
# upload.wikimedia.org only serves thumbnails at fixed bucket widths
# (400 "Use thumbnail sizes listed" otherwise); 500 is a bucket.
WIDTH = 500

# (ordinal label, wiki page title, answer, [accepts], years, note)
# One card per person: Cleveland and Trump each served twice.
PRESIDENTS = [
    ("1st", "George Washington", "George Washington", ["Washington"],
     "1789–1797", None),
    ("2nd", "John Adams", "John Adams", [],
     "1797–1801", "Not to be confused with his son John Quincy Adams, the 6th."),
    ("3rd", "Thomas Jefferson", "Thomas Jefferson", ["Jefferson"],
     "1801–1809", None),
    ("4th", "James Madison", "James Madison", ["Madison"],
     "1809–1817", None),
    ("5th", "James Monroe", "James Monroe", ["Monroe"],
     "1817–1825", None),
    ("6th", "John Quincy Adams", "John Quincy Adams", [],
     "1825–1829", "Son of John Adams, the 2nd."),
    ("7th", "Andrew Jackson", "Andrew Jackson", ["Jackson"],
     "1829–1837", None),
    ("8th", "Martin Van Buren", "Martin Van Buren", ["Van Buren"],
     "1837–1841", None),
    ("9th", "William Henry Harrison", "William Henry Harrison", [],
     "1841", "Died a month into office — the shortest presidency. His "
     "grandson Benjamin was the 23rd."),
    ("10th", "John Tyler", "John Tyler", ["Tyler"],
     "1841–1845", None),
    ("11th", "James K. Polk", "James K. Polk", ["Polk", "James Polk"],
     "1845–1849", None),
    ("12th", "Zachary Taylor", "Zachary Taylor", ["Taylor"],
     "1849–1850", None),
    ("13th", "Millard Fillmore", "Millard Fillmore", ["Fillmore"],
     "1850–1853", None),
    ("14th", "Franklin Pierce", "Franklin Pierce", ["Pierce"],
     "1853–1857", None),
    ("15th", "James Buchanan", "James Buchanan", ["Buchanan"],
     "1857–1861", None),
    ("16th", "Abraham Lincoln", "Abraham Lincoln", ["Lincoln", "Abe Lincoln"],
     "1861–1865", None),
    ("17th", "Andrew Johnson", "Andrew Johnson", [],
     "1865–1869", "Succeeded Lincoln. Not Lyndon Johnson, the 36th."),
    ("18th", "Ulysses S. Grant", "Ulysses S. Grant",
     ["Grant", "Ulysses Grant"], "1869–1877", None),
    ("19th", "Rutherford B. Hayes", "Rutherford B. Hayes",
     ["Hayes", "Rutherford Hayes"], "1877–1881", None),
    ("20th", "James A. Garfield", "James A. Garfield",
     ["Garfield", "James Garfield"], "1881",
     "Assassinated six months into office."),
    ("21st", "Chester A. Arthur", "Chester A. Arthur",
     ["Arthur", "Chester Arthur"], "1881–1885", None),
    ("22nd & 24th", "Grover Cleveland", "Grover Cleveland", ["Cleveland"],
     "1885–1889, 1893–1897",
     "The only president with two non-consecutive terms until Trump."),
    ("23rd", "Benjamin Harrison", "Benjamin Harrison", [],
     "1889–1893", "Grandson of William Henry Harrison, the 9th."),
    ("25th", "William McKinley", "William McKinley", ["McKinley"],
     "1897–1901", None),
    ("26th", "Theodore Roosevelt", "Theodore Roosevelt", ["Teddy Roosevelt"],
     "1901–1909", "Not FDR — Franklin, the 32nd, was his fifth cousin."),
    ("27th", "William Howard Taft", "William Howard Taft",
     ["Taft", "William Taft"], "1909–1913", None),
    ("28th", "Woodrow Wilson", "Woodrow Wilson", ["Wilson"],
     "1913–1921", None),
    ("29th", "Warren G. Harding", "Warren G. Harding",
     ["Harding", "Warren Harding"], "1921–1923", None),
    ("30th", "Calvin Coolidge", "Calvin Coolidge", ["Coolidge"],
     "1923–1929", None),
    ("31st", "Herbert Hoover", "Herbert Hoover", ["Hoover"],
     "1929–1933", None),
    ("32nd", "Franklin D. Roosevelt", "Franklin D. Roosevelt",
     ["FDR", "Franklin Roosevelt"], "1933–1945",
     "Four terms — the only president elected more than twice."),
    ("33rd", "Harry S. Truman", "Harry S. Truman",
     ["Truman", "Harry Truman"], "1945–1953", None),
    ("34th", "Dwight D. Eisenhower", "Dwight D. Eisenhower",
     ["Eisenhower", "Ike", "Dwight Eisenhower"], "1953–1961", None),
    ("35th", "John F. Kennedy", "John F. Kennedy",
     ["JFK", "Kennedy", "John Kennedy"], "1961–1963", None),
    ("36th", "Lyndon B. Johnson", "Lyndon B. Johnson",
     ["LBJ", "Lyndon Johnson"], "1963–1969",
     "Succeeded Kennedy. Not Andrew Johnson, the 17th."),
    ("37th", "Richard Nixon", "Richard Nixon", ["Nixon"],
     "1969–1974", "The only president to resign."),
    ("38th", "Gerald Ford", "Gerald Ford", ["Ford"],
     "1974–1977", "The only president never elected president or vice "
     "president."),
    ("39th", "Jimmy Carter", "Jimmy Carter", ["Carter", "James Carter"],
     "1977–1981", None),
    ("40th", "Ronald Reagan", "Ronald Reagan", ["Reagan"],
     "1981–1989", None),
    ("41st", "George H. W. Bush", "George H. W. Bush",
     ["Bush Sr", "George Bush Sr"], "1989–1993",
     "Father of George W., the 43rd. Bare \"Bush\" is never accepted."),
    ("42nd", "Bill Clinton", "Bill Clinton", ["Clinton", "William Clinton"],
     "1993–2001", None),
    ("43rd", "George W. Bush", "George W. Bush",
     ["Bush Jr", "George Bush Jr"], "2001–2009",
     "Son of George H. W., the 41st."),
    ("44th", "Barack Obama", "Barack Obama", ["Obama"],
     "2009–2017", None),
    ("45th & 47th", "Donald Trump", "Donald Trump", ["Trump"],
     "2017–2021, 2025–", None),
    ("46th", "Joe Biden", "Joe Biden", ["Biden", "Joseph Biden"],
     "2021–2025", None),
]


# Fame tiers, so the household names can be learned before the forgettable
# middle of the 1800s. Judgment calls, keyed by answer name.
# 1 = famous (faces most people know), 2 = notable (known by name, face
# less certain), 3 = obscure (the pre-Civil-War parade and the Gilded Age).
LEVEL = {
    "George Washington": 1, "Thomas Jefferson": 1, "Abraham Lincoln": 1,
    "Theodore Roosevelt": 1, "Franklin D. Roosevelt": 1,
    "Dwight D. Eisenhower": 1, "John F. Kennedy": 1, "Richard Nixon": 1,
    "Ronald Reagan": 1, "Bill Clinton": 1, "George W. Bush": 1,
    "Barack Obama": 1, "Donald Trump": 1, "Joe Biden": 1,

    "John Adams": 2, "John Quincy Adams": 2, "James Madison": 2,
    "James Monroe": 2, "Andrew Jackson": 2, "Ulysses S. Grant": 2,
    "William McKinley": 2, "William Howard Taft": 2, "Woodrow Wilson": 2,
    "Herbert Hoover": 2, "Harry S. Truman": 2, "Lyndon B. Johnson": 2,
    "Gerald Ford": 2, "Jimmy Carter": 2, "George H. W. Bush": 2,

    "Martin Van Buren": 3, "William Henry Harrison": 3, "John Tyler": 3,
    "James K. Polk": 3, "Zachary Taylor": 3, "Millard Fillmore": 3,
    "Franklin Pierce": 3, "James Buchanan": 3, "Andrew Johnson": 3,
    "Rutherford B. Hayes": 3, "James A. Garfield": 3, "Chester A. Arthur": 3,
    "Grover Cleveland": 3, "Benjamin Harrison": 3, "Warren G. Harding": 3,
    "Calvin Coolidge": 3,
}

LEVELS = {
    1: ("level1-famous", "US Presidents — Level 1 (Famous)"),
    2: ("level2-notable", "US Presidents — Level 2 (Notable)"),
    3: ("level3-obscure", "US Presidents — Level 3 (Obscure)"),
}


def slugify(name):
    slug = "".join(c if c.isalnum() else "-" for c in name.lower())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def portrait_url(page):
    """The infobox portrait, re-thumbed to WIDTH."""
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
    url = portrait_url(page)
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
    dest = os.path.join(IMG_DIR, slug + ext)
    with open(dest, "wb") as f:
        f.write(data)
    return dest


def image_for(slug):
    for ext in (".jpg", ".png"):
        if os.path.exists(os.path.join(IMG_DIR, slug + ext)):
            return slug + ext
    return None


def download():
    os.makedirs(IMG_DIR, exist_ok=True)
    failed = []
    for _, page, answer, _, _, _ in PRESIDENTS:
        slug = slugify(answer)
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
    for p in PRESIDENTS:
        assert p[2] in LEVEL, f"no level for {p[2]}"
    for level, (fname, name) in LEVELS.items():
        cards = []
        for ordinal, _, answer, accepts, years, note in PRESIDENTS:
            if LEVEL[answer] != level:
                continue
            slug = slugify(answer)
            img = image_for(slug)
            if not img:
                print(f"skipping {slug}: no image", file=sys.stderr)
                continue
            card = f"@img images/{img}\n---\n{answer}\n"
            for a in accepts:
                card += f"= {a}\n"
            card += f"---\nThe {ordinal} president, {years}."
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
