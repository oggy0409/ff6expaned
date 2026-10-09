#!/usr/bin/env python3
"""Dev-only, run once: draws the two TECH v0.6 QA test creatures and writes them as indexed PNG
sources (monsters/tech6_0180/sprite.png, monsters/tech6_0181/sprite.png) + palette.json.
The PNGs are the committed asset sources; the builder only reads the PNG + palette.json."""
import json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from ff6x.png import write_indexed

# ---- TESTCUBE A: 4bpp, 32x40 (4x5 tiles), blue gel cube with two antennae -------------------
PAL_A = ["#000000", "#101828", "#183878", "#2858B8", "#4080E0", "#70B0F8", "#C8F0FF", "#FFFFFF",
         "#901828", "#F8D030", "#60D8A0", "#000000", "#000000", "#000000", "#000000", "#000000"]
W, H = 32, 40
A = [[0] * W for _ in range(H)]
def put(img, x, y, v):
    if 0 <= y < len(img) and 0 <= x < len(img[0]): img[y][x] = v
for ax in (9, 22):                                     # antennae (tile row 0, columns 1 and 2)
    for y in range(2, 9): put(A, ax, y, 1); put(A, ax + 1, y, 3)
    for dy in range(3):
        for dx in range(3): put(A, ax - 1 + dx, dy, 9 if (dx, dy) != (1, 1) else 7)
for y in range(8, 40):                                 # body x 1..30, y 8..39, rounded corners
    for x in range(1, 31):
        corner = (x in (1, 30) and y in (8, 39)) or (x in (1, 30) and y in (9, 38)) and False
        if (x, y) in ((1, 8), (30, 8), (1, 39), (30, 39)): continue
        edge = x in (1, 30) or y in (8, 39)
        if edge: A[y][x] = 1; continue
        shade = 2 if y > 32 else 3 if y > 24 else 4 if y > 14 else 5
        A[y][x] = shade
for x in range(4, 14): A[11][x] = 6                    # highlight
for y in range(11, 16): A[y][4] = 6
for ex in (9, 20):                                     # eyes
    for y in range(17, 24):
        for x in range(ex, ex + 4): A[y][x] = 7
    for y in range(19, 23):
        A[y][ex + 1] = 1; A[y][ex + 2] = 1
for x in range(12, 21): A[29][x] = 8                   # mouth
for x in range(13, 20): A[30][x] = 8
for x in (6, 25): A[27][x] = 10; A[27][x + 1] = 10      # cheeks

# ---- TESTEYE B: 3bpp, 32x32 (4x4 tiles), orange spiked eye-orb -------------------------------
PAL_B = ["#000000", "#200808", "#C03010", "#F07818", "#F8D848", "#FFFFFF", "#30A830", "#081008"]
B = [[0] * 32 for _ in range(32)]
cx, cy = 15.5, 15.5
for y in range(32):
    for x in range(32):
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if d <= 11.5:
            B[y][x] = 1 if d > 10.5 else (2 if d > 8.5 else 3)
for (x0, y0, dx, dy) in ((15, 0, 0, 1), (16, 0, 0, 1), (15, 31, 0, -1), (16, 31, 0, -1),
                         (0, 15, 1, 0), (0, 16, 1, 0), (31, 15, -1, 0), (31, 16, -1, 0)):
    for k in range(5):                                 # four spikes
        put(B, x0 + dx * k, y0 + dy * k, 1 if k < 1 else 4)
for y in range(32):
    for x in range(32):
        d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        if d <= 6.5: B[y][x] = 5                       # eye white
        if ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 <= 4.0: B[y][x] = 6   # iris
        if abs(x - cx) <= 1 and abs(y - cy) <= 2.5: B[y][x] = 7         # slit pupil
B[11][12] = 5; B[12][12] = 5                           # glint

def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
for folder, img, pal in (("tech6_0180", A, PAL_A), ("tech6_0181", B, PAL_B)):
    d = os.path.join(HERE, "monsters", folder); os.makedirs(d, exist_ok=True)
    write_indexed(os.path.join(d, "sprite.png"), img, [rgb(c) for c in pal])
    json.dump({"_comment": "Palette resource (RGB888, converted to SNES BGR555 by the builder). Index 0 = transparent.",
               "colors": pal}, open(os.path.join(d, "palette.json"), "w"), indent=1)
    print("wrote", d)
