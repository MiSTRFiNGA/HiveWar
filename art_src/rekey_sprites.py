"""
HiVE WAR — sprite re-keying tool (2026-08-07).

THE DEFECT THIS FIXES
---------------------
The existing sprites were keyed against *pure black*. But the source art sits on a
dark grey panel around RGB(42..47). So the key only bit where the panel happened to
be darkest, leaving opaque slabs behind in some cells and not others:

    weapon_icons.png  cell0/1 corners -> (0,0,0,0)        keyed clean
                      cell3   corners -> (45,45,44,255)   panel survived
                      cell4   corners -> (47,47,47,255)   panel survived

Second defect: every re-keyed sprite has **0.00% semi-transparent pixels** — the
alpha is binary, so edges are hard-cut and alias badly at any scale. Sprites that
went through a better path (hive_brute_walk 7.2% semi, xenoptera_fly 2.7%) look
noticeably smoother in game.

THE FIX — three passes, in this order:
  1. `key_background`  flood-fill from the BORDERS only, with tolerance.
     Border-connected means interior dark detail (outlines, shading, the gun's own
     black body) is never touched. A global colour key cannot make that distinction
     and is what punches holes in sprites.
  2. `feather_edges`   1px anti-aliased alpha rim, so edges stop being jagged.
  3. `decontaminate`   un-mix the dark panel colour out of edge pixels, which
     otherwise leaves a dirty grey halo when composited on a light background.

Non-destructive: writes to an output dir, never overwrites the source.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

DEFAULT_TOLERANCE = 60      # covers the RGB(42..47) panel with headroom
FEATHER_RADIUS = 1


def _border_seeds(h: int, w: int):
    for x in range(w):
        yield 0, x
        yield h - 1, x
    for y in range(h):
        yield y, 0
        yield y, w - 1


def has_opaque_panel(rgba: np.ndarray) -> bool:
    """True only if this image actually still has a solid background to remove.

    Most of these sprites are ALREADY correctly keyed — their only defect is hard
    binary alpha. Running a flood-fill on them is actively destructive: the art is
    near-black, so a dark-background fill reaches straight into the silhouette and
    eats it (measured: xeno_walk 38.99% -> 6.77% opaque). Only touch an image whose
    border ring is genuinely opaque.
    """
    a = rgba[..., 3]
    ring = np.concatenate([a[0, :], a[-1, :], a[:, 0], a[:, -1]])
    return (ring > 250).mean() > 0.25


def key_background(rgba: np.ndarray, tolerance: int = DEFAULT_TOLERANCE) -> np.ndarray:
    """Flood-fill transparency inward from the borders.

    Only background reachable from an edge is removed, so dark pixels *inside* the
    silhouette survive. No-ops when there is no opaque panel to remove. Returns a
    new array; the input is not modified.
    """
    out = rgba.copy()
    if not has_opaque_panel(out):
        return out
    h, w = out.shape[:2]
    rgb = out[..., :3].astype(np.int16)

    # Seed colour = median of the OPAQUE border pixels only. Including transparent
    # border pixels drags the median to (0,0,0) and turns this into a black key.
    ring = np.concatenate([rgb[0, :], rgb[-1, :], rgb[:, 0], rgb[:, -1]])
    ring_a = np.concatenate([out[0, :, 3], out[-1, :, 3], out[:, 0, 3], out[:, -1, 3]])
    opaque_ring = ring[ring_a > 250]
    if opaque_ring.size == 0:
        return out
    bg = np.median(opaque_ring, axis=0)

    close = (np.abs(rgb - bg).max(axis=2) <= tolerance) | (out[..., 3] <= 10)
    seen = np.zeros((h, w), dtype=bool)
    dq: deque = deque()
    for y, x in _border_seeds(h, w):
        if close[y, x] and not seen[y, x]:
            seen[y, x] = True
            dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and close[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                dq.append((ny, nx))

    out[..., 3] = np.where(seen, 0, out[..., 3])
    return out


def feather_edges(rgba: np.ndarray, radius: int = FEATHER_RADIUS) -> np.ndarray:
    """Give the alpha a soft rim so edges stop aliasing.

    Box-blurs alpha, then keeps the blurred value only where it is *lower* than the
    original. That softens the outside boundary without eroding solid interior.
    """
    out = rgba.copy()
    a = out[..., 3].astype(np.float32)
    k = radius * 2 + 1
    pad = np.pad(a, radius, mode="edge")
    acc = np.zeros_like(a)
    for dy in range(k):
        for dx in range(k):
            acc += pad[dy:dy + a.shape[0], dx:dx + a.shape[1]]
    blurred = acc / (k * k)
    out[..., 3] = np.minimum(a, blurred).astype(np.uint8)
    return out


def decontaminate(rgba: np.ndarray, tolerance: int = DEFAULT_TOLERANCE) -> np.ndarray:
    """Push edge pixels away from the background colour.

    Partially transparent edge pixels are a *mix* of sprite and panel. Left alone
    they read as a grey halo. Nudging them toward the nearest opaque neighbour's
    colour is cheap and removes the fringe.
    """
    out = rgba.copy()
    a = out[..., 3]
    edge = (a > 10) & (a < 250)
    if not edge.any():
        return out
    rgb = out[..., :3].astype(np.float32)
    solid = (a >= 250).astype(np.float32)
    acc = np.zeros_like(rgb)
    wsum = np.zeros(a.shape, dtype=np.float32)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sr = np.roll(np.roll(rgb, dy, axis=0), dx, axis=1)
        sw = np.roll(np.roll(solid, dy, axis=0), dx, axis=1)
        acc += sr * sw[..., None]
        wsum += sw
    have = wsum > 0
    fix = edge & have
    out[..., :3][fix] = (acc[fix] / wsum[fix][..., None]).astype(np.uint8)
    return out


def is_magenta_keyed(rgba: np.ndarray) -> float:
    """Fraction of VISIBLE pixels that are chroma magenta.

    Several sheets shipped with the magenta backdrop never removed at all —
    measured: hive_runner_walk 64.61%, hive_zombie_colossus_walk 54.86%. Those
    render in game as a bright pink box around the character.
    """
    a = rgba[..., 3]
    vis = a > 10
    if not vis.any():
        return 0.0
    r, g, b = (rgba[..., i].astype(int) for i in range(3))
    mag = vis & (r > 120) & (b > 120) & (g < r - 60) & (g < b - 60)
    return mag.sum() / vis.sum() * 100


def key_chroma_magenta(rgba: np.ndarray, despill: bool = True) -> np.ndarray:
    """Remove a magenta chroma backdrop and despill the residual pink rim.

    Magenta is well separated from this art (greenish zombies, teal tech), so a
    global colour key is safe here — unlike the dark-grey weapon panels, where the
    background and the gun body are the same luminance and no colour key can
    separate them.
    """
    out = rgba.copy()
    r, g, b = (out[..., i].astype(int) for i in range(3))
    mag = (r > 110) & (b > 110) & (g < r - 45) & (g < b - 45)
    out[..., 3] = np.where(mag, 0, out[..., 3])
    if despill:
        # Edge pixels keep a pink cast: clamp G's deficit relative to R/B.
        a = out[..., 3]
        edge = a > 10
        rr, gg, bb = (out[..., i].astype(np.int16) for i in range(3))
        spill = edge & (gg < np.minimum(rr, bb) - 25)
        cap = ((rr + bb) // 2).astype(np.int16)
        newg = np.where(spill, np.minimum(cap, gg + 40), gg)
        out[..., 1] = np.clip(newg, 0, 255).astype(np.uint8)
    return out


def keep_largest_per_cell(rgba: np.ndarray, cell: int) -> np.ndarray:
    """Within each cell, keep only the biggest connected blob.

    Drops baked-in title text and stray specks that survive the chroma key.
    """
    out = rgba.copy()
    h, w = out.shape[:2]
    for c0 in range(0, w, cell):
        c1 = min(c0 + cell, w)
        sub = out[:, c0:c1, 3]
        vis = sub > 10
        seen = np.zeros_like(vis)
        best, best_n = None, 0
        for sy in range(vis.shape[0]):
            for sx in range(vis.shape[1]):
                if not vis[sy, sx] or seen[sy, sx]:
                    continue
                comp, dq = [], deque([(sy, sx)])
                seen[sy, sx] = True
                while dq:
                    y, x = dq.popleft()
                    comp.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < vis.shape[0] and 0 <= nx < vis.shape[1]
                                and vis[ny, nx] and not seen[ny, nx]):
                            seen[ny, nx] = True
                            dq.append((ny, nx))
                if len(comp) > best_n:
                    best, best_n = comp, len(comp)
        if best is None:
            continue
        keep = np.zeros_like(vis)
        for y, x in best:
            keep[y, x] = True
        sub[~keep] = 0
    return out


def stats(rgba: np.ndarray) -> dict:
    a = rgba[..., 3]
    tot = a.size
    return {
        "opaque%": round((a > 250).sum() / tot * 100, 2),
        "semi%": round(((a > 10) & (a <= 250)).sum() / tot * 100, 2),
        "transparent%": round((a <= 10).sum() / tot * 100, 2),
    }


def process(src: Path, dest: Path, tolerance: int = DEFAULT_TOLERANCE,
            cell: int = 0) -> dict:
    before = np.array(Image.open(src).convert("RGBA"))
    mag_pct = is_magenta_keyed(before)

    if mag_pct > 15:
        # A real un-keyed chroma backdrop. Key it, then drop the baked-in title
        # text by keeping only the largest blob per cell.
        after = key_chroma_magenta(before)
        if cell:
            after = keep_largest_per_cell(after, cell)
        mode = f"chroma-magenta ({mag_pct:.1f}% magenta)"
    else:
        after = key_background(before, tolerance)
        mode = "panel-key" if has_opaque_panel(before) else "feather-only"

    after = decontaminate(feather_edges(after), tolerance)
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(after, "RGBA").save(dest)
    return {"file": src.name, "mode": mode,
            "before": stats(before), "after": stats(after),
            "magenta_before": round(mag_pct, 2),
            "magenta_after": round(is_magenta_keyed(after), 2)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-key HiVE WAR sprites (non-destructive).")
    ap.add_argument("sources", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, required=True, help="output DIRECTORY")
    ap.add_argument("--tolerance", type=int, default=DEFAULT_TOLERANCE)
    ap.add_argument("--cell", type=int, default=0, help="sprite cell width, enables title-text removal")
    args = ap.parse_args()

    for src in args.sources:
        r = process(src, args.out / src.name, args.tolerance, args.cell)
        b, a = r["before"], r["after"]
        print(f"{r['file']:30} [{r['mode']:28}] "
              f"semi {b['semi%']:5}->{a['semi%']:5} | "
              f"magenta {r['magenta_before']:5}%->{r['magenta_after']:5}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# ── APPLIED 2026-08-07 ────────────────────────────────────────────────────────
# Six sheets shipped with the magenta chroma backdrop NEVER removed — they
# rendered in game as a bright pink box around the character, including the
# PLAYER. Measured magenta-as-%-of-visible before -> after:
#
#   hive_player_walk.png            69.6% -> 0.0%   <- the player character
#   hive_necro_node_walk.png        69.4% -> 0.0%
#   hive_runner_walk.png            64.6% -> 0.0%
#   hive_zombie_colossus_walk.png   54.9% -> 0.0%
#   hive_armored_dead_walk.png      53.3% -> 0.0%
#   hive_mutant_enforcer_walk.png   39.2% -> 0.0%
#
# Originals backed up to assets/_bak_pre_rekey_20260807/.
#
# NOT FIXED — weapon_icons.png. Its background is a dark grey panel at the SAME
# luminance as the gun bodies. Every colour key that removes the panel also eats
# the gun (measured: 38.6% -> 5.2% opaque, guns reduced to teal fragments). No
# automated key can separate them. That sheet needs re-generating on a contrasting
# background, or hand-masking.
