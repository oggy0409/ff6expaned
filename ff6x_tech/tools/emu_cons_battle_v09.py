#!/usr/bin/env python3
"""TECH v0.9 emulator checks, part 2: the 8 consumables in battle (stable-retro / snes9x).

Setup: New Game (QA ROM) -> QA "Grant all 8 (x5)" (+ "Grant all 39" for B1) -> QA party preset (P1 Terra/Locke/Celes/
Edgar, P2 Terra/Sabin/Cyan/Shadow for the Throw case) -> field statuses / HP / MP set with event commands $88/$89 or
POKEs (test setup only) -> QA consumable test battle (event battle $01, Narshe guards). Terra uses the item through
the real battle menu: Item -> the entry -> A -> A (use) -> target -> A.

  B1 battle Item list: exactly the 8 consumables (9-bit names, quantity, usable flags, targeting) + vanilla items;
     none of the 39 signature equipment items in the inventory appears (critical v0.9 rule)
  B2-B9 per consumable: effect of its record on the target(s) (HP / MP / revive / status cure / status removal from an
     enemy / Fire damage to all enemies), quantity -1 when the action is chosen, extended name window and item
     animation flags consumed (screenshots in the contact sheet)
  BH a held extended consumable (action queued, Terra petrified before acting) comes back at battle end
  BT Throw (Shadow) of the vanilla katana Blossom ($27 = Gaia Tonic's low byte): the katana is thrown and removed,
     Gaia Tonic untouched (marker-aware C1 searches)
  BR battle end: inventory = before - used, the 39 equipment / signature gear and bitmaps unchanged, no stale bit

usage: emu_cons_battle_v09.py <qa.sfc> <qa.manifest.json> <out>
writes <out>/CONSUMABLE_BATTLE_REPORT.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T, ev_give
from emu_item_qa import Report, boot_new_game, inv16
from emu_item_battle import labels, talk, to_terra, bslot
from emu_equip_battle_v08 import finish_battle

CONS = json.load(open(os.path.join(HERE, "items/production_v09/consumables.json")))["items"]
BYID = {int(c["id"], 16): c for c in CONS}
IDS = sorted(BYID)
HP, MP, MAXHP, MAXMP, ST12, ST34 = 0x3BF4, 0x3C08, 0x3C1C, 0x3C30, 0x3EE4, 0x3EF8
CMD_CURSOR, XATKX = 0x2C, 0x1E37


def menu(h, L, picks):
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def qty(h, i):
    return sum(n for s, j, n in h.inv() if j == i)


def bstate(h):
    return {"hp": [h.r16(HP + 2 * t) for t in range(10)], "mp": [h.r16(MP + 2 * t) for t in range(4)],
            "maxhp": [h.r16(MAXHP + 2 * t) for t in range(4)], "maxmp": [h.r16(MAXMP + 2 * t) for t in range(4)],
            "st12": [h.r16(ST12 + 2 * t) for t in range(10)], "st34": [h.r16(ST34 + 2 * t) for t in range(10)]}


def blist(h):
    return [bslot(h, s) for s in range(256)]


def start(h, L):
    h.call_event(L["QaConsBtl9"], frames=1)
    for _ in range(900):
        h.step(1)
    to_terra(h)
    h.step(30)


def choose_item(h, entry, cmd=3, moves=(), shots=None, q=None, tag=""):
    """Terra (active menu): command `cmd` -> list entry `entry` -> A A -> target moves -> A"""
    for _ in range(8):
        if h.r8(CMD_CURSOR) == cmd:
            break
        h.press("DOWN", 8, 24)
    h.press("A", 8, 60)
    for _ in range(entry):
        h.press("DOWN", 8, 16)
    h.step(10)
    if q:
        q.shot(h, f"{tag}_list")
    h.press("A", 8, 40); h.press("A", 8, 60)
    for m in moves:
        h.press(m, 8, 24)
    if q:
        q.shot(h, f"{tag}_target")
    h.press("A", 8, 10)


def run_action(h, q, tag, frames=700):
    """step until the item's name / animation flags are consumed (or `frames`); shots of the name and animation"""
    seen_name = seen_anim = None
    for t in range(frames):
        h.step(1)
        x = h.r8(XATKX)
        if seen_name is None and x == 0x02:
            seen_name = t
            h.step(8); q.shot(h, f"{tag}_name")
        if seen_anim is None and seen_name is not None and x == 0x00:
            seen_anim = t
            h.step(20); q.shot(h, f"{tag}_anim")
            h.step(160)
            break
    return seen_name, seen_anim


