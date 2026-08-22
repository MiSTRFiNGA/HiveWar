"""Install repaired runner/colossus frames into Swarm source and War copies."""
from __future__ import annotations

from collections import deque
from pathlib import Path
import shutil

from PIL import Image

CELL = 256
SESS = [
    Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C%3A%5CWINDOWS%5Csystem32\01a0272f-2b8d-76c2-a7ee-27779c7bca46\images"),
    Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C%3A%5CWindows%5CSystem32\01a0272f-2b8d-76c2-a7ee-27779c7bca46\images"),
]
SWARM = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
WAR = Path(r"D:\Dev\HiveWar\assets\swarm")


def find_jpg(name: str) -> Path:
    for d in SESS:
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(name)


def key_black(im: Image.Image, lum: int = 36) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    vis = bytearray(w * h)
    q = deque()

    def idx(x, y):
        return y * w + x

    def is_bg(c):
        r, g, b, a = c
        if a < 8:
            return True
        return (r + g + b) / 3 <= lum and max(r, g, b) <= lum + 12

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
        i = idx(x, y)
        if vis[i]:
            continue
        vis[i] = 1
        if is_bg(px[x, y]):
            px[x, y] = (0, 0, 0, 0)
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def opaque_bbox(im: Image.Image):
    return im.split()[-1].getbbox()


