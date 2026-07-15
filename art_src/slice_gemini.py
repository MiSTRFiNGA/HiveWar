"""Slice HiVE SWARM sprites out of the Gemini realistic asset sheet (xwuxhb...)
and alpha-key them by flood-filling the flat dark background from the borders."""
from PIL import Image
from collections import deque
import os

SHEET = os.path.join(os.path.dirname(__file__), "gemini", "Gemini_Generated_Image_xwuxhbxwuxhbxwux.png")
OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)

# crop boxes in original 2816x1536 coords: name -> (l, t, r, b)
BOXES = {
    "soldier_front":  (63, 190, 317, 514),      # temp — back view coming from Eric
    "tank_front":     (789, 169, 1239, 479),    # temp — rear view coming from Eric
    "biomorph_a":     (1338, 176, 1591, 507),
    "biomorph_b":     (1591, 176, 1830, 507),
    "cyber_a":        (1845, 169, 2098, 507),
    "cyber_b":        (2098, 169, 2337, 500),
    "burrower":       (2535, 197, 2809, 514),
    "eldritch":       (35, 648, 465, 986),
    "praetorian":     (472, 627, 810, 1000),
    "winged":         (831, 620, 1225, 986),
    "tile_highway":   (28, 1120, 422, 1500),    # kept opaque (ground tile)
    "parallax_city":  (1338, 1113, 2464, 1239), # kept opaque (backdrop strip)
}
OPAQUE = {"tile_highway", "parallax_city"}
TOL = 26  # per-channel tolerance for background match


def key_bg(im):
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    # background reference = median-ish of the 4 corners
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    br = sum(c[0] for c in corners) // 4
    bg = (br, sum(c[1] for c in corners) // 4, sum(c[2] for c in corners) // 4)

    def is_bg(p):
        return abs(p[0] - bg[0]) <= TOL and abs(p[1] - bg[1]) <= TOL and abs(p[2] - bg[2]) <= TOL

    seen = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(px[x, y]) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(px[x, y]) and not seen[y][x]:
                seen[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and is_bg(px[nx, ny]):
                seen[ny][nx] = True
                q.append((nx, ny))
    return im


def keep_main_component(im, keep_frac=0.10):
    """Erase opaque islands smaller than keep_frac of the largest one (neighbor-sprite fragments)."""
    w, h = im.size
    px = im.load()
    label = [[0] * w for _ in range(h)]
    comps = []
    for y0 in range(h):
        for x0 in range(w):
            if label[y0][x0] == 0 and px[x0, y0][3] > 0:
                cid = len(comps) + 1
                cells = []
                q = deque([(x0, y0)])
                label[y0][x0] = cid
                while q:
                    x, y = q.popleft()
                    cells.append((x, y))
                    for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                        if 0 <= nx < w and 0 <= ny < h and label[ny][nx] == 0 and px[nx, ny][3] > 0:
                            label[ny][nx] = cid
                            q.append((nx, ny))
                comps.append(cells)
    if not comps:
        return im
    biggest = max(len(c) for c in comps)
    for cells in comps:
        if len(cells) < biggest * keep_frac:
            for x, y in cells:
                px[x, y] = (0, 0, 0, 0)
    return im


def autocrop(im):
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


def main():
    sheet = Image.open(SHEET)
    for name, box in BOXES.items():
        im = sheet.crop(box)
        if name not in OPAQUE:
            im = key_bg(im)
            im = keep_main_component(im)
            im = autocrop(im)
        path = os.path.join(OUT, f"{name}.png")
        im.save(path)
        print(name, im.size, "->", path)


if __name__ == "__main__":
    main()
