"""TECH v0.6.2 formation preview images (deterministic, no third-party libraries).

Left: the battle field at 1:1 SNES pixels (scaled x2) - masked edges (x < 8, x > 247, y < 4) black, battle
window from y = 151, margin guides (orange = 8 px, yellow = 16 px, purple = vanilla party-lane x = 167),
each sprite drawn from the built ROM data with its palette and an outline coloured by status
(green OK / yellow WARNING / red ERROR). Right: the 16x16-cell monster VRAM area with the formation's VRAM-map
boxes, used cells and the Magitek conflict area (red hatching; red cell = conflict). Bottom: issue list."""
from .png import write_rgb
from .enemygfx import VRAM_MAPS, VRAM_MAP_POS
from .formation_safety import decode_sprite, magitek_cells, VISIBLE, MIN_MARGIN, PREFERRED_MARGIN, PARTY_LANE_X, FORM_PC

FONT = {  # 3x5
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001",
    "5": "111100111001111", "6": "111100111101111", "7": "111001010010010", "8": "111101111101111", "9": "111101111001111",
    "A": "010101111101101", "B": "110101110101110", "C": "011100100100011", "D": "110101101101110", "E": "111100110100111",
    "F": "111100110100100", "G": "011100101101011", "H": "101101111101101", "I": "111010010010111", "J": "001001001101010",
    "K": "101101110101101", "L": "100100100100111", "M": "101111111101101", "N": "110101101101101", "O": "010101101101010",
    "P": "110101110100100", "Q": "010101101110011", "R": "110101110101101", "S": "011100010001110", "T": "111010010010010",
    "U": "101101101101111", "V": "101101101101010", "W": "101101111111101", "X": "101101010101101", "Y": "101101010010010",
    "Z": "111001010100111", " ": "000000000000000", "$": "011110010011110", ":": "000010000010000", ".": "000000000000010",
    "-": "000000111000000", "/": "001001010100100", "(": "010100100100010", ")": "010001001001010", "=": "000111000111000",
    ">": "100010001010100", "<": "001010100010001", "+": "000010111010000", ",": "000000000010100", "[": "110100100100110",
    "]": "011001001001011", "_": "000000000000111", "'": "010010000000000", "%": "101001010100101", "#": "101111101111101",
}
STATUS_COL = {"OK": (0, 230, 0), "WARNING": (255, 210, 0), "ERROR": (255, 40, 40)}
SLOT_COL = [(80, 160, 255), (255, 140, 60), (120, 230, 120), (230, 120, 230), (240, 240, 120), (120, 230, 230)]


