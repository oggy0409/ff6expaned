#!/usr/bin/env python3
"""TECH v0.9.2 timing probe (diagnostic, REGRESSION_REPORT_v0.9.2.md / KNOWN_RISKS_v0.9.2.md R67).

Same battle state, extended weapon vs template vanilla weapon in hand (as emu_equip_battle_v08 J1 / O1), started at 8
different frame phases (k = 0..7 extra frames before the command). Reports, per phase, whether the whole 1200-frame run
shows the same sequence of distinct screens and how many frames differ exactly. Run on the frozen v0.9 QA ROM and on
the v0.9.2 QA ROM to compare.

usage: [FF6X_PROBE_HPPOKE=1] [FF6X_PROBE_PHASES=n] emu_timing_probe_v092.py <qa.sfc> <qa.manifest.json> <tag>   (writes /tmp/claude-0/probe_<tag>.json)
"""
import sys, os, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(HERE, "tools")); sys.path.insert(0, HERE)
os.environ.setdefault("FF6X_QA_V08_ROOT", '{"0": [2, 1], "1": [2, 2, 0]}')
import emu_equip_battle_v08 as E
from emu_item_tech import T
from emu_item_qa import boot_new_game
from emu_item_battle import labels
qa, man, tag = sys.argv[1:4]
L = labels(man); E.LABELS.update(L)
h = T(qa); boot_new_game(h); E.menu(h, L, [0, 0]); st_all = h.em.get_state()
res = {}
for wid, tpl in ((0x104, 0x20), (0x106, None)):
    c = E.CHARS.index("Edgar") if wid == 0x104 else E.CHARS.index("Shadow")
    h.em.set_state(st_all); h.step(10)
    E.menu(h, L, E.PRESET_PICKS[E.preset_for(c)]); h.run_event([0x8D, c])
    if wid == 0x106:
        E.equip_relic_vanilla(h, c, 0xD3); tpl = int(E.BYID[0x106]["template"], 16)
    E.equip_menu(h, c, wid)
    si = E.party_order(h).index(c)
    if wid == 0x104:
        h.w8(0x1600 + 0x25 * c + 0x16, E.CMD_JUMP)
    E.start_battle(h, si)
    if os.environ.get("FF6X_PROBE_HPPOKE"):      # POKE (as emu_equip_battle_v08 O1): the guards survive and keep acting
        for m in [m for m in range(6) if h.r16(0x3C1C + 8 + 2 * m) not in (0, 0xFFFF)]:
            h.w8(0x3BF4 + 8 + 2 * m, 0x30); h.w8(0x3BF4 + 9 + 2 * m, 0x75)
    st_menu = h.em.get_state()
    out = []
    for k in range(int(os.environ.get("FF6X_PROBE_PHASES", "8"))):
        h.em.set_state(st_menu); h.step(k)
        sa, ha = E.fight_hashes(h, 1200)
        h.em.set_state(st_menu); h.step(k)
        h.w8(0x3CA8 + 2 * si, tpl); h.w8(0x2B86 + 5 * si, tpl)
        bit = 256 + c * 6; h.w8(0x1CF8 + bit // 8, h.r8(0x1CF8 + bit // 8) & ~(1 << (bit % 8)))
        sb, hb = E.fight_hashes(h, 1200)
        same, nd = E.lag_tolerant(ha, hb)
        out.append({"k": k, "same": same, "nd": nd, "runs": E.runs(sa)[:8], "truns": E.runs(sb)[:8]})
    res[f"{wid:03X}"] = out
json.dump(res, open(os.path.join(os.environ.get("FF6X_PROBE_OUT", "/tmp/claude-0"), f"probe_{tag}.json"), "w"), indent=0)
for w, o in res.items():
    print(tag, w, [(x["k"], x["same"], x["nd"]) for x in o])
