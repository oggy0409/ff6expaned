#!/usr/bin/env python3
"""ART ASSET GATE v1.0 exporter (read-only: no ROM byte is written).

Exports the visual source material of map $1A2 (Vector Outer Ward, Celes enabler map) and vanilla FFVI reference crops
for a human art pass. Every number comes from ROM data decoded by ff6x/fieldgfx.py, and the $1A2 data is verified
against the running game (bsnes capture by tools/art_gate_capture_v10.py: VRAM, CGRAM, tileset WRAM, BG1 buffer,
screenshots of the four E8 states).

usage: art_gate_v10.py <qa.sfc> <clean Rev1.sfc> <capture dir> <out dir>
       art_gate_v10.py --previews <clean Rev1.sfc> <out dir> <map hex> ...   (full-map previews only)
"""
import json, os, sys, hashlib
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ff6x import fieldgfx as F
from ff6x.hirom import snes_to_pc
from ff6x.mapsrc import load_tileprops

REF = "/home/claude/ref/ff6/src"            # names only (enum labels); every value is read from the ROM
QA_SUBTILEMAP_PTRS = 0xF78400               # MAPX_SUBTILEMAP_PTRS (data/allocations.json)
MAP = 0x1A2
ENGINE_COLOURS = {1, 2, 3} | set(range(121, 128))
STATES_JSON = os.path.join(HERE, "maps", "celes_outer_v092", "states.json")
CANDIDATES_JSON = os.path.join(HERE, "art", "vanilla_reference_candidates_v1.0.json")


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def enum_names(path, name):
    out, on = [], False
    for line in open(path):
        s = line.split(";")[0].strip()
        if s.startswith(".enum " + name) and s.split()[1] == name:
            on = True
            continue
        if on:
            if not s:
                continue
            if s.startswith(("COUNT", ".endenum")):
                break
            if "=" in s:
                continue
            out.append(s)
    return out


def names():
    try:
        return {"layout": enum_names(f"{REF}/field/sub_tilemap.inc", "SUB_TILEMAP"),
                "tileset": enum_names(f"{REF}/field/map_tileset.inc", "MAP_TILESET"),
                "gfx": enum_names(f"{REF}/gfx/map_gfx.inc", "MAP_GFX"),
                "pal": enum_names(f"{REF}/gfx/map_pal.inc", "MAP_PAL")}
    except OSError:
        return {"layout": [], "tileset": [], "gfx": [], "pal": []}


NM = names()


def nm(kind, i):
    a = NM.get(kind, [])
    return a[i] if 0 <= i < len(a) else f"#{i:02X}"


