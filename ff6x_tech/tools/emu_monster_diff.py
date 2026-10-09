#!/usr/bin/env python3
"""TECH v0.5 differential vanilla-formation regression (Claude-side EMULATOR check, NOT user QA).

Same start state (first field control, map $013) in two ROMs; for every requested vanilla
formation the same event command `battle $FE` is injected and the field battle index $11E0
is overwritten with the formation number during the 32-frame battle mosaic (before
Battle_ext / LoadBattleProp). At battle start (wBattleID == formation, monster records loaded)
plus a fixed delay, a fingerprint of everything the battle engine loads from the relocated
monster / formation tables is taken:

  formation aux     $2F48-$2F4B, wBattleMonsters $2F4E-$2F5D? (copied 16 bytes)
  btlgfx monster    $2001-$200C (monster IDs as seen by the graphics engine)
  TargetProp1/2     monster entries (y = 8..19) of every 20-byte block in
                    $3204-$35EB and $3AA0-$3EAF (HP/MP/stats/level/elements/status/
                    steal+drop items/AI script pointers/control/special anim/...)
  battle screen     SHA-1 of the frame buffer (sprites/palettes/names) at +D2 frames

usage: emu_monster_diff.py mkstate <rom> <state_out>
       emu_monster_diff.py dump <rom> <state> <out.json> <first> <last>
       emu_monster_diff.py compare <a.json> <b.json> [report.json]"""
import sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
import emu_celes_suite as S

# D1: frames after battle start before the engine-data fingerprint. TECH v0.7.1 battle init does a bit lookup
# per inventory slot (extended slots -> empty), which moves the end of LoadBattleProp by up to a frame; use
# MONDIFF_D1=30 (same value for both ROMs) when comparing against a v0.7.x ROM.
D1, D2 = int(os.environ.get("MONDIFF_D1", "4")), 90
# FF6X_XINIT=1 (TECH v0.7.x ROM under test only): the shared start state was made on the reference ROM, whose New
# Game copies the Bushido names to $1CF8-$1D27. A v0.7.x New Game writes zero metadata + signature there instead
# (and every load sanitizes it), so apply exactly that to the state before the run.
XINIT = os.environ.get("FF6X_XINIT") == "1"


def xinit(h):
    if XINIT:
        for a in range(0x1CF8, 0x1D24):
            h.w8(a, 0)
        for i, v in enumerate((0x58, 0x49, 0x01, 0xFE)):
            h.w8(0x1D24 + i, v)


def mem(h, a, n):
    h.gd.update_ram()
    return bytes(h.gd.memory.extract(0x7E0000 + a + i, '|u1') for i in range(n))


def fp(h):
    t1 = mem(h, 0x3204, 0x35EC - 0x3204)
    t2 = mem(h, 0x3AA0, 0x3EB0 - 0x3AA0)
    mons = lambda blob, base: {f"{base + 20 * k + 8:04X}": blob[20 * k + 8:20 * k + 20].hex() for k in range(len(blob) // 20)}
    return {"aux": mem(h, 0x2F48, 4).hex(), "btlgfx_ids": mem(h, 0x2001, 12).hex(),
            "tp1": mons(t1, 0x3204), "tp2": mons(t2, 0x3AA0)}


def fp_gfx(h):
    return {
            # TECH v0.6: btlgfx graphics/palette outputs (decoded monster tiles, per-slot palette numbers,
            # loaded palettes, palette bytes copied for the battle, sprite sizes, overlap)
            "gfx_buffer_sha1": hashlib.sha1(mem(h, 0xAE3F, 0x2000)).hexdigest(),
            "pal_per_slot": mem(h, 0x8117, 12).hex(), "pal_loaded": mem(h, 0x8123, 6).hex(),
            "pal_bytes": mem(h, 0x7F00, 0x60).hex(), "sizes": mem(h, 0x812F, 12).hex(), "overlap": mem(h, 0x8057, 12).hex()}


def run_one(h, snap, f):
    h.em.set_state(snap); xinit(h); h.step(2)
    for i, v in enumerate([0x4D, 0xFE, 0x3F, 0xFE]):
        h.gd.memory.assign(S.SCRIPT_RAM + i, '|u1', v)
    S.inject(h, S.SCRIPT_RAM)
    started = False
    for t in range(900):
        if t < 26:
            h.w8(0x11E0, f & 0xFF); h.w8(0x11E1, f >> 8)
        h.step(1)
        if h.r16(0x3ED4) == f and h.r16(0x3BF4) != 0xFFFF and t > 26:
            started = True; break
    if not started:
        return {"started": False}
    h.step(D1)
    r = fp(h)
    h.step(D2)
    r.update(fp_gfx(h))                 # btlgfx outputs are complete once the battle has faded in
    r["screen"] = hashlib.sha1(h.em.get_screen().tobytes()).hexdigest()
    r["started"] = True
    return r


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "mkstate":
        from emu_qa_access import boot_new_game
        h = H(sys.argv[2]); boot_new_game(h, "/tmp"); h.step(60)
        assert h.r16(0x82) == 0x013
        open(sys.argv[3], "wb").write(h.em.get_state())
    elif cmd == "dump":
        rom, state, out, a, b = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5], 16), int(sys.argv[6], 16)
        h = H(rom); snap = open(state, "rb").read()
        res = {}
        for f in range(a, b + 1):
            res[f"{f:03X}"] = run_one(h, snap, f)
        json.dump(res, open(out, "w"))
    else:
        A = {}; B = {}
        for p in sys.argv[2].split(","): A.update(json.load(open(p)))
        for p in sys.argv[3].split(","): B.update(json.load(open(p)))
        rep = {"formations": len(A), "identical_engine_data": 0, "identical_screen": 0, "not_started_both": [],
               "engine_diffs": {}, "screen_diffs": []}
        for k in sorted(A):
            x, y = A[k], B[k]
            if not x["started"] or not y["started"]:
                if x["started"] == y["started"]: rep["not_started_both"].append(k)
                else: rep["engine_diffs"][k] = "started mismatch"
                continue
            d = []
            for fld in ("aux", "btlgfx_ids", "gfx_buffer_sha1", "pal_per_slot", "pal_loaded", "pal_bytes", "sizes", "overlap"):
                if fld not in x: continue
                if x[fld] != y[fld]: d.append(fld)
            for tb in ("tp1", "tp2"):
                for addr in x[tb]:
                    if x[tb][addr] != y[tb][addr]:
                        xb, yb = bytes.fromhex(x[tb][addr]), bytes.fromhex(y[tb][addr])
                        d += [f"${int(addr, 16) + i:04X}:{xb[i]:02X}/{yb[i]:02X}" for i in range(12) if xb[i] != yb[i]]
            if d: rep["engine_diffs"][k] = d
            else: rep["identical_engine_data"] += 1
            if x["screen"] == y["screen"]: rep["identical_screen"] += 1
            else: rep["screen_diffs"].append(k)
        print(json.dumps({k: (v if k != "engine_diffs" else dict(list(v.items())[:15])) for k, v in rep.items()}, indent=1)[:4000])
        if len(sys.argv) > 4: json.dump(rep, open(sys.argv[4], "w"), indent=1)
        sys.exit(1 if rep["engine_diffs"] else 0)
