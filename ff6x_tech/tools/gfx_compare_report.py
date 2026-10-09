#!/usr/bin/env python3
"""TECH v0.6.1 enemy-graphics routing comparison report (Claude-side EMULATOR evidence).

For every scenario (ROM, formation, party mode) the battle is injected from the same start RAM
($11E0 = formation, as emu_monster_diff.py). For every monster slot the report records

  ROM side   : monster ID, router gfx-prop slot, the 5-byte MonsterGfxProp record actually read
               (vanilla D2:7000 or relocated F8:8000), decoded fields (graphics index, 3bpp, large,
               palette, stencil, expansion flag), selected graphics base + tile source address,
               stencil bytes (vanilla D2:A820 or relocated FB:4000 table), stencil size, palette bytes,
               formation position byte, VRAM map + box
  RAM side   : $8117 palette per slot, $812F sprite size per slot, decoded 4bpp tiles in the btlgfx
               buffer (7E:AE3F) for the slot box, compared with the tiles decoded from the ROM source
  screen     : expected sprite rendered from (tiles + palette); searched pixel-exact on screen every
               10 frames for 900 frames (Dark Wind flies in) -> first exact match frame or best mismatch

usage: gfx_compare_report.py <out_dir> <scenario.json>   (scenario list: [{rom, formation, party, tag}])"""
import sys, os, json, hashlib, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def rom_tables(rom):
    if len(rom) == 0x300000:
        return {"gfx": 0x127000, "stencil": 0x12A820, "stencil_bank": 0x120000, "pal": 0x127820, "form": 0xF6200, "layout": "vanilla"}
    return {"gfx": 0x388000, "stencil": 0x3B4000, "stencil_bank": 0x3B0000, "pal": 0x3B0000, "form": 0x38A000, "layout": "v0.5+/v0.6 relocated"}


def decode_slot(rom, T, mid):
    slot = mid if (mid < 0x180 or T["layout"] == "vanilla") else mid + 0x20
    rec = rom[T["gfx"] + 5 * slot:T["gfx"] + 5 * slot + 5]
    w = rec[0] | rec[1] << 8
    gidx, bpp3, large = w & 0x7FFF, bool(w & 0x8000), bool(rec[2] & 0x80)
    pal = ((rec[2] << 8) | rec[3]) & 0x3FF
    exp = bool(rec[2] & 0x20)
    st_idx = rec[4] | ((rec[2] & 0x40) << 2)
    base = 0xFB0000 if exp else 0xE97000
    src = base + gidx * 8
    sp = rom[T["stencil"]] | rom[T["stencil"] + 1] << 8; lp = rom[T["stencil"] + 2] | rom[T["stencil"] + 3] << 8
    if large:
        a = T["stencil_bank"] + lp + 32 * st_idx; stb = rom[a:a + 32]
        rows = [(stb[2 * k] << 8) | stb[2 * k + 1] for k in range(16)]
    else:
        a = T["stencil_bank"] + sp + 8 * st_idx; stb = rom[a:a + 8]
        rows = [b << 8 for b in stb]
    n = 0
    while n < len(rows) and rows[n]: n += 1
    acc = 0
    for r in rows[:n]: acc |= r
    cols = max([c + 1 for c in range(16) if acc & (0x8000 >> c)] or [0])
    tsz = 24 if bpp3 else 32
    tiles, k = {}, 0
    pc = src - 0xC00000
    for r in range(n):
        for c in range(cols):
            if rows[r] & (0x8000 >> c):
                t = rom[pc + k * tsz:pc + (k + 1) * tsz]; k += 1
                if bpp3: t = t[:16] + b"".join(bytes([t[16 + y], 0]) for y in range(8))
                tiles[(r, c)] = t
    palb = rom[T["pal"] + 16 * pal:T["pal"] + 16 * pal + 32]
    return {"monster": f"{mid:03X}", "gfx_prop_slot": f"{slot:03X}", "gfx_prop_record": rec.hex(" ").upper(),
            "graphics_index": f"{gidx:04X}", "bpp": 3 if bpp3 else 4, "large_stencil": large, "expansion_flag": exp,
            "graphics_base": f"{base:06X}", "tile_source_snes": f"{src:06X}", "tile_source_pc": f"{pc:06X}",
            "tile_count": k, "tile_bytes": k * tsz, "stencil_index": f"{st_idx:03X}", "stencil_bytes": stb.hex(" ").upper(),
            "stencil_cols_rows": [cols, n], "palette_index": f"{pal:03X}", "palette_bytes": palb.hex(" ").upper()}, tiles, palb