# ---------------------------------------------------------------------------------------------------- decoding
class MapGfx:
    """everything needed to draw one map, decoded from ROM"""

    def __init__(self, rom, m, layout_ptrs=F.SUBTILEMAP_PTRS_VANILLA, pal_base=None, anim_frame=0):
        self.rom, self.m = rom, m
        self.row = F.map_props(rom, m)
        self.p = p = F.decode_props(self.row)
        s = p["bg12_size"]
        self.w1, self.h1 = 16 << (s >> 6 & 3), 16 << (s >> 4 & 3)
        self.w2, self.h2 = 16 << (s >> 2 & 3), 16 << (s & 3)
        self.vram0, self.vsrc = F.vram_bg12(rom, p["gfx"])
        self.anim = F.anim_slots(rom, p["bg_anim"])
        self.vram = F.apply_anim(self.vram0, rom, self.anim, anim_frame)
        self.ts1, self.ts1_addr = F.tileset(rom, p["tileset_bg1"])
        self.ts2, self.ts2_addr = F.tileset(rom, p["tileset_bg2"])
        self.pal_base = pal_base if pal_base is not None else F.map_pal_base(rom)
        self.pal = F.palette(rom, p["palette"], self.pal_base)
        self.lay1 = F.layout(rom, p["layout_bg1"], layout_ptrs)
        self.lay2 = F.layout(rom, p["layout_bg2"], layout_ptrs)
        self.tp1, self.tp2 = F.tileprops(rom, p["tile_prop_set"])
        self.tiles = tile_cache(self.vram)
        self.rgb = np.array([F.bgr555_rgb(c) for c in self.pal], np.uint8)

    def with_frame(self, f):
        """copy with BG animation frame f (0-3) in VRAM"""
        import copy
        o = copy.copy(self)
        o.vram = F.apply_anim(self.vram0, self.rom, self.anim, f)
        o.tiles = tile_cache(o.vram)
        return o

    def info(self):
        p = self.p
        return {"map": f"{self.m:03X}", "layout_bg1": f"{p['layout_bg1']:03X}", "layout_bg1_name": nm("layout", p["layout_bg1"]),
                "layout_bg2": f"{p['layout_bg2']:03X}", "layout_bg2_name": nm("layout", p["layout_bg2"]),
                "layout_bg3": f"{p['layout_bg3']:03X}",
                "bg1_size_tiles": [self.w1, self.h1], "bg2_size_tiles": [self.w2, self.h2],
                "tileset_bg1": f"{p['tileset_bg1']:02X}", "tileset_bg1_name": nm("tileset", p["tileset_bg1"]),
                "tileset_bg2": f"{p['tileset_bg2']:02X}", "tileset_bg2_name": nm("tileset", p["tileset_bg2"]),
                "gfx_sets": [f"{g:02X}" for g in p["gfx"]], "gfx_set_names": [nm("gfx", g) for g in p["gfx"]],
                "gfx_bg3": f"{p['gfx_bg3']:02X}",
                "palette": f"{p['palette']:02X}", "palette_name": nm("pal", p["palette"]) if p["palette"] < 48 else "new (QA)",
                "tile_prop_set": f"{p['tile_prop_set']:02X}", "bg_anim": f"{p['bg_anim']:02X}",
                "property_row": self.row.hex(" ").upper()}


def tile_cache(vram):
    """(768, 8, 8) colour indices of VRAM tiles $000-$2FF"""
    v = np.frombuffer(vram[:0x6000], np.uint8).reshape(768, 32)
    out = np.zeros((768, 8, 8), np.uint8)
    for plane, (off, sh) in enumerate(((0, 0), (1, 1), (16, 2), (17, 3))):
        rows = v[:, off:off + 16:2]                                      # (768, 8)
        bits = np.unpackbits(rows[:, :, None], axis=2)                    # (768, 8, 8) MSB first
        out |= bits << sh
    return out


def word_img(mg, w):
    """8x8 palette-index image (0..127, -1 transparent) of one BG word"""
    t = w & 0x3FF
    px = mg.tiles[t] if t < 768 else np.zeros((8, 8), np.uint8)
    if w & 0x4000:
        px = px[:, ::-1]
    if w & 0x8000:
        px = px[::-1, :]
    pal = (w >> 10 & 7) * 16
    return np.where(px == 0, -1, px.astype(np.int16) + pal)


def meta_idx(mg, ts, t, prio=None):
    """16x16 index image of metatile t (prio None = both priorities, low first)"""
    out = np.full((16, 16), -1, np.int16)
    for pr in ((0, 1) if prio is None else (prio,)):
        for k, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
            w = ts[t][k]
            if (w >> 13 & 1) != pr:
                continue
            im = word_img(mg, w)
            sub = out[dy:dy + 8, dx:dx + 8]
            out[dy:dy + 8, dx:dx + 8] = np.where(im >= 0, im, sub)
    return out


def to_rgb(mg, idx, backdrop=True):
    rgb = mg.rgb[np.clip(idx, 0, 127)]
    if backdrop:
        rgb = np.where(idx[..., None] >= 0, rgb, mg.rgb[0])
    return rgb.astype(np.uint8)


