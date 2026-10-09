"""Field-map graphics decoder (read-only): map properties -> BG1/BG2 graphics sets, tilesets (16x16 metatiles),
map palette, BG animation tiles, tile properties, layouts. Used by the ART ASSET GATE v1.0 exporter
(tools/art_gate_v10.py). Pure stdlib except the optional render helpers (Pillow).

Engine references (Rev 1, ff6 disassembly src/field):
  LoadMapProp   C0:1CAD   33-byte row (MapProp ED:8F00, relocated in v0.4+ builds) -> $0520-$0540
  LoadMapGfx    C0:268D   gfx1 -> VRAM word $0000 ($2000 B), gfx2 -> $1000, gfx3 -> $1800, gfx4 -> $2000 (skipped when
                          gfx4 == gfx3); TfrBG12Gfx always DMAs $2000 B from MapGfx (DF:DB00 + 3-byte ptr, DF:DA00)
  TfrBG3Gfx     C0:275F   BG3 gfx (E6:8780 + ptr E6:CD60, LZSS) -> VRAM $3000
  LoadTileset   C0:27DA   tileset 1 ($052B >> 2 & $7F) -> $7FC000, tileset 2 ($052C >> 1 & $7F) -> $7FC800;
                          MapTileset DE:0000 + 3-byte ptr DF:BA00, LZSS, $800 B: lo bytes [q*256 + t], hi bytes
                          [$400 + q*256 + t]; q = 0 TL, 1 TR, 2 BL, 3 BR (BG1 draw @1F6B: $C000/$C200/$C400/$C600)
  LoadMapPal    C0:265C   MapPal ED:C480 (256 B per palette; relocated to F7:A000 in v0.9.2+ QA builds)
  InitBG12Anim  (anim.asm) $053B & $1F -> MapBGAnimPropPtrs C0:91D5 (offsets from MapBGAnimProp C0:91FF);
                          16 records x (speed, 4 frame ptrs into E6:0000); the Frame1 graphics of all 16 records
                          ($80 B = 4 tiles each) are loaded to VRAM word $2800 -> tiles $280-$2BF; records 0-7 then
                          cycle their 4 frames every frame (TfrBGAnimGfx), records 8-15 stay static
  LoadTileProp  C0:1CCE   tile properties D9:A800 + ptr D9:CD10, LZSS, 512 B (byte1 plane, byte2 plane)
BG tilemap word: vhopppcc cccccccc (tile 0-$3FF, palette row 0-7, priority, h / v flip).
"""
from .lzss import decompress
from .hirom import snes_to_pc

MAP_PROPS_VANILLA = 0xED8F00
MAP_PAL_VANILLA = 0xEDC480
MAP_GFX_PTRS, MAP_GFX_BASE = 0xDFDA00, 0xDFDB00
TILESET_PTRS, TILESET_BASE = 0xDFBA00, 0xDE0000
BG3_GFX_PTRS, BG3_GFX_BASE = 0xE6CD60, 0xE68780
ANIM_PROP_PTRS = 0xC091D5          # MapBGAnimPropPtrs: 16-bit offsets relative to MapBGAnimProp
ANIM_PROP_BASE = 0xC091FF          # MapBGAnimProp (= ptrs + 21 x 2)
ANIM_GFX_BANK = 0xE60000
TILEPROP_PTRS, TILEPROP_BASE = 0xD9CD10, 0xD9A800
SUBTILEMAP_PTRS_VANILLA, SUBTILEMAP_BASE = 0xD9CD90, 0xD9D1B0
LOADMAPPROP_OPERAND = 0xC01CC0          # lda f:MapProp,x (C0:1CBF) operand
LOADMAPPAL_OPERAND = 0xC0266D           # lda f:MapPal,x (C0:266C) operand
VANILLA_MAPS = 0x19F
GFX_SLOT_VRAM = ((0, 0x0000), (1, 0x1000), (2, 0x1800), (3, 0x2000))   # (gfx n, VRAM word address)
ANIM_TILE_FIRST = 0x280                 # 8 slots x 4 tiles


def r24(rom, snes):
    p = snes_to_pc(snes)
    return rom[p] | rom[p + 1] << 8 | rom[p + 2] << 16


