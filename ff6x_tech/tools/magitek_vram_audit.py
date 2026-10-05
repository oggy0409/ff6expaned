#!/usr/bin/env python3
"""TECH v0.6.2 R13 audit: which monster-graphics tile cells does the Magitek party overwrite in VRAM?

Battle monster graphics: btlgfx buffer 7E:AE3F (16x16 cells of 32 B, cell c = row*16 + col) is uploaded linearly to
VRAM bytes $6000-$7FFF (word $3000-$3FFF), cell c at $6000 + 32*c (verified: every non-empty buffer cell is found
there). A cell is "overwritten" when VRAM differs from the buffer. Each scenario samples VRAM every 30 frames for
900 frames after the formation is loaded, ORs the overwritten cells, and records the party Magitek status.

usage: magitek_vram_audit.py <out_dir> <scenario.json>  ([{rom, formation, clear:[char idx], tag}])"""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
STATE_DEFAULT = "/tmp/claude-0/-home-claude/e9754b14-965a-5227-a65a-523f4cfb8ebd/scratchpad/mdiff/vanilla.state"


def worker(sc, out):
    from emu_harness import H
    import emu_celes_suite as S
    import emu_monster_tech as M
    f = int(sc["formation"], 16)
    h = H(sc["rom"]); h.em.set_state(open(sc.get("state", STATE_DEFAULT), "rb").read()); h.step(2)
    for k in sc.get("clear", []):
        a = 0x1614 + 37 * k; h.w8(a, h.r8(a) & 0xF7)
    for k in sc.get("set", []):
        a = 0x1614 + 37 * k; h.w8(a, h.r8(a) | 0x08)
    for i, v in enumerate([0x4D, 0xFE, 0x3F, 0xFE]): h.gd.memory.assign(S.SCRIPT_RAM + i, '|u1', v)
    S.inject(h, S.SCRIPT_RAM)
    for t in range(900):
        if t < 26: h.w8(0x11E0, f & 0xFF); h.w8(0x11E1, f >> 8)
        h.step(1)
        if h.r16(0x3ED4) == f and t > 26 and any(M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)): break
    magitek = [k for k in range(16) if h.r8(0x1614 + 37 * k) & 0x08]
    party = [h.r8(0x3ED8 + 2 * s) if h.r8(0x3ED8 + 2 * s) != 0xFF else None for s in range(4)]
    over, first = set(), {}
    nonempty = set(); dumps = []
    h.step(90)                                         # graphics decoded/uploaded (as gfx_compare_report)
    h.gd.update_ram()
    buf0 = bytes(h.gd.memory.extract(0x7EAE3F + i, '|u1') for i in range(0x2000))
    nonempty = {c for c in range(256) if buf0[32 * c:32 * c + 32] != b"\0" * 32}
    # cells actually used by this formation's sprites (stencil tiles placed at the slot's VRAM-map box origin)
    from gfx_compare_report import rom_tables, decode_slot
    from ff6x.enemygfx import VRAM_MAPS, VRAM_MAP_POS
    rom = open(sc["rom"], "rb").read(); T = rom_tables(rom)
    fr = rom[T["form"] + 15 * f:T["form"] + 15 * f + 15]; vm = fr[0] >> 4; used = {}
    for s_ in range(6):
        mid = h.r16(0x2001 + 2 * s_)
        if mid == 0xFFFF or s_ >= len(VRAM_MAPS[vm]): continue
        d, tiles, _ = decode_slot(rom, T, mid); bx, by = VRAM_MAP_POS[vm][s_]; bc, br = VRAM_MAPS[vm][s_]
        for (r, c) in tiles:
            if r < br and c < bc: used[16 * (by + r) + bx + c] = s_
    over_used = {}
    step = sc.get("sample_every", 30); stopped_at = None
    for t in range(0, 930, step):
        h.gd.update_ram()
        alive = any(h.r16(0x3BF4 + 8 + 2 * k) not in (0, 0xFFFF) and M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6))
        if not alive:
            stopped_at = t; break                      # all monsters dead: battle teardown is not part of the audit
        buf = bytes(h.gd.memory.extract(0x7EAE3F + i, '|u1') for i in range(0x2000))
        st = h.em.get_state(); j = st.index(b"VRA:065536:") + 11; v = st[j:j + 65536]
        if t % 30 == 0: dumps.append(v[0x6000:0x8000])
        for c in range(256):
            if v[0x6000 + 32 * c:0x6000 + 32 * c + 32] != buf[32 * c:32 * c + 32]:
                over.add(c); first.setdefault(c, t)
            if c in used and v[0x6000 + 32 * c:0x6000 + 32 * c + 32] != buf0[32 * c:32 * c + 32]:
                over_used.setdefault(c, t)                  # sprite cell no longer holds the sprite's tile
        if t < sc.get("press_a_until", 0) and (t // step) % max(1, 30 // step) == 0:
            h.step(4, ("A",)); h.step(step - 4)       # drive the battle menu: MagiTek -> first beam -> target
        else:
            h.step(step)
    cur_hp = [h.r16(0x3BF4 + 8 + 2 * k) for k in range(6)]
    res = {"scenario": sc, "magitek_chars": magitek, "party_battle_chars": party,
           "overwritten_cells": sorted(over), "first_frame": {str(c): first[c] for c in sorted(first)},
           "overwritten_grid": ["".join("X" if 16 * r + c in over else "." for c in range(16)) for r in range(16)],
           "buffer_nonempty_cells": len(nonempty),
           "monster_hp_now": cur_hp, "sampling_stopped_all_dead_at": stopped_at, "overwritten_nonempty_cells": sorted(over & nonempty),
           "vram_map": vm, "sprite_cells": len(used),
           "sprite_cells_overwritten": {str(c): {"slot": used[c], "first_frame": t_} for c, t_ in sorted(over_used.items())},
           "slots_affected": sorted({used[c] for c in over_used})}
    json.dump(res, open(os.path.join(out, sc["tag"] + ".json"), "w"), indent=1)
    open(os.path.join(out, sc["tag"] + ".vram6000.bin"), "wb").write(b"".join(dumps))   # 31 samples x 8 KB


if __name__ == "__main__":
    if sys.argv[1] == "--worker":
        worker(json.loads(sys.argv[2]), sys.argv[3]); sys.exit(0)
    out, scen = sys.argv[1], json.load(open(sys.argv[2]))
    os.makedirs(out, exist_ok=True)
    for sc in scen:
        subprocess.check_call([sys.executable, __file__, "--worker", json.dumps(sc), out])
        r = json.load(open(os.path.join(out, sc["tag"] + ".json")))
        print(sc["tag"], "magitek", r["magitek_chars"], "overwritten", len(r["overwritten_cells"]))
        for row in r["overwritten_grid"]: print("   ", row)
