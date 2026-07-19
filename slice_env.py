"""Slice per-level environment art from Eric's Desktop breakdown sheets into assets/env/.

Each 'Level N.png' sheet contains three labeled panels:
  bg   — horizon/backdrop strip (anchors on the game horizon)
  path — 4-wide road tile segment (perspective-tiled down the highway)
  side — vertical wall panel (pattern-fills the off-road areas)

Crop boxes are hand-picked per sheet (they were AI-composited with different layouts).
Outputs: assets/env/L{n}_{bg,path,side}.png  (bg max 1080 wide, tiles max 512).
Also copies the standalone shared tilesets into assets/env/shared/.
"""
import os
from PIL import Image

SRC = r"C:\Users\MiSTRFiNGA\Desktop\HiVE Swarm\assets\Environment"
DST = r"D:\Dev\HiveSwarm\assets\env"

# level: {slot: (file, (l, t, r, b))}  in original pixel coords
CROPS = {
    1: {"bg":   ("Level 1.png", (1912, 168, 2904, 684)),
        "path": ("Level 1.png", (3002, 260, 3436, 556)),
        "side": ("Level 1.png", (3738, 216, 3962, 700))},
    2: {"bg":   ("Level 2.png", (1358, 180, 1962, 541)),
        "path": ("Level 2.png", (1360, 639, 1969, 793)),
        "side": ("Level 2.png", (1360, 901, 1506, 1262))},
    3: {"bg":   ("Level 3.png", (1590, 166, 2679, 769)),
        "path": ("Level 3.png", (1509, 931, 2432, 1241)),
        "side": ("Level 3.png", (2373, 825, 2721, 1417))},
    4: {"bg":   ("Level 4.png", (1586, 162, 2704, 773)),
        "path": ("Level 4.png", (1506, 931, 2298, 1255)),
        "side": ("Level 4.png", (2373, 825, 2721, 1424))},
    5: {"bg":   ("Level 5.png", (1587, 166, 2260, 545)),
        "path": ("Level 5.png", (1587, 780, 2260, 1283)),
        "side": ("Level 5.png", (2309, 166, 2708, 1283))},
    6: {"bg":   ("Level 6.png", (1908, 121, 2695, 500)),
        "path": ("Level 6.png", (1898, 697, 2695, 897)),
        "side": ("Level 6.png", (1900, 1065, 2640, 1378))},
    7: {"bg":   ("Level 7.png", (1428, 104, 2018, 455)),
        "path": ("Level 7.png", (1435, 683, 2018, 876)),
        "side": ("Level 7.png", (1499, 1076, 1946, 1489))},
    8: {"bg":   ("Level 8.png", (2252, 200, 2721, 469)),
        "path": ("Level 8.png", (2252, 628, 2721, 780)),
        "side": ("Level 8.png", (2312, 869, 2721, 1525))},
    9: {"bg":   ("Level 9.png", (2217, 204, 2785, 522)),
        "path": ("Level 9.png", (2226, 731, 2776, 889)),
        "side": ("Level 9.png", (2392, 1119, 2722, 1493))},
    10: {"bg":  ("Level 10.png", (2139, 179, 2739, 497)),
         "path": ("Level 10.png", (1777, 676, 2725, 883)),
         "side": ("Level 10.png", (2056, 1007, 2745, 1532))},
}

SHARED = ["Tile_cyber01.png", "Tile_Hive01.png", "Wall_City01.png", "Wall_Hive01.png"]
MAX = {"bg": 1080, "path": 512, "side": 512}


def shrink(im, cap):
    w, h = im.size
    m = max(w, h)
    if m <= cap:
        return im
    s = cap / m
    return im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)


def main():
    os.makedirs(DST, exist_ok=True)
    cache = {}
    for lvl, slots in sorted(CROPS.items()):
        for slot, (fname, box) in slots.items():
            if fname not in cache:
                cache[fname] = Image.open(os.path.join(SRC, fname)).convert("RGB")
            im = cache[fname]
            l, t, r, b = box
            r, b = min(r, im.width), min(b, im.height)
            crop = shrink(im.crop((l, t, r, b)), MAX[slot])
            out = os.path.join(DST, f"L{lvl}_{slot}.png")
            crop.save(out)
            print(f"L{lvl}_{slot}.png  {crop.size[0]}x{crop.size[1]}")
    shared_dir = os.path.join(DST, "shared")
    os.makedirs(shared_dir, exist_ok=True)
    for f in SHARED:
        Image.open(os.path.join(SRC, f)).save(os.path.join(shared_dir, f))
        print(f"shared/{f}")


if __name__ == "__main__":
    main()
