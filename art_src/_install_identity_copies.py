"""Unify leftover identity breaks by copying the good facing onto the broken ones.

Crawler: skull-hopper S is the live identity; SE/E/W were a skeletal dog.
Praetorian: SE/NE stills and walks were shattered claws.
Runner idle_s was a side-run strip — standing front belongs there.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
import shutil

from PIL import Image

CELL = 256
SWARM = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
WAR = Path(r"D:\Dev\HiveWar\assets\swarm")
SESS = [
    Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C%3A%5CWINDOWS%5Csystem32\01a0272f-2b8d-76c2-a7ee-27779c7bca46\images"),
    Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C%3A%5CWindows%5CSystem32\01a0272f-2b8d-76c2-a7ee-27779c7bca46\images"),
]
DIRS8 = ("s", "se", "sw", "e", "w", "n", "ne", "nw")


def find_jpg(name: str) -> Path:
    for d in SESS:
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


def key_black(im: Image.Image, lum: int = 28) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    vis = bytearray(w * h)
    q = deque()

    def is_bg(c):
        r, g, b, a = c
        if a < 8:
            return True
        return (r + g + b) / 3 <= lum and max(r, g, b) <= lum + 10

    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        i = y * w + x
        if vis[i]:
            continue
        vis[i] = 1
        if is_bg(px[x, y]):
            px[x, y] = (0, 0, 0, 0)
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def opaque_bbox(im: Image.Image):
    return im.split()[-1].getbbox()


def fit_cell(im: Image.Image, fill: float = 0.90) -> Image.Image:
    bbox = opaque_bbox(im)
    if not bbox:
        return Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    crop = im.crop(bbox)
    cw, ch = crop.size
    scale = min(fill * CELL / cw, fill * CELL / ch)
    nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    canvas.paste(crop, ((CELL - nw) // 2, CELL - nh - int(CELL * 0.04)), crop)
    return canvas


def strip4(cell: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
    for i in range(4):
        out.paste(cell, (i * CELL, 0))
    return out


def strip_two_pose(a: Image.Image, b: Image.Image) -> Image.Image:
    out = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
    for i, fr in enumerate((a, b, a, b)):
        out.paste(fr, (i * CELL, 0))
    return out


def copy_over(src: Path, dst: Path) -> None:
    if not src.exists():
        print("missing src", src.name)
        return
    shutil.copy2(src, dst)
    print("copy", src.name, "->", dst.name)


def main() -> None:
    # --- crawler: hopper S is canonical ---
    for state, src_name in (
        ("", "crawler_s.png"),
        ("idle_", "crawler_idle_s.png"),
        ("walk_", "crawler_walk_s.png"),
        ("attack_", "crawler_attack_s.png"),
    ):
        src = SWARM / f"crawler_{state}s.png" if state else SWARM / "crawler_s.png"
        src = SWARM / src_name
        if not src.exists():
            print("skip missing", src_name)
            continue
        for d in DIRS8:
            if d == "s":
                continue
            if state:
                dst = SWARM / f"crawler_{state}{d}.png"
            else:
                dst = SWARM / f"crawler_{d}.png"
            copy_over(src, dst)
        copy_over(src, SWARM / src_name.replace("_s", ""))  # un-suffixed aliases

    for d in ("s", "se", "sw"):
        copy_over(SWARM / f"crawler_walk_{d}.png", WAR / f"crawler_walk_{d}.png")

    # hopper side profile from Imagine, for E/W only (360 game needs a side)
    stand = fit_cell(key_black(Image.open(find_jpg("24.jpg"))))
    step = fit_cell(key_black(Image.open(find_jpg("23.jpg"))))
    stand.save(SWARM / "crawler_e.png")
    stand.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "crawler_w.png")
    strip4(stand).save(SWARM / "crawler_idle_e.png")
    strip4(stand).transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "crawler_idle_w.png")
    strip_two_pose(stand, step).save(SWARM / "crawler_walk_e.png")
    strip_two_pose(stand, step).transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "crawler_walk_w.png")
    print("wrote crawler e/w hopper profile")

    # --- runner idle facing camera ---
    front = Image.open(SWARM / "runner_s.png").convert("RGBA")
    if front.size != (CELL, CELL):
        front = fit_cell(front)
    strip4(front).save(SWARM / "runner_idle_s.png")
    back = Image.open(SWARM / "runner_n.png").convert("RGBA")
    if back.size != (CELL, CELL):
        back = fit_cell(back)
    strip4(back).save(SWARM / "runner_idle_n.png")
    print("wrote runner idle s/n standing")

    # --- praetorian shattered SE/NE ---
    for state, good_s, good_n, dests_s, dests_n in (
        ("", "praetorian_s.png", "praetorian_n.png", ("se", "sw"), ("ne", "nw")),
        ("idle_", "praetorian_idle_s.png", "praetorian_idle_n.png", ("se", "sw"), ("ne", "nw")),
        ("walk_", "praetorian_walk_s.png", "praetorian_walk_n.png", ("se", "sw"), ("ne", "nw")),
        ("attack_", "praetorian_attack_s.png", "praetorian_attack_n.png", ("se", "sw"), ("ne", "nw")),
    ):
        for d in dests_s:
            name = f"praetorian_{state}{d}.png" if state else f"praetorian_{d}.png"
            copy_over(SWARM / good_s, SWARM / name)
        for d in dests_n:
            name = f"praetorian_{state}{d}.png" if state else f"praetorian_{d}.png"
            copy_over(SWARM / good_n, SWARM / name)

    print("DONE")


if __name__ == "__main__":
    main()
