"""Slice the Items sheets (already transparent-background) into game-ready PNGs:
  - tank_front.png     : the Ironclad Centurion top-down tank (trimmed)
  - perk_icons.png     : 5 square power-up icons in a horizontal strip (captions dropped)
  - weapon_icons.png   : 5 gun icons in a horizontal strip (for weapon-gate pickups)
All source art is already alpha-cut, so we only key on alpha, split by content gaps, and trim.
"""
from __future__ import annotations
import numpy as np
from PIL import Image

SRC = r"C:\Users\MiSTRFiNGA\Desktop\HiVE Swarm\assets\Items"
OUT = r"D:\Dev\HiveSwarm\assets"


def _trim(a):
    ys, xs = np.where(a[..., 3] > 20)
    if not len(xs):
        return None
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def _col_runs(a, thresh=0.02, gap=15):
    col = (a[..., 3] >= 128).mean(axis=0)
    runs, s = [], None
    for x in range(len(col)):
        if col[x] > thresh and s is None: s = x
        elif col[x] <= thresh and s is not None:
            if x - s > gap: runs.append((s, x))
            s = None
    if s is not None and len(col) - s > gap: runs.append((s, len(col)))
    return runs


def _row_runs(a, thresh=0.02, gap=8):
    row = (a[..., 3] >= 128).mean(axis=1)
    runs, s = [], None
    for y in range(len(row)):
        if row[y] > thresh and s is None: s = y
        elif row[y] <= thresh and s is not None:
            if y - s > gap: runs.append((s, y))
            s = None
    if s is not None and len(row) - s > gap: runs.append((s, len(row)))
    return runs


def tank():
    im = np.array(Image.open(fr"{SRC}\Ironclad Centurion.png").convert("RGBA"))
    t = _trim(im)
    Image.fromarray(t, "RGBA").save(fr"{OUT}\tank_front.png")
    print("tank_front.png ->", (t.shape[1], t.shape[0]))


def _pack(sprites, cell):
    strip = Image.new("RGBA", (cell * len(sprites), cell), (0, 0, 0, 0))
    for i, sp in enumerate(sprites):
        s = sp.copy(); s.thumbnail((cell - 6, cell - 6))
        strip.paste(s, (i * cell + (cell - s.width) // 2, (cell - s.height) // 2), s)
    return strip


def perk_icons(cell=128):
    im = np.array(Image.open(fr"{SRC}\Perk Icons.png").convert("RGBA"))
    sprites = []
    for (cs, ce) in _col_runs(im)[:5]:
        band = im[:, cs:ce]
        rr = _row_runs(band)
        if not rr:
            continue
        y0, y1 = rr[0]                                   # topmost block = the square icon (drop caption)
        t = _trim(band[y0:y1])
        if t is not None:
            sprites.append(Image.fromarray(t, "RGBA"))
    _pack(sprites, cell).save(fr"{OUT}\perk_icons.png")
    print("perk_icons.png ->", len(sprites), "icons")


def weapon_icons(cell=128):
    im = np.array(Image.open(fr"{SRC}\Weapons.png").convert("RGBA"))
    sprites = []
    for (cs, ce) in _col_runs(im)[:5]:                  # first 5 runs = the 5 guns
        t = _trim(im[:, cs:ce])
        if t is not None:
            sprites.append(Image.fromarray(t, "RGBA"))
    _pack(sprites, cell).save(fr"{OUT}\weapon_icons.png")
    print("weapon_icons.png ->", len(sprites), "guns")


if __name__ == "__main__":
    tank(); perk_icons(); weapon_icons()