def r16(rom, snes):
    p = snes_to_pc(snes)
    return rom[p] | rom[p + 1] << 8


def map_props_base(rom):
    """MapProp table address actually read by LoadMapProp in this ROM (vanilla ED:8F00 or relocated)."""
    return r24(rom, LOADMAPPROP_OPERAND)


def map_pal_base(rom):
    return r24(rom, LOADMAPPAL_OPERAND)


def map_props(rom, m):
    p = snes_to_pc(map_props_base(rom)) + 33 * m
    return bytes(rom[p:p + 33])


def decode_props(row):
    """Field the engine derives from a 33-byte map property row (RAM $0520 + n)."""
    b = row
    w = lambda i: b[i] | b[i + 1] << 8
    return {
        "title": b[0], "tile_prop_set": b[4],
        "gfx": [b[7] & 0x7F, (w(7) << 1 & 0x7F00) >> 8, (w(8) << 2 & 0x7F00) >> 8, (w(9) << 3 & 0x7F00) >> 8],
        "gfx_bg3": w(10) >> 4 & 0x3F,
        "tileset_bg1": w(11) >> 2 & 0x7F,
        "tileset_bg2": b[12] >> 1 & 0x7F,
        "layout_bg1": w(13) & 0x3FF,
        "layout_bg2": w(14) >> 2 & 0x3FF,
        "layout_bg3": w(15) >> 4 & 0x3FF,
        "palette": b[25], "pal_anim": b[26], "bg_anim": b[27] & 0x1F, "bg3_anim": b[27] >> 5,
        "song": b[28], "width_mask": b[30], "height_mask": b[31],
        "bg12_size": b[23], "bg3_size": b[24],
    }


def gfx_set(rom, n):
    off = r24(rom, MAP_GFX_PTRS + 3 * n)
    p = snes_to_pc(MAP_GFX_BASE + off)
    return bytes(rom[p:p + 0x2000]), MAP_GFX_BASE + off


