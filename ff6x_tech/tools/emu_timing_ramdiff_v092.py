#!/usr/bin/env python3
"""TECH v0.9.2 diagnostic (KNOWN_RISKS_v0.9.2.md R67): Sandpiercer Jump vs the template Partisan from the same battle
state (phase k = 0); prints the WRAM bytes that start to differ, frame by frame (the expected hand-item bytes at frame 0,
then the weapon animation number $B7 / $2D71 at the landing, then the ATB / timer bytes one tick apart).

usage: [FF6X_PROBE_MODE=jump|offering] emu_timing_ramdiff_v092.py <qa.sfc> <qa.manifest.json>
"""
import sys, os, json, hashlib
import numpy as np
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(HERE, "tools")); sys.path.insert(0, HERE)
os.environ.setdefault("FF6X_QA_V08_ROOT", '{"0": [2, 1], "1": [2, 2, 0]}')
import emu_equip_battle_v08 as E
from emu_item_tech import T
from emu_item_qa import boot_new_game
from emu_item_battle import labels
qa, man = sys.argv[1:3]
L = labels(man); E.LABELS.update(L)
h = T(qa); boot_new_game(h); E.menu(h, L, [0, 0]); st_all = h.em.get_state()
MODE = os.environ.get("FF6X_PROBE_MODE", "jump")
if MODE == "jump":
    c = E.CHARS.index("Edgar"); wid, tpl = 0x104, 0x20
    h.em.set_state(st_all); h.step(10)
    E.menu(h, L, E.PRESET_PICKS[E.preset_for(c)]); h.run_event([0x8D, c]); E.equip_menu(h, c, wid)
    si = E.party_order(h).index(c)
    h.w8(0x1600 + 0x25 * c + 0x16, E.CMD_JUMP)
    E.start_battle(h, si)
else:                                   # "offering": the emu_equip_battle_v08 O1 state (HP POKEs included)
    c = E.CHARS.index("Shadow"); wid = 0x106; tpl = int(E.BYID[0x106]["template"], 16)
    h.em.set_state(st_all); h.step(10)
    E.menu(h, L, E.PRESET_PICKS[E.preset_for(c)]); h.run_event([0x8D, c])
    E.equip_relic_vanilla(h, c, 0xD3); E.equip_menu(h, c, wid)
    si = E.party_order(h).index(c)
    E.start_battle(h, si)
    for k in [k for k in range(6) if h.r16(0x3C1C + 8 + 2 * k) not in (0, 0xFFFF)]:
        h.w8(0x3BF4 + 8 + 2 * k, 0x30); h.w8(0x3BF4 + 9 + 2 * k, 0x75)
st_menu = h.em.get_state()
def wram():
    h.gd.update_ram(); return np.frombuffer(bytes(h.gd.memory.blocks[0x7E0000])[:0x10000], dtype=np.uint8).copy()
def run(poke):
    h.em.set_state(st_menu)
    if poke:
        h.w8(0x3CA8 + 2 * si, tpl); h.w8(0x2B86 + 5 * si, tpl)
        bit = 256 + c * 6; h.w8(0x1CF8 + bit // 8, h.r8(0x1CF8 + bit // 8) & ~(1 << (bit % 8)))
    h.press("A", 8, 30); h.press("A", 8, 10)
    rs, hs, anim = [], [], []
    for t in range(1200):
        h.step(1); rs.append(wram()); hs.append(hashlib.sha1(np.asarray(h.em.get_screen()).tobytes()).hexdigest()[:12]); anim.append(h.r8(E.ANIM_NO))
    return rs, hs, anim
ra, ha, aa = run(False); rb, hb, ab = run(True)
base = np.nonzero(ra[0] != rb[0])[0]
print("frame0 diffs", [hex(x) for x in base[:40]])
fd = next((t for t in range(1200) if ha[t] != hb[t]), None); print("first screen diff", fd, E.runs(aa)[:10], E.runs(ab)[:10])
seen = set(base.tolist())
for t in range(1200):
    d = set(np.nonzero(ra[t] != rb[t])[0].tolist()) - seen
    if d:
        print("frame", t, "new diffs", [(hex(x), ra[t][x], rb[t][x]) for x in sorted(d)[:30]])
        seen |= d
        if t > (fd or 0) + 5: break
