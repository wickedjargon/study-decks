import asyncio
import os

import edge_tts

VOICE = "zh-CN-XiaoxiaoNeural"
HERE = os.path.dirname(os.path.abspath(__file__))

# (hanzi to speak, output slug) — feed the hanzi as the tile is called at a
# Chinese table: numbered suits as number + suit word (一万, 一筒, 一条),
# winds with 风, dragons by their spoken names (红中 fā cái 白板), flowers
# and seasons by their single character. The last group is the calls a
# player says out loud during a game (spoken-calls.deck).
CARDS = [
    # Characters / wàn (万子)
    ("一万", "wan1"),
    ("二万", "wan2"),
    ("三万", "wan3"),
    ("四万", "wan4"),
    ("五万", "wan5"),
    ("六万", "wan6"),
    ("七万", "wan7"),
    ("八万", "wan8"),
    ("九万", "wan9"),
    # Dots / tǒng (筒子)
    ("一筒", "tong1"),
    ("二筒", "tong2"),
    ("三筒", "tong3"),
    ("四筒", "tong4"),
    ("五筒", "tong5"),
    ("六筒", "tong6"),
    ("七筒", "tong7"),
    ("八筒", "tong8"),
    ("九筒", "tong9"),
    # Bamboos / tiáo (条子)
    ("一条", "tiao1"),
    ("二条", "tiao2"),
    ("三条", "tiao3"),
    ("四条", "tiao4"),
    ("五条", "tiao5"),
    ("六条", "tiao6"),
    ("七条", "tiao7"),
    ("八条", "tiao8"),
    ("九条", "tiao9"),
    # Winds (风牌)
    ("东风", "dongfeng"),
    ("南风", "nanfeng"),
    ("西风", "xifeng"),
    ("北风", "beifeng"),
    # Dragons (箭牌)
    ("红中", "hongzhong"),
    ("发财", "facai"),
    ("白板", "baiban"),
    # Flowers (花牌)
    ("梅", "mei"),
    ("兰", "lan"),
    ("菊", "ju"),
    ("竹", "zhu"),
    # Seasons (季牌)
    ("春", "chun"),
    ("夏", "xia"),
    ("秋", "qiu"),
    ("冬", "dong"),
    # Calls (spoken-calls.deck)
    ("吃", "chi"),
    ("碰", "peng"),
    ("杠", "gang"),
    ("胡", "hu"),
    ("自摸", "zimo"),
    ("听牌", "tingpai"),
]


async def main():
    outdir = os.path.join(HERE, "audio")
    os.makedirs(outdir, exist_ok=True)
    for text, slug in CARDS:
        path = os.path.join(outdir, slug + ".mp3")
        if os.path.exists(path):
            continue
        await edge_tts.Communicate(text, VOICE).save(path)
        print(slug, "←", text)


asyncio.run(main())
