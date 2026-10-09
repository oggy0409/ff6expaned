#!/usr/bin/env python3
"""TECH v0.9.3 VRAM audit (bsnes, accurate PPU): per formation slot, which monster tile cells hold the monster's own ROM
tiles after the battle has drawn them, and which were overwritten - for the user-runtime cases V2 (WoR Lunaris) and V3
(Praetor + Bit + Bit after the 70% reveal), on the v0.9.2 and the v0.9.3 QA ROM, both from New Game without a party preset.

Monster tile VRAM (measured, matches data/vram_safety.json): byte $6000 + (row * 16 + col) * 32 for cell (row, col) of
the 16 x 16 cell grid; a slot's cells = its VRAM-map box origin (ff6x/enemygfx.VRAM_MAP_POS) + the stencil cells of
its graphics. Magitek armor cells (vram_safety.json): rows 0-11, columns 12-15.

usage: vram_audit_v093.py <v0.9.2 qa.sfc> <its manifest> <v0.9.3 qa.sfc> <its manifest> <out>
writes <out>/VRAM_AUDIT_v093.json (VRAM_AUDIT_v0.9.3.md is written from it)
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import emu_bsnes
emu_bsnes.use_bsnes()
import numpy as np
from PIL import Image
from emu_item_tech import T
from emu_item_qa import boot_new_game
import emu_enablers_v092 as EN
import gfx_compare_report as GC
from ff6x.enemygfx import VRAM_MAPS, VRAM_MAP_POS
from ff6x.formation_safety import magitek_cells

MAGITEK_MODE = 0x64BA


def hold_step(h, n=1):
    for _ in range(n):
        for m in range(6):
            h.w8(0x3218 + 8 + 2 * m, 0); h.w8(0x3219 + 8 + 2 * m, 0)
        h.step(1)


def audit(h, romb, Tb, out, tag):
    vram = h.vram()
    open(os.path.join(out, f"{tag}_vram.bin"), "wb").write(vram)
    open(os.path.join(out, f"{tag}_oam.bin"), "wb").write(h.oam())
    Image.fromarray(np.asarray(h.em.get_screen())).save(os.path.join(out, f"{tag}.png"))
    fid = h.r16(0x3ED4)
    frec = romb[Tb["form"] + 15 * fid:Tb["form"] + 15 * fid + 15]
    vmap = frec[0] >> 4
    mask = magitek_cells()
    slots = []
    for s in range(6):
        mid = h.r16(0x2001 + 2 * s)
        if mid == 0xFFFF or mid >= 0x200:
            continue
        dd, tiles, _ = GC.decode_slot(romb, Tb, mid)
        bx, by = VRAM_MAP_POS[vmap][s]
        bc, br = VRAM_MAPS[vmap][s]
        good, bad, bad_mt = [], [], []
        for (r, c), t in sorted(tiles.items()):
            if r >= br or c >= bc:
                continue
            cell = (by + r, bx + c)
            a = 0x6000 + (cell[0] * 16 + cell[1]) * 32
            if vram[a:a + 32] == t:
                good.append(cell)
            else:
                bad.append(cell)
                if cell in mask:
                    bad_mt.append(cell)
        rng = lambda cs: [f"${0x6000 + (r * 16 + c) * 32:04X}" for r, c in cs]
        slots.append({"slot": s, "monster": f"{mid:03X}", "box_origin_col_row": [bx, by], "box_cols_rows": [bc, br],
                      "vram_box_bytes": f"${0x6000 + (by * 16 + bx) * 32:04X}-${0x6000 + ((by + br - 1) * 16 + bx + bc - 1) * 32 + 31:04X} (box rows)",
                      "stencil_cols_rows": dd["stencil_cols_rows"], "tiles_used": len(good) + len(bad),
                      "tiles_correct": len(good), "tiles_overwritten": len(bad),
                      "overwritten_in_magitek_area": len(bad_mt), "overwritten_cells": [list(c) for c in bad][:24],
                      "overwritten_vram": rng(bad)[:12],
                      "used_cells_in_magitek_area": len([c for c in good + bad if c in mask])})
    party = [i for i in range(16) if h.r8(0x1850 + i) & 7]
    return {"tag": tag, "formation": f"{fid:03X}", "vram_map": vmap, "magitek_mode": h.r8(MAGITEK_MODE),
            "party_records": party, "party_magitek": [i for i in party if h.r8(0x1614 + 37 * i) & 8], "slots": slots}


def praetor(qa, man, out, tag):
    L = EN.evlabels(man)
    romb = open(qa, "rb").read(); Tb = GC.rom_tables(romb)
    h = T(qa)
    boot_new_game(h)
    EN.start_battle(h, L, "QaPraetorS92")
    EN.set_hp(h, h.r16(EN.MAXHP + 2 * EN.PRAETOR) * 70 // 100 + 10)
    EN.terra_fight(h)
    for _ in range(4):
        if h.r8(0x2F2F) == 7:
            break
        h.press("A", 8, 10); EN.run(h, 300)
    hold_step(h, 240)
    r = audit(h, romb, Tb, out, tag)
    r["shown_mask"] = f"{h.r8(0x2F2F):02X}"
    h.close()
    return r


def lunaris(qa, man, out, tag):
    L = EN.evlabels(man)
    romb = open(qa, "rb").read(); Tb = GC.rom_tables(romb)
    r = bytearray(romb)
    x, y = 146, 204
    sec = 256 + (y >> 5) * 32 + (x >> 5) * 4
    for g in {r[0x0F5400 + sec + k] for k in range(4)}:
        for j, f in enumerate((0xCB, 0xCA, 0xCB, 0xCA)):
            r[0x0F4800 + 8 * g + 2 * j] = f; r[0x0F4800 + 8 * g + 2 * j + 1] = 0
    tmp = os.path.join(out, "_tmp.sfc"); open(tmp, "wb").write(r)
    h = T(tmp)
    boot_new_game(h)
    h.call_event(L["QaWor92"], frames=1); h.step(700)
    h.step(20, ("B",)); h.step(400)
    for k in range(400):
        h.step(16, (("LEFT", "RIGHT")[k % 2],)); h.step(4)
        sc = np.asarray(h.em.get_screen())[165:215].reshape(-1, 3).mean(axis=0)
        if sc[2] > sc[0] + 50 and sc[2] > 90:
            break
    h.step(240); hold_step(h, 60)
    res = audit(h, romb, Tb, out, tag)
    h.close()
    os.remove(tmp)
    return res


def main(qa92, man92, qa93, man93, out):
    os.makedirs(out, exist_ok=True)
    rep = {"cell_vram": "byte $6000 + (row * 16 + col) * 32", "magitek_cells": "rows 0-11, columns 12-15 (data/vram_safety.json)",
           "cases": [praetor(qa92, man92, out, "v092_praetor_bits"), praetor(qa93, man93, out, "v093_praetor_bits"),
                     lunaris(qa92, man92, out, "v092_wor_lunaris"), lunaris(qa93, man93, out, "v093_wor_lunaris")]}
    json.dump(rep, open(os.path.join(out, "VRAM_AUDIT_v093.json"), "w"), indent=1)
    for c in rep["cases"]:
        print(c["tag"], "formation", c["formation"], "map", c["vram_map"], "magitek", c["magitek_mode"],
              [(s["slot"], s["monster"], s["tiles_used"], s["tiles_overwritten"], s["overwritten_in_magitek_area"]) for s in c["slots"]])


if __name__ == "__main__":
    main(*sys.argv[1:6])
