"""Slice the labeled enemy animation sheets into game-ready horizontal strip atlases.

Keys the solid background (green for Xenoid/Psychoid/Cyber Mutant, gray for Subterra),
keeps only the largest opaque blob per cell (auto-discards baked label text), trims to
content, and packs the chosen animation frames into one horizontal strip PNG.
"""
from __future__ import annotations
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = r"C:\Users\MiSTRFiNGA\Desktop\HiVE Swarm\assets\Enemies"
OUT = r"D:\Dev\HiveSwarm\assets"


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
    return _border_flood(_green(a))                         # keep interior green (Subterra's radioactive head)


def cell_sprite(cell_rgba, keyfn):
    """Return a trimmed RGBA of just the largest creature blob in the cell,
    with the green halo eroded away and any green spill neutralised."""
    a = np.array(cell_rgba)
    bg = keyfn(a)
    a[bg, 3] = 0
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


def make_strip(sheet, region, cols, keyfn, frames, out_name, cell=128):
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
        sp = cell_sprite(cell_img, keyfn)
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
make_strip("Xenoid.png", (0.0, 0.055, 1.0, 0.30), 4, key_green, [0, 1, 2, 3], "xeno_walk.png")
# Psychoid (kind 5): 4x2 grid, swim loop = row 0 frames 0-3
make_strip("Psychoid.png", (0.0, 0.06, 1.0, 0.50), 4, key_green, [0, 1, 2, 3], "psychoid_swim.png")
# Cyber Mutant (kind 2): top idle row = 4 frames across the top
make_strip("Cyber Mutant.png", (0.0, 0.015, 1.0, 0.185), 4, key_green, [0, 1, 2, 3], "cyber_idle.png")
# Subterra (burrower, kind 4): scanning row = 5 frames (head weaving); gray-keyed
make_strip("Subterra.png", (0.0, 0.365, 1.0, 0.55), 5, key_green_flood, [0, 1, 2, 3, 4], "subterra_scan.png")
