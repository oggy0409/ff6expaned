#!/usr/bin/env python3
"""TECH v0.9: contact sheets of the emulator screenshots.

usage: sheet_v09.py <consumables out> <battle out> <rare out> <stress out> <output dir>
writes CONSUMABLE_V09_MENUS_SHEET.png, CONSUMABLE_V09_BATTLE_SHEET.png, RARE_ITEMS_V09_SHEET.png, STRESS_V09_SHEET.png
"""
import glob, os, sys
from PIL import Image, ImageDraw


def sheet(paths, cols, cell, out, title):
    if not paths:
        return None
    rows = (len(paths) + cols - 1) // cols
    W, H = cell
    img = Image.new("RGB", (cols * W, 28 + rows * (H + 18)), (24, 24, 32))
    d = ImageDraw.Draw(img)
    d.text((8, 8), title, fill=(240, 240, 240))
    for n, p in enumerate(paths):
        im = Image.open(p).convert("RGB")
        im.thumbnail((W - 8, H - 4))
        x, y = (n % cols) * W, 28 + (n // cols) * (H + 18)
        img.paste(im, (x + 4, y + 16))
        d.text((x + 4, y + 2), os.path.basename(p)[4:-4], fill=(200, 220, 255))
    img.save(out)
    return out


def main(c1, c2, c3, c4, out):
    os.makedirs(out, exist_ok=True)
    print(sheet(sorted(glob.glob(os.path.join(c1, "*.png"))), 4, (272, 250),
                os.path.join(out, "CONSUMABLE_V09_MENUS_SHEET.png"),
                "TECH v0.9 consumables - Item list, Arrange, extended shops $80/$81, vanilla shop alias check, Sell, Colosseum"))
    b = [p for p in sorted(glob.glob(os.path.join(c2, "*.png"))) if any(t in p for t in ("_list", "_name", "_anim", "B1_"))]
    print(sheet(b, 4, (272, 250), os.path.join(out, "CONSUMABLE_V09_BATTLE_SHEET.png"),
                "TECH v0.9 consumables in battle - list (no signature equipment), extended name window, item animation; "
                "BT = Shadow throws the vanilla katana"))
    print(sheet(sorted(glob.glob(os.path.join(c3, "*.png"))), 4, (272, 250), os.path.join(out, "RARE_ITEMS_V09_SHEET.png"),
                "TECH v0.9 Rare Items menu - 5 key items + descriptions, 52 entries on 3 pages (Down / R paging)"))
    print(sheet(sorted(glob.glob(os.path.join(c4, "*.png"))), 4, (272, 250), os.path.join(out, "STRESS_V09_SHEET.png"),
                "TECH v0.9 stress - battle with everything, Arrange with everything, Colosseum, after power cycle"))


if __name__ == "__main__":
    main(*sys.argv[1:6])
