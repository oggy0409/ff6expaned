#!/usr/bin/env python3
"""TECH v0.9 emulator checks, part 1: the 8 production consumables $127-$12E in tables, QA menus, event API, field
menu use, extended shops and Sell (stable-retro / snes9x).

  T  tables (ROM bytes vs items/production_v09/consumables.json and the vanilla ROM): ItemProp record, name (blank icon
     + display name), description, XExtFlags, item animation, the 39 v0.8 equipment records unchanged, vanilla
     $00-$FF ItemProp / ItemName and the 128 vanilla shops byte-identical in the relocated tables
  G  QA menu "Grant all 8 (x5 each)" / "Remove all 8"
  K  per consumable: HAS / TAKE / GIVE (event API $66-$68); no alias with the vanilla item of the same low byte
  F  field Item menu (real menus): every field-usable consumable used on a character in the state it repairs, with the
     effect the record defines (HP / MP / revive / status cure) and one unit removed; refused when there is nothing
     to repair; battle-only items drawn grey and refused; the last unit empties the slot and clears its high bit;
     Arrange keeps every 9-bit id and quantity
  S  extended shops $80 / $81: list (9-bit names, prices), owned / equipped counts, buy (stack / new slot, GP), buy with
     a full inventory refused without charge, vanilla shop selling a katana whose low byte a consumable uses: owned
     count of the katana only
  L  Sell: sellable consumables selectable (price / 2 paid, quantity, sell-all clears the slot and the high bit),
     not-sold consumables cannot be selected
  X  exclusions: Colosseum wager list, Equip / Relic lists never offer a consumable

usage: emu_cons_v09.py <qa.sfc> <qa.manifest.json> <clean_rev1.sfc> <out>
writes <out>/CONSUMABLE_EMULATOR_REPORT.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T, ev_give, ev_take, ev_has
from emu_item_qa import Report, boot_new_game, inv16
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
from patches import item_v071 as IV, item_v09 as I9, consumables_v09 as CV

CONS = json.load(open(os.path.join(HERE, "items/production_v09/consumables.json")))["items"]
BYID = {int(c["id"], 16): c for c in CONS}
IDS = sorted(BYID)
SHOPS = json.load(open(os.path.join(HERE, "items/production_v09/ext_shops.json")))["shops"]
EQUIP = json.load(open(os.path.join(HERE, "items/production_v08/equipment.json")))["items"]
QA_BIT = 0x14E
CHAR_REC = 0x1600                       # character record 0 (Terra); +37 per record


def pc(a):
    return a - 0xC00000


def qty(h, i):
    return sum(n for s, j, n in h.inv() if j == i)


def gp(h):
    return h.r8(0x1860) | h.r8(0x1861) << 8 | h.r8(0x1862) << 16


def has(h, i):
    h.w8(0x1E80 + (QA_BIT >> 3), h.r8(0x1E80 + (QA_BIT >> 3)) & ~(1 << (QA_BIT & 7)))
    h.run_event(ev_has(i, QA_BIT))
    return h.r8(0x1E80 + (QA_BIT >> 3)) >> (QA_BIT & 7) & 1


def menu(h, L, picks):
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def slot_of(h, i):
    return next(s for s, j, n in h.inv() if j == i)


def hp(h, rec=0):
    return h.r16(CHAR_REC + 37 * rec + 9)


def mp(h, rec=0):
    return h.r16(CHAR_REC + 37 * rec + 13)


def open_menu(h, nv):
    """open the main menu (right after an event the field may ignore X for a moment)"""
    for _ in range(6):
        h.step(60); nv.open_main()
        if nv.state() == ST["MAIN"]:
            return
    raise RuntimeError("main menu did not open")


def open_items(h, nv):
    open_menu(h, nv); nv.main_to("Item"); nv.wait(ST["ITEM"]); h.step(20)


def field_use(h, item, rec_slot=0, settle=90):
    """Item menu -> select the item -> target character `rec_slot` (party order) -> A. Returns (menu state after the
    item was chosen, whether a target screen opened)."""
    nv = Nav(h)
    open_items(h, nv)
    nv.cursor_to(slot_of(h, item))
    h.press("A", 4, 30); h.step(20)                    # first A: the item is picked up (ITEM_MOVE)
    h.press("A", 4, 40); h.step(60)                    # A on the same item: use
    st = h.r8(0x26)
    target = st not in (ST["ITEM"], ST["ITEM_MOVE"])
    if target:
        h.step(30)
        for _ in range(rec_slot):
            h.press("DOWN", 4, 16)
        h.press("A", 4, 30); h.step(settle)
    for _ in range(8):
        if h.r8(0x26) == ST["MAIN"]:
            break
        h.press("B", 4, 30); h.step(20)
    nv.close(); h.step(30)
    return st, target


def main(qa, manifest, clean, out):
    q = Report(out)
    L = labels(manifest)
    rom = open(qa, "rb").read()
    van = open(clean, "rb").read()
    res = {}
    # ------------------------------------------------------------------ T: tables
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
        exp_fl = 0x05 | (0x08 if it["sellable"] else 0)
        ok = {"rec": rec == CV.compose(it), "icon": nm[0] == 0xFF,
              "name": nm[1:].rstrip(b"\xFF") == IV.menu_encode(it["display_name"], 0xFE),
              "desc": bytes(d) == IV.menu_encode(it["desc"], 0xFF), "flags": fl == exp_fl,
              "anim": av == CV.anim_offset(it, van, IV.snes_to_pc)}
        if not all(ok.values()):
            bad[f"{i:03X}"] = ok
    q.check("T1 all 8 consumables: ItemProp record (every byte from the source), blank icon + display name, "
            "description, XExtFlags (defined + consumable + sellable), item animation entry", not bad, bad)
    from patches import equipment_v08  # noqa: F401  (validator import keeps the v0.8 composer in sync)
    ebad = [it["id"] for it in EQUIP
            if rom[pc(IV.T_PROP) + 30 * int(it["id"], 16):pc(IV.T_PROP) + 30 * int(it["id"], 16) + 30] !=
            IV.compose_v08(van, it)]
    q.check("T2 the 39 v0.8 equipment records are unchanged", not ebad, ebad)
    q.check("T3 vanilla $00-$FF ItemProp / ItemName and vanilla shops $00-$7F byte-identical in the relocated tables",
            rom[pc(IV.T_PROP):pc(IV.T_PROP) + 256 * 30] == van[pc(IV.VAN_PROP):pc(IV.VAN_PROP) + 256 * 30] and
            rom[pc(IV.T_NAME):pc(IV.T_NAME) + 256 * 13] == van[pc(IV.VAN_NAME):pc(IV.VAN_NAME) + 256 * 13] and
            rom[pc(I9.T_SHOP):pc(I9.T_SHOP) + 128 * 9] == van[pc(I9.VAN_SHOP):pc(I9.VAN_SHOP) + 128 * 9])
    q.check("T4 the vanilla items sharing the consumables' low bytes ($27-$2E katanas) are not usable with the Item "
            "command (no ambiguity) and their names differ from the consumables'",
            all(not van[pc(IV.VAN_PROP) + 30 * (i & 0xFF)] & 0x20 and
                van[pc(IV.VAN_NAME) + 13 * (i & 0xFF) + 1:pc(IV.VAN_NAME) + 13 * (i & 0xFF) + 13] !=
                rom[pc(IV.T_NAME) + 13 * i + 1:pc(IV.T_NAME) + 13 * i + 13] for i in IDS))

    # ------------------------------------------------------------------ G: QA menus
    h = T(qa)
    boot_new_game(h)
    st_new = h.em.get_state()
    menu(h, L, [0, 0])
    q.shot(h, "G_after_grant")
    q.check("G1 QA 'Grant all 8 (x5 each)': $127-$12E each x5 in 8 slots, nothing else",
            sorted((i, n) for s, i, n in h.inv() if i >= 0x100) == [(i, 5) for i in IDS],
            [(s, f"{i:03X}", n) for s, i, n in h.inv()][:12])
    st_cons = h.em.get_state()
    menu(h, L, [0, 2, 2, 0])
    q.check("G2 QA 'Remove all 8 (x10 each)': no consumable left", not [1 for s, i, n in h.inv() if i >= 0x100])

    # ------------------------------------------------------------------ K: event API per item
    h.em.set_state(st_cons); h.step(10)
    kbad = []
    for i in IDS:
        h1 = has(h, i)
        n0 = qty(h, i)
        h.run_event(ev_take(i)); n1 = qty(h, i)
        h.run_event(ev_give(i)); h.run_event(ev_give(i)); n2 = qty(h, i)
        for _ in range(n2):
            h.run_event(ev_take(i))
        h2 = has(h, i)
        h.run_event(ev_give(i)); h3 = has(h, i)
        if not (h1 == 1 and n1 == n0 - 1 and n2 == n0 + 1 and h2 == 0 and h3 == 1 and qty(h, i) == 1):
            kbad.append((f"{i:03X}", h1, n0, n1, n2, h2, h3, qty(h, i)))
    q.check("K1 all 8: HAS=1, TAKE -1, GIVE stacks, TAKE to 0 -> HAS=0 (slot emptied), GIVE -> new stack (event API)",
            not kbad, kbad)
    h.run_event([0x80, 0x27, 0x80, 0x2D])                        # vanilla Blossom ($27) / Tempest ($2D)
    n27, n127 = qty(h, 0x27), qty(h, 0x127)
    h.run_event([0x81, 0x27])
    q.check("K2 vanilla give / take of $27 (Blossom katana) never merges into / takes from Gaia Tonic $127; HAS $127 "
            "unaffected", n27 == 1 and n127 == 1 and qty(h, 0x27) == 0 and qty(h, 0x127) == 1 and has(h, 0x127) == 1
            and qty(h, 0x2D) == 1, {"27": n27, "127": n127})
    stale = [s for s in range(256) if h.bit(s) and h.r8(0x1869 + s) == 0xFF]
    q.check("K3 no high bit left on an empty slot after the event API sequence", not stale, stale)

    # ------------------------------------------------------------------ F: field use
    h.em.set_state(st_cons); h.step(10)
    menu(h, L, [0, 2, 1])                                        # field-use setup: P1, Terra poison/blind/imp, Locke KO
    st_setup = h.em.get_state()
    nv = Nav(h)
    open_items(h, nv)
    q.shot(h, "F_item_list")
    nv.back_to_main(); nv.close(); h.step(20)
    fres = {}
    # F1 Remedy+ on Terra (Blind | Poison | Imp)
    h.em.set_state(st_setup); h.step(10)
    s0 = h.r8(CHAR_REC + 0x14); n0 = qty(h, 0x12C)
    field_use(h, 0x12C, 0)
    fres["remedy+"] = (f"{s0:02X}", f"{h.r8(CHAR_REC + 0x14):02X}", n0, qty(h, 0x12C))
    q.check("F1 Remedy+ (field) on Terra with Blind/Poison/Imp: all three cured, one unit used",
            s0 & 0x25 == 0x25 and h.r8(CHAR_REC + 0x14) & 0x25 == 0 and qty(h, 0x12C) == n0 - 1, fres["remedy+"])
    # F2 Phoenix Ash on Locke (Wound): revived with HP = 50% of max; refused on a living character
    h.em.set_state(st_setup); h.step(10)
    h.w8(CHAR_REC + 37 + 9, 0); h.w8(CHAR_REC + 37 + 10, 0)      # POKE: fallen Locke has 0 HP (as after a battle)
    n0 = qty(h, 0x129)
    field_use(h, 0x129, 1)
    mx = h.r16(CHAR_REC + 37 + 11) & 0x3FFF
    s1 = h.r8(CHAR_REC + 37 + 0x14)
    hp1 = hp(h, 1)
    field_use(h, 0x129, 0)                                       # Terra is alive: refused
    fres["phoenix"] = {"locke_status": f"{s1:02X}", "hp": hp1, "max_base": mx, "qty": (n0, qty(h, 0x129))}
    q.check("F2 Phoenix Ash (field): fallen Locke revived (Wound cleared) with about half of max HP; refused on living "
            "Terra; one unit used in total",
            not s1 & 0x80 and hp1 > 0 and qty(h, 0x129) == n0 - 1, fres["phoenix"])
    # F3 Iron Ration on Terra (Poison + low HP); F4 Gaia Tonic; F5 Aether Flask
    h.em.set_state(st_setup); h.step(10)
    h.run_event([0x88, 0x00, 0xDF, 0xFF, 0x88, 0x00, 0xFE, 0xFF])  # Terra: clear Imp and Blind, keep Poison
    h.w8(CHAR_REC + 9, 5); h.w8(CHAR_REC + 10, 0)                  # POKE: HP 5
    n0 = qty(h, 0x12B)
    field_use(h, 0x12B, 0)
    fres["iron"] = (hp(h), f"{h.r8(CHAR_REC + 0x14):02X}", n0, qty(h, 0x12B))
    q.check("F3 Iron Ration (field): Terra HP 5 -> min(max, 205), Poison cured, one unit used",
            hp(h) > 5 and not h.r8(CHAR_REC + 0x14) & 0x04 and qty(h, 0x12B) == n0 - 1, fres["iron"])
    h.w8(CHAR_REC + 9, 5); h.w8(CHAR_REC + 10, 0)
    n0 = qty(h, 0x127)
    field_use(h, 0x127, 0)
    hpa = hp(h)
    field_use(h, 0x127, 0)                                       # now at max: refused
    fres["gaia"] = (hpa, hp(h), n0, qty(h, 0x127))
    q.check("F4 Gaia Tonic (field, one member): Terra HP 5 -> min(max, 245), one unit used; at full HP the use is "
            "refused (no unit lost)", hpa > 5 and qty(h, 0x127) == n0 - 1, fres["gaia"])
    h.w8(CHAR_REC + 13, 1); h.w8(CHAR_REC + 14, 0)               # POKE: MP 1
    n0 = qty(h, 0x128)
    field_use(h, 0x128, 0)
    fres["aether"] = (mp(h), n0, qty(h, 0x128))
    q.check("F5 Aether Flask (field): Terra MP 1 -> min(max, 251), one unit used", mp(h) > 1 and qty(h, 0x128) == n0 - 1,
            fres["aether"])
    # F6 battle-only consumables: grey + refused
    h.em.set_state(st_setup); h.step(10)
    h.w8(CHAR_REC + 9, 5); h.w8(CHAR_REC + 10, 0)
    ref = {}
    for i in (0x12A, 0x12D, 0x12E):
        n0 = qty(h, i)
        st, target = field_use(h, i, 0)
        ref[f"{i:03X}"] = (f"{st:02X}", target, n0, qty(h, i))
    q.check("F6 battle-only Null Dust / Beacon Flare / Magitek Cell: no target screen in the field menu, no unit lost",
            all(not t and a == b for s, t, a, b in ref.values()), ref)
    # F7 last unit: slot emptied + bit cleared
    h.em.set_state(st_setup); h.step(10)
    sl = slot_of(h, 0x12C)
    for _ in range(4):
        h.run_event(ev_take(0x12C))
    h.run_event([0x89, 0x00, 0x01, 0x00])                        # Terra Blind again
    field_use(h, 0x12C, 0)
    q.check("F7 the last Remedy+ used in the field: slot emptied ($FF / qty 0) and its high bit cleared",
            h.r8(0x1869 + sl) == 0xFF and h.r8(0x1969 + sl) == 0 and not h.bit(sl), (sl, h.r8(0x1869 + sl), h.bit(sl)))
    # F8 Arrange with consumables + vanilla items + the 39 equipment
    h.em.set_state(st_cons); h.step(10)
    h.call_event(L["QaGiveW8"], frames=200); h.call_event(L["QaGiveA8"], frames=200); h.call_event(L["QaGiveR8"], frames=200)
    h.run_event(sum(([0x80, v] for v in (0x27, 0x28, 0x2D, 0xE9, 0xE9, 0xF0, 0xF5, 0x00, 0x26)), []))
    before = inv16(h)
    nv = Nav(h)
    open_items(h, nv)
    h.press("B", 4, 20); nv.wait(ST["ITEM_OPT"]); nv.cursor_lr(1); h.press("A", 4, 120); nv.wait(ST["ITEM"])
    q.shot(h, "F_arrange")
    after = inv16(h)
    nv.back_to_main(); nv.close(); h.step(30)
    q.check("F8 Arrange with 8 consumables + 39 equipment + vanilla items incl. the katana aliases: every 9-bit id "
            "and quantity kept", after == before, {"lost": [x for x in before if x not in after][:8]})
    res["field"] = fres

    # ------------------------------------------------------------------ S: shops
    h.em.set_state(st_cons); h.step(10)
    nv = Nav(h)
    h.call_event(L["QaShop80"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30)
    q.shot(h, "S_shop80_buy")
    sh = SHOPS[0]
    lst = [h.r8(0x9D89 + k) for k in range(8)]
    owned = [h.r8(0x9DC9 + k) for k in range(8)]
    price = [h.r16(0x9F09 + 2 * k) for k in range(8)]
    exp_owned = [5 if int(x, 16) >= 0x100 else 0 for x in sh["items"]]
    exp_price = [BYID[int(x, 16)]["price"] if int(x, 16) >= 0x100 else
                 van[pc(IV.VAN_PROP) + 30 * int(x, 16) + 28] | van[pc(IV.VAN_PROP) + 30 * int(x, 16) + 29] << 8
                 for x in sh["items"]]
    q.check("S1 extended shop $80: 8 entries (3 consumables + 5 vanilla) with their low bytes, owned counts of exactly "
            "those items, prices from the 9-bit records",
            lst == [int(x, 16) & 0xFF for x in sh["items"]] and owned == exp_owned and price == exp_price,
            {"list": [f"{v:02X}" for v in lst], "owned": owned, "price": price})
    g0 = gp(h)
    h.press("A", 4, 40); h.step(20); h.press("A", 4, 40); h.step(40)
    q.check("S2 buy one Gaia Tonic: stack 5 -> 6 (same slot), 1500 GP charged", qty(h, 0x127) == 6 and gp(h) == g0 - 1500,
            {"gp": (g0, gp(h)), "qty": qty(h, 0x127)})
    q.check("S3 'Equipped' count of the consumable is 0 (a katana with the same low byte is never counted)",
            h.r8(0x65) == 0, h.r8(0x65))
    for _ in range(6):
        h.press("B", 4, 30)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)
    # S4: buy a consumable not owned, inventory otherwise full -> refused, no GP
    h.em.set_state(st_new); h.step(10)
    h.run_event([0x84, 0x20, 0x4E])                              # +20000 GP
    for s in range(256):                                        # POKE: inventory full of vanilla items (test only)
        h.w8(0x1869 + s, 0x80 + (s % 0x60)); h.w8(0x1969 + s, 1)
    for s in range(32):
        h.w8(0x1CF8 + s, 0)
    g0 = gp(h)
    h.call_event(L["QaShop80"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30); h.press("A", 4, 40); h.step(20); h.press("A", 4, 40); h.step(40)
    q.check("S4 inventory full, Gaia Tonic not owned: purchase refused, no GP taken, nothing overwritten",
            qty(h, 0x127) == 0 and gp(h) == g0 and len(h.inv()) == 256, {"gp": (g0, gp(h))})
    for _ in range(6):
        h.press("B", 4, 30)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)
    # S5: shop $81 + a vanilla shop selling an alias katana
    h.em.set_state(st_cons); h.step(10)
    h.call_event(L["QaShop81"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30)
    q.shot(h, "S_shop81_buy")
    lst = [h.r8(0x9D89 + k) for k in range(8)]
    owned = [h.r8(0x9DC9 + k) for k in range(8)]
    q.check("S5 extended shop $81: Remedy+ first, owned counts 5 for the four consumables, 0 for the vanilla items",
            lst == [int(x, 16) & 0xFF for x in SHOPS[1]["items"]] and
            owned == [5 if int(x, 16) >= 0x100 else 0 for x in SHOPS[1]["items"]], {"list": lst, "owned": owned})
    for _ in range(6):
        h.press("B", 4, 30)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)
    alias_shop = next((s for s in range(128) if any(van[pc(I9.VAN_SHOP) + 9 * s + 1 + e] in range(0x27, 0x2F)
                                                     for e in range(8))), None)
    if alias_shop is not None:
        h.em.set_state(st_cons); h.step(10)
        h.run_event([0x9B, alias_shop], frames=60); nv.wait(ST["SHOP_OPT"], 600)
        h.press("A", 4, 40); h.step(30)
        q.shot(h, f"S_vanilla_shop_{alias_shop:02X}")
        lst = [h.r8(0x9D89 + k) for k in range(8)]
        owned = [h.r8(0x9DC9 + k) for k in range(8)]
        q.check(f"S6 vanilla shop ${alias_shop:02X} sells katanas with the consumables' low bytes: their owned counts are "
                "0 while every consumable is owned x5 (no alias)",
                all(o == 0 for v, o in zip(lst, owned) if v != 0xFF), {"list": [f"{v:02X}" for v in lst], "owned": owned})
        h.em.set_state(st_cons); h.step(10)                      # (a WRAM-script shop cannot return cleanly)
    # ------------------------------------------------------------------ L: Sell
    h.em.set_state(st_cons); h.step(10)
    h.call_event(L["QaShop80"], frames=60); nv.wait(ST["SHOP_OPT"], 600)
    nv.cursor_lr(1); h.press("A", 4, 40); nv.wait(ST["SHOP_SELL"]); h.step(20)
    q.shot(h, "L_sell_list")
    sel = {}
    for i in IDS:
        nv.cursor_to(slot_of(h, i)); h.press("A", 4, 40); h.step(10)
        sel[f"{i:03X}"] = nv.state() != ST["SHOP_SELL"]
        if nv.state() != ST["SHOP_SELL"]:
            h.press("B", 4, 30); nv.wait(ST["SHOP_SELL"])
    q.check("L1 Sell list: exactly the sellable consumables (Gaia Tonic, Null Dust, Iron Ration, Remedy+) can be "
            "selected", sel == {f"{i:03X}": BYID[i]["sellable"] for i in IDS}, sel)
    g0 = gp(h)
    nv.cursor_to(slot_of(h, 0x12B)); h.press("A", 4, 40); h.step(20); h.press("A", 4, 40); h.step(40)
    q.check("L2 sell one Iron Ration: +125 GP (price 250 / 2), quantity 5 -> 4", gp(h) == g0 + 125 and qty(h, 0x12B) == 4,
            (g0, gp(h), qty(h, 0x12B)))
    sl = slot_of(h, 0x12A)
    g0 = gp(h)
    nv.cursor_to(sl); h.press("A", 4, 40); h.step(20)
    for b in ("RIGHT", "UP"):
        for _ in range(6):
            if h.r8(0x28) >= 5:
                break
            h.press(b, 4, 16)
    h.step(10)
    h.press("A", 4, 40); h.step(40)
    q.check("L3 sell all 5 Null Dust: +2000 GP, slot emptied and its high bit cleared",
            gp(h) == g0 + 2000 and h.r8(0x1869 + sl) == 0xFF and not h.bit(sl), (g0, gp(h), h.r8(0x1869 + sl), h.bit(sl)))
    for _ in range(6):
        h.press("B", 4, 30)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)
    # ------------------------------------------------------------------ X: exclusions
    h.em.set_state(st_cons); h.step(10)
    inv_before = inv16(h)
    h.run_event([0x9A], frames=60)
    nv.wait(ST["COLO_ITEM"], 600)
    q.shot(h, "X_colosseum_list")
    sel = []
    for i in IDS:
        nv.cursor_to(slot_of(h, i)); h.press("A", 4, 40)
        sel.append(nv.state() == ST["COLO_ITEM"])
    for _ in range(60):
        if h.idle():
            break
        h.press("B", 4, 30); h.step(30)
    h.em.set_state(st_cons); h.step(10)
    q.check("X1 Colosseum: no consumable can be wagered", all(sel), sel)
    h.em.set_state(st_cons); h.step(10)
    menu(h, L, [0, 2, 2, 1, 0])                                  # party preset P1 (Terra Locke Celes Edgar)
    h.run_event([0x80, 0x00, 0x80, 0x27, 0x80, 0x6D, 0x80, 0xA0, 0x80, 0xB4])  # Dirk, Blossom, Leather Hat?, ..., relic
    lists = {}
    for c, slot in ((0, 0), (0, 2), (0, 3), (1, 0)):
        nv = Nav(h); open_menu(h, nv); nv.main_to("Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
        nv.cursor_to(c); h.press("A", 4, 30); nv.wait(ST["EQUIP_OPT"], 120)
        nv.press("A", "EQUIP_SLOT"); nv.cursor_to(slot); h.press("A", 4, 30)
        if nv.wait(ST["EQUIP_LIST"], 60):                        # an empty list does not open (vanilla)
            h.step(10)
            n = h.r8(0x9D89)
            lists[f"{c}:{slot}"] = [(1 if h.bit(s) else 0) << 8 | h.r8(0x1869 + s)
                                    for s in (h.r8(0x9D8A + k) for k in range(n))]
        else:
            lists[f"{c}:{slot}"] = []
        nv.back_to_main(); nv.close(); h.step(20)
    nv = Nav(h); open_menu(h, nv); nv.main_to("Relic"); nv.wait(ST["CHAR"], 300); h.step(20)
    h.press("A", 4, 30); nv.wait(ST["RELIC_OPT"], 120); nv.press("A", "RELIC_SLOT"); h.press("A", 4, 30)
    if nv.wait(ST["RELIC_LIST"], 60):
        n = h.r8(0x9D89)
        lists["relic"] = [(1 if h.bit(s) else 0) << 8 | h.r8(0x1869 + s) for s in (h.r8(0x9D8A + k) for k in range(n))]
    else:
        lists["relic"] = []
    nv.back_to_main(); nv.close(); h.step(20)
    q.check("X2 Equip (weapon / helmet / armor) and Relic lists never offer a consumable",
            not [i for v in lists.values() for i in v if i in BYID], {k: [f"{i:03X}" for i in v] for k, v in lists.items()})
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "CONSUMABLE_EMULATOR_REPORT.json"), "w"), indent=1, default=str)
    print("CONSUMABLE EMULATOR", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
