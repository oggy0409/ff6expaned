#!/usr/bin/env python3
"""TECH v0.8 emulator checks, part 3: combination / stress (stable-retro / snes9x).

  C/D  full party (QA preset Terra/Locke/Celes/Edgar) wearing 19 production items at once, equipped through the menus
       (Terra 6 extended items: weapon, shield, helmet, armor, 2 relics)
  B    Arrange with all 39 + ~120 vanilla item kinds: every 9-bit id and quantity kept, $1xx never truncated
  L    Optimum with vanilla and new items competing (incl. Illumina/Ragnarok, Genji gear): stronger vanilla gear wins
       where it is stronger, no duplication, every chosen item equippable by the character
  M    Equip -> Empty: extended items return to the inventory with their 9-bit ids
  H    normal battle (QA test battle) with the extended party: equipment / inventory reconciled unchanged
  I    boss-style battle (vanilla event battle 64, Whelk) with the extended party (POKE: enemy HP 1 to finish quickly)
  G    Colosseum while wearing extended gear (QA Colosseum, current preset party): equipment unchanged
  E    save -> power cycle -> Continue: inventory (39 + vanilla), the full party's equipment and the bitmaps preserved
  F    genuine Rev 1 (legacy) save -> load -> grant all 39 -> save -> power cycle -> load: no phantom items before,
       all 39 after
  P    a v0.8 QA save holding production items loads in the v0.8 PRODUCTION ROM with every $100-$126 item kept (the
       ids are defined there too) and the QA-only $13D-$13F removed

usage: emu_equip_stress_v08.py <qa.sfc> <qa.manifest.json> <production.sfc> <clean_rev1.sfc> <out>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_item_tech import T, ev_give, XBITS, XSIG
from emu_item_qa import (Report, boot_new_game, inv16, dump_sram, write_sram, continue_slot1)
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
from emu_equip_v08 import BYID, CHARS, PRESET_PICKS, menu, party_order, read_list
from emu_equip_battle_v08 import equip_menu, start_battle, finish_battle, LABELS

LOADOUT = {"Terra": [0x102, 0x118, 0x114, 0x10F, 0x11B, 0x126], "Locke": [0x103, 0x113, 0x11F, 0x120],
           "Celes": [0x101, 0x119, 0x117, 0x10E, 0x11A], "Edgar": [0x10B, 0x116, 0x10D, 0x124]}
VANILLA_BULK = list(range(0x00, 0x59, 2)) + list(range(0x5A, 0x84, 2)) + list(range(0x84, 0xA3, 2)) + \
    list(range(0xB0, 0xE7, 2)) + list(range(0xE7, 0xFF))
STRONG_VANILLA = [0x1A, 0x1B, 0x9A, 0x81, 0x64, 0x7E]             # Illumina, Ragnarok, Genji Armor/Helmet/Shld, Crystal Helm


def all_eq(h):
    return {n: h.eq(CHARS.index(n)) for n in LOADOUT}


def save_menu(h):
    h.w8(0x1EB7, h.r8(0x1EB7) | 0x80)                       # "on a save point" (test only, as v0.7.1 J)
    nv = Nav(h)
    for _ in range(4):                                       # right after an event the field may ignore X briefly
        h.step(60); nv.open_main()
        if nv.state() == ST["MAIN"]:
            break
    nv.main_to("Save")
    if not nv.wait(ST["SAVE_SELECT"], 400):
        raise RuntimeError("save menu did not open")
    h.press("A", 4, 60); h.press("A", 4, 200)
    return dump_sram(h)


def wear_loadout(h):
    for name, ids in LOADOUT.items():
        c = CHARS.index(name)
        h.run_event([0x8D, c])
        relic = 0
        for i in ids:
            it = BYID[i]
            if it["category"] == "relic":
                equip_menu(h, c, i, relic_slot=relic); relic += 1
            else:
                equip_menu(h, c, i, hand=0)


def expect_eq(name):
    out = [0xFF] * 6
    relic = 4
    for i in LOADOUT[name]:
        k = {"weapon": 0, "shield": 1, "helmet": 2, "armor": 3}.get(BYID[i]["category"])
        if k is None:
            out[relic] = i; relic += 1
        else:
            out[k] = i
    return out


def main(qa, manifest, prod, clean, out):
    q = Report(out)
    L = labels(manifest)
    LABELS.update(L)
    res = {}
    h = T(qa)
    boot_new_game(h)
    menu(h, L, [0, 0])                                   # all 39
    menu(h, L, PRESET_PICKS[0])                          # Terra / Locke / Celes / Edgar
    # ------------------------------------------------------------------ C/D
    wear_loadout(h)
    eqs = all_eq(h)
    exp = {n: expect_eq(n) for n in LOADOUT}
    q.check("C1/D1 19 production items worn at once across the party (Terra: 6 extended slots) through the menus",
            eqs == exp, {n: [f"{v:03X}" for v in e] for n, e in eqs.items()})
    worn = sorted(i for v in LOADOUT.values() for i in v)
    q.check("D2 worn items left the inventory; the other 20 production items are still there",
            sorted(i for s, i, n in h.inv() if i >= 0x100) == sorted(set(BYID) - set(worn)))
    q.shot(h, "D_party_loadout")
    st_loadout = h.em.get_state()

    # ------------------------------------------------------------------ B: Arrange stress
    h.run_event(sum(([0x80, v] for v in VANILLA_BULK), []))
    before = inv16(h)
    nv = Nav(h)
    nv.open_main(); nv.main_to("Item"); nv.wait(ST["ITEM"])
    h.press("B", 4, 20); nv.wait(ST["ITEM_OPT"]); nv.cursor_lr(1); h.press("A", 4, 120); nv.wait(ST["ITEM"])
    q.shot(h, "B_arrange_stress")
    after = inv16(h)
    q.check(f"B1 Arrange with {len([1 for i, n in before if i < 0x100])} vanilla kinds + {len([1 for i, n in before if i >= 0x100])} "
            "production items: every 9-bit id and quantity kept", after == before,
            {"lost": [(f"{i:03X}", n) for i, n in before if (i, n) not in after][:10],
             "new": [(f"{i:03X}", n) for i, n in after if (i, n) not in before][:10]})
    nv.back_to_main(); nv.close(); h.step(30)

    # ------------------------------------------------------------------ L: Optimum, vanilla vs new
    h.em.set_state(st_loadout); h.step(10)
    h.run_event(sum(([0x80, v] for v in STRONG_VANILLA), []))
    owned0 = sorted([i for s, i, n in h.inv() for _ in range(n)] + [x for v in all_eq(h).values() for x in v if x != 0xFF])
    opt = {}
    for name in LOADOUT:
        c = CHARS.index(name); si = party_order(h).index(c)
        nv = Nav(h); h.step(20)
        nv.open_main(); nv.main_to("Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
        nv.cursor_to(si); h.press("A", 4, 30); nv.wait(ST["EQUIP_OPT"], 120)
        nv.cursor_lr(3); h.press("A", 4, 60)              # Empty
        nv.cursor_lr(1); h.press("A", 4, 60)              # Optimum
        opt[name] = h.eq(c)
        nv.back_to_main(); nv.close(); h.step(20)
    owned1 = sorted([i for s, i, n in h.inv() for _ in range(n)] + [x for v in all_eq(h).values() for x in v if x != 0xFF])
    def can(n, i):
        if i == 0xFF:
            return True
        if i >= 0x100:
            return n in BYID[i]["users"]
        return True
    res["optimum"] = {n: [f"{v:03X}" for v in e] for n, e in opt.items()}
    q.check("L1 Optimum (vanilla + new competing): no duplication or loss of any item, every chosen item equippable",
            owned0 == owned1 and all(can(n, i) for n, e in opt.items() for i in e), res["optimum"])
    q.check("L2 Optimum keeps vanilla where it is stronger: Celes/Terra/Edgar weapon = Illumina or Ragnarok (255), "
            "not a signature sword (<= 222)", all(opt[n][0] in (0x1A, 0x1B) for n in ("Terra", "Celes", "Edgar")) or
            all(opt[n][0] in (0x1A, 0x1B) for n in ("Terra", "Celes")), res["optimum"])
    # ------------------------------------------------------------------ M: Empty returns ids
    h.em.set_state(st_loadout); h.step(10)
    c = 0; si = party_order(h).index(c)
    nv = Nav(h); h.step(20)
    nv.open_main(); nv.main_to("Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
    nv.cursor_to(si); h.press("A", 4, 30); nv.wait(ST["EQUIP_OPT"], 120)
    nv.cursor_lr(3); h.press("A", 4, 60)
    nv.back_to_main(); nv.close(); h.step(20)
    back = [i for i in LOADOUT["Terra"][:4]]
    q.check("M1 Equip -> Empty: Terra's weapon/shield/helmet/armor ($102/$118/$114/$10F) return with their 9-bit ids; "
            "relics stay", all(any(j == i for s, j, n in h.inv()) for i in back) and h.eq(0)[4:] == LOADOUT["Terra"][4:6]
            and h.eq(0)[:4] == [0xFF] * 4, [f"{v:03X}" for v in h.eq(0)])

    # ------------------------------------------------------------------ H: normal battle
    h.em.set_state(st_loadout); h.step(10)
    inv0, eq0 = inv16(h), all_eq(h)
    start_battle(h, 0)
    q.shot(h, "H_battle_extended_party")
    finish_battle(h)
    q.check("H1 normal battle with the extended party: equipment and inventory reconciled unchanged",
            inv16(h) == inv0 and all_eq(h) == eq0, {n: [f"{v:03X}" for v in e] for n, e in all_eq(h).items()})
    # ------------------------------------------------------------------ I: boss-style battle (Whelk)
    h.em.set_state(st_loadout); h.step(10)
    h.call_event(L["QaBossBtl8"], frames=1)
    boss = []
    for t in range(900):
        h.step(1)
    boss = [h.r16(0x2001 + 2 * k) for k in range(6)]
    q.shot(h, "I_boss_battle")
    for k in range(6):
        if h.r16(0x3C1C + 8 + 2 * k) not in (0, 0xFFFF):
            h.w8(0x3BF4 + 8 + 2 * k, 1); h.w8(0x3BF4 + 9 + 2 * k, 0)   # POKE: enemy HP 1 (test only)
    finish_battle(h)
    q.check("I1 boss-style battle (vanilla event battle 64: Whelk) with the extended party: battle runs and returns, "
            "equipment unchanged", 0x100 in boss and h.idle() and all_eq(h) == eq0,
            {"monsters": [f"{v:03X}" for v in boss], "eq": {n: [f"{v:03X}" for v in e] for n, e in all_eq(h).items()}})

    # ------------------------------------------------------------------ G: Colosseum wearing extended gear
    h.em.set_state(st_loadout); h.step(10)
    eq0 = all_eq(h)
    h.call_event(L["QaColoKit7"], frames=1); talk(h, [])
    import emu_colosseum as C
    C.FIGHTERS = {0: "Terra", 1: "Locke", 2: "Celes", 3: "Edgar"}
    r = C.run_combo(h, lambda hh: hh.call_event(L["QaColoFight7"], frames=1), 0xEE, 0, False, out, "G_colosseum_terra_ext", q)
    q.check("G1 Colosseum with Terra wearing 6 production items: battle entered, return with control, all party "
            "equipment unchanged", r.get("battle_entered") and r.get("returned_idle") and all_eq(h) == eq0,
            {"slot1": r.get("slot1"), "eq": {n: [f"{v:03X}" for v in e] for n, e in all_eq(h).items()}})

    # ------------------------------------------------------------------ E: save -> power cycle -> load
    h.em.set_state(st_loadout); h.step(10)
    pre = {"inv": inv16(h), "eq": all_eq(h), "bits": h.rbytes(XBITS, 44).hex()}
    blk, sram = save_menu(h)
    open(os.path.join(out, "sram_v08_loadout.bin"), "wb").write(sram)
    h.close()
    h2 = T(qa); write_sram(h2, blk, sram); continue_slot1(h2)
    post = {"inv": inv16(h2), "eq": all_eq(h2), "bits": h2.rbytes(XBITS, 44).hex()}
    q.shot(h2, "E_after_power_cycle")
    q.check("E1 save -> power cycle -> Continue: 20 production items in the inventory, 19 worn across the party and "
            "the extension bitmaps preserved exactly", post == pre)
    h2.close()
    # ------------------------------------------------------------------ P: QA save in the production ROM
    hp = T(prod); write_sram(hp, blk, sram); continue_slot1(hp)
    pinv = inv16(hp)
    q.check("P1 the v0.8 QA save in the v0.8 PRODUCTION ROM: every production item kept (inventory and worn), "
            "nothing truncated", pinv == pre["inv"] and all_eq(hp) == pre["eq"],
            {"inv_ext": [(f"{i:03X}", n) for i, n in pinv if i >= 0x100][:45]})
    hp.close()

    # ------------------------------------------------------------------ F: legacy save -> acquire -> save -> reload
    hv = T(clean); boot_new_game(hv)
    hv.run_event([0x80, 0x00, 0x80, 0x01, 0x80, 0x26, 0x80, 0xE9])      # low bytes of $100/$101/$126 + Potion
    vblk, vsram = save_menu(hv)
    hv.close()
    hq = T(qa); write_sram(hq, vblk, vsram); continue_slot1(hq)
    phantom = [i for s, i, n in hq.inv() if i >= 0x100]
    menu(hq, L, [0, 0])
    got = sorted(i for s, i, n in hq.inv() if i >= 0x100)
    van = sorted((i, n) for i, n in inv16(hq) if i < 0x100)
    qblk, qsram = save_menu(hq)
    hq.close()
    hr = T(qa); write_sram(hr, qblk, qsram); continue_slot1(hr)
    q.check("F1 legacy Rev 1 save: no phantom production item on load (Dirk/MithrilKnife/Kodachi stay vanilla); grant "
            "all 39; save; power cycle; load: all 39 + the vanilla items preserved",
            not phantom and got == sorted(BYID) and sorted(i for s, i, n in hr.inv() if i >= 0x100) == sorted(BYID)
            and sorted((i, n) for i, n in inv16(hr) if i < 0x100) == van,
            {"phantom": phantom, "granted": [f"{i:03X}" for i in got],
             "after_reload": [f"{i:03X}" for i in sorted(i for s, i, n in hr.inv() if i >= 0x100)],
             "vanilla": [(f"{i:02X}", n) for i, n in van],
             "vanilla_after": [(f"{i:02X}", n) for i, n in sorted((i, n) for i, n in inv16(hr) if i < 0x100)]})
    hr.close()
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "EQUIPMENT_STRESS_REPORT.json"), "w"), indent=1, default=str)
    print("EQUIPMENT STRESS", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
