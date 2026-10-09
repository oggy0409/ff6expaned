#!/usr/bin/env python3
"""TECH v0.8: contact sheets of the emulator screenshots (equip / battle / stress suites).

usage: equipment_sheet_v08.py <emulator out root (with equip/ battle/ stress/)> <output dir>
writes EQUIPMENT_V08_WEAPONS_SHEET.png (13 weapons: extended | template, same battle state) and
       EQUIPMENT_V08_MENUS_STRESS_SHEET.png (grant list, equipped stats, shop/sell/colosseum lists, party loadout, battles,
       Colosseum, after power cycle)
"""
import glob, os, sys
from PIL import Image, ImageDraw


def sheet(paths, cols, cell, out, title):
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


def main(root, out):
    os.makedirs(out, exist_ok=True)
    w = sorted(glob.glob(os.path.join(root, "battle", "*_W_*_ext_vs_template*.png")))
    print(sheet(w, 3, (520, 240), os.path.join(out, "EQUIPMENT_V08_WEAPONS_SHEET.png"),
                "TECH v0.8 W1 - left: signature weapon, right: same battle state with the template vanilla weapon in hand"))
    m = sorted(glob.glob(os.path.join(root, "equip", "*.png"))) + \
        sorted(glob.glob(os.path.join(root, "battle", "*_[JG]_*.png"))) + \
        sorted(glob.glob(os.path.join(root, "stress", "*.png")))
    print(sheet(m, 5, (272, 250), os.path.join(out, "EQUIPMENT_V08_MENUS_STRESS_SHEET.png"),
                "TECH v0.8 emulator screenshots - menus, exclusions, Jump / Genji, party loadout, battles, Colosseum, save/load"))


if __name__ == "__main__":
    main(*sys.argv[1:3])
