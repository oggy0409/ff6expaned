"""Find a source sprite (indexed PNG + palette.json) in an emulator frame and compare every opaque pixel
(colours compared at SNES 5-bit precision). Dev/QA evidence tool."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ff6x.png import read_indexed
from ff6x.enemygfx import parse_color


def load_sprite(folder):
    w, h, rows, _ = read_indexed(os.path.join(folder, "sprite.png"))
    pal = [parse_color(c) for c in json.load(open(os.path.join(folder, "palette.json")))["colors"]]
    idx = np.array(rows)
    rgb = np.array([[pal[v] for v in r] for r in rows], dtype=np.int32) >> 3
    return idx, rgb


def find(screen, idx, rgb, region=(0, 0, 256, 150)):
    scr = (np.asarray(screen, dtype=np.int32) >> 3)
    h, w = idx.shape
    mask = idx != 0
    best = None
    x0, y0, x1, y1 = region
    for y in range(y0, y1 - h + 1):
        for x in range(x0, x1 - w + 1):
            win = scr[y:y + h, x:x + w]
            bad = int(np.any(win != rgb, axis=2)[mask].sum())
            if best is None or bad < best[0]:
                best = (bad, x, y)
                if bad == 0:
                    return {"x": x, "y": y, "opaque_px": int(mask.sum()), "mismatched_px": 0}
    return {"x": best[1], "y": best[2], "opaque_px": int(mask.sum()), "mismatched_px": best[0]}
