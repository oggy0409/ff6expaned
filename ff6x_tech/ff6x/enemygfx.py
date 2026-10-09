"""TECH v0.6 enemy graphics asset compiler (custom battle sprites for monster IDs >= $180).

Rev 1 battle-sprite format (btlgfx C1:204E LoadMonsterGfxProp, C1:2153 InitStencil,
C1:2299 LoadMonsterGfx, C1:2227 LoadMonsterGfxTile, C1:22D1 LoadMonsterPal):

  MonsterGfxProp (5 B)  word0 bits 0-14 graphics index (data = base + index*8), bit 15 = 3bpp
                        byte2 bit7 = large stencil (16x16 tiles), bits 0-1 + byte3 = palette (10 bit)
                        byte2 bit5 = TECH v0.6 expansion-graphics flag (base FB:0000 instead of E9:7000);
                                     vanilla never sets bits 2-6 (audited, 416 records). Bit 6 must stay 0:
                                     it lands in $81AB, the high byte of the 16-bit stencil number.
                        byte4 = stencil number
  stencil               small: 8 rows x 1 byte (8x8 tiles); large: 16 rows x 2 bytes, MSB = leftmost tile.
                        sprite rows = rows from the top until the first empty row; columns = highest set
                        column + 1; both clipped to the formation's VRAM-map box for that slot.
  tile data             only tiles whose stencil bit is set, row-major. 4bpp = SNES 32-byte tile;
                        3bpp = 16 bytes planes 0/1 + 8 bytes plane 2.
  palette               index * 16 bytes into MonsterPal; LoadMonsterPal always copies 32 bytes (16 colours);
                        at most 3 distinct monster palettes per battle.
"""
import json, os
from .png import read_indexed

EXP_FLAG = 0x20                        # MonsterGfxProp byte 2 bit 5
SMALL, LARGE = "small", "large"
GRID = {SMALL: 8, LARGE: 16}

# MonsterVRAMMapPtrs C2:D01A - per formation VRAM map (formation byte 0 >> 4), slot boxes (cols, rows)
VRAM_MAPS = {
    0: [(8, 8)] * 4, 1: [(8, 8), (8, 8), (4, 4), (4, 4), (4, 4), (4, 4)], 2: [(12, 8), (12, 8)],
    3: [(8, 16), (8, 16)], 4: [(12, 8), (8, 8), (8, 8)], 5: [(8, 16), (8, 8), (8, 8)], 6: [(16, 16)],
    7: [(12, 12), (4, 12), (4, 4), (4, 4), (4, 4), (4, 4)], 8: [(8, 8), (8, 8), (4, 8), (4, 8)],
    9: [(12, 12)], 10: [(8, 12), (4, 8), (4, 8), (4, 4), (4, 4)],
    11: [(4, 8), (4, 8), (4, 8), (4, 8), (8, 8)], 12: [(8, 8), (8, 8), (4, 8), (4, 8), (4, 8), (4, 8)],
}


# same table with the box origin (tile x, y) in the 16x16-tile monster graphics buffer / VRAM area
VRAM_MAP_POS = {
    0: [(0, 0), (8, 0), (0, 8), (8, 8)], 1: [(0, 0), (8, 0), (0, 8), (4, 8), (8, 8), (12, 8)], 2: [(0, 0), (0, 8)],
    3: [(0, 0), (8, 0)], 4: [(0, 0), (0, 8), (8, 8)], 5: [(0, 0), (8, 0), (8, 8)], 6: [(0, 0)],
    7: [(0, 0), (12, 0), (0, 12), (4, 12), (8, 12), (12, 12)], 8: [(0, 0), (0, 8), (8, 0), (8, 8)], 9: [(0, 0)],
    10: [(0, 0), (8, 0), (8, 8), (0, 12), (4, 12)], 11: [(0, 0), (4, 0), (8, 0), (8, 8), (0, 8)],
    12: [(0, 0), (8, 0), (0, 8), (4, 8), (8, 8), (12, 8)],
}


class AssetError(ValueError):
    pass