def vram_bg12(rom, gfx):
    """VRAM byte image of the BG1/BG2 character area (words $0000-$2FFF = tiles $000-$2FF) after LoadMapGfx.
    Returns (bytes 0x6000, {tile: (gfx slot, gfx index, tile within set)})."""
    v = bytearray(0x8000)
    src = {}
    for slot, word in GFX_SLOT_VRAM:
        if slot == 3 and gfx[3] == gfx[2]:
            continue
        data, _ = gfx_set(rom, gfx[slot])
        a = word * 2
        n = min(0x2000, len(v) - a)
        v[a:a + n] = data[:n]
        for k in range(n // 32):
            src[word // 16 + k] = (slot, gfx[slot], k)
    return bytes(v[:0x6000]), src


def anim_slots(rom, idx):
    """BG1/BG2 animation (map prop byte 27 & $1F): 16 records {speed, frames: [4 x E6 pointer]}; record s -> tiles
    $280 + 4s .. +3 ($80 bytes). Records 0-7 animate (4 frames), 8-15 keep Frame1."""
    if idx == 0:
        return []
    base = ANIM_PROP_BASE + r16(rom, ANIM_PROP_PTRS + 2 * idx)
    out = []
    for s in range(16):
        a = base + 10 * s
        out.append({"slot": s, "tiles": [ANIM_TILE_FIRST + 4 * s + k for k in range(4)], "animated": s < 8,
                    "speed": r16(rom, a), "frames": [r16(rom, a + 2 + 2 * f) for f in range(4)]})
    return out


def anim_frame_gfx(rom, ptr):
    p = snes_to_pc(ANIM_GFX_BANK | ptr)
    return bytes(rom[p:p + 0x80])


def apply_anim(vram, rom, slots, frame=0):
    v = bytearray(vram)
    for s in slots:
        a = s["tiles"][0] * 32
        v[a:a + 0x80] = anim_frame_gfx(rom, s["frames"][frame if s["animated"] else 0])
    return bytes(v)


def tileset(rom, n):
    """256 metatiles x [TL, TR, BL, BR] 16-bit BG words."""
    off = r24(rom, TILESET_PTRS + 3 * n)
    d = decompress(rom[snes_to_pc(TILESET_BASE + off):])
    if len(d) < 0x800:
        raise ValueError(f"tileset {n:02X} decompresses to {len(d)} bytes")
    return [[d[q * 256 + t] | d[0x400 + q * 256 + t] << 8 for q in range(4)] for t in range(256)], TILESET_BASE + off


def tileprops(rom, n):
    off = r16(rom, TILEPROP_PTRS + 2 * n)
    d = decompress(rom[snes_to_pc(TILEPROP_BASE + off):])
    return list(d[:256]), list(d[256:512])


def palette(rom, idx, base=None):
    base = base if base is not None else map_pal_base(rom)
    p = snes_to_pc(base) + 256 * idx
    raw = rom[p:p + 256]
    return [raw[2 * i] | raw[2 * i + 1] << 8 for i in range(128)]


def bgr555_rgb(c):
    r, g, b = c & 31, c >> 5 & 31, c >> 10 & 31
    return (r << 3 | r >> 2, g << 3 | g >> 2, b << 3 | b >> 2)


def layout(rom, idx, ptrs=SUBTILEMAP_PTRS_VANILLA):
    if idx == 0:
        return None
    off = r24(rom, ptrs + 3 * idx)
    return decompress(rom[snes_to_pc(SUBTILEMAP_BASE + off):])


def tile_pixels(vram, t):
    """8x8 4bpp planar tile -> 64 colour indices (0-15)."""
    a = t * 32
    px = []
    for y in range(8):
        p0, p1, p2, p3 = vram[a + 2 * y], vram[a + 2 * y + 1], vram[a + 16 + 2 * y], vram[a + 17 + 2 * y]
        for x in range(8):
            bit = 7 - x
            px.append((p0 >> bit & 1) | (p1 >> bit & 1) << 1 | (p2 >> bit & 1) << 2 | (p3 >> bit & 1) << 3)
    return px


def word_fields(w):
    return {"tile": w & 0x3FF, "pal": w >> 10 & 7, "prio": w >> 13 & 1, "hflip": w >> 14 & 1, "vflip": w >> 15 & 1}


def draw_word(img_px, W, x0, y0, vram, pal, w, only_prio=None):
    """Draw one 8x8 tilemap word into an RGB pixel list (row-major, width W). Index 0 = transparent."""
    f = word_fields(w)
    if only_prio is not None and f["prio"] != only_prio:
        return
    px = tile_pixels(vram, f["tile"])
    for y in range(8):
        for x in range(8):
            sx, sy = (7 - x if f["hflip"] else x), (7 - y if f["vflip"] else y)
            c = px[sy * 8 + sx]
            if c:
                img_px[(y0 + y) * W + x0 + x] = bgr555_rgb(pal[f["pal"] * 16 + c])


def metatile_words(ts, t):
    return ts[t]


def render_metatile(vram, pal, ts, t, backdrop=None):
    """16x16 RGB pixels of metatile t (both priorities)."""
    bd = backdrop if backdrop is not None else bgr555_rgb(pal[0])
    px = [bd] * 256
    q = ts[t]
    for pr in (0, 1):
        for k, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
            draw_word(px, 16, dx, dy, vram, pal, q[k], pr)
    return px


def render_layers(vram, pal, layers, w, h):
    """layers: list of (tileset, layout bytes (row-major, 256 wide in RAM or w wide), stride) drawn BG2 then BG1,
    per priority (BG2 p0, BG1 p0, BG2 p1, BG1 p1). Returns w*16 x h*16 RGB pixel list."""
    W, H = w * 16, h * 16
    px = [bgr555_rgb(pal[0])] * (W * H)
    for pr in (0, 1):
        for ts, lay, stride in layers:
            if lay is None:
                continue
            for y in range(h):
                for x in range(w):
                    t = lay[y * stride + x] if y * stride + x < len(lay) else 0
                    q = ts[t]
                    for k, (dx, dy) in enumerate(((0, 0), (8, 0), (0, 8), (8, 8))):
                        draw_word(px, W, x * 16 + dx, y * 16 + dy, vram, pal, q[k], pr)
    return px
