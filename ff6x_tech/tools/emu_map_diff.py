#!/usr/bin/env python3
"""Differential map-load regression (Claude-side emulator check, NOT user QA).
Loads the same start state in two ROMs, teleports through a list of vanilla maps with the
same event-command injection, and dumps per-map fingerprints:
  map index, map property RAM $0520-$0540, NPC object data (event ptr, position, gfx,
  switch-derived visibility), BG1/BG2/BG3 RAM tilemaps, layout decompression buffer.
usage: emu_map_diff.py dump <rom> <state> <out.json> [maps...]
       emu_map_diff.py compare <a.json> <b.json>"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
import emu_celes_suite as S

def fp(h):
    h.gd.update_ram()
    mem = lambda a, n: bytes(h.gd.memory.extract(a + i, '|u1') for i in range(n))
    objs = []
    for o in range(0x10, 0x30):
        b = 0x7E0867 + o * 0x29
        d = mem(b, 0x29)
        objs.append(d.hex())
    static = []
    for o in range(0x10, 0x30):
        d = bytes.fromhex(objs[o - 0x10])
        moving = (d[0x15] & 0x0F) not in (0, 4)          # $087C movement type (0 none, 4 activated)
        st = [d[0x00] & 0xC0, d[0x0E], d[0x11], d[0x12], d[0x19], d[0x1A], d[0x22], d[0x23], d[0x24], d[0x26], d[0x27]]
        if not moving:
            st += [(d[0x03] | d[0x04] << 8) >> 4, (d[0x06] | d[0x07] << 8) >> 4]
        static.append(bytes(st).hex())
    return {"map": h.r16(0x82), "props": mem(0x7E0520, 33).hex(), "objs_static": static,
            "objs": hashlib.sha1("".join(objs).encode()).hexdigest(), "objs_raw": objs,
            "evptrs": [mem(0x7E0867 + o * 0x29 + 0x22, 3).hex() for o in range(0x10, 0x30)],
            "bg": hashlib.sha1(mem(0x7F0000, 0x10000)).hexdigest(),
            "tileprops": hashlib.sha1(mem(0x7E7600, 0x200)).hexdigest()}

if sys.argv[1] == "dump":
    rom, state, out = sys.argv[2], sys.argv[3], sys.argv[4]
    maps = [int(x, 16) for x in sys.argv[5:]]
    h = H(rom); h.em.set_state(open(state, 'rb').read())
    if os.environ.get("FF6X_XINIT") == "1":      # TECH v0.7.x: New Game metadata init (see emu_monster_diff.py)
        for a in range(0x1CF8, 0x1D24): h.w8(a, 0)
        for i, v in enumerate((0x58, 0x49, 0x01, 0xFE)): h.w8(0x1D24 + i, v)
    h.step(2)
    res = {}
    for m in maps:
        S.teleport(h, m, 10, 10, "DOWN"); h.step(150)
        res[f"{m:03X}"] = fp(h)
    json.dump(res, open(out, "w"), indent=0)
else:
    a, b = json.load(open(sys.argv[2])), json.load(open(sys.argv[3]))
    bad = {k: [f for f in a[k] if a[k][f] != b[k][f] and f != "objs_raw"] for k in a if a[k] != b[k]}
    detail = {}
    for k in bad:
        if "objs_raw" in a[k]:
            for o, (x, y) in enumerate(zip(a[k]["objs_raw"], b[k]["objs_raw"])):
                if x != y:
                    xb, yb = bytes.fromhex(x), bytes.fromhex(y)
                    detail.setdefault(k, []).append((hex(0x10 + o), [f"+{i:02X}:{xb[i]:02X}/{yb[i]:02X}" for i in range(len(xb)) if xb[i] != yb[i]]))
    for k, v in list(detail.items())[:12]: print("  detail", k, v[:4])
    print("maps compared", len(a), "identical", len(a) - len(bad), "different", len(bad))
    for k, v in list(bad.items())[:20]: print(" ", k, v)
    sys.exit(1 if bad else 0)