def render(tiles, palb, cols, rows):
    import numpy as np
    idx = np.zeros((rows * 8, cols * 8), np.int32); rgb = np.zeros((rows * 8, cols * 8, 3), np.int32)
    for (r, c), t in tiles.items():
        for y in range(8):
            for x in range(8):
                b = 7 - x
                v = ((t[2 * y] >> b) & 1) | (((t[2 * y + 1] >> b) & 1) << 1) | (((t[16 + 2 * y] >> b) & 1) << 2) | (((t[17 + 2 * y] >> b) & 1) << 3)
                idx[r * 8 + y, c * 8 + x] = v
                if v:
                    col = palb[2 * v] | palb[2 * v + 1] << 8
                    rgb[r * 8 + y, c * 8 + x] = [col & 31, (col >> 5) & 31, (col >> 10) & 31]
    return idx, rgb


def worker(sc, out):
    import numpy as np
    from PIL import Image
    from emu_harness import H
    import emu_celes_suite as S
    import emu_monster_tech as M
    from sprite_match import find
    from ff6x.enemygfx import VRAM_MAPS, VRAM_MAP_POS
    rom = open(sc["rom"], "rb").read(); T = rom_tables(rom)
    f = int(sc["formation"], 16)
    h = H(sc["rom"]); h.em.set_state(open(sc["state"], "rb").read()); h.step(2)
    if sc["party"] == "no_magitek":                                        # POKE: clear Magitek on every character
        for k in range(16):
            a = 0x1614 + 37 * k; h.w8(a, h.r8(a) & 0xF7)
    for i, v in enumerate([0x4D, 0xFE, 0x3F, 0xFE]): h.gd.memory.assign(S.SCRIPT_RAM + i, '|u1', v)
    S.inject(h, S.SCRIPT_RAM)
    for t in range(900):
        if t < 26: h.w8(0x11E0, f & 0xFF); h.w8(0x11E1, f >> 8)
        h.step(1)
        if h.r16(0x3ED4) == f and t > 26 and any(M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)): break
    h.step(90)
    mem = lambda a, n: (h.gd.update_ram(), bytes(h.gd.memory.extract(0x7E0000 + a + i, '|u1') for i in range(n)))[1]
    frec = rom[T["form"] + 15 * f:T["form"] + 15 * f + 15]
    vmap = frec[0] >> 4
    buf = mem(0xAE3F, 0x2000)
    slots, expect = [], {}
    for s in range(6):
        mid = h.r16(0x2001 + 2 * s)
        if mid == 0xFFFF: continue
        d, tiles, palb = decode_slot(rom, T, mid)
        bx, by = VRAM_MAP_POS[vmap][s]
        bad = [list(rc) for rc, t in tiles.items() if buf[(bx + rc[1]) * 0x20 + (by + rc[0]) * 0x200:(bx + rc[1]) * 0x20 + (by + rc[0]) * 0x200 + 32] != t]
        d.update({"slot": s, "formation_position_byte": f"{frec[8 + s]:02X}", "vram_map": vmap,
                  "vram_box_origin": [bx, by], "vram_box_cols_rows": list(VRAM_MAPS[vmap][s]),
                  "ram_palette_8117": f"{h.r16(0x8117 + 2 * s):04X}", "ram_size_812F_cols_rows": list(mem(0x812F + 2 * s, 2)),
                  "buffer_tiles_equal_rom_source": not bad, "buffer_tile_mismatches": bad,
                  "buffer_box_sha1": hashlib.sha1(b"".join(buf[(bx + c) * 0x20 + (by + r) * 0x200:(bx + c) * 0x20 + (by + r) * 0x200 + 32]
                                                           for r in range(d["stencil_cols_rows"][1]) for c in range(d["stencil_cols_rows"][0]))).hexdigest()})
        slots.append(d)
        expect[s] = render(tiles, palb, *d["stencil_cols_rows"])
    # screen: sample every 10 frames for 900 frames; per slot: exact samples, first/last exact frame, final state
    stats = {s: {"samples": 0, "exact": 0, "first_exact": None, "last_exact": None, "final": None} for s in expect}
    snap_img = None
    for t in range(0, 910, 10):
        scr = h.em.get_screen()
        for s, (idx, rgb) in expect.items():
            # expected screen position from the formation position byte (x = high nibble * 8, y = low nibble * 8);
            # duplicate sprites make a free search ambiguous, so each slot is checked at its own position
            pb = frec[8 + s]; x, y = (pb >> 4) * 8, (pb & 15) * 8
            win = (np.asarray(scr, dtype=np.int32) >> 3)[y:y + idx.shape[0], x:x + idx.shape[1]]
            bad = int(np.any(win != rgb, axis=2)[idx != 0].sum()) if win.shape[:2] == idx.shape else int((idx != 0).sum())
            r = {"x": x, "y": y, "opaque_px": int((idx != 0).sum()), "mismatched_px": bad}
            st = stats[s]; st["samples"] += 1
            if r["mismatched_px"] == 0:
                st["exact"] += 1; st["last_exact"] = t
                if st["first_exact"] is None: st["first_exact"] = t
            st["final"] = r
        if t == 600: snap_img = scr.copy()
        h.step(10)
    Image.fromarray(snap_img).resize((512, 448), Image.NEAREST).save(os.path.join(out, f"{sc['tag']}_f600.png"))
    Image.fromarray(h.em.get_screen()).resize((512, 448), Image.NEAREST).save(os.path.join(out, f"{sc['tag']}_f900.png"))
    for d in slots:
        st = stats[d["slot"]]; st.pop("loc", None)
        d["screen"] = st
        d["screen_pixel_exact_final"] = st["final"]["mismatched_px"] == 0
    res = {"scenario": {k: v for k, v in sc.items() if k != "state"}, "rom_sha1": hashlib.sha1(rom).hexdigest(),
           "table_layout": T["layout"], "formation_record": frec.hex(" ").upper(), "vram_map": vmap, "slots": slots}
    json.dump(res, open(os.path.join(out, sc["tag"] + ".json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "--worker":
        worker(json.loads(sys.argv[2]), sys.argv[3]); sys.exit(0)
    out, scen = sys.argv[1], json.load(open(sys.argv[2]))
    os.makedirs(out, exist_ok=True)
    for sc in scen:
        subprocess.check_call([sys.executable, __file__, "--worker", json.dumps(sc), out])
    allr = [json.load(open(os.path.join(out, sc["tag"] + ".json"))) for sc in scen]
    json.dump(allr, open(os.path.join(out, "GFX_COMPARE_REPORT.json"), "w"), indent=1)
    for r in allr:
        print(r["scenario"]["tag"], [(d["slot"], d["monster"], d["gfx_prop_record"], "buf_ok" if d["buffer_tiles_equal_rom_source"] else "BUF_BAD",
                                      f'exact {d["screen"]["exact"]}/{d["screen"]["samples"]}', f'final_bad {d["screen"]["final"]["mismatched_px"]}') for d in r["slots"]])
