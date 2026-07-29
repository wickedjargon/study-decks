import asyncio
import os

import edge_tts

VOICE = "ja-JP-NanamiNeural"
HERE = os.path.dirname(os.path.abspath(__file__))

# (katakana reading to speak, output slug) — feed the katakana so the audio
# matches how the tile is actually called at a Japanese table. The numbers use
# the Chinese-derived mahjong readings (ii, ryan, san, suu, uu, roo, chii, paa,
# kyuu), NOT the everyday ichi/ni/san — and feeding katakana avoids the TTS
# reading kanji like 一萬 as "ichi-man" (10,000).
CARDS = [
    # Characters / man (萬子)
    ("イーマン", "man1"),
    ("リャンマン", "man2"),
    ("サンマン", "man3"),
    ("スーマン", "man4"),
    ("ウーマン", "man5"),
    ("ローマン", "man6"),
    ("チーマン", "man7"),
    ("パーマン", "man8"),
    ("キューマン", "man9"),
    # Dots / pin (筒子)
    ("イーピン", "pin1"),
    ("リャンピン", "pin2"),
    ("サンピン", "pin3"),
    ("スーピン", "pin4"),
    ("ウーピン", "pin5"),
    ("ローピン", "pin6"),
    ("チーピン", "pin7"),
    ("パーピン", "pin8"),
    ("キューピン", "pin9"),
    # Bamboo / sou (索子)
    ("イーソー", "sou1"),
    ("リャンソー", "sou2"),
    ("サンソー", "sou3"),
    ("スーソー", "sou4"),
    ("ウーソー", "sou5"),
    ("ローソー", "sou6"),
    ("チーソー", "sou7"),
    ("パーソー", "sou8"),
    ("キューソー", "sou9"),
    # Winds / kaze (風牌)
    ("トン", "ton"),
    ("ナン", "nan"),
    ("シャー", "shaa"),
    ("ペー", "pei"),
    # Dragons / sangen (三元牌)
    ("チュン", "chun"),
    ("ハツ", "hatsu"),
    ("ハク", "haku"),
]


async def main():
    for text, slug in CARDS:
        out = os.path.join(HERE, "audio", f"{slug}.mp3")
        await edge_tts.Communicate(text, VOICE).save(out)
        print(f"  {out}  ({text})")


asyncio.run(main())
