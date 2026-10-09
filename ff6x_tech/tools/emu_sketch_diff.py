#!/usr/bin/env python3
"""TECH v0.6 Sketch graphics-path regression (Claude-side EMULATOR, POKE TEST): vanilla Rev 1 vs a v0.6 ROM.
Same start RAM state; Terra's commands poked to Steal/Sketch/Control/Item (Magitek bit cleared); the
formation is injected with $11E0; Terra's menu is opened and Sketch is used on the default target with a
fixed input sequence. While the action plays, every distinct STABLE (>= 12 frames) (graphics-buffer SHA-1, $6169 palette pointer)
pair is recorded (transient partial-load frames are timing-dependent); the sets must be identical between ROMs (vanilla graphics, stencil and palette reads
through the relocated tables and the EnemyGfxBase hook).
usage: emu_sketch_diff.py dump <rom> <state> <out.json> <formation,...> | compare <a> <b>"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def dump(rom, state, out, forms):
    from emu_harness import H
    import emu_celes_suite as S
    import emu_monster_tech as M
    import emu_enemy_tech as E
    h = H(rom); snap = open(state, "rb").read()
    res = {}
    for f in forms:
        h.em.set_state(snap); h.step(2)
        h.w8(0x1614, h.r8(0x1614) & 0xF7)
        for i, c in enumerate((0x05, 0x0D, 0x0E, 0x01)): h.w8(0x1616 + i, c)
        for i, v in enumerate([0x4D, 0xFE, 0x3F, 0xFE]):
            h.gd.memory.assign(S.SCRIPT_RAM + i, '|u1', v)
        S.inject(h, S.SCRIPT_RAM)
        for t in range(900):
            if t < 26: h.w8(0x11E0, f & 0xFF); h.w8(0x11E1, f >> 8)
            h.step(1)
            if h.r16(0x3ED4) == f and t > 26 and any(M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)): break
        h.step(200); M.close_submenus(h)
        E.terra_menu(h)
        base = h.em.get_state()
        states = []
        for delay in (0, 7, 11, 23, 31, 43):
            h.em.set_state(base); h.step(delay)
            for b in ("DOWN", "A", "A"): h.press(b, 4, 30)
            seen, last, run = [], None, 0
            for t in range(500):
                h.step(1)
                key = (hashlib.sha1(E.mem(h, 0xAE3F, 0x2000)).hexdigest()[:16], f"{h.r16(0x6169):04X}")
                run = run + 1 if key == last else 1
                last = key
                if run == 12 and key not in seen: seen.append(key)      # stable states only (>= 12 frames)
            states.append(sorted(set(map(tuple, seen))))
        res[f"{f:03X}"] = {"ids": [f"{M.mon_id(h, k):03X}" for k in range(6)], "buffer_palptr_states": states}
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump(sys.argv[2], sys.argv[3], sys.argv[4], [int(x, 16) for x in sys.argv[5].split(",")])
    else:
        a, b = json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
        rows = {k: a[k] == b[k] for k in a}
        print(json.dumps({"formations": len(a), "identical": sum(rows.values()), "rows": rows,
                          "distinct_states": {k: [len(s) for s in a[k]["buffer_palptr_states"]] for k in a}}, indent=1))
        sys.exit(0 if all(rows.values()) else 1)
