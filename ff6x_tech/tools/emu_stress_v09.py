#!/usr/bin/env python3
"""TECH v0.9 emulator checks, part 4: combination / stress / save migration / vanilla item regression
(stable-retro / snes9x).

  A  QA "Grant everything": 39 equipment + 8 consumables x10 + the 5 key items in one inventory
  B  19 signature items worn across the party (menus) next to the consumables
  C  battle with everything: Item list = consumables + vanilla only; a Gaia Tonic used; battle end: inventory
     = before - 1 Gaia Tonic, worn equipment unchanged
  D  Arrange with everything + ~120 vanilla kinds: every 9-bit id and quantity kept
  E  Optimum (Terra, Locke) with consumables in the inventory: no duplication / loss
  F  extended shop with everything: owned counts, buy 3 Iron Ration, sell 2 Gaia Tonic
  G  Colosseum (QA kit, current party wearing signature gear): battle entered / returned, worn gear unchanged,
     consumables / equipment never offered as a wager
  H  save -> power cycle -> Continue: inventory (equipment + consumables), worn gear, rare items, bitmaps preserved
  I  the v0.9 QA save in the v0.9 PRODUCTION ROM: everything defined in production kept
  J  genuine Rev 1 save holding the vanilla katanas $27-$2E (the consumables' low bytes) + Potions -> v0.9: the
     katanas stay katanas, no phantom consumable / rare item
  K  TECH v0.7.3 QA save (QA equipment $13D-$13F) -> v0.9 QA ROM: kept
  L  TECH v0.8 QA save (39 equipment, 19 worn) -> v0.9 QA and PRODUCTION: kept, nothing reset
  M  v0.9 save -> v0.8 PRODUCTION (downgrade, informative): consumables removed cleanly (undefined there, never
     aliased to katanas), equipment kept
  N  bitmap consistency after the whole run (no bit on an empty slot, every extended id defined)
  O  GIVE x120 of one consumable: stack capped at 99
  P  inventory full: GIVE of a consumable not owned changes nothing
  Q  vanilla Potion / Fenix Down in battle (marker 0 entries) still work
  R  vanilla Potion / Antidote in the field menu still work
  S  vanilla shop ($48): buy and sell a vanilla item
  T  vanilla event give / take ($80 / $81) of an item whose low byte is shared with a consumable / equipment

usage: emu_stress_v09.py <out dir with the built ROMs + manifests> <clean_rev1.sfc> <out>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T, ev_give, XBITS
from emu_item_qa import Report, boot_new_game, inv16, write_sram, continue_slot1
from emu_item_battle import labels, talk, to_terra, bslot
from emu_menu_nav import Nav, ST
import emu_equip_v08 as E8
from emu_equip_battle_v08 import equip_menu, finish_battle, LABELS
from emu_equip_stress_v08 import save_menu, LOADOUT, VANILLA_BULK, expect_eq
from emu_cons_battle_v09 import choose_item, run_action, start as battle_start
from emu_cons_v09 import field_use, open_items

CONS = json.load(open(os.path.join(HERE, "items/production_v09/consumables.json")))["items"]
CIDS = sorted(int(c["id"], 16) for c in CONS)
EQIDS = sorted(E8.BYID)


def menu(h, L, picks):
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def qty(h, i):
    return sum(n for s, j, n in h.inv() if j == i)


def gp(h):
    return h.r8(0x1860) | h.r8(0x1861) << 8 | h.r8(0x1862) << 16


def all_eq(h):
    return {n: h.eq(E8.CHARS.index(n)) for n in LOADOUT}


def rare(h):
    return [20 + k for k in range(32) if h.r8(0x1E1D + (k >> 3)) >> (k & 7) & 1]


def wear(h):
    for name, ids in LOADOUT.items():
        c = E8.CHARS.index(name)
        h.run_event([0x8D, c])
        relic = 0
        for i in ids:
            if E8.BYID[i]["category"] == "relic":
                equip_menu(h, c, i, relic_slot=relic); relic += 1
            else:
                equip_menu(h, c, i, hand=0)


def stale_bits(h, defined):
    bad = [("inv", s) for s in range(256) if h.bit(s) and (h.r8(0x1869 + s) == 0xFF or (0x100 | h.r8(0x1869 + s)) not in defined)]
    for rec in range(16):
        for k in range(6):
            if h.bit(256 + rec * 6 + k) and h.r8(0x161F + rec * 37 + k) == 0xFF:
                bad.append(("eq", rec, k))
    return bad


def leave(h, n=6):
    for _ in range(n):
        h.press("B", 4, 30)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)


def main(odir, clean, out):
    q = Report(out)
    QA = os.path.join(odir, "FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc")
    PROD = os.path.join(odir, "FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc")
    QA8 = os.path.join(odir, "FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc")
    PROD8 = os.path.join(odir, "FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc")
    QA73 = os.path.join(odir, "FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.sfc")
    L = labels(QA[:-4] + ".manifest.json")
    LABELS.update(L)
    defined = set(EQIDS) | set(CIDS) | {0x13D, 0x13E, 0x13F}
    res = {}
    # ------------------------------------------------------------------ A
    h = T(QA)
    boot_new_game(h)
    st_new = h.em.get_state()
    menu(h, L, [2, 0, 0])
    q.check("A1 QA 'Grant everything': 39 equipment x1, 8 consumables x10, 5 key items, +20000 GP",
            all(qty(h, i) == 1 for i in EQIDS) and all(qty(h, i) == 10 for i in CIDS) and rare(h) == [20, 21, 22, 23, 24],
            {"ext": len([1 for s, i, n in h.inv() if i >= 0x100]), "rare": rare(h)})
    menu(h, L, [0, 2, 2, 1, 0])                                      # P1
    # ------------------------------------------------------------------ B
    wear(h)
    eqs = all_eq(h)
    q.check("B1 19 signature items worn across the party (menus) with the consumables in the inventory",
            eqs == {n: expect_eq(n) for n in LOADOUT}, {n: [f"{v:03X}" for v in e] for n, e in eqs.items()})
    st_full = h.em.get_state()
    # ------------------------------------------------------------------ C
    inv0, eq0 = inv16(h), all_eq(h)
    battle_start(h, L)
    ents = [(e[0] | (0x100 if e[1] & 1 else 0)) for e in (bslot(h, s) for s in range(256)) if e[0] != 0xFF]
    entry = next(s for s in range(256) if bslot(h, s)[0] == 0x27 and bslot(h, s)[1] & 1)
    choose_item(h, entry)
    run_action(h, q, "C_gaia", 700)
    finish_battle(h)
    exp = [(i, n - 1 if i == 0x127 else n) for i, n in inv0]
    q.check("C1 battle with everything: Item list = the 8 consumables + vanilla (no signature equipment); after using "
            "one Gaia Tonic the extended inventory is the old one minus that unit, worn gear unchanged, vanilla items "
            "kept (+ anything stolen / dropped: Locke's Raider Knife steals on hit)",
            sorted(i for i in ents if i >= 0x100) == CIDS and all_eq(h) == eq0 and
            [x for x in inv16(h) if x[0] >= 0x100] == [x for x in exp if x[0] >= 0x100] and
            all(x in inv16(h) or any(y[0] == x[0] and y[1] >= x[1] for y in inv16(h)) for x in exp if x[0] < 0x100),
            {"list_ext": [f"{i:03X}" for i in ents if i >= 0x100],
             "inv_diff": [(f"{i:03X}", n) for i, n in inv16(h) if (i, n) not in exp][:10],
             "missing": [(f"{i:03X}", n) for i, n in exp if (i, n) not in inv16(h)][:10],
             "eq_same": all_eq(h) == eq0})
    # ------------------------------------------------------------------ D
    h.em.set_state(st_full); h.step(10)
    h.run_event(sum(([0x80, v] for v in VANILLA_BULK), []))
    before = inv16(h)
    nv = Nav(h)
    open_items(h, nv)
    h.press("B", 4, 20); nv.wait(ST["ITEM_OPT"]); nv.cursor_lr(1); h.press("A", 4, 120); nv.wait(ST["ITEM"])
    q.shot(h, "D_arrange_everything")
    after = inv16(h)
    nv.back_to_main(); nv.close(); h.step(30)
    q.check(f"D1 Arrange with {len(before)} item kinds (vanilla + 20 equipment + 8 consumables): every 9-bit id and "
            "quantity kept", after == before, {"lost": [x for x in before if x not in after][:8]})
    # ------------------------------------------------------------------ E
    h.em.set_state(st_full); h.step(10)
    owned0 = sorted([i for s, i, n in h.inv() for _ in range(n)] + [x for v in all_eq(h).values() for x in v if x != 0xFF])
    for name in ("Terra", "Locke"):
        c = E8.CHARS.index(name); si = E8.party_order(h).index(c)
        nv = Nav(h); h.step(20)
        for _ in range(6):
            h.step(40); nv.open_main()
            if nv.state() == ST["MAIN"]:
                break
        nv.main_to("Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
        nv.cursor_to(si); h.press("A", 4, 30); nv.wait(ST["EQUIP_OPT"], 120)
        nv.cursor_lr(3); h.press("A", 4, 60); nv.cursor_lr(1); h.press("A", 4, 60)
        nv.back_to_main(); nv.close(); h.step(20)
    owned1 = sorted([i for s, i, n in h.inv() for _ in range(n)] + [x for v in all_eq(h).values() for x in v if x != 0xFF])
    q.check("E1 Empty + Optimum (Terra, Locke) with consumables present: no item duplicated or lost, no consumable "
            "equipped", owned0 == owned1 and not [x for v in all_eq(h).values() for x in v if x in CIDS])
    # ------------------------------------------------------------------ F
    h.em.set_state(st_full); h.step(10)
    nv = Nav(h)
    h.call_event(L["QaShop80"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30)
    owned = [h.r8(0x9DC9 + k) for k in range(8)]
    nv.cursor_to(1); g0 = gp(h)
    h.press("A", 4, 40); h.step(20)
    for b in ("RIGHT", "UP"):
        for _ in range(4):
            if h.r8(0x28) >= 3:
                break
            h.press(b, 4, 16)
    nb = h.r8(0x28)
    h.press("A", 4, 40); h.step(40)
    bought = (qty(h, 0x12B), gp(h))
    h.press("B", 4, 30); nv.wait(ST["SHOP_OPT"])
    nv.cursor_lr(1); h.press("A", 4, 40); nv.wait(ST["SHOP_SELL"]); h.step(20)
    nv.cursor_to(next(s for s, i, n in h.inv() if i == 0x127)); h.press("A", 4, 40); h.step(20)
    for b in ("RIGHT", "UP"):
        for _ in range(3):
            if h.r8(0x28) >= 2:
                break
            h.press(b, 4, 16)
    ns = h.r8(0x28); g1 = gp(h)
    h.press("A", 4, 40); h.step(40)
    sold = (qty(h, 0x127), gp(h) - g1)
    leave(h)
    q.check("F1 extended shop with everything: owned counts (10 / 10 / 10 for the three consumables), buy n Iron Ration "
            "(stack +n, n x 250 GP), sell m Gaia Tonic (+m x 750 GP)",
            owned[:3] == [10, 10, 10] and bought == (10 + nb, g0 - 250 * nb) and sold == (10 - ns, 750 * ns) and nb >= 1 and ns >= 1,
            {"owned": owned, "bought": bought, "n_buy": nb, "sold": sold, "n_sell": ns})
    # ------------------------------------------------------------------ G
    h.em.set_state(st_full); h.step(10)
    eq0 = all_eq(h)
    h.call_event(L["QaColoKit7"], frames=1); talk(h, [])
    import emu_colosseum as C
    C.FIGHTERS = {0: "Terra", 1: "Locke", 2: "Celes", 3: "Edgar"}
    r = C.run_combo(h, lambda hh: hh.call_event(L["QaColoFight7"], frames=1), 0xEE, 0, False, out, "G_colosseum", q)
    q.check("G1 Colosseum (Elixir wager) with the party wearing signature gear and all consumables owned: battle entered, "
            "return with control, worn gear unchanged, consumables untouched",
            r.get("battle_entered") and r.get("returned_idle") and all_eq(h) == eq0 and all(qty(h, i) == 10 for i in CIDS),
            {"slot1": r.get("slot1")})
    # ------------------------------------------------------------------ H / I
    h.em.set_state(st_full); h.step(10)
    pre = {"inv": inv16(h), "eq": all_eq(h), "bits": h.rbytes(XBITS, 44).hex(), "rare": rare(h)}
    blk, sram = save_menu(h)
    h.close()
    h2 = T(QA); write_sram(h2, blk, sram); continue_slot1(h2)
    post = {"inv": inv16(h2), "eq": all_eq(h2), "bits": h2.rbytes(XBITS, 44).hex(), "rare": rare(h2)}
    q.shot(h2, "H_after_power_cycle")
    q.check("H1 save -> power cycle -> Continue: inventory (20 equipment + 8 consumables + vanilla), 19 worn items, the 5 "
            "key items and the bitmaps preserved exactly", post == pre)
    h2.close()
    hp = T(PROD); write_sram(hp, blk, sram); continue_slot1(hp)
    q.check("I1 the v0.9 QA save in the v0.9 PRODUCTION ROM: every equipment item, consumable and key item kept",
            inv16(hp) == pre["inv"] and all_eq(hp) == pre["eq"] and rare(hp) == pre["rare"])
    hp.close()
    # ------------------------------------------------------------------ M downgrade
    h8 = T(PROD8); write_sram(h8, blk, sram); continue_slot1(h8)
    inv8 = inv16(h8)
    q.check("M1 (informative) the v0.9 save in the accepted v0.8 PRODUCTION ROM: the 8 consumables are removed cleanly "
            "(undefined in v0.8, no katana alias appears), the 20 equipment items and 19 worn items kept",
            not [i for i, n in inv8 if i in CIDS or 0x27 <= i <= 0x2E] and all_eq(h8) == pre["eq"] and
            sorted(i for i, n in inv8 if i >= 0x100) == sorted(i for i, n in pre["inv"] if 0x100 <= i < 0x127),
            {"ext": [f"{i:03X}" for i, n in inv8 if i >= 0x100]})
    h8.close()
    # ------------------------------------------------------------------ J legacy Rev 1
    hv = T(clean); boot_new_game(hv)
    hv.run_event(sum(([0x80, v] for v in range(0x27, 0x2F)), []) + [0x80, 0xE9, 0x80, 0xE9])
    vinv = sorted((hv.r8(0x1869 + s), hv.r8(0x1969 + s)) for s in range(256) if hv.r8(0x1869 + s) != 0xFF)  # raw (no bitmap in Rev 1)
    vblk, vsram = save_menu(hv)
    hv.close()
    hq = T(QA); write_sram(hq, vblk, vsram); continue_slot1(hq)
    q.check("J1 genuine Rev 1 save holding the katanas $27-$2E + Potions: loads in v0.9 with the katanas as katanas "
            "(no phantom consumable), no FF6X rare item",
            inv16(hq) == vinv and not [1 for s, i, n in hq.inv() if i >= 0x100] and rare(hq) == [],
            {"inv": [(f"{i:03X}", n) for i, n in inv16(hq)][:12], "vinv": [(f"{i:03X}", n) for i, n in vinv][:12],
             "rare": rare(hq), "block": hq.rbytes(0x1E1D, 6).hex()})
    hq.close()
    # ------------------------------------------------------------------ K v0.7.3
    if os.path.exists(QA73):
        L73 = labels(QA73[:-4] + ".manifest.json")
        h73 = T(QA73); boot_new_game(h73)
        h73.call_event(L73["QaGive7"], frames=400); talk(h73, [])
        i73 = inv16(h73)
        b73, s73 = save_menu(h73)
        h73.close()
        hq = T(QA); write_sram(hq, b73, s73); continue_slot1(hq)
        q.check("K1 TECH v0.7.3 QA save (QA equipment $13D-$13F + same-low-byte vanilla items) -> v0.9 QA ROM: kept",
                inv16(hq) == i73 and sorted(i for s, i, n in hq.inv() if i >= 0x100) == [0x13D, 0x13E, 0x13F])
        hq.close()
    else:
        q.check("K1 TECH v0.7.3 QA ROM present for the migration test", False, QA73)
    # ------------------------------------------------------------------ L v0.8
    L8 = labels(QA8[:-4] + ".manifest.json")
    h8 = T(QA8); boot_new_game(h8)
    LABELS.clear(); LABELS.update(L8)
    h8.call_event(L8["QaAccess6"], frames=1); talk(h8, [0, 0])
    h8.call_event(L8["QaAccess6"], frames=1); talk(h8, [0, 1, 0])
    wear(h8)
    i8, e8 = inv16(h8), all_eq(h8)
    b8, s8 = save_menu(h8)
    h8.close()
    LABELS.clear(); LABELS.update(L)
    ok = True
    det = {}
    for nm, rom in (("qa", QA), ("prod", PROD)):
        hx = T(rom); write_sram(hx, b8, s8); continue_slot1(hx)
        det[nm] = (inv16(hx) == i8, all_eq(hx) == e8)
        ok = ok and inv16(hx) == i8 and all_eq(hx) == e8
        hx.close()
    q.check("L1 TECH v0.8 QA save (20 equipment in the inventory, 19 worn) -> v0.9 QA and v0.9 PRODUCTION: every "
            "item and every worn slot kept (the item-bank metadata is not reset)", ok, det)
    # ------------------------------------------------------------------ O / P / T
    h = T(QA); h.em.set_state(st_new); h.step(10)
    for _ in range(4):
        h.run_event(sum((ev_give(0x12B) for _ in range(30)), []))
    q.check("O1 120 x GIVE Iron Ration: one stack capped at 99", qty(h, 0x12B) == 99 and
            len([1 for s, i, n in h.inv() if i == 0x12B]) == 1, qty(h, 0x12B))
    for s in range(256):                                              # POKE: inventory full of vanilla items (test)
        h.w8(0x1869 + s, 0x80 + (s % 0x60)); h.w8(0x1969 + s, 1)
    for s in range(32):
        h.w8(0x1CF8 + s, 0)
    full = inv16(h)
    h.run_event(ev_give(0x127))
    q.check("P1 inventory full: GIVE of a consumable not owned changes nothing (no slot overwritten)", inv16(h) == full)
    h.em.set_state(st_new); h.step(10)
    menu(h, L, [0, 0])
    h.run_event([0x80, 0x27, 0x80, 0x2B, 0x80, 0x00])
    a = (qty(h, 0x27), qty(h, 0x2B), qty(h, 0x127), qty(h, 0x12B))
    h.run_event([0x81, 0x27, 0x81, 0x2B])
    b = (qty(h, 0x27), qty(h, 0x2B), qty(h, 0x127), qty(h, 0x12B), qty(h, 0x00))
    q.check("T1 vanilla give / take ($80 / $81) of Blossom $27 and Tempest $2B (low bytes of Gaia Tonic / Iron Ration): "
            "separate vanilla slots, the consumables untouched", a == (1, 1, 5, 5) and b == (0, 0, 5, 5, 1), (a, b))
    # ------------------------------------------------------------------ Q vanilla in battle
    h.em.set_state(st_new); h.step(10)
    h.run_event([0x80, 0xE9, 0x80, 0xF0])                             # Potion, Fenix Down
    menu(h, L, [0, 2, 2, 1, 0])
    h.run_event([0x89, 0x01, 0x80, 0x00]); h.w8(0x1600 + 37 + 9, 0); h.w8(0x1600 + 37 + 10, 0)   # Locke fallen
    h.w8(0x1609, 10); h.w8(0x160A, 0)
    n0 = (qty(h, 0xE9), qty(h, 0xF0))
    battle_start(h, L)
    e_p = next(s for s in range(256) if bslot(h, s)[0] == 0xE9)
    hp0 = h.r16(0x3BF4)
    choose_item(h, e_p)
    for _ in range(500):
        h.step(1)
    hp1 = h.r16(0x3BF4)
    to_terra(h); h.step(30)
    e_f = next(s for s in range(256) if bslot(h, s)[0] == 0xF0)
    choose_item(h, e_f, moves=("DOWN",))
    for _ in range(500):
        h.step(1)
    locke = (h.r16(0x3EE4 + 2) & 0x80, h.r16(0x3BF4 + 2))
    finish_battle(h)
    q.check("Q1 vanilla Potion (Terra HP 10 -> healed) and Fenix Down (fallen Locke revived) in battle; one of each used",
            hp1 > hp0 and locke[0] == 0 and locke[1] > 0 and (qty(h, 0xE9), qty(h, 0xF0)) == (n0[0] - 1, n0[1] - 1),
            {"terra_hp": (hp0, hp1), "locke": locke})
    # ------------------------------------------------------------------ R vanilla in the field
    h.em.set_state(st_new); h.step(10)
    h.run_event([0x80, 0xE9, 0x80, 0xF2, 0x89, 0x00, 0x04, 0x00])     # Potion, Antidote, Terra poisoned
    h.w8(0x1609, 10); h.w8(0x160A, 0)
    field_use(h, 0xE9, 0)
    hpa = h.r16(0x1609)
    field_use(h, 0xF2, 0)
    q.check("R1 vanilla Potion (field: Terra HP 10 -> healed) and Antidote (Poison cured)",
            hpa > 10 and not h.r8(0x1614) & 0x04 and qty(h, 0xE9) == 0 and qty(h, 0xF2) == 0, (hpa, h.r8(0x1614)))
    # ------------------------------------------------------------------ S vanilla shop
    h.em.set_state(st_new); h.step(10)
    h.run_event([0x80, 0xE9])
    nv = Nav(h)
    h.call_event(L["QaShop7"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30)
    g0 = gp(h)
    k = min((k for k in range(8) if h.r8(0x9D89 + k) != 0xFF), key=lambda k: h.r16(0x9F09 + 2 * k))
    first = h.r8(0x9D89 + k); price = h.r16(0x9F09 + 2 * k); n0 = qty(h, first)
    nv.cursor_to(k)
    h.press("A", 4, 40); h.step(20); h.press("A", 4, 40); h.step(40)
    buy = (qty(h, first) - n0, g0 - gp(h))
    h.press("B", 4, 30); nv.wait(ST["SHOP_OPT"])
    nv.cursor_lr(1); h.press("A", 4, 40); nv.wait(ST["SHOP_SELL"]); h.step(20)
    nv.cursor_to(next(s for s, i, n in h.inv() if i == 0xE9)); g1 = gp(h)
    h.press("A", 4, 40); h.step(20); h.press("A", 4, 40); h.step(40)
    sell = (qty(h, 0xE9), gp(h) - g1)
    leave(h)
    q.check("S1 vanilla shop $48: buy one of its cheapest item (stack +1, its price charged), sell the Potion (+150 GP)",
            buy == (1, price) and sell == (0, 150), {"buy": buy, "price": price, "sell": sell, "item": f"{first:02X}"})
    # ------------------------------------------------------------------ N
    q.check("N1 bitmap consistency at the end (no bit on an empty slot / undefined id; equipment bits on worn slots)",
            not stale_bits(h, defined), stale_bits(h, defined)[:10])
    h.close()
    rep = {"checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "STRESS_V09_REPORT.json"), "w"), indent=1, default=str)
    print("STRESS v0.9", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