class Canvas:
    def __init__(s, w, h, bg):
        s.w, s.h = w, h
        s.p = [[bg] * w for _ in range(h)]

    def set(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.p[y][x] = c

    def rect(s, x0, y0, x1, y1, c, fill=False):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if fill or x in (x0, x1) or y in (y0, y1):
                    s.set(x, y, c)

    def text(s, x, y, t, c=(255, 255, 255), shadow=(0, 0, 0)):
        for ch in t.upper():
            g = FONT.get(ch, FONT[" "])
            for k, bit in enumerate(g):
                if bit == "1":
                    if shadow: s.set(x + k % 3 + 1, y + k // 3 + 1, shadow)
            for k, bit in enumerate(g):
                if bit == "1":
                    s.set(x + k % 3, y + k // 3, c)
            x += 4

    def save(s, path, scale=2):
        rows = []
        for row in s.p:
            line = bytearray()
            for c in row:
                line += bytes(c) * scale
            rows += [bytes(line)] * scale
        write_rgb(path, rows)


def render(img, rep, path):
    FW, FH = 256, 224
    PX = FW + 12
    lines = [x["level"][0] + " " + x["msg"] for x in rep["issues"]]
    W, H = PX + 16 * 8 + 12, FH + 14 + 7 * max(3, len(lines) + 2)
    cv = Canvas(W, H, (24, 24, 28))
    # field
    cv.rect(0, 0, FW - 1, FH - 1, (0, 0, 0), fill=True)
    cv.rect(VISIBLE["x_min"], VISIBLE["y_min"], VISIBLE["x_max"], VISIBLE["y_max"], (52, 60, 78), fill=True)
    for y in range(VISIBLE["y_min"], VISIBLE["y_max"] + 1, 8):          # light grid every 8 px (position units)
        for x in range(VISIBLE["x_min"], VISIBLE["x_max"] + 1, 2):
            cv.set(x, y, (60, 68, 88))
    cv.rect(VISIBLE["x_min"], VISIBLE["y_max"] + 1, VISIBLE["x_max"], FH - 1, (40, 40, 120), fill=True)
    cv.rect(VISIBLE["x_min"], VISIBLE["y_max"] + 1, VISIBLE["x_max"], VISIBLE["y_max"] + 1, (240, 240, 240))
    cv.text(VISIBLE["x_min"] + 4, VISIBLE["y_max"] + 6, "BATTLE WINDOW (Y >= 151)", (200, 200, 255))

    def vline(x, y0, y1, c, step):
        for y in range(y0, y1 + 1, step): cv.set(x, y, c)

    def hline(y, x0, x1, c, step):
        for x in range(x0, x1 + 1, step): cv.set(x, y, c)
    for mgn, col, st in ((MIN_MARGIN, (255, 140, 0), 2), (PREFERRED_MARGIN, (230, 210, 0), 4)):
        vline(VISIBLE["x_min"] + mgn, VISIBLE["y_min"], VISIBLE["y_max"], col, st)
        vline(VISIBLE["x_max"] - mgn, VISIBLE["y_min"], VISIBLE["y_max"], col, st)
        hline(VISIBLE["y_min"] + mgn, VISIBLE["x_min"], VISIBLE["x_max"], col, st)
    hline(VISIBLE["y_max"] - 8, VISIBLE["x_min"], VISIBLE["x_max"], (230, 210, 0), 4)
    vline(PARTY_LANE_X + 1, VISIBLE["y_min"], VISIBLE["y_max"], (200, 90, 255), 3)
    cv.text(PARTY_LANE_X + 4, VISIBLE["y_min"] + 3, "PARTY LANE", (200, 90, 255))
    rec = img[FORM_PC + 15 * int(rep["formation"], 16):FORM_PC + 15 * int(rep["formation"], 16) + 15]
    vmap = rep["vram_map"]
    sprites = []
    for so in rep["slots"]:
        s, mid = so["slot"], int(so["monster"], 16)
        sp = decode_sprite(img, mid, vmap, s)
        ox, oy = so["origin_xy"]
        for y, row in enumerate(sp["pixels"]):
            for x, v in enumerate(row):
                if v and VISIBLE["x_min"] <= ox + x <= VISIBLE["x_max"] and VISIBLE["y_min"] <= oy + y <= VISIBLE["y_max"]:
                    cv.set(ox + x, oy + y, sp["colours"][v])
        sprites.append((so, sp))
    for so, sp in sprites:
        x0, y0, x1, y1 = so["opaque_bbox"]
        cv.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, STATUS_COL[so["status"]])
        cv.text(max(0, x0), max(0, y0 - 7), f"S{so['slot']} {so['monster']} L{so['margins']['left']} T{so['margins']['top']}",
                STATUS_COL[so["status"]])
    # VRAM panel
    cv.text(PX, 1, f"VRAM MAP {vmap}  (16X16 TILE CELLS)", (255, 255, 255))
    mask = magitek_cells()
    gy = 9
    for r in range(16):
        for c in range(16):
            x, y = PX + c * 8, gy + r * 8
            cv.rect(x, y, x + 7, y + 7, (44, 44, 52), fill=True)
            cv.rect(x, y, x + 7, y + 7, (70, 70, 80))
            if (r, c) in mask:
                for k in range(0, 8, 2): cv.set(x + k, y + k, (170, 40, 40)); cv.set(x + 7 - k, y + k, (170, 40, 40))
    for s, ((bc, br), (bx, by)) in enumerate(zip(VRAM_MAPS[vmap], VRAM_MAP_POS[vmap])):
        cv.rect(PX + bx * 8, gy + by * 8, PX + (bx + bc) * 8 - 1, gy + (by + br) * 8 - 1, (90, 200, 220))
        cv.text(PX + bx * 8 + 2, gy + by * 8 + 2, str(s), (90, 200, 220))
    for so, sp in sprites:
        for (r, c) in sp["cells"]:
            x, y = PX + c * 8, gy + r * 8
            col = (255, 30, 30) if (r, c) in mask else SLOT_COL[so["slot"]]
            cv.rect(x + 2, y + 2, x + 5, y + 5, col, fill=True)
    cv.text(PX, gy + 16 * 8 + 3, "RED HATCH = MAGITEK AREA", (230, 120, 120))
    # status lines
    ty = FH + 4
    cv.text(2, ty, f"FORMATION ${rep['formation']}  MAP {vmap}  MAGITEK_POSSIBLE {rep['magitek_possible']}  STATUS {rep['status']}"
            + (f"  SAFE MAPS {rep['suggested_vram_maps']}" if "suggested_vram_maps" in rep else ""), STATUS_COL[rep["status"]])
    for k, ln in enumerate(lines):
        cv.text(2, ty + 7 * (k + 1), ln[:98], STATUS_COL["ERROR" if ln.startswith("E") else "WARNING"])
    cv.save(path)