def main(qa, manifest, out):
    q = Report(out)
    L = labels(manifest)
    res = {}
    h = T(qa)
    boot_new_game(h)
    menu(h, L, [0, 0])                                            # 8 consumables x5
    st_cons = h.em.get_state()
    menu(h, L, [2, 1, 0])                                         # + all 39 equipment (v0.8 tools)
    menu(h, L, [0, 2, 2, 1, 0])                                   # preset P1
    st_all = h.em.get_state()

    # ------------------------------------------------------------------ B1: battle list
    inv0 = inv16(h)
    start(h, L)
    bl = blist(h)
    ents = [(e[0] | (0x100 if e[1] & 1 else 0), e) for e in bl if e[0] != 0xFF]
    cons_ok = all(any(i == c and e[3] == 5 and e[2] == {"ONE_ALLY": 0x01, "ONE_ENEMY": 0x41, "ALL_ALLIES": 0x2E,
                                                          "ALL_ENEMIES": 0x6E}[BYID[c]["targeting"]] and
                      (e[1] & 0x80 == 0) == BYID[c]["usable_battle"] for i, e in ents) for c in IDS)
    eq_vis = [f"{e[0]:02X}" for i, e in ents if i < 0x100 and e[0] < 0x27]
    q.shot(h, "B1_battle_list")
    q.check("B1 battle Item list: the 8 consumables with marker, quantity 5, their own targeting and usable flags; "
            "none of the 39 signature equipment in the inventory is listed (equipment slots stay empty)",
            cons_ok and len([1 for i, e in ents if i >= 0x100]) == 8 and not eq_vis,
            {"entries": [(f"{i:03X}", " ".join(f"{b:02X}" for b in e)) for i, e in ents][:16], "equipment_seen": eq_vis})
    finish_battle(h)
    q.check("B1b battle end with everything in the inventory: inventory (8 consumables + 39 equipment) unchanged",
            inv16(h) == inv0)

    # ------------------------------------------------------------------ per consumable
    def case(tag, item, setup_field, moves, check, extra_frames=0):
        h.em.set_state(st_all); h.step(10)
        if setup_field:
            setup_field(h)
        n0 = qty(h, item)
        start(h, L)
        if tag.startswith("B7"):
            h.w8(ST12 + 1, h.r8(ST12 + 1) | 0x08)                 # POKE (test only): Terra Mute
        if tag.startswith("B5"):
            for t in range(4, 10):                                # POKE (test only): Haste/Shell/Safe/Reflect + Float
                if h.r16(HP + 2 * t):
                    h.w8(ST34 + 2 * t, h.r8(ST34 + 2 * t) | 0xE8)
                    h.w8(ST34 + 2 * t + 1, h.r8(ST34 + 2 * t + 1) | 0x80)
        entry = next(s for s in range(256) if bslot(h, s)[0] == item & 0xFF and bslot(h, s)[1] & 1)
        lq0 = bslot(h, entry)[3]
        b0 = bstate(h)
        choose_item(h, entry, moves=moves, q=q, tag=tag)
        h.step(2)
        lq1 = bslot(h, entry)[3] if bslot(h, entry)[0] != 0xFF else 0
        sn, sa = run_action(h, q, tag, 700 + extra_frames)
        b1 = bstate(h)
        ok, det = check(b0, b1)
        finish_battle(h)
        det.update({"list_qty": (lq0, lq1), "name_flag_at": sn, "anim_flag_at": sa, "field_qty": (n0, qty(h, item))})
        res[tag] = det
        q.check(f"{tag} {BYID[item]['display_name']} in battle: {det.get('rule', '')}; list quantity -1 at the "
                f"command, extended name and animation drawn (flags consumed), one unit used after the battle",
                ok and lq1 == lq0 - 1 and sn is not None and sa is not None and qty(h, item) == n0 - 1, det)

    def poke_hp(rec, v):
        return lambda hh: (hh.w8(0x1600 + 37 * rec + 9, v & 0xFF), hh.w8(0x1600 + 37 * rec + 10, v >> 8))

    def gaia(b0, b1):
        gain = [b1["hp"][t] - b0["hp"][t] for t in range(4)]
        ok = all(b1["hp"][t] == b1["maxhp"][t] or gain[t] >= 90 for t in range(4)) and b1["hp"][0] > b0["hp"][0]
        return ok, {"rule": "every ally healed (power 240 halved over 4 targets: ~105-120 each, capped)", "gain": gain}
    case("B2", 0x127, poke_hp(0, 10), (), gaia)

    def aether(b0, b1):
        return (b1["mp"][0] == min(b1["maxmp"][0], b0["mp"][0] + 250) or b1["mp"][0] - b0["mp"][0] >= 200,
                {"rule": "Terra MP +~250 (capped)", "mp": (b0["mp"][0], b1["mp"][0], b1["maxmp"][0])})
    case("B3", 0x128, lambda hh: (hh.w8(0x1600 + 13, 1), hh.w8(0x1600 + 14, 0)), (), aether)

    def phoenix(b0, b1):
        return (b0["st12"][1] & 0x80 and not b1["st12"][1] & 0x80 and b1["hp"][1] > 0,
                {"rule": "fallen Locke revived with HP (8/16 of max)", "st": (f"{b0['st12'][1]:04X}", f"{b1['st12'][1]:04X}"),
                 "hp": (b0["hp"][1], b1["hp"][1], b1["maxhp"][1])})
    case("B4", 0x129, lambda hh: (hh.run_event([0x89, 0x01, 0x80, 0x00]), hh.w8(0x1600 + 37 + 9, 0), hh.w8(0x1600 + 37 + 10, 0)),
         ("DOWN",), phoenix)

    def null_dust(b0, b1):
        hit = [t for t in range(4, 10) if b0["hp"][t] and b0["st34"][t] & 0x80E8 == 0x80E8 and not b1["st34"][t] & 0x80E8]
        return (len(hit) == 1, {"rule": "the targeted enemy loses Haste/Shell/Safe/Reflect/Float (POKEd on all enemies)",
                                "cleared": hit, "st34": [f"{v:04X}" for v in b1["st34"][4:]]})
    case("B5", 0x12A, None, (), null_dust)

    def iron(b0, b1):
        return (b0["st12"][0] & 0x04 and not b1["st12"][0] & 0x04 and b1["hp"][0] - b0["hp"][0] >= 150 or
                b1["hp"][0] == b1["maxhp"][0] and not b1["st12"][0] & 0x04,
                {"rule": "Terra HP +~200 and Poison cured", "hp": (b0["hp"][0], b1["hp"][0]),
                 "st": (f"{b0['st12'][0]:04X}", f"{b1['st12'][0]:04X}")})
    case("B6", 0x12B, lambda hh: (hh.run_event([0x89, 0x00, 0x04, 0x00]), hh.w8(0x1600 + 9, 30), hh.w8(0x1600 + 10, 0)), (), iron)

    def remedy(b0, b1):
        return (b0["st12"][0] & 0x0821 == 0x0821 and not b1["st12"][0] & 0x0821,
                {"rule": "Terra Blind / Imp (field) and Mute (POKE) cured", "st": (f"{b0['st12'][0]:04X}", f"{b1['st12'][0]:04X}")})
    case("B7", 0x12C, lambda hh: hh.run_event([0x89, 0x00, 0x21, 0x00]), (), remedy)

    def beacon(b0, b1):
        alive = [t for t in range(4, 10) if b0["hp"][t]]
        dmg = [b0["hp"][t] - b1["hp"][t] for t in alive]
        return (alive and all(d > 0 for d in dmg), {"rule": "Fire damage to every enemy", "enemy_hp": [(b0["hp"][t], b1["hp"][t]) for t in alive]})
    case("B8", 0x12D, None, (), beacon)

    def cell(b0, b1):
        return (b1["mp"][0] > b0["mp"][0], {"rule": "party MP restored (power 120 halved: ~60 each)",
                                             "mp": [(b0["mp"][t], b1["mp"][t], b1["maxmp"][t]) for t in range(4)]})
    case("B9", 0x12E, lambda hh: (hh.w8(0x1600 + 13, 1), hh.w8(0x1600 + 14, 0)), (), cell)

    # ------------------------------------------------------------------ BH: held item returned
    h.em.set_state(st_all); h.step(10)
    n0 = qty(h, 0x127)
    start(h, L)
    entry = next(s for s in range(256) if bslot(h, s)[0] == 0x27 and bslot(h, s)[1] & 1)
    choose_item(h, entry)
    h.step(2)
    lq = bslot(h, entry)[3]
    h.w8(ST12, h.r8(ST12) | 0x40)                                 # POKE: Terra petrified before her action
    finish_battle(h)
    res["held"] = {"list_qty_after_choice": lq, "field_qty": (n0, qty(h, 0x127)),
                   "held_flags": h.rbytes(0x1E38, 4).hex()}
    q.check("BH Gaia Tonic chosen (list quantity -1), Terra petrified before acting: the held item comes back as Gaia "
            "Tonic at battle end (no unit lost, no vanilla katana created)",
            lq == 4 and qty(h, 0x127) == n0 and qty(h, 0x27) == 0, res["held"])

    # ------------------------------------------------------------------ BT: Throw the katana alias
    h.em.set_state(st_all); h.step(10)
    menu(h, L, [0, 2, 2, 1, 1])                                   # preset P2 Terra Sabin Cyan Shadow
    h.run_event([0x80, 0x27])                                     # vanilla Blossom
    n27, n127 = qty(h, 0x27), qty(h, 0x127)
    h.call_event(L["QaConsBtl9"], frames=1)
    for _ in range(900):
        h.step(1)
    shadow = None
    for _ in range(80):
        if h.r8(0x62CA) == 3:
            shadow = True; break
        h.press("Y", 4, 30); h.step(30)
    thrown = False
    tlist = []
    if shadow:
        h.step(30)
        for _ in range(8):
            if h.r8(CMD_CURSOR) == 1:
                break
            h.press("DOWN", 8, 24)
        h.press("A", 8, 60)                                       # Throw: filtered list wToolsThrowItemList (7E:4005)
        tlist = [(h.r8(0x4005 + 3 * k), h.r8(0x4006 + 3 * k)) for k in range(256) if h.r8(0x4005 + 3 * k) != 0xFF]
        q.shot(h, "BT_throw_list")
        h.press("A", 8, 40); h.press("A", 8, 60); h.press("A", 8, 10)
        sn, sa = run_action(h, q, "BT", 500)
        thrown = True
    finish_battle(h)
    res["throw"] = {"shadow_menu": shadow, "katana": (n27, qty(h, 0x27)), "gaia": (n127, qty(h, 0x127)),
                    "throw_list": [(f"{i:02X}", n) for i, n in tlist]}
    q.check("BT Shadow throws the vanilla katana Blossom ($27): the katana is used up, Gaia Tonic ($127, same low "
            "byte) is untouched; the Throw list holds only the katana (x1) - no consumable is throwable",
            thrown and qty(h, 0x27) == n27 - 1 and qty(h, 0x127) == n127 and tlist == [(0x27, 1)], res["throw"])

    # ------------------------------------------------------------------ BR: reconciliation, bitmaps
    stale = [s for s in range(256) if h.bit(s) and h.r8(0x1869 + s) == 0xFF]
    q.check("BR no stale high bit on an empty slot after all battle cases", not stale, stale)
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "CONSUMABLE_BATTLE_REPORT.json"), "w"), indent=1, default=str)
    print("CONSUMABLE BATTLE", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
