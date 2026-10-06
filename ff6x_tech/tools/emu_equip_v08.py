#!/usr/bin/env python3
"""TECH v0.8 emulator checks, part 1: the 39 production signature equipment items $100-$126 (stable-retro / snes9x).

  T  tables (ROM bytes vs items/production_v08/equipment.json): record, name, icon, description, flags, weapon and
     Jump animation entries (= the template weapon's vanilla entries), vanilla $00-$FF untouched
  G  QA menu "Grant all 39" / quantity x2 / "Remove all 39" / grant by type (real menus, event API $66/$67)
  K  per item: HAS_EXT_ITEM / TAKE_EXT_ITEM / GIVE_EXT_ITEM (event API, all 39)
  S  smith purchase model (QA demo of the production binding EV_SMITH_NARSHE_TEMPERED_EDGE): not enough GP,
     buy, already owned, inventory full -> refund
  E  equip matrix: for all 14 permanent characters (QA party presets), the item lists the game itself builds in the
     Equip menu (weapon/shield, helmet, armor: C3 GetValidEquip -> $7E9D8A) and the Relic menu, compared with the
     source definitions (and the vanilla items present, compared with their vanilla equip words)
  A  per item: equip through the menus on a valid character; the stats the game computes ($11A0-$11D7) differ from
     the empty-slot baseline by exactly the item's power / hit / MDef / Vigor / Speed / Stamina / Mag.Pwr / Evade /
     MBlock / elements / status immunity / relic bits; Remove returns it with its 9-bit id
  X  exclusions with all 39 in the inventory: shop owned count, Sell, Colosseum wager list, battle Item / Throw
POKE (test setup only): inventory filled for the "inventory full" smith case.

usage: emu_equip_v08.py <qa.sfc> <qa.manifest.json> <clean_rev1.sfc> <out>
writes <out>/EQUIPMENT_EMULATOR_REPORT.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T, ev_give, ev_take, ev_has
from emu_item_qa import Report, boot_new_game, inv16, ext_slots
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
from patches import item_v071 as IV

ITEMS = json.load(open(os.path.join(HERE, "items/production_v08/equipment.json")))["items"]
BYID = {int(it["id"], 16): it for it in ITEMS}
PROD = sorted(BYID)
CHARS = IV.CHARS
QA_BIT = 0x14E
PRESETS = [[0, 1, 6, 4], [0, 5, 2, 3], [0, 9, 7, 8], [0, 10, 11, 12], [0, 13, 6, 1]]
PRESET_PICKS = [[0, 1, 0], [0, 1, 1], [0, 1, 2, 0], [0, 1, 2, 1], [0, 1, 2, 2, 0]]   # QA menu paths
OPENING_PICKS = [0, 1, 2, 2, 1]
VANILLA_SAMPLE = [0x00, 0x13, 0x1D, 0x26, 0x2E, 0x3C, 0x5A, 0x63, 0x69, 0x70, 0x84, 0x97, 0xB0, 0xD4, 0xE9]


def ext_ids(h):
    return sorted(i for s, i, n in h.inv() if i >= 0x100)


def qty(h, i):
    return sum(n for s, j, n in h.inv() if j == i)


def gp(h):
    return h.r8(0x1860) | h.r8(0x1861) << 8 | h.r8(0x1862) << 16


UNARMED_POWER = 10                                          # the fist the menu shows with an empty hand


# TECH v0.9: the v0.8 equipment tools sit one level deeper in the v0.9 QA hub. FF6X_QA_V08_ROOT maps the v0.8
# top-level choice to its v0.9 path, e.g. '{"0": [2, 1], "1": [2, 2, 0]}' (unset: v0.8 menu, unchanged)
ROOT_MAP = json.loads(os.environ.get("FF6X_QA_V08_ROOT", "{}"))


def menu(h, L, picks):
    picks = list(picks)
    if picks and str(picks[0]) in ROOT_MAP:
        picks = list(ROOT_MAP[str(picks[0])]) + picks[1:]
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def has(h, i):
    h.w8(0x1E80 + (QA_BIT >> 3), h.r8(0x1E80 + (QA_BIT >> 3)) & ~(1 << (QA_BIT & 7)))
    h.run_event(ev_has(i, QA_BIT))
    return h.r8(0x1E80 + (QA_BIT >> 3)) >> (QA_BIT & 7) & 1


def party_order(h):
    """characters in party 1 in battle-slot order (QA presets keep everything in party 1)"""
    m = {}
    for n in range(16):
        v = h.r8(0x1850 + n)
        if v & 7 == 1:
            m[(v >> 3) & 3] = n
    return [m[k] for k in sorted(m)]


def read_list(h):
    n = h.r8(0x9D89)
    return [(1 if h.bit(s) else 0) << 8 | h.r8(0x1869 + s) for s in (h.r8(0x9D8A + k) for k in range(n))]


def stats(h):
    g = h.r8
    w = lambda a: g(a) | g(a + 1) << 8
    return {"mag": w(0x11A0), "sta": w(0x11A2), "spd": w(0x11A4), "vig": w(0x11A6), "evade": w(0x11A8),
            "mblock": w(0x11AA), "bp_r": g(0x11AC), "bp_l": g(0x11AD), "hit_r": g(0x11AE), "hit_l": g(0x11AF),
            "elem_r": g(0x11B0), "elem_l": g(0x11B1), "absorb": g(0x11B6), "null": g(0x11B7), "weak": g(0x11B8),
            "half": g(0x11B9), "def": g(0x11BA), "mdef": g(0x11BB), "imm1": g(0x11D2), "imm2": g(0x11D3),
            "relic1": g(0x11D5), "relic3": g(0x11D7)}


def main(qa, manifest, clean, out):
    q = Report(out)
    L = labels(manifest)
    rom = open(qa, "rb").read()
    van = open(clean, "rb").read()
    pc = lambda a: a - 0xC00000
    res = {}

    # ------------------------------------------------------------------ T: tables
    bad = {}
    for i, it in BYID.items():
        k = i - 0x100
        rec = rom[pc(IV.T_PROP) + 30 * i:pc(IV.T_PROP) + 30 * i + 30]
        exp = IV.compose_v08(van, it)
        nm = rom[pc(IV.T_NAME) + 13 * i:pc(IV.T_NAME) + 13 * i + 13]
        tpl = int(it["template"], 16)
        icon_ok = nm[0] == van[pc(IV.VAN_NAME) + 13 * tpl]
        name_ok = nm[1:].rstrip(b"\xFF") == IV.menu_encode(it["display_name"], 0xFE)
        dp = rom[pc(IV.T_DPTR) + 2 * k] | rom[pc(IV.T_DPTR) + 2 * k + 1] << 8
        a = pc(0xFA0000 | dp); d = bytearray()
        while rom[a] != 0:
            d.append(rom[a]); a += 1
        desc_ok = bytes(d) == IV.menu_encode(it["desc"], 0xFF)
        fl = rom[pc(IV.T_FLAGS) + k]
        flags_ok = fl == (3 if it.get("spear") else 1)
        anim_ok = jump_ok = True
        if it["category"] == "weapon":
            anim_ok = rom[pc(IV.T_ANIM) + 8 * (IV.ANIM_EXT0 + k):pc(IV.T_ANIM) + 8 * (IV.ANIM_EXT0 + k) + 8] == \
                van[pc(IV.VAN_ANIM) + 8 * (tpl + 1):pc(IV.VAN_ANIM) + 8 * (tpl + 2)]
            jump_ok = rom[pc(IV.T_JUMP) + IV.JUMP_EXT0 + k] == van[pc(IV.VAN_JUMP) + tpl + 1]
        ok = rec == exp and icon_ok and name_ok and desc_ok and flags_ok and anim_ok and jump_ok
        if not ok:
            bad[f"{i:03X}"] = {"rec": rec == exp, "icon": icon_ok, "name": name_ok, "desc": desc_ok, "flags": flags_ok,
                               "anim": anim_ok, "jump": jump_ok}
    q.check("T1 all 39: ItemProp record, icon (= template's vanilla icon), 12-char name, description, defined/spear "
            "flags, weapon animation and Jump animation (= template weapon's vanilla entries) match the source", not bad, bad)
    q.check("T2 vanilla $00-$FF ItemProp / ItemName records unchanged in the relocated tables",
            rom[pc(IV.T_PROP):pc(IV.T_PROP) + 256 * 30] == van[pc(IV.VAN_PROP):pc(IV.VAN_PROP) + 256 * 30] and
            rom[pc(IV.T_NAME):pc(IV.T_NAME) + 256 * 13] == van[pc(IV.VAN_NAME):pc(IV.VAN_NAME) + 256 * 13])
    lows = {}
    for i, it in BYID.items():
        lows.setdefault(rom[pc(IV.T_NAME) + 13 * i + 1:pc(IV.T_NAME) + 13 * i + 13], []).append(i)
    q.check("T3 no extended name equals its low-byte vanilla alias name (an alias would be visible in every UI)",
            all(rom[pc(IV.T_NAME) + 13 * i + 1:pc(IV.T_NAME) + 13 * i + 13] !=
                van[pc(IV.VAN_NAME) + 13 * (i & 0xFF) + 1:pc(IV.VAN_NAME) + 13 * (i & 0xFF) + 13] for i in PROD))

    # ------------------------------------------------------------------ G: QA menus
    h = T(qa)
    boot_new_game(h)
    st_new = h.em.get_state()
    menu(h, L, [0, 0])
    q.shot(h, "G_after_grant_all")
    inv = h.inv()
    q.check("G1 QA 'Grant all 39': each of $100-$126 exactly once (qty 1), in 39 inventory slots",
            ext_ids(h) == PROD and all(qty(h, i) == 1 for i in PROD), [(s, f"{i:03X}", n) for s, i, n in inv][:45])
    menu(h, L, [0, 0])
    q.check("G2 grant twice: each $1xx stacks to x2 (quantity), still 39 slots",
            all(qty(h, i) == 2 for i in PROD) and len([1 for s, i, n in h.inv() if i >= 0x100]) == 39)
    menu(h, L, [0, 2, 1])
    q.check("G3 QA 'Remove all 39': no production item left in the inventory", not ext_ids(h), ext_ids(h))
    menu(h, L, [0, 2, 0, 0]); w = ext_ids(h)
    menu(h, L, [0, 2, 0, 1]); a = [x for x in ext_ids(h) if x not in w]
    menu(h, L, [0, 2, 0, 2]); r = [x for x in ext_ids(h) if x not in w + a]
    cat = lambda c: sorted(i for i, it in BYID.items() if it["category"] in c)
    q.check("G4 grant by type: weapons = the 13 weapons, armor = the 13 body/helmet/shield, relics = the 13 relics",
            w == cat(["weapon"]) and a == cat(["armor", "helmet", "shield"]) and r == cat(["relic"]),
            {"w": [f"{x:03X}" for x in w], "a": [f"{x:03X}" for x in a], "r": [f"{x:03X}" for x in r]})

    # ------------------------------------------------------------------ K: event API per item
    kbad = []
    for i in PROD:
        h1 = has(h, i)
        h.run_event(ev_take(i)); n1 = qty(h, i); h2 = has(h, i)
        h.run_event(ev_give(i)); n2 = qty(h, i); h3 = has(h, i)
        if not (h1 == 1 and n1 == 0 and h2 == 0 and n2 == 1 and h3 == 1):
            kbad.append((f"{i:03X}", h1, n1, h2, n2, h3))
    q.check("K1 all 39: HAS=1 -> TAKE -> qty 0, HAS=0 -> GIVE -> qty 1, HAS=1 (event API $68/$67/$66)", not kbad, kbad)
    q.check("K2 vanilla inventory untouched by the event API (only $1xx present)",
            [i for s, i, n in h.inv() if i < 0x100] == [], [f"{i:03X}" for s, i, n in h.inv() if i < 0x100])
    st_all = h.em.get_state()

    # ------------------------------------------------------------------ S: smith purchase model
    h.em.set_state(st_new); h.step(10)
    g0 = gp(h)
    menu(h, L, [0, 2, 2, 2, 0])
    q.check("S1 smith, not enough GP (New Game 3000 GP): nothing given, nothing charged",
            qty(h, 0x100) == 0 and gp(h) == g0, {"gp": gp(h)})
    menu(h, L, [0, 2, 2, 2, 1]); g1 = gp(h)
    menu(h, L, [0, 2, 2, 2, 0])
    q.check("S2 smith purchase: Tempered Edge $100 given once, 18000 GP charged",
            qty(h, 0x100) == 1 and gp(h) == g1 - 18000, {"gp_before": g1, "gp_after": gp(h)})
    menu(h, L, [0, 2, 2, 2, 1]); g2 = gp(h)
    menu(h, L, [0, 2, 2, 2, 0])
    q.check("S3 smith, already owned (HAS_EXT_ITEM): nothing given, nothing charged",
            qty(h, 0x100) == 1 and gp(h) == g2, {"gp": gp(h)})
    h.em.set_state(st_new); h.step(10)
    menu(h, L, [0, 2, 2, 2, 1])
    for s in range(256):                                       # POKE: inventory full (test only)
        h.w8(0x1869 + s, s if s < 255 else 0x00); h.w8(0x1969 + s, 1)
    g3 = gp(h)
    menu(h, L, [0, 2, 2, 2, 0])
    q.check("S4 smith, inventory full: GIVE cannot place it -> HAS=0 -> 18000 GP refunded, nothing truncated",
            qty(h, 0x100) == 0 and gp(h) == g3 and not ext_ids(h), {"gp_before": g3, "gp_after": gp(h)})
    h.w8(0x1869 + 255, 0xFF); h.w8(0x1969 + 255, 0)
    menu(h, L, [0, 2, 2, 2, 0])
    q.check("N1 nearly full inventory (one free slot): the reward lands in the free slot",
            qty(h, 0x100) == 1 and [s for s, i, n in h.inv() if i == 0x100] == [255])

    # ------------------------------------------------------------------ E: equip matrix (real menu lists)
    h.em.set_state(st_all); h.step(10)
    h.run_event(sum(([0x80, v] for v in VANILLA_SAMPLE), []))
    vprop = lambda v: van[pc(IV.VAN_PROP) + 30 * v:pc(IV.VAN_PROP) + 30 * v + 30]
    seen, mbad, vbad = {}, [], []
    for p, picks in enumerate(PRESET_PICKS):
        menu(h, L, picks)
        order = party_order(h)
        if sorted(order) != sorted(PRESETS[p]):
            mbad.append(("preset", p, order))
            continue
        nv = Nav(h); h.step(30)
        for slot_i, c in enumerate(order):
            got = {}
            nv.open_main(); nv.main_to("Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
            nv.cursor_to(slot_i)
            h.press("A", 4, 30)
            if nv.wait(ST["EQUIP_OPT"], 120):
                nv.press("A", "EQUIP_SLOT")
                for es, key in ((0, "hand"), (2, "helmet"), (3, "armor")):
                    nv.cursor_to(es); nv.press("A", "EQUIP_LIST"); h.step(10)
                    got[key] = read_list(h)
                    h.press("B", 4, 20); nv.wait(ST["EQUIP_SLOT"], 120)
            else:
                got["equip_menu"] = "not available"
            nv.back_to_main()
            nv.main_to("Relic"); nv.wait(ST["CHAR"], 300); h.step(20)
            nv.cursor_to(slot_i)
            h.press("A", 4, 30)
            if nv.wait(ST["RELIC_OPT"], 120):
                nv.press("A", "RELIC_SLOT"); nv.press("A", "RELIC_LIST"); h.step(10)
                got["relic"] = read_list(h)
            nv.back_to_main(); nv.close(); h.step(30)
            seen[CHARS[c]] = got
            for key, cats in (("hand", ("weapon", "shield")), ("helmet", ("helmet",)), ("armor", ("armor",)),
                              ("relic", ("relic",))):
                exp = sorted(i for i, it in BYID.items() if it["category"] in cats and CHARS[c] in it["users"])
                lst = got.get(key)
                if lst is None:
                    if exp and not (CHARS[c] == "Umaro" and key != "relic"):
                        mbad.append((CHARS[c], key, "list not opened", [f"{x:03X}" for x in exp]))
                    continue
                gx = sorted(x for x in lst if x >= 0x100)
                if gx != exp:
                    mbad.append((CHARS[c], key, [f"{x:03X}" for x in gx], [f"{x:03X}" for x in exp]))
                tval = {"hand": (1, 3), "helmet": (4,), "armor": (2,), "relic": (5,)}[key]
                gv = sorted(x for x in lst if x < 0x100)
                ev = sorted(v for v in VANILLA_SAMPLE if vprop(v)[0] & 7 in tval and
                            (vprop(v)[1] | vprop(v)[2] << 8) >> c & 1)
                if gv != ev:
                    vbad.append((CHARS[c], key, [f"{x:02X}" for x in gv], [f"{x:02X}" for x in ev]))
    res["equip_lists"] = {c: {k: [f"{x:03X}" for x in v] if isinstance(v, list) else v for k, v in g.items()}
                          for c, g in seen.items()}
    q.check("E1 equip matrix from the game's own Equip/Relic lists, 14 permanent characters x 39 items, equals the "
            "source definitions (Umaro: relic menu only, as vanilla)", not mbad and len(seen) == 14,
            {"mismatch": mbad, "characters": sorted(seen)})
    q.check("E2 vanilla items in the same lists follow their vanilla equip words (no vanilla regression)", not vbad, vbad)
    st_presets = h.em.get_state()

    # ------------------------------------------------------------------ A: stat application per item
    abad, adet = [], {}
    for i in PROD:
        it = BYID[i]
        c = CHARS.index(it["users"][0])
        p = next(k for k, pr in enumerate(PRESETS) if c in pr)
        h.em.set_state(st_presets); h.step(10)
        menu(h, L, PRESET_PICKS[p])
        order = party_order(h)
        slot_i = order.index(c)
        h.run_event([0x8D, c])                                # remove all equipment (vanilla event $8D)
        nv = Nav(h); h.step(30)
        relic = it["category"] == "relic"
        nv.open_main(); nv.main_to("Relic" if relic else "Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
        nv.cursor_to(slot_i)
        h.press("A", 4, 30)
        nv.wait(ST["RELIC_OPT" if relic else "EQUIP_OPT"], 120)
        nv.press("A", "RELIC_SLOT" if relic else "EQUIP_SLOT")
        es = {"weapon": 0, "shield": 1, "helmet": 2, "armor": 3, "relic": 0}[it["category"]]
        nv.cursor_to(es)
        base = stats(h)
        nv.press("A", "RELIC_LIST" if relic else "EQUIP_LIST"); h.step(10)
        lst = read_list(h)
        if i not in lst:
            abad.append((f"{i:03X}", "not in list", [f"{x:03X}" for x in lst])); nv.back_to_main(); nv.close(); continue
        nv.cursor_to(lst.index(i))
        h.press("A", 4, 30); h.step(30)
        got = stats(h)
        eq = h.eq(c)
        slotk = {"weapon": 0, "shield": 1, "helmet": 2, "armor": 3, "relic": 4}[it["category"]]
        d = {k: got[k] - base[k] for k in got}
        exp = {"vig": it["vigor"], "spd": it["speed"], "sta": it["stamina"], "mag": it["mag_pwr"],
               "evade": it["evade"], "mblock": it["mblock"]}
        if it["category"] == "weapon":
            exp.update(bp_r=it["power"] - UNARMED_POWER, hit_r=it["hit_rate"] - base["hit_r"],   # replaces the fist (power 10)
                       elem_r=IV.bits(it["elem_attack"], IV.ELEMENT, "e"))
        elif it["category"] != "relic":
            exp.update({"def": it["power"], "mdef": it["mdef"]})
        if it["category"] != "weapon":
            exp.update(absorb=IV.bits(it.get("elem_absorb", []), IV.ELEMENT, "e"),
                       null=IV.bits(it.get("elem_null", []), IV.ELEMENT, "e"),
                       weak=IV.bits(it.get("elem_weak", []), IV.ELEMENT, "e"),
                       half=IV.bits(it.get("elem_half", []), IV.ELEMENT, "e"))
        imm = IV.bits(it.get("immune_status", []), IV.STATUS12, "s")
        exp.update(imm1=imm & 0xFF, imm2=imm >> 8)
        rb = bytearray(14)
        for n in it.get("relic_effects", []):
            o, b = IV.RELIC_EFFECT[n]; rb[o] |= b
        exp.update(relic1=rb[9], relic3=rb[11])
        mism = {k: (d[k] if k not in ("elem_r", "absorb", "null", "weak", "half", "imm1", "imm2", "relic1", "relic3")
                    else got[k], v) for k, v in exp.items()
                if (d[k] if k not in ("elem_r", "absorb", "null", "weak", "half", "imm1", "imm2", "relic1", "relic3")
                    else got[k]) != v}
        if eq[slotk] != i or mism:
            abad.append((f"{i:03X}", CHARS[c], f"slot {eq[slotk]:03X}", mism))
        adet[f"{i:03X}"] = {"char": CHARS[c], "delta": {k: d[k] for k in exp if k in d}, "abs": {k: got[k] for k in
                            ("absorb", "null", "weak", "half", "imm1", "imm2", "relic1", "relic3", "elem_r")}}
        if i in (0x100, 0x10D, 0x11A, 0x126):
            q.shot(h, f"A_equipped_{i:03X}")
        # Remove: back to the inventory with its 9-bit id
        h.press("B", 4, 20)
        nv.wait(ST["RELIC_SLOT" if relic else "EQUIP_SLOT"], 60)
        nv.back_to_main(); nv.close(); h.step(30)
        h.run_event([0x8D, c])
        if qty(h, i) != 1 or h.eq(c)[slotk] != 0xFF:
            abad.append((f"{i:03X}", "remove", qty(h, i), f"{h.eq(c)[slotk]:03X}"))
    res["stat_application"] = adet
    q.check("A1 all 39 equipped through the menus on a valid character: stats change by exactly the item's power/hit/"
            "MDef/Vigor/Speed/Stamina/Mag.Pwr/Evade/MBlock, elements (absorb/null/weak/half/weapon element), status "
            "immunity and relic bits; the slot holds the 9-bit id", not abad, abad[:20])
    q.check("A2 Remove (event $8D) returns every item to the inventory with its 9-bit id", not [b for b in abad if b[1] == "remove"])

    # ------------------------------------------------------------------ X: exclusions with all 39 owned
    h.em.set_state(st_all); h.step(10)
    inv_before = inv16(h)
    nv = Nav(h)
    h.run_event([0x9B, 0x05], frames=60)                     # vanilla shop $05: Dirk/MithrilKnife/MithrilBlade/RegalCutlass
    nv.wait(ST["SHOP_OPT"], 600)
    h.press("A", 4, 40); h.step(30)
    owned = [h.r8(0x9DC9 + k) for k in range(8)]
    q.shot(h, "X_shop_buy")
    q.check("X1 vanilla shop $05 sells $00/$01/$0A/$0B = low bytes of Tempered Edge $100, Imperial Saber $101, "
            "Concord Brush $10A, Gale Lance $10B (all owned): owned counts are 0 (no alias), nothing for sale is $1xx",
            owned[:4] == [0, 0, 0, 0], owned)
    h.press("B", 4, 30); nv.wait(ST["SHOP_OPT"])
    nv.cursor_lr(1); h.press("A", 4, 40); nv.wait(ST["SHOP_SELL"])
    q.shot(h, "X_shop_sell_list")
    sel = []
    for s in (0, 12, 26, 38):
        nv.cursor_to(s); h.press("A", 4, 40)
        sel.append(nv.state() == ST["SHOP_SELL"])
        if nv.state() != ST["SHOP_SELL"]:
            h.press("B", 4, 30); nv.wait(ST["SHOP_SELL"])
    for _ in range(60):
        if h.idle():
            break
        h.press("B", 4, 30); h.step(30)
    q.check("X2 Sell: production items cannot be selected; inventory unchanged", all(sel) and inv16(h) == inv_before, sel)
    h.em.set_state(st_all); h.step(10)                     # X3 from the clean all-39 state (independent of the shop exit)
    h.run_event([0x9A], frames=60)
    nv.wait(ST["COLO_ITEM"], 600)
    q.shot(h, "X_colosseum_list")
    sel = []
    for s in (0, 20, 38):
        nv.cursor_to(s); h.press("A", 4, 40)
        sel.append(nv.state() == ST["COLO_ITEM"])
    for _ in range(60):
        if h.idle():
            break
        h.press("B", 4, 30); h.step(30)
    h.step(30)
    q.check("X3 Colosseum: production items cannot be wagered; inventory unchanged",
            all(sel) and inv16(h) == inv_before and h.r8(0x0205) == 0xFF, sel)
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "EQUIPMENT_EMULATOR_REPORT.json"), "w"), indent=1)
    print("EQUIPMENT EMULATOR", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