def bgr555(rgb):
    r, g, b = rgb
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def parse_color(s):
    s = s.lstrip("#")
    if len(s) != 6:
        raise AssetError(f"bad colour {s!r}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def tile_4bpp(px):
    out = bytearray(32)
    for r in range(8):
        for c in range(8):
            v, bit = px[r][c], 0x80 >> c
            if v & 1: out[2 * r] |= bit
            if v & 2: out[2 * r + 1] |= bit
            if v & 4: out[16 + 2 * r] |= bit
            if v & 8: out[16 + 2 * r + 1] |= bit
    return bytes(out)


def tile_3bpp(px):
    out = bytearray(24)
    for r in range(8):
        for c in range(8):
            v, bit = px[r][c], 0x80 >> c
            if v & 1: out[2 * r] |= bit
            if v & 2: out[2 * r + 1] |= bit
            if v & 4: out[16 + r] |= bit
    return bytes(out)


def stencil_rows(stencil_bytes, kind):
    if kind == SMALL:
        return [b << 8 for b in stencil_bytes]
    return [(stencil_bytes[2 * k] << 8) | stencil_bytes[2 * k + 1] for k in range(16)]


def stencil_size(stencil_bytes, kind):
    """(cols, rows) exactly as InitStencil computes them (before box clipping)."""
    rows = stencil_rows(stencil_bytes, kind)
    n = 0
    while n < len(rows) and rows[n]:
        n += 1
    acc = 0
    for r in rows[:n]:
        acc |= r
    cols = 0
    for c in range(16):
        if acc & (0x8000 >> c):
            cols = c + 1
    return cols, n


class EnemyAsset:
    """monsters/<m>/graphics.json {"custom": {"image", "bpp", "stencil"}, "overlap"} + palette.json {"colors"}"""

    def __init__(self, folder):
        self.folder = folder
        g = json.load(open(os.path.join(folder, "graphics.json")))
        p = json.load(open(os.path.join(folder, "palette.json")))
        c = g["custom"]
        self.bpp, self.kind = int(c["bpp"]), c.get("stencil", SMALL)
        if self.bpp not in (3, 4) or self.kind not in GRID:
            raise AssetError(f"{folder}: bpp must be 3/4, stencil small/large")
        self.image = os.path.join(folder, c["image"])
        self.overlap = int(g.get("overlap", 0))
        self.colors = [parse_color(x) for x in p["colors"]]
        ncol = 16 if self.bpp == 4 else 8
        if len(self.colors) != ncol:
            raise AssetError(f"{folder}: {self.bpp}bpp palette needs exactly {ncol} colours")
        w, h, rows, plte = read_indexed(self.image)
        grid = GRID[self.kind]
        if w % 8 or h % 8 or w > 8 * grid or h > 8 * grid:
            raise AssetError(f"{folder}: image {w}x{h} must be multiples of 8 and <= {8 * grid}x{8 * grid} ({self.kind} stencil)")
        if any(v >= ncol for r in rows for v in r):
            raise AssetError(f"{folder}: pixel index >= {ncol} in a {self.bpp}bpp sprite")
        for i, col in enumerate(self.colors):
            if i < len(plte) and tuple(plte[i]) != col and i:
                raise AssetError(f"{folder}: PNG palette entry {i} {plte[i]} != palette.json {col}")
        self.w, self.h, self.rows = w, h, rows
        tc, tr = w // 8, h // 8
        tiles = [[[[rows[8 * ty + y][8 * tx + x] for x in range(8)] for y in range(8)] for tx in range(tc)] for ty in range(tr)]
        mask = [[any(v for line in tiles[ty][tx] for v in line) for tx in range(tc)] for ty in range(tr)]
        if not any(mask[0]):
            raise AssetError(f"{folder}: top tile row is empty (sprite must start at the top edge)")
        last = max(ty for ty in range(tr) if any(mask[ty]))
        self.filled_gaps = []
        for ty in range(last + 1):
            if not any(mask[ty]):               # an empty row would end the sprite early (InitStencil)
                mask[ty][0] = True; self.filled_gaps.append(ty)
        self.tile_rows = last + 1
        self.mask = mask[:last + 1]
        enc = tile_4bpp if self.bpp == 4 else tile_3bpp
        data = bytearray()
        for ty in range(self.tile_rows):
            for tx in range(tc):
                if self.mask[ty][tx]:
                    data += enc(tiles[ty][tx])
        self.data = bytes(data)
        self.tile_count = sum(sum(r) for r in self.mask)
        sb = bytearray(8 if self.kind == SMALL else 32)
        for ty in range(self.tile_rows):
            bits = sum(0x8000 >> tx for tx in range(tc) if self.mask[ty][tx])
            if self.kind == SMALL:
                sb[ty] = bits >> 8
            else:
                sb[2 * ty], sb[2 * ty + 1] = bits >> 8, bits & 0xFF
        self.stencil = bytes(sb)
        self.cols, self.rows_used = stencil_size(self.stencil, self.kind)
        pal = bytearray()
        for col in self.colors:
            pal += bgr555(col).to_bytes(2, "little")
        self.palette = bytes(pal) + b"\x00" * (32 - len(pal))   # always 2 units (LoadMonsterPal copies 32 B)

    def gfx_prop(self, gfx_index, pal_index, stencil_index):
        if not 0 <= gfx_index <= 0x7FFF: raise AssetError("graphics index out of range")
        if not 0 <= pal_index <= 0x3FF: raise AssetError("palette index out of range")
        if not 0 <= stencil_index <= 0xFF: raise AssetError("stencil index must be 8-bit")
        w = gfx_index | (0x8000 if self.bpp == 3 else 0)
        b2 = (0x80 if self.kind == LARGE else 0) | EXP_FLAG | (pal_index >> 8)
        return bytes([w & 0xFF, w >> 8, b2, pal_index & 0xFF, stencil_index])
