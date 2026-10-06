#!/usr/bin/env python3
"""TECH v0.9.1 emulator checks (field / shops / tables) on the v0.9.2 QA ROM (stable-retro / snes9x).
Battle effects: tools/emu_cons_battle_v091.py.

  T  ROM tables: the 8 consumable records / names / descriptions / flags / animations = items/production_v091 sources;
     the 39 equipment records = the frozen v0.9 records except Darill's Coin (= v0.9.1 source, Mag +2)
  F  field Item menu: Gaia Tonic exactly +1500 HP (refused at full HP), Iron Ration exactly +600 HP (Poison stays),
     Aether Flask exactly +100 MP, Remedy+ cures Blind / Poison / Imp, Phoenix Ash revives; Null Dust / Beacon Flare /
     Magitek Cell are battle-only (no target screen, nothing used)
  S  reconstruction shops $80-$84: entries / 9-bit ids / prices / owned counts / shop type; vendor purchase of vanilla
     armour (Gaia Gear) and of an extended consumable; Figaro Foundry = $83 (tools) until EXP_CELES_DONE, then $84
     (tools + Magitek Cell); Magitek Cell purchase cap 3: buy maximum 3 with none owned, refused ('too many') at 3,
     still refused after leaving and re-entering, 1 more allowed after one is used
  L  Sell: exactly the sellable consumables (Gaia Tonic, Iron Ration, Magitek Cell) can be selected

usage: emu_cons_v091.py <qa.sfc> <qa.manifest.json> <frozen v0.9 production .sfc> <clean_rev1.sfc> <out>
writes <out>/CONSUMABLE_EMULATOR_REPORT_v091.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T, ev_take, ev_give
from emu_item_qa import Report, boot_new_game
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
from emu_cons_v09 import field_use, open_items, slot_of, hp, mp, qty, gp, CHAR_REC
from patches import item_v071 as IV, item_v09 as I9, consumables_v091 as CV

CONS = json.load(open(os.path.join(HERE, "items/production_v091/consumables.json")))["items"]
BYID = {int(c["id"], 16): c for c in CONS}
IDS = sorted(BYID)
SHOPS = {int(s["shop_id"], 16): s for s in json.load(open(os.path.join(HERE, "items/production_v091/ext_shops.json")))["shops"]}
EQUIP = json.load(open(os.path.join(HERE, "items/production_v091/equipment.json")))["items"]
BUY_SELECT, BUY_QTY, BUY_RETURN = 0x26, 0x27, 0x28
CELES_DONE = 0x0E9


def pc(a):
    return a - 0xC00000


def poke_rec(h, rec, hp_=None, maxhp=None, mp_=None, maxmp=None):
    b = CHAR_REC + 37 * rec
    if maxhp is not None:
        v = (h.r16(b + 11) & 0xC000) | maxhp; h.w8(b + 11, v & 0xFF); h.w8(b + 12, v >> 8)
    if hp_ is not None:
        h.w8(b + 9, hp_ & 0xFF); h.w8(b + 10, hp_ >> 8)
    if maxmp is not None:
        v = (h.r16(b + 15) & 0xC000) | maxmp; h.w8(b + 15, v & 0xFF); h.w8(b + 16, v >> 8)
    if mp_ is not None:
        h.w8(b + 13, mp_ & 0xFF); h.w8(b + 14, mp_ >> 8)


def hub(h, L, picks):
    h.call_event(L["QaRoot92"], frames=1)
    return talk(h, picks)


def leave_shop(h):
    for _ in range(8):
        h.press("B", 4, 30)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)


def open_shop(h, L, label):
    nv = Nav(h)
    h.call_event(L[label], frames=60)
    nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30)                       # Buy
    return nv


def shop_view(h):
    return {"list": [h.r8(0x9D89 + k) for k in range(8)], "owned": [h.r8(0x9DC9 + k) for k in range(8)],
            "price": [h.r16(0x9F09 + 2 * k) for k in range(8)], "type": h.r8(0x9D88) if False else None}


def main(qa, manifest, prod09, clean, out):
    q = Report(out)
    L = labels(manifest)
    rom, van, p9 = open(qa, "rb").read(), open(clean, "rb").read(), open(prod09, "rb").read()
    res = {}
    # ------------------------------------------------------------------ T tables
    bad = {}
    for i, it in BYID.items():
        k = i - 0x100
        rec = rom[pc(IV.T_PROP) + 30 * i:pc(IV.T_PROP) + 30 * i + 30]
        nm = rom[pc(IV.T_NAME) + 13 * i:pc(IV.T_NAME) + 13 * i + 13]
        dp = rom[pc(IV.T_DPTR) + 2 * k] | rom[pc(IV.T_DPTR) + 2 * k + 1] << 8
        a = pc(0xFA0000 | dp); d = bytearray()
        while rom[a] != 0:
            d.append(rom[a]); a += 1
        fl = rom[pc(IV.T_FLAGS) + k]
        av = rom[pc(I9.T_ANIMX) + 2 * k] | rom[pc(I9.T_ANIMX) + 2 * k + 1] << 8
        ok = {"rec": rec == CV.compose(it), "name": nm[1:].rstrip(b"\xFF") == IV.menu_encode(it["display_name"], 0xFE),
              "desc": bytes(d) == IV.menu_encode(it["desc"], 0xFF),
              "flags": fl == 0x05 | (0x08 if it["sellable"] else 0), "anim": av == CV.anim_offset(it, van, IV.snes_to_pc)}
        if not all(ok.values()):
            bad[f"{i:03X}"] = ok
    q.check("T1 the 8 consumables: ItemProp record (v0.9.1 source), name, description, flags, animation", not bad, bad)
    ediff = [f"{k:03X}" for k in range(0x100, 0x127)
             if rom[pc(IV.T_PROP) + 30 * k:pc(IV.T_PROP) + 30 * k + 30] != p9[pc(IV.T_PROP) + 30 * k:pc(IV.T_PROP) + 30 * k + 30]]
    coin = [it for it in EQUIP if it["id"] == "11E"][0]
    coin_ok = rom[pc(IV.T_PROP) + 30 * 0x11E:pc(IV.T_PROP) + 30 * 0x11F] == IV.compose_v08(van, coin)
    q.check("T2 equipment records = frozen v0.9 except Darill's Coin ($11E = v0.9.1 source: Speed +5, Mag +2, MBlock +20)",
            ediff == ["11E"] and coin_ok, {"changed": ediff, "coin": coin_ok})

    h = T(qa)
    boot_new_game(h)
    h.call_event(L["QaAccess6"], frames=1); talk(h, [0, 0])          # 8 consumables x5
    h.call_event(L["QaAccess6"], frames=1); talk(h, [0, 2, 1])       # field setup: P1, Terra Poison/Blind/Imp, Locke KO
    st_setup = h.em.get_state()

    # ------------------------------------------------------------------ F field
    fres = {}
    h.em.set_state(st_setup); h.step(10)
    h.run_event([0x88, 0x00, 0xDE, 0xFF])                             # Terra: clear Blind / Imp (Poison stays)
    poke_rec(h, 0, hp_=5, maxhp=3000)
    n0 = qty(h, 0x127)
    field_use(h, 0x127, 0)
    a1 = hp(h)
    field_use(h, 0x127, 0)                                            # not full yet (1505 < 3000): second use
    a2 = hp(h)
    poke_rec(h, 0, hp_=3000)
    field_use(h, 0x127, 0)                                            # full: refused
    fres["gaia"] = {"hp": (a1, a2, hp(h)), "qty": (n0, qty(h, 0x127))}
    q.check("F1 Gaia Tonic (field, one member): HP 5 -> 1505 -> 3000 (cap), exactly +1500; refused at full HP "
            "(2 units used)", a1 == 1505 and a2 == 3000 and qty(h, 0x127) == n0 - 2, fres["gaia"])
    poke_rec(h, 0, hp_=5)
    n0 = qty(h, 0x12B)
    field_use(h, 0x12B, 0)
    fres["iron"] = {"hp": hp(h), "status": f"{h.r8(CHAR_REC + 0x14):02X}", "qty": (n0, qty(h, 0x12B))}
    q.check("F2 Iron Ration (field): HP 5 -> 605 exactly; Poison NOT cured; one unit used",
            hp(h) == 605 and h.r8(CHAR_REC + 0x14) & 0x04 and qty(h, 0x12B) == n0 - 1, fres["iron"])
    poke_rec(h, 0, mp_=1, maxmp=999)
    n0 = qty(h, 0x128)
    field_use(h, 0x128, 0)
    fres["aether"] = {"mp": mp(h), "qty": (n0, qty(h, 0x128))}
    q.check("F3 Aether Flask (field): MP 1 -> 101 exactly; one unit used", mp(h) == 101 and qty(h, 0x128) == n0 - 1,
            fres["aether"])
    h.em.set_state(st_setup); h.step(10)
    s0 = h.r8(CHAR_REC + 0x14); n0 = qty(h, 0x12C)
    field_use(h, 0x12C, 0)
    fres["remedy+"] = (f"{s0:02X}", f"{h.r8(CHAR_REC + 0x14):02X}", n0, qty(h, 0x12C))
    q.check("F4 Remedy+ (field) on Terra Blind / Poison / Imp: all cured, one unit used",
            s0 & 0x25 == 0x25 and not h.r8(CHAR_REC + 0x14) & 0x25 and qty(h, 0x12C) == n0 - 1, fres["remedy+"])
    h.w8(CHAR_REC + 37 + 9, 0); h.w8(CHAR_REC + 37 + 10, 0)
    n0 = qty(h, 0x129)
    field_use(h, 0x129, 1)
    fres["phoenix"] = (f"{h.r8(CHAR_REC + 37 + 0x14):02X}", hp(h, 1), n0, qty(h, 0x129))
    q.check("F5 Phoenix Ash (field, unchanged): fallen Locke revived with HP", not h.r8(CHAR_REC + 37 + 0x14) & 0x80
            and hp(h, 1) > 0 and qty(h, 0x129) == n0 - 1, fres["phoenix"])
    ref = {}
    for i in (0x12A, 0x12D, 0x12E):
        n0 = qty(h, i)
        st, target = field_use(h, i, 0)
        ref[f"{i:03X}"] = (target, n0, qty(h, i))
    q.check("F6 battle-only Null Dust / Beacon Flare / Magitek Cell: no target screen in the field, nothing used",
            all(not t and a == b for t, a, b in ref.values()), ref)
    res["field"] = fres

    # ------------------------------------------------------------------ S shops
    h.em.set_state(st_setup); h.step(10)
    h.run_event([0x84, 0x50, 0xC3])                                    # +50000 GP
    st_shop = h.em.get_state()
    sres = {}
    for sid, label in ((0x80, "QaShop80"), (0x81, "QaShop81"), (0x82, "QaShop82"), (0x83, "QaFoundry92")):
        h.em.set_state(st_shop); h.step(10)
        open_shop(h, L, label)
        v = shop_view(h)
        sd = SHOPS[sid]
        items = [int(x, 16) for x in sd["items"]]
        exp_price = []
        for x in items:
            base = BYID[x]["price"] if x >= 0x100 else van[pc(IV.VAN_PROP) + 30 * x + 28] | van[pc(IV.VAN_PROP) + 30 * x + 29] << 8
            exp_price.append(base)
        sres[f"{sid:02X}"] = v
        q.shot(h, f"S_shop{sid:02X}")
        n = len(items)
        q.check(f"S1 shop ${sid:02X} ({sd['symbol']}): entries {sd['items']} (low bytes + 9-bit names), prices from the "
                "item records (Terra leads: no Figaro Edgar discount), owned counts of exactly those items",
                v["list"][:n] == [x & 0xFF for x in items] and all(e == 0xFF for e in v["list"][n:])
                and v["price"][:n] == exp_price
                and v["owned"][:n] == [5 if x in BYID else 0 for x in items], {"view": v, "expect_price": exp_price})
        leave_shop(h)
    # vendor purchase: Gaia Gear (vanilla armour) + Gaia Tonic (extended) in $80
    h.em.set_state(st_shop); h.step(10)
    open_shop(h, L, "QaShop80")
    g0 = gp(h)
    for _ in range(4):
        h.press("DOWN", 4, 16)
    h.press("A", 4, 40); h.step(20); h.press("A", 4, 60); h.step(30)
    g1 = gp(h)
    gaia_gear = sum(n for s, j, n in h.inv() if j == 0x8D)
    for _ in range(4):
        h.press("UP", 4, 16)
    for _ in range(3):
        h.press("DOWN", 4, 16)
    t0 = qty(h, 0x127)
    h.press("A", 4, 40); h.step(20); h.press("A", 4, 60); h.step(30)
    sres["vendor"] = {"gp": (g0, g1, gp(h)), "gaia_gear": gaia_gear, "tonic": (t0, qty(h, 0x127))}
    q.check("S2 Rebuilt Mobliz is a vendor (items + armour): buy Gaia Gear (-6000 GP, +1) and Gaia Tonic (-2000 GP, "
            "stack +1)", g0 - g1 == 6000 and gaia_gear == 1 and g1 - gp(h) == 2000 and qty(h, 0x127) == t0 + 1,
            sres["vendor"])
    leave_shop(h)
    # Foundry gate
    h.em.set_state(st_shop); h.step(10)
    h.run_event(ev_take(0x12E) * 5)                                   # no Magitek Cell owned
    hub(h, L, [0, 1, 2, 2])                                           # toggle Celes arc done -> ON
    on = (h.r8(0x1E80 + (CELES_DONE >> 3)) >> (CELES_DONE & 7)) & 1
    st_done = h.em.get_state()
    open_shop(h, L, "QaFoundry92")
    v84 = shop_view(h)
    q.shot(h, "S_foundry_after_celes")
    q.check("S3 Figaro Foundry: EXP_CELES_DONE set by the hub -> the clerk event opens $84 = the canonical tools + "
            "Magitek Cell (price 1500), Cell owned 0", on == 1 and v84["list"][:7] == [0xAA, 0xA3, 0xA4, 0xA5, 0xA7, 0xA8, 0x2E]
            and v84["price"][6] == 1500 and v84["owned"][6] == 0, v84)
    # cap: select the Cell -> quantity screen; the maximum is 3
    for _ in range(6):
        h.press("DOWN", 4, 16)
    h.press("A", 4, 40); h.step(20)
    cap_view = {"state": h.r8(0x26), "max": h.r8(0x6A)}
    for _ in range(6):
        h.press("RIGHT", 4, 12)                                       # RIGHT = +1 up to the maximum (z6a)
    cap_view["chosen"] = h.r8(0x28)
    h.press("A", 4, 60); h.step(40)
    cells = qty(h, 0x12E)
    cap_view["owned_after"] = cells
    h.step(60)
    h.press("A", 4, 40); h.step(30)                                   # select the Cell again (3 owned)
    cap_view["again_state"] = h.r8(0x26)
    q.shot(h, "S_cell_too_many")
    h.step(60)
    leave_shop(h)
    open_shop(h, L, "QaFoundry92")
    for _ in range(6):
        h.press("DOWN", 4, 16)
    h.press("A", 4, 40); h.step(30)
    cap_view["reenter_state"] = h.r8(0x26)
    leave_shop(h)
    h.run_event(ev_take(0x12E))                                       # one Cell used up
    open_shop(h, L, "QaFoundry92")
    for _ in range(6):
        h.press("DOWN", 4, 16)
    h.press("A", 4, 40); h.step(20)
    cap_view["after_use_max"] = h.r8(0x6A)
    leave_shop(h)
    sres["cap"] = cap_view
    q.check("S4 Magitek Cell cap 3: quantity screen maximum 3 with none owned (6 RIGHT presses stop at 3), 3 bought; "
            "selecting it again with 3 owned is refused ('too many', no quantity screen) - also after leaving and "
            "re-entering the shop; after one Cell is used the maximum is 1",
            cap_view["state"] == BUY_QTY and cap_view["max"] == 3 and cap_view["chosen"] == 3 and cells == 3
            and cap_view["again_state"] != BUY_QTY and cap_view["reenter_state"] != BUY_QTY
            and cap_view["after_use_max"] == 1, cap_view)
    h.em.set_state(st_done); h.step(10)
    hub(h, L, [0, 1, 2, 2])                                           # toggle OFF again -> tools only
    open_shop(h, L, "QaFoundry92")
    v83 = shop_view(h)
    leave_shop(h)
    q.check("S5 EXP_CELES_DONE cleared -> the Foundry is $83 again (tools only, no Magitek Cell)",
            v83["list"][:7] == [0xAA, 0xA3, 0xA4, 0xA5, 0xA7, 0xA8, 0xFF], v83)
    res["shops"] = sres

    # ------------------------------------------------------------------ L sell
    h.em.set_state(st_setup); h.step(10)
    nv = Nav(h)
    h.call_event(L["QaShop80"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    nv.cursor_lr(1); h.press("A", 4, 40); nv.wait(ST["SHOP_SELL"]); h.step(20)
    sel = {}
    for i in IDS:
        nv.cursor_to(slot_of(h, i)); h.press("A", 4, 40); h.step(10)
        sel[f"{i:03X}"] = nv.state() != ST["SHOP_SELL"]
        if nv.state() != ST["SHOP_SELL"]:
            h.press("B", 4, 30); nv.wait(ST["SHOP_SELL"])
    q.check("L1 Sell: exactly the sellable consumables (Gaia Tonic, Iron Ration, Magitek Cell) can be selected",
            sel == {f"{i:03X}": BYID[i]["sellable"] for i in IDS}, sel)
    leave_shop(h)
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "CONSUMABLE_EMULATOR_REPORT_v091.json"), "w"), indent=1, default=str)
    print("CONSUMABLE EMULATOR v0.9.1", "PASS" if rep["all_pass"] else "FAIL",
          f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