def render_map(mg, lay1=None, x0=0, y0=0, w=None, h=None, layers=("bg2", "bg1")):
    """RGB image of the map region (metatile units), BG2 then BG1, per priority (BG2 lo, BG1 lo, BG2 hi, BG1 hi)"""
    lay1 = mg.lay1 if lay1 is None else lay1
    w = mg.w1 if w is None else w
    h = mg.h1 if h is None else h
    idx = np.full((h * 16, w * 16), -1, np.int16)
    cache = {}
    for pr in (0, 1):
        for name in layers:
            ts, lay, lw = (mg.ts2, mg.lay2, mg.w2) if name == "bg2" else (mg.ts1, lay1, mg.w1)
            lh = (mg.h2 if name == "bg2" else mg.h1)
            if lay is None:
                continue
            for y in range(h):
                for x in range(w):
                    yy, xx = (y0 + y) % lh, (x0 + x) % lw
                    t = lay[yy * lw + xx]
                    key = (name, t, pr)
                    if key not in cache:
                        cache[key] = meta_idx(mg, ts, t, pr)
                    im = cache[key]
                    sub = idx[y * 16:y * 16 + 16, x * 16:x * 16 + 16]
                    idx[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = np.where(im >= 0, im, sub)
    return to_rgb(mg, idx)


def passability(b1, b2):
    """decoded tile property (Rev 1 C0:4E35 movement rule, ff6x/mapsrc4.can_move)"""
    return {"byte1": f"{b1:02X}", "byte2": f"{b2:02X}", "impassable": b1 & 7 == 7,
            "z": {0: "both", 1: "upper", 2: "lower", 3: "both (stairs / transition)"}[b1 & 3] if b1 & 7 != 7 else None,
            "bridge": bool(b1 & 4) and b1 & 7 != 7, "dir_mask_byte2": f"{b2 & 0x0F:X}"}


def wdesc(w):
    f = F.word_fields(w)
    return {"word": f"{w:04X}", "tile": f"{f['tile']:03X}", "pal_row": f["pal"], "prio": f["prio"],
            "hflip": f["hflip"], "vflip": f["vflip"]}


def tile_bytes(vram, t):
    return bytes(vram[t * 32:t * 32 + 32])


def tile_key_set(tiles):
    """set of 8x8 index images (with all flips) for dedupe across maps"""
    out = {}
    for t in range(len(tiles)):
        a = tiles[t]
        for fl, im in ((0, a), (1, a[:, ::-1]), (2, a[::-1, :]), (3, a[::-1, ::-1])):
            out.setdefault(im.tobytes(), (t, fl))
    return out


# ---------------------------------------------------------------------------------------------------- drawing helpers
def scale(img, k):
    return np.repeat(np.repeat(img, k, axis=0), k, axis=1)


def save(img, path):
    Image.fromarray(img).save(path, optimize=True)


def label_grid(cells, cols, cell_px, labels, sub_labels=None, title=None, marks=None, fsz=11, pad=2):
    """cells: list of RGB arrays (cell_px x cell_px); labels under each; marks: list of (colour or None)"""
    f, fs = font(fsz), font(fsz - 2)
    lh = fsz + 3 + (fsz if sub_labels else 0)
    rows = (len(cells) + cols - 1) // cols
    W = cols * (cell_px + 2 * pad + 2)
    if title:                                    # wrap the title to the sheet width
        tf, lines = font(fsz + 1), []
        for para in title.split("\n"):
            cur = ""
            for wd in para.split(" "):
                nxt = (cur + " " + wd).strip()
                if tf.getlength(nxt) > W - 10 and cur:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = nxt
            lines.append(cur)
        title = "\n".join(lines)
    th = (fsz + 5) * (len(title.split("\n")) if title else 0) + (8 if title else 0)
    H = th + rows * (cell_px + lh + 2 * pad + 2)
    im = Image.new("RGB", (W, H), (24, 24, 28))
    d = ImageDraw.Draw(im)
    if title:
        d.multiline_text((4, 2), title, fill=(235, 235, 235), font=font(fsz + 1))
    for i, c in enumerate(cells):
        x = (i % cols) * (cell_px + 2 * pad + 2) + pad + 1
        y = th + (i // cols) * (cell_px + lh + 2 * pad + 2) + pad + 1
        if marks and marks[i]:
            d.rectangle([x - 2, y - 2, x + cell_px + 1, y + cell_px + 1], outline=marks[i], width=2)
        im.paste(Image.fromarray(c), (x, y))
        d.text((x, y + cell_px + 1), labels[i], fill=(255, 255, 255), font=f)
        if sub_labels and sub_labels[i]:
            d.text((x, y + cell_px + fsz + 1), sub_labels[i], fill=(170, 200, 255), font=fs)
    return np.asarray(im)


def annotate_map(img, k, grid=True, boxes=(), ids=None, coord=True, fsz=10):
    """img: RGB at 1x (16 px per metatile); returns scaled image with grid, coordinates, labelled boxes, optional ids"""
    big = Image.fromarray(scale(img, k))
    m = 22 if coord else 0
    W, H = big.width + m, big.height + m
    canvas = Image.new("RGB", (W, H), (20, 20, 24))
    canvas.paste(big, (m, m))
    d = ImageDraw.Draw(canvas)
    f = font(fsz)
    cw = 16 * k
    nx, ny = img.shape[1] // 16, img.shape[0] // 16
    if grid:
        for x in range(nx + 1):
            d.line([(m + x * cw, m), (m + x * cw, H)], fill=(0, 0, 0), width=1)
        for y in range(ny + 1):
            d.line([(m, m + y * cw), (W, m + y * cw)], fill=(0, 0, 0), width=1)
    if coord:
        for x in range(nx):
            d.text((m + x * cw + 2, 4), f"{x}", fill=(220, 220, 220), font=f)
        for y in range(ny):
            d.text((2, m + y * cw + 2), f"{y}", fill=(220, 220, 220), font=f)
    if ids is not None:
        fi = font(max(8, fsz - 1))
        for y in range(ny):
            for x in range(nx):
                t = f"{ids[y][x]:02X}"
                px, py = m + x * cw + 2, m + y * cw + 2
                d.rectangle([px - 1, py, px + 13, py + 10], fill=(0, 0, 0))
                d.text((px, py - 1), t, fill=(255, 255, 120), font=fi)
    for (bx, by, bw, bh, col, lab) in boxes:
        d.rectangle([m + bx * cw, m + by * cw, m + (bx + bw) * cw - 1, m + (by + bh) * cw - 1], outline=col, width=3)
        if lab:
            d.rectangle([m + bx * cw, m + by * cw - 14, m + bx * cw + 7 * len(lab) + 4, m + by * cw - 1], fill=(0, 0, 0))
            d.text((m + bx * cw + 2, m + by * cw - 14), lab, fill=col, font=f)
    return np.asarray(canvas)


# ---------------------------------------------------------------------------------------------------- vanilla previews
def preview(clean, m, out):
    mg = MapGfx(clean, m)
    img = render_map(mg)
    k = 1 if mg.w1 * mg.h1 > 4096 else 2
    ids = None
    save(annotate_map(img, k, grid=True, coord=True), os.path.join(out, f"MAP_{m:03X}_preview.png"))
    return mg


def main_previews(clean_path, out, maps):
    os.makedirs(out, exist_ok=True)
    clean = open(clean_path, "rb").read()
    for m in maps:
        mg = preview(clean, int(m, 16), out)
        print(m, json.dumps(mg.info()))


def main_crops(clean_path, out, specs):
    """--crops: spec = MAP:x:y:w:h (metatiles) -> 3x crops with grid, coordinates and BG1 metatile ids"""
    os.makedirs(out, exist_ok=True)
    clean = open(clean_path, "rb").read()
    cache = {}
    for s in specs:
        m, x, y, w, h = s.split(":")
        m, x, y, w, h = int(m, 16), int(x), int(y), int(w), int(h)
        mg = cache.get(m) or cache.setdefault(m, MapGfx(clean, m))
        img = render_map(mg, x0=x, y0=y, w=w, h=h)
        ids = [[mg.lay1[(y + j) * mg.w1 + x + i] for i in range(w)] for j in range(h)]
        a = annotate_map(img, 3, ids=ids, coord=False)
        save(a, os.path.join(out, f"CROP_{m:03X}_{x}_{y}_{w}x{h}.png"))


if __name__ == "__main__":
    if sys.argv[1] == "--previews":
        main_previews(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif sys.argv[1] == "--crops":
        main_crops(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        import art_gate_export_v10 as X
        X.main(*sys.argv[1:5])
