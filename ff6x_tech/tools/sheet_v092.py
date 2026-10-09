#!/usr/bin/env python3
"""TECH v0.9.1 / v0.9.2: contact sheets of the emulator screenshots.

usage: sheet_v092.py <evidence dir (run_regression_v092.sh)> <output dir>
writes ITEM_ALIGNMENT_V091_SHEET.png (shops + consumable battles) and CELES_ENABLERS_V092_SHEET.png (E1-E8)
"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet_v09 import sheet


def main(ev, out):
    os.makedirs(out, exist_ok=True)
    shops = sorted(glob.glob(os.path.join(ev, "consumables_v091", "*.png")))
    btl = [p for p in sorted(glob.glob(os.path.join(ev, "consumable_battle_v091", "*.png")))
           if p.endswith(("_after.png", "_anim.png")) or "_V8_" in p]
    print(sheet(shops + btl, 6, (270, 250), os.path.join(out, "ITEM_ALIGNMENT_V091_SHEET.png"),
                "TECH v0.9.1 item alignment - shops $80-$84 / cap, consumable battles V1-V9 (stable-retro snes9x)"))
    en = sorted(glob.glob(os.path.join(ev, "enablers_v092", "*.png")))
    print(sheet(en, 5, (270, 250), os.path.join(out, "CELES_ENABLERS_V092_SHEET.png"),
                "TECH v0.9.2 Celes enablers E1-E9 (QA target, placeholder graphics D-14; stable-retro snes9x)"))


if __name__ == "__main__":
    main(*sys.argv[1:3])