def fit_to_cell(im: Image.Image, cell: int = CELL, fill: float = 0.90) -> Image.Image:
    bbox = opaque_bbox(im)
    if not bbox:
        return Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    crop = im.crop(bbox)
    cw, ch = crop.size
    scale = min(fill * cell / cw, fill * cell / ch)
    nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    canvas.paste(crop, ((cell - nw) // 2, cell - nh - int(cell * 0.04)), crop)
    return canvas


def neighbor_metrics(strip: Image.Image, skip: int):
    n = strip.width // CELL
    heights, feet = [], []
    for i in range(n):
        if i == skip:
            continue
        fr = strip.crop((i * CELL, 0, (i + 1) * CELL, CELL))
        bb = opaque_bbox(fr)
        if not bb:
            continue
        heights.append(bb[3] - bb[1])
        feet.append(bb[3])
    if not heights:
        return 200, CELL - 20
    heights.sort()
    feet.sort()
    return heights[len(heights) // 2], feet[len(feet) // 2]


def place_like_neighbors(keyed: Image.Image, strip: Image.Image, skip: int) -> Image.Image:
    target_h, target_foot = neighbor_metrics(strip, skip)
    bbox = opaque_bbox(keyed)
    crop = keyed.crop(bbox)
    cw, ch = crop.size
    scale = target_h / ch
    max_scale = (CELL - 8) / max(cw, ch)
    scale = min(scale, max_scale)
    nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    x = (CELL - nw) // 2
    y = max(4, min(CELL - nh - 4, target_foot - nh))
    canvas.paste(crop, (x, y), crop)
    return canvas


def patch_strip(path: Path, frame_i: int, keyed: Image.Image) -> None:
    strip = Image.open(path).convert("RGBA")
    cell = place_like_neighbors(keyed, strip, frame_i)
    strip.paste(cell, (frame_i * CELL, 0))
    strip.save(path)
    print("patched", path.name, "frame", frame_i, "bbox", opaque_bbox(cell))


def save_square(keyed: Image.Image, dest: Path, fill: float = 0.92) -> Image.Image:
    cell = fit_to_cell(keyed, CELL, fill)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cell.save(dest)
    print("wrote", dest.name, opaque_bbox(cell))
    return cell


def main() -> None:
    bak = SWARM / "_bak_art_0_6_23"
    bak.mkdir(exist_ok=True)
    for name in [
        "runner_walk_s.png",
        "runner_e.png",
        "runner_idle_e.png",
        "runner_w.png",
        "runner_idle_w.png",
        "zombie_colossus_walk_s.png",
        "zombie_colossus_walk_se.png",
        "zombie_colossus_walk_sw.png",
        "zombie_colossus_walk_e.png",
        "zombie_colossus_walk_w.png",
        "zombie_colossus_e.png",
        "zombie_colossus_w.png",
        "zombie_colossus_idle_e.png",
        "zombie_colossus_idle_w.png",
        "crawler_s.png",
        "crawler_idle_s.png",
    ]:
        src = SWARM / name
        if src.exists() and not (bak / name).exists():
            shutil.copy2(src, bak / name)

    runner_f0 = key_black(Image.open(find_jpg("12.jpg")))
    col_s_f1 = key_black(Image.open(find_jpg("14.jpg")))
    col_se_f3 = key_black(Image.open(find_jpg("11.jpg")))
    col_sw_f3 = key_black(Image.open(find_jpg("13.jpg")))
    col_e = key_black(Image.open(find_jpg("17.jpg")))
    col_e_walk = key_black(Image.open(find_jpg("18.jpg")))
    runner_e = key_black(Image.open(find_jpg("15.jpg")))

    patch_strip(SWARM / "runner_walk_s.png", 0, runner_f0)
    patch_strip(SWARM / "zombie_colossus_walk_s.png", 1, col_s_f1)
    patch_strip(SWARM / "zombie_colossus_walk_se.png", 3, col_se_f3)
    patch_strip(SWARM / "zombie_colossus_walk_sw.png", 3, col_sw_f3)

    e_idle = save_square(col_e, SWARM / "zombie_colossus_e.png")
    e_idle.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "zombie_colossus_w.png")
    if (SWARM / "zombie_colossus_idle_e.png").exists():
        idle = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
        for i in range(4):
            idle.paste(e_idle, (i * CELL, 0))
        idle.save(SWARM / "zombie_colossus_idle_e.png")
        idle.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "zombie_colossus_idle_w.png")
        print("wrote colossus idle e/w strips")

    c0 = fit_to_cell(col_e, CELL, 0.90)
    c1 = fit_to_cell(col_e_walk, CELL, 0.90)
    walk_e = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
    for i, fr in enumerate((c0, c1, c0, c1)):
        walk_e.paste(fr, (i * CELL, 0))
    walk_e.save(SWARM / "zombie_colossus_walk_e.png")
    walk_e.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "zombie_colossus_walk_w.png")
    print("wrote colossus walk e/w")

    re = save_square(runner_e, SWARM / "runner_e.png", fill=0.88)
    re.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "runner_w.png")
    if (SWARM / "runner_idle_e.png").exists():
        idle = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
        for i in range(4):
            idle.paste(re, (i * CELL, 0))
        idle.save(SWARM / "runner_idle_e.png")
        idle.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(SWARM / "runner_idle_w.png")
        print("wrote runner idle e/w")

    craw = Image.open(SWARM / "crawler_s.png").convert("RGBA")
    bb = opaque_bbox(craw)
    if bb:
        ch = bb[3] - bb[1]
        if ch < CELL * 0.55:
            save_square(craw, SWARM / "crawler_s.png", fill=0.88)
            print("upscaled crawler_s", ch, "-> fill 0.88")
            if (SWARM / "crawler_idle_s.png").exists():
                strip = Image.open(SWARM / "crawler_idle_s.png").convert("RGBA")
                n = max(1, strip.width // CELL)
                out = Image.new("RGBA", strip.size, (0, 0, 0, 0))
                cell = Image.open(SWARM / "crawler_s.png")
                for i in range(n):
                    out.paste(cell, (i * CELL, 0))
                out.save(SWARM / "crawler_idle_s.png")
                print("filled crawler_idle_s from scaled idle")

    for stem in ("runner", "zombie_colossus"):
        for d in ("s", "se", "sw"):
            src = SWARM / f"{stem}_walk_{d}.png"
            dst = WAR / f"{stem}_walk_{d}.png"
            shutil.copy2(src, dst)
            print("war copy", dst.name)

    print("DONE")


if __name__ == "__main__":
    main()
