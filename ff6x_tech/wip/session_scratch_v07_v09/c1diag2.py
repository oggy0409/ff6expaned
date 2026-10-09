import sys, os, numpy as np
sys.path.insert(0, "/home/user/ff6expaned/ff6x_tech/tools")
from emu_colosseum import *
from emu_menu_nav import Nav, ST
def ram(h):
    h.gd.update_ram(); return np.frombuffer(bytes(h.gd.memory.blocks[0x7E0000]), dtype=np.uint8).copy()
def go(rom, ext, nframes):
    h = T(rom); h.ext_aware = ext; boot_new_game(h)
    h.run_event(sum(([0x80, i] for i in WAGERS), []))
    nv = Nav(h)
    h.call_event(VANILLA_COLO, frames=1)
    nv.wait(ST["COLO_ITEM"], 600); nv.cursor_to(0); h.press("A", 4, 10); nv.wait(0x76, 600)
    nv.cursor_lr(0); h.step(4, ("A",))
    snaps = []; t0 = None
    for t in range(nframes):
        h.step(1)
        if t0 is None and MT.in_battle(h): t0 = t
        snaps.append(ram(h))
    print(rom, "frames", h.f, "t_inbattle", t0, "len", len(snaps[0]))
    return snaps, t0
a, ta = go("final/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc", False, 1400)
b, tb = go("out072/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc", True, 1400)
BAT = lambda x: x[0x2000:0x4000]
np.save("c1a.npy", np.array(a)[:, :0x4000]); np.save("c1b.npy", np.array(b)[:, :0x4000])
for off in (0, 1, -1):
    first = None
    for t in range(max(ta, tb), 1400 - 2):
        if not 0 <= t + off < 1400: continue
        u, v = a[t], b[t + off] if 0 <= t + off < 1400 else None
        d = np.nonzero(BAT(u) != BAT(v))[0]
        if len(d):
            first = (t, [hex(0x2000 + x) for x in d[:30]]); break
    print("offset", off, "first battle-RAM diff", first)
# DP diffs at entry
for off in (0, 1):
    for t in range(max(ta, tb), max(ta, tb) + 400):
        d = np.nonzero(a[t][:0x100] != b[t + off][:0x100])[0]
        if len(d): print("off", off, "t", t, "DP diff", [hex(x) for x in d[:30]]); break
np.save("c1a.npy", np.array(a)[:, :0x4000]); np.save("c1b.npy", np.array(b)[:, :0x4000])
