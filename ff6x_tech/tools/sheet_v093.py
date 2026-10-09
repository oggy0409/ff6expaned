#!/usr/bin/env python3
"""TECH v0.9.3 before / after contact sheets from the visual suite outputs (tools/emu_visual_v093.py).

usage: sheet_v093.py <before dir (v0.9.2 ROM)> <after dir (v0.9.3 ROM)> <out dir> <emulator tag>
writes VISUAL_BEFORE_AFTER_<tag>.png (S1 palette, S2 dog, S3 Bits, S4 states) and E8_STATES_<tag>.png (crops + pixel diff)
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

ROWS = [("S1 map $1A2 palette (RESET room)", "S1_1A2_reset.png"),
        ("S2 WoR Lunaris encounter (New Game path)", "S2_wor_lunaris_battle.png"),
        ("S3 Praetor + Bits after 70% ($245, QA-scaled)", "S3_245_scaled_after_70.png"),
        ("S3 Praetor + Bits after 70% ($244, locked)", "S3_244_locked_after_70.png"),
        ("S4 E8 RESET", "S4_reset.png"), ("S4 E8 PRESERVE", "S4_preserve.png"),
        ("S4 E8 BURN", "S4_burn.png"), ("S4 E8 GRAVES", "S4_graves.png"),
        ("S4 GRAVES + PRESERVE after save / power cycle / Continue", "S4_persist_after_power_cycle.png")]


def load(d, f):
    p = os.path.join(d, f)
    return Image.open(p).convert("RGB") if os.path.exists(p) else Image.new("RGB", (256, 224), (60, 0, 0))


def main(before, after, out, tag):
    W, H, PAD, LBL = 256, 224, 6, 16
    img = Image.new("RGB", (2 * W + 3 * PAD + 220, len(ROWS) * (H + LBL + PAD) + 30), (24, 24, 32))
    d = ImageDraw.Draw(img)
    d.text((PAD, 6), f"TECH v0.9.3 visual hotfix - BEFORE = v0.9.2 QA ROM (left) / AFTER = v0.9.3 QA ROM (right), "
                     f"same path from New Game, {tag}", fill=(240, 240, 240))
    for k, (label, f) in enumerate(ROWS):
        y = 30 + k * (H + LBL + PAD)
        d.text((PAD, y), label, fill=(200, 220, 255))
        img.paste(load(before, f), (PAD, y + LBL))
        img.paste(load(after, f), (2 * PAD + W, y + LBL))
        d.text((3 * PAD + 2 * W, y + LBL + 4), "BEFORE (v0.9.2)", fill=(255, 140, 140))
        d.text((3 * PAD + 2 * W, y + LBL + 20), "AFTER (v0.9.3)", fill=(140, 255, 140))
    p1 = os.path.join(out, f"VISUAL_BEFORE_AFTER_{tag}.png")
    img.save(p1)
    # E8 crops (memorial 64 x 32, archive 32 x 32, x4) and per-state pixel difference vs RESET
    states = ["reset", "preserve", "burn", "graves"]
    cw, ch = 4 * 64 + 8 + 4 * 32, 4 * 32
    e = Image.new("RGB", (len(states) * (cw + 12) + 12, 2 * (ch + 40) + 20), (24, 24, 32))
    d = ImageDraw.Draw(e)
    for r, (name, dd) in enumerate((("BEFORE v0.9.2", before), ("AFTER v0.9.3", after))):
        base = None
        for c, s in enumerate(states):
            x, y = 12 + c * (cw + 12), 10 + r * (ch + 40)
            m = load(dd, f"S4_{s}_memorial.png").resize((256, 128), Image.NEAREST)
            a = load(dd, f"S4_{s}_archive.png").resize((128, 128), Image.NEAREST)
            e.paste(m, (x, y + 14)); e.paste(a, (x + 264, y + 14))
            if base is None:
                base = (np.asarray(m), np.asarray(a))
            fm = float(np.mean(np.any(np.asarray(m) != base[0], axis=2)))
            fa = float(np.mean(np.any(np.asarray(a) != base[1], axis=2)))
            d.text((x, y), f"{name} {s.upper()}  diff vs RESET: memorial {fm:.0%} archive {fa:.0%}", fill=(220, 220, 220))
    p2 = os.path.join(out, f"E8_STATES_{tag}.png")
    e.save(p2)
    print(p1, p2)


if __name__ == "__main__":
    main(*sys.argv[1:5])
