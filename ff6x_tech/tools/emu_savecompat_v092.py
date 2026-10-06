#!/usr/bin/env python3
"""TECH v0.9.1 / v0.9.2 save compatibility with the accepted TECH v0.9 (stable-retro / snes9x).

A save made in the frozen v0.9 QA ROM (item-tech-v0.9: 39 signature equipment, 8 consumables x10, the 5 key items,
GP, one extended relic equipped) is loaded after a power cycle in
  * the v0.9.1 production ROM (production) and
  * the v0.9.2 QA ROM (item-tech)
and must come back identical: inventory (9-bit ids + quantities), equipment of every character record, extended-item
bitmap + signature, FF6X rare-item block + signature, GP. The v0.9.1 transient bytes $1E23-$1E26 read 0 after the
load (ClrTrans). A Gaia Tonic from the old save then heals exactly 1500 HP in the field (the new effect applies to
items carried over from v0.9).

usage: emu_savecompat_v092.py <item-tech-v0.9 .sfc> <its manifest> <production v0.9.1 .sfc> <item-tech v0.9.2 .sfc> <out>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, inv16, dump_sram, write_sram, continue_slot1
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
from emu_cons_v09 import field_use, hp, qty, gp, CHAR_REC

XBITS, XRARE = 0x1CF8, 0x1E1D


def snapshot(h):
    return {"inv": inv16(h), "eq": [h.eq(r) for r in range(16)], "xbits": h.rbytes(XBITS, 48).hex(),
            "rare": h.rbytes(XRARE, 6).hex(), "gp": gp(h)}


def save_slot1(h):
    for _ in range(600):
        if h.idle():
            break
        h.step(1)
    h.step(60)
    h.w8(0x1EB7, h.r8(0x1EB7) | 0x80)                      # POKE (test only): "on a save point"
    nv = Nav(h)
    for _ in range(6):
        h.step(60); nv.open_main()
        if nv.state() == ST["MAIN"]:
            break
    nv.main_to("Save"); nv.wait(ST["SAVE_SELECT"], 400)
    h.press("A", 4, 60); h.press("A", 4, 200)


def main(old_rom, old_manifest, prod, qa92, out):
    q = Report(out)
    L = labels(old_manifest)
    h = T(old_rom)
    boot_new_game(h)
    h.call_event(L["QaAccess6"], frames=1); talk(h, [2, 0, 0])      # v0.9 stress: all 39 + 10 x 8 consumables + keys + GP
    h.call_event(L["QaAccess6"], frames=1); talk(h, [0, 2, 2, 1, 0])  # preset P1
    h.run_event([0x66, 0x1B, 0x01])                               # one more Maduin's Locket ...
    rec = 0                                                     # ... equipped as Terra's relic 1 (POKE: slot + high bit)
    for s in range(256):
        if h.r8(0x1869 + s) == 0x1B and h.bit(s):
            h.w8(0x1869 + s, 0xFF); h.w8(0x1969 + s, 0)
            h.w8(XBITS + (s >> 3), h.r8(XBITS + (s >> 3)) & ~(1 << (s & 7)))
            break
    h.w8(0x161F + 37 * rec + 4, 0x1B)
    n = 256 + rec * 6 + 4
    h.w8(XBITS + (n >> 3), h.r8(XBITS + (n >> 3)) | (1 << (n & 7)))
    pre = snapshot(h)
    save_slot1(h)
    q.shot(h, "saved_in_v09")
    blk, sram = dump_sram(h)
    h.close()
    q.check("C0 v0.9 save prepared: 39 equipment + 8 consumables + key items + an equipped extended relic",
            len([i for i, n in pre["inv"] if i >= 0x100]) >= 40 and pre["eq"][0][4] == 0x11B and pre["rare"][:1] != "00",
            {"ext_items": len([i for i, n in pre["inv"] if i >= 0x100]), "eq0": pre["eq"][0], "rare": pre["rare"]})
    for tag, rom in (("production v0.9.1", prod), ("QA v0.9.2", qa92)):
        h2 = T(rom)
        write_sram(h2, blk, sram)
        continue_slot1(h2)
        q.shot(h2, f"loaded_{tag.split()[0]}")
        post = snapshot(h2)
        trans = h2.rbytes(0x1E23, 4).hex()
        diff = {k: (pre[k] if k != "inv" else len(pre[k]), post[k] if k != "inv" else len(post[k]))
                for k in pre if pre[k] != post[k]}
        q.check(f"C1 v0.9 save -> power cycle -> {tag}: inventory (9-bit ids, quantities), equipment of all 16 records, "
                "extended bitmap + signature, rare block + signature, GP identical; v0.9.1 transient bytes $1E23-$1E26 = 0",
                not diff and trans == "00000000", {"diff": diff, "transient": trans})
        for _ in range(600):
            if h2.idle():
                break
            h2.step(1)
        b = CHAR_REC
        v = (h2.r16(b + 11) & 0xC000) | 3000
        h2.w8(b + 11, v & 0xFF); h2.w8(b + 12, v >> 8); h2.w8(b + 9, 5); h2.w8(b + 10, 0)
        n0 = qty(h2, 0x127)
        field_use(h2, 0x127, 0)
        q.check(f"C2 {tag}: a Gaia Tonic carried over from the v0.9 save heals exactly 1500 HP in the field",
                hp(h2) == 1505 and qty(h2, 0x127) == n0 - 1, {"hp": hp(h2), "qty": (n0, qty(h2, 0x127))})
        h2.close()
    rep = {"checks": q.checks, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "SAVE_COMPAT_REPORT_v092.json"), "w"), indent=1, default=str)
    print("SAVE COMPAT v0.9 -> v0.9.1/v0.9.2", "PASS" if rep["all_pass"] else "FAIL",
          f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
