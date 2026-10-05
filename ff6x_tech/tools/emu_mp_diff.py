#!/usr/bin/env python3
"""TECH v0.6 Magic Point regression (Claude-side EMULATOR, POKE TEST): vanilla Rev 1 vs a v0.6 ROM.
Same start RAM state; Ramuh is given and equipped on Terra by RAM poke ($1A69 bit 0, $161E = 0);
the formation is injected with $11E0 (as emu_monster_diff.py); monster HP poked to 1 so the
opening party wins quickly; after the victory text, Terra's learn progress for Ramuh's spells
(Bolt $1A70, Poison $1A71, Bolt 2 $1A75) is read. Expected learn = MP x rate (Bolt x10, Poison x5, Bolt2 x2).
usage: emu_mp_diff.py dump <rom> <state> <out.json> <formation,...>
       emu_mp_diff.py compare <a.json> <b.json>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def dump(rom, state, out, forms):
    from emu_harness import H
    import emu_celes_suite as S
    import emu_monster_tech as M
    h = H(rom); snap = open(state, "rb").read()
    res = {}
    for f in forms:
        h.em.set_state(snap); h.step(2)
        h.w8(0x1A69, h.r8(0x1A69) | 1); h.w8(0x161E, 0)              # POKE: give + equip Ramuh (Terra)
        for i, v in enumerate([0x4D, 0xFE, 0x3F, 0xFE]):
            h.gd.memory.assign(S.SCRIPT_RAM + i, '|u1', v)
        S.inject(h, S.SCRIPT_RAM)
        started = False
        for t in range(900):
            if t < 26: h.w8(0x11E0, f & 0xFF); h.w8(0x11E1, f >> 8)
            h.step(1)
            if h.r16(0x3ED4) == f and h.r16(0x3BF4) != 0xFFFF and t > 26 and any(M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)):
                started = True; break
        if not started:
            res[f"{f:03X}"] = {"started": False}; continue
        h.step(120)
        for k in range(6):                                            # POKE: monster HP 1
            if M.mon_hp(h, k) not in (0, 0xFFFF):
                h.w8(0x3BFC + 2 * k, 1); h.w8(0x3BFD + 2 * k, 0)
        M.close_submenus(h)
        won, _ = M.fight_to_end(h, "/tmp", "mpd", max_cycles=60)
        for t in range(1500):
            h.step(1)
            if t % 20 == 0: h.press("A", 4, 4)
            if h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and t > 300: break
        res[f"{f:03X}"] = {"started": True, "won": won, "learn_bolt_poison_bolt2": [h.r8(0x1A6E + s) for s in (2, 3, 7)]}
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        dump(sys.argv[2], sys.argv[3], sys.argv[4], [int(x, 16) for x in sys.argv[5].split(",")])
    else:
        a, b = json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
        same = {k: a[k] == b[k] for k in a}
        print(json.dumps({"formations": len(a), "identical": sum(same.values()), "rows": {k: [a[k], b[k]] for k in a}}, indent=1))
        sys.exit(0 if all(same.values()) else 1)
