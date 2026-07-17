"""Slice the labeled enemy animation sheets into game-ready horizontal strip atlases.

Keys the solid background (green for Xenoid/Psychoid/Cyber Mutant, gray for Subterra),
keeps only the largest opaque blob per cell (auto-discards baked label text), trims to
content, and packs the chosen animation frames into one horizontal strip PNG.
"""
from __future__ import annotations
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = r"C:\Users\MiSTRFiNGA\Desktop\HiVE Swarm\assets"
OUT = r"D:\Dev\HiveSwarm\assets"
E = "Enemies\\"          # enemy sheets live in the Enemies subfolder


def _border_flood(mask):
    """Keep only mask regions connected to the cell border (= the background),
    so interior same-colored accents (green heads, glowing legs) survive."""
    lbl, n = ndimage.label(mask)
    if n == 0:
        return mask
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    return np.isin(lbl, list(border))


def _green(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    return (g > 100) & (g - r > 30) & (g - b > 30)


def key_green(a):
    return _green(a)                                        # remove ALL green (no intentional green on creature)


def key_green_flood(a):
    return _border_flood(_green(a))                         # keep interior green (Subterra head, Xenoptera core)


def key_dark(a):                                            # tight key on the (48,58,67) panel + existing alpha
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    already = a[..., 3] < 200
    panel = (abs(r - 48) < 16) & (abs(g - 58) < 16) & (abs(b - 67) < 18)  # only the flat panel colour
    return already | panel                                  # soldier's dark joints (not this exact hue) stay connected


def cell_sprite(cell_rgba, keyfn, largest=True):
    """Return a trimmed RGBA of the cell's content. largest=True keeps only the
    biggest blob (drops labels/insets) + erodes the color halo; largest=False just
    keys + trims (for sheets that are already clean / would fragment)."""
    a = np.array(cell_rgba)
    bg = keyfn(a)
    a[bg, 3] = 0
    if not largest:
        ys, xs = np.where(a[..., 3] > 0)
        if len(xs) == 0:
            return None
        return Image.fromarray(a, "RGBA").crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    opaque = a[..., 3] > 0
    lbl, n = ndimage.label(opaque)
    if n == 0:
        return None
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    keep = int(np.argmax(sizes)) + 1                        # largest blob = the creature
    mask = (lbl == keep)
    mask = ndimage.binary_erosion(mask, iterations=2)       # shave the anti-aliased green halo
    a[~mask, 3] = 0
    # green de-spill ONLY on the outer edge ring (interior green accents like the
    # Subterra head are far from the boundary and stay untouched)
    edge = mask & ~ndimage.binary_erosion(mask, iterations=2)
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    spill = edge & (g > r + 12) & (g > b + 12)
    a[spill, 1] = np.maximum(r[spill], b[spill]).astype(np.uint8)
    ys, xs = np.where(a[..., 3] > 0)
    if len(xs) == 0:
        return None
    img = Image.fromarray(a, "RGBA").crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return img


def auto_strip(sheet, region, keyfn, out_name, take=None, cell=128, minw=40):
    """Auto-detect frames in a row band by background gaps (for irregular sheets).
    region=(x0,y0,x1,y1) fractional; take=list of frame indices to keep (None=all)."""
    im = Image.open(fr"{SRC}\{sheet}").convert("RGBA")
    W, H = im.size
    x0, y0, x1, y1 = int(region[0]*W), int(region[1]*H), int(region[2]*W), int(region[3]*H)
    band = np.array(im.crop((x0, y0, x1, y1)))
    bg = keyfn(band)
    colhas = (~bg).sum(axis=0) > (band.shape[0] * 0.06)      # columns with real content
    # find runs of content
    runs, s = [], None
    for x in range(len(colhas)):
        if colhas[x] and s is None: s = x
        elif not colhas[x] and s is not None:
            if x - s >= minw: runs.append((s, x)); s = None
            else: s = None
    if s is not None and len(colhas) - s >= minw: runs.append((s, len(colhas)))
    sprites = []
    for idx, (cs, ce) in enumerate(runs):
        if take is not None and idx not in take: continue
        cell_img = Image.fromarray(band[:, cs:ce])
        sp = cell_sprite(cell_img, keyfn, True)
        if sp: sprites.append(sp)
    if not sprites:
        print("NO SPRITES for", out_name, "(runs=", len(runs), ")"); return
    strip = Image.new("RGBA", (cell*len(sprites), cell), (0,0,0,0))
    for i, sp in enumerate(sprites):
        s2 = sp.copy(); s2.thumbnail((cell-8, cell-8))
        strip.paste(s2, (i*cell+(cell-s2.width)//2, (cell-s2.height)//2), s2)
    strip.save(fr"{OUT}\{out_name}")
    print(f"{out_name}: {len(sprites)}/{len(runs)} frames -> {strip.size}")


def make_strip(sheet, region, cols, keyfn, frames, out_name, cell=128, largest=True):
    """region=(x0,y0,x1,y1) fractional box holding the frame ROW(s); cols=frames across."""
    im = Image.open(fr"{SRC}\{sheet}").convert("RGBA")
    W, H = im.size
    x0, y0, x1, y1 = int(region[0] * W), int(region[1] * H), int(region[2] * W), int(region[3] * H)
    cw = (x1 - x0) / cols
    sprites = []
    for i in frames:
        cx0 = int(x0 + (i % cols) * cw); cx1 = int(x0 + (i % cols + 1) * cw)
        row = i // cols
        rh = (y1 - y0)                                       # single-row region
        cell_img = im.crop((cx0 + 4, y0 + 4, cx1 - 4, y1 - 4))
        sp = cell_sprite(cell_img, keyfn, largest)
        if sp: sprites.append(sp)
    if not sprites:
        print("NO SPRITES for", out_name); return
    strip = Image.new("RGBA", (cell * len(sprites), cell), (0, 0, 0, 0))
    for i, sp in enumerate(sprites):
        s = sp.copy(); s.thumbnail((cell - 8, cell - 8))
        strip.paste(s, (i * cell + (cell - s.width) // 2, (cell - s.height) // 2), s)
    strip.save(fr"{OUT}\{out_name}")
    print(f"{out_name}: {len(sprites)} frames -> {strip.size}")


# Xenoid (biomorph, kind 0): 4x4 grid, walk cycle = row 0 frames 0-3
make_strip(E+"Xenoid.png", (0.0, 0.055, 1.0, 0.30), 4, key_green, [0, 1, 2, 3], "xeno_walk.png")
# Psychoid (kind 5): 4x2 grid, swim loop = row 0 frames 0-3
make_strip(E+"Psychoid.png", (0.0, 0.06, 1.0, 0.50), 4, key_green, [0, 1, 2, 3], "psychoid_swim.png")
# Cyber Mutant (kind 2): top idle row = 4 frames — taller band so the LEGS aren't cut off
make_strip(E+"Cyber Mutant.png", (0.0, 0.012, 1.0, 0.27), 4, key_green, [0, 1, 2, 3], "cyber_idle.png")
# Eldritch Sponge (kind 1): auto-detect top-row frames, take idle + ooze (first 4) as the loop
auto_strip(E+"Eldritch Sponge.png", (0.0, 0.05, 1.0, 0.52), key_green, "eldritch_ooze.png", take=[0,1,2,3])
# Subterra (burrower, kind 4): scanning row = 5 frames (head weaving); gray-keyed
make_strip(E+"Subterra.png", (0.0, 0.365, 1.0, 0.55), 5, key_green_flood, [0, 1, 2, 3, 4], "subterra_scan.png")
# Xenoptera (winged, kind 3): flight loop = top row 4 frames (green bg + green core -> flood)
make_strip(E+"Xenoptera.png", (0.0, 0.06, 1.0, 0.34), 4, key_green_flood, [0, 1, 2, 3], "xenoptera_fly.png")
# Player soldier (rear view): shooting loop = top row 4 frames (dark bg -> flood)
make_strip("Player soilders.png", (0.0, 0.045, 1.0, 0.33), 4, key_dark, [0, 1, 2, 3], "soldier_fire.png")
# Praetorian mini-boss ANIMATIONS (green bg + green eyes -> flood): idle / attack / death rows
auto_strip(E+"Mini boss Praetorian.png", (0.0, 0.015, 1.0, 0.205), key_green_flood, "praet_idle.png",   cell=192, minw=120)
auto_strip(E+"Mini boss Praetorian.png", (0.0, 0.225, 1.0, 0.395), key_green_flood, "praet_attack.png", cell=192, minw=120)
auto_strip(E+"Mini boss Praetorian.png", (0.0, 0.775, 1.0, 0.99),  key_green_flood, "praet_death.png",  cell=192, minw=120)
# Bosses: one clean hero frame each (green bg + green core -> flood)
make_strip("Enemies\\Mini boss Praetorian.png", (0.0, 0.06, 0.5, 0.55), 1, key_green_flood, [0], "praetorian_hero.png", cell=192)
make_strip("Enemies\\Alien  Queen.png", (0.30, 0.10, 0.70, 0.95), 1, key_green_flood, [0], "queen_hero.png", cell=224)
