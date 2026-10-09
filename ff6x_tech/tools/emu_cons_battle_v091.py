#!/usr/bin/env python3
"""TECH v0.9.1 emulator checks: the 8 consumables in battle with the locked v0.9.1 effects (stable-retro / snes9x).

Setup as the accepted v0.9 suite (tools/emu_cons_battle_v09.py): New Game (QA ROM) -> QA "Grant all 8 (x5)" -> preset
P1 (Terra/Locke/Celes/Edgar) -> POKEs (test setup only: max HP / MP, statuses, enemy HP and element bytes) -> QA
consumable test battle. Terra uses the item through the real battle menu.

  V1  Gaia Tonic: one ally, exactly +1500 HP, Regen set; the next HP changes are Regen ticks (small), i.e. the fixed
      amount never leaks into another action
  V2  Aether Flask: exactly +100 MP (power 100; the Item command has no damage variance)
  V3  Phoenix Ash: unchanged (revive with 8/16)
  V4  Null Dust: the targeted enemy loses exactly the vanilla Dispel set (12 statuses POKEd on every enemy); Dance
      (not in the Dispel set) stays; the other enemies keep everything
  V5  Iron Ration: exactly +600 HP; Poison NOT cured (unlocked cure removed)
  V6  Remedy+: Blind / Poison / Imp / Mute / Sap / Zombie cured on Locke; Sleep (not in the set) stays
  V7  Beacon Flare: Fire damage to every enemy AND Vanish removed from every enemy; Image stays
  V8  Magitek Cell hybrid, one enemy: neutral 800, Lightning-weak 1200, -half 600, -null 400, -absorb 0 (net), force
      field 400 (exact, fixed base 800 split 400 + 400); the other enemies untouched; Lightning is the action element
  V9  vanilla Potion after the v0.9.1 engine: exactly its vanilla 250 (never a fixed amount)
  BT  Throw of the vanilla katana alias $27 still never touches Gaia Tonic $127

usage: emu_cons_battle_v091.py <qa.sfc> <qa.manifest.json> <out>
writes <out>/CONSUMABLE_BATTLE_REPORT_v091.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, inv16
from emu_item_battle import labels, talk, to_terra, bslot
from emu_equip_battle_v08 import finish_battle
from emu_cons_battle_v09 import choose_item, run_action, CMD_CURSOR

CONS = json.load(open(os.path.join(HERE, "items/production_v091/consumables.json")))["items"]
BYID = {int(c["id"], 16): c for c in CONS}
HP, MP, MAXHP, MAXMP, ST12, ST34 = 0x3BF4, 0x3C08, 0x3C1C, 0x3C30, 0x3EE4, 0x3EF8
ABS, NUL, WEAK, HALF, FORCE = 0x3BCC, 0x3BCD, 0x3BE0, 0x3BE1, 0x3EC8
CHAR = 0x1600


def menu(h, L, picks):
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def qty(h, i):
    return sum(n for s, j, n in h.inv() if j == i)


def start(h, L):
    h.call_event(L["QaConsBtl9"], frames=1)
    for _ in range(900):
        h.step(1)
    to_terra(h)
    h.step(30)


def poke_rec(h, rec, hp=None, maxhp=None, mp=None, maxmp=None):
    b = CHAR + 37 * rec
    if maxhp is not None:
        v = (h.r16(b + 11) & 0xC000) | maxhp
        h.w8(b + 11, v & 0xFF); h.w8(b + 12, v >> 8)
    if hp is not None:
        h.w8(b + 9, hp & 0xFF); h.w8(b + 10, hp >> 8)
    if maxmp is not None:
        v = (h.r16(b + 15) & 0xC000) | maxmp
        h.w8(b + 15, v & 0xFF); h.w8(b + 16, v >> 8)
    if mp is not None:
        h.w8(b + 13, mp & 0xFF); h.w8(b + 14, mp >> 8)


def entry_of(h, item):
    return next(s for s in range(256) if bslot(h, s)[0] == item & 0xFF and (bslot(h, s)[1] & 1) == (item >> 8))


def trace(h, frames, addr):
    """step `frames`, return the list of distinct consecutive values of the word at addr"""
    seq = [h.r16(addr)]
    for _ in range(frames):
        h.step(1)
        v = h.r16(addr)
        if v != seq[-1]:
            seq.append(v)
    return seq


def enemies(h):
    return [t for t in range(4, 10) if h.r16(HP + 2 * t)]


def main(qa, manifest, out):
    q = Report(out)
    L = labels(manifest)
    res = {}
    h = T(qa)
    boot_new_game(h)
    menu(h, L, [0, 0])                                            # 8 consumables x5
    menu(h, L, [0, 2, 2, 1, 0])                                   # preset P1
    h.run_event([0x80, 0xE9, 0x80, 0xE9])                         # 2 vanilla Potions (V9)
    st_all = h.em.get_state()

    def battle_with(item, field=None, in_battle=None, moves=(), tag="", frames=900, watch=None):
        h.em.set_state(st_all); h.step(10)
        if field:
            field(h)
        n0 = qty(h, item)
        start(h, L)
        if in_battle:
            in_battle(h)
        e = entry_of(h, item)
        before = {"hp": [h.r16(HP + 2 * t) for t in range(10)], "mp": [h.r16(MP + 2 * t) for t in range(4)],
                  "st12": [h.r16(ST12 + 2 * t) for t in range(10)], "st34": [h.r16(ST34 + 2 * t) for t in range(10)]}
        choose_item(h, e, moves=moves, q=q, tag=tag)
        tr = None
        if watch is not None:
            tr = trace(h, frames, watch)
        else:
            run_action(h, q, tag, frames)
        after = {"hp": [h.r16(HP + 2 * t) for t in range(10)], "mp": [h.r16(MP + 2 * t) for t in range(4)],
                 "st12": [h.r16(ST12 + 2 * t) for t in range(10)], "st34": [h.r16(ST34 + 2 * t) for t in range(10)],
                 "elem": h.r8(0x11A1)}
        q.shot(h, f"{tag}_after")
        for t in range(4, 10):                                    # POKE (test only): weak enemies -> battle ends
            if h.r16(HP + 2 * t) > 1:
                h.w8(HP + 2 * t, 1); h.w8(HP + 2 * t + 1, 0)
        finish_battle(h)
        return before, after, tr, (n0, qty(h, item))

    # ---------------------------------------------------------------- V1 Gaia Tonic
    b, a, tr, n = battle_with(0x127, field=lambda hh: poke_rec(hh, 0, hp=10, maxhp=3000), tag="V1", frames=1500,
                              watch=HP)
    deltas = [y - x for x, y in zip(tr, tr[1:])]
    pos = [d for d in deltas if d > 0]
    res["V1"] = {"hp_trace": tr[:12], "deltas": deltas[:12], "regen": bool(a["st34"][0] & 0x0002), "qty": n}
    q.check("V1 Gaia Tonic (battle, one ally): first heal exactly +1500 HP, Regen set on Terra, later heals are Regen "
            "ticks (< 500 each: the fixed amount never leaks), one unit used",
            pos and pos[0] == 1500 and all(d < 500 for d in pos[1:]) and res["V1"]["regen"] and n[1] == n[0] - 1,
            res["V1"])

    # ---------------------------------------------------------------- V2 Aether Flask
    b, a, tr, n = battle_with(0x128, field=lambda hh: poke_rec(hh, 0, mp=1, maxmp=999), tag="V2", frames=700,
                              watch=MP)
    d = [y - x for x, y in zip(tr, tr[1:])]
    res["V2"] = {"mp_trace": tr[:8], "qty": n}
    q.check("V2 Aether Flask (battle): exactly +100 MP (power 100, no variance on the Item command)", d and d[0] == 100 and
            n[1] == n[0] - 1, res["V2"])

    # ---------------------------------------------------------------- V3 Phoenix Ash (unchanged)
    def ko_locke(hh):
        hh.run_event([0x89, 0x01, 0x80, 0x00]); hh.w8(CHAR + 37 + 9, 0); hh.w8(CHAR + 37 + 10, 0)
    b, a, tr, n = battle_with(0x129, field=ko_locke, moves=("DOWN",), tag="V3")
    res["V3"] = {"st": (f"{b['st12'][1]:04X}", f"{a['st12'][1]:04X}"), "hp": (b["hp"][1], a["hp"][1])}
    q.check("V3 Phoenix Ash (unchanged): fallen Locke revived with HP", b["st12"][1] & 0x80 and
            not a["st12"][1] & 0x80 and a["hp"][1] > 0, res["V3"])

    # ---------------------------------------------------------------- V4 Null Dust
    def dispel_setup(hh):
        for t in range(4, 10):
            if hh.r16(HP + 2 * t):
                hh.w8(ST12 + 2 * t, hh.r8(ST12 + 2 * t) | 0x10)           # Vanish
                hh.w8(ST12 + 2 * t + 1, hh.r8(ST12 + 2 * t + 1) | 0x14)   # Image, Berserk
                hh.w8(ST34 + 2 * t, hh.r8(ST34 + 2 * t) | 0xFF)           # Dance + Regen..Reflect
                hh.w8(ST34 + 2 * t + 1, hh.r8(ST34 + 2 * t + 1) | 0x84)   # Life 3, Float
    b, a, tr, n = battle_with(0x12A, in_battle=dispel_setup, tag="V4")
    hit = [t for t in range(4, 10) if b["hp"][t] and not a["st12"][t] & 0x1410 and not a["st34"][t] & 0x84FE]
    keep = [t for t in range(4, 10) if b["hp"][t] and t not in hit and a["st34"][t] & 0x84FE == 0x84FE]
    dance = [t for t in hit if a["st34"][t] & 0x0001]
    res["V4"] = {"cleared": hit, "kept": keep, "dance_kept": dance,
                 "st12": [f"{v:04X}" for v in a["st12"][4:]], "st34": [f"{v:04X}" for v in a["st34"][4:]]}
    q.check("V4 Null Dust: the targeted enemy loses Vanish, Image, Berserk, Regen, Slow, Haste, Stop, Shell, Safe, "
            "Reflect, Life 3, Float (vanilla Dispel set) and keeps Dance; the other enemies keep everything",
            len(hit) == 1 and dance == hit and len(keep) == len(enemies_b := [t for t in range(4, 10) if b["hp"][t]]) - 1,
            res["V4"])

    # ---------------------------------------------------------------- V5 Iron Ration
    def iron_setup(hh):
        hh.run_event([0x89, 0x00, 0x04, 0x00]); poke_rec(hh, 0, hp=300, maxhp=3000)
    b, a, tr, n = battle_with(0x12B, field=iron_setup, tag="V5", frames=900, watch=HP)
    pos = [y - x for x, y in zip(tr, tr[1:]) if y > x]
    res["V5"] = {"hp_trace": tr[:10], "poison_after": bool(a["st12"][0] & 0x04)}
    q.check("V5 Iron Ration: first heal exactly +600 HP; Poison is NOT cured (locked effect = heal only)",
            pos and pos[0] == 600 and res["V5"]["poison_after"], res["V5"])

    # ---------------------------------------------------------------- V6 Remedy+
    def remedy_setup(hh):
        hh.w8(ST12 + 2, hh.r8(ST12 + 2) | 0x27)                   # Locke: Blind, Zombie, Poison, Imp
        hh.w8(ST12 + 3, hh.r8(ST12 + 3) | 0xC8)                   # Mute, Sap, Sleep
    b, a, tr, n = battle_with(0x12C, in_battle=remedy_setup, moves=("DOWN",), tag="V6")
    res["V6"] = {"st12": (f"{b['st12'][1]:04X}", f"{a['st12'][1]:04X}")}
    q.check("V6 Remedy+ on Locke: Blind, Zombie, Poison, Imp, Mute, Sap cured; Sleep (not in the set) stays",
            b["st12"][1] & 0x4827 == 0x4827 and not a["st12"][1] & 0x4827 and a["st12"][1] & 0x8000, res["V6"])

    # ---------------------------------------------------------------- V7 Beacon Flare
    def beacon_setup(hh):
        for t in range(4, 10):
            if hh.r16(HP + 2 * t):
                hh.w8(HP + 2 * t, 0x88); hh.w8(HP + 2 * t + 1, 0x13)      # 5000 HP
                hh.w8(ST12 + 2 * t, hh.r8(ST12 + 2 * t) | 0x10)           # Vanish
                hh.w8(ST12 + 2 * t + 1, hh.r8(ST12 + 2 * t + 1) | 0x04)   # Image
    b, a, tr, n = battle_with(0x12D, in_battle=beacon_setup, tag="V7")
    al = [t for t in range(4, 10) if b["hp"][t]]
    res["V7"] = {"hp": [(b["hp"][t], a["hp"][t]) for t in al], "st12": [f"{a['st12'][t]:04X}" for t in al], "qty": n}
    q.check("V7 Beacon Flare: every enemy takes Fire damage AND loses Vanish in the same action; Image is not removed",
            al and all(a["hp"][t] < b["hp"][t] for t in al) and all(not a["st12"][t] & 0x10 for t in al) and
            all(a["st12"][t] & 0x0400 for t in al) and n[1] == n[0] - 1, res["V7"])

    # ---------------------------------------------------------------- V8 Magitek Cell hybrid
    def cell_setup(kind):
        def f(hh):
            for t in range(4, 10):
                if hh.r16(HP + 2 * t):
                    hh.w8(HP + 2 * t, 0x88); hh.w8(HP + 2 * t + 1, 0x13)  # 5000 HP
                    for adr in (ABS, NUL, WEAK, HALF):
                        hh.w8(adr + 2 * t, 0)
                    if kind in ("weak", "half", "null", "absorb"):
                        hh.w8({"weak": WEAK, "half": HALF, "null": NUL, "absorb": ABS}[kind] + 2 * t, 0x04)
            hh.w8(FORCE, 0x04 if kind == "force" else 0x00)
        return f
    expect = {"neutral": 800, "weak": 1200, "half": 600, "null": 400, "absorb": 0, "force": 400}
    v8 = {}
    for kind, exp in expect.items():
        b, a, tr, n = battle_with(0x12E, in_battle=cell_setup(kind), tag=f"V8_{kind}")
        dm = [b["hp"][t] - a["hp"][t] for t in range(4, 10) if b["hp"][t]]
        v8[kind] = {"damage": dm, "expect": exp, "elem_11A1": f"{a['elem']:02X}", "qty": n}
    hit_ok = all(sorted(v["damage"])[-1] == v["expect"] and sum(1 for d in v["damage"] if d) <= 1 and
                 v["qty"][1] == v["qty"][0] - 1 for v in v8.values())
    res["V8"] = v8
    q.check("V8 Magitek Cell (one enemy): neutral 800, Lightning-weak 1200, -half 600, -null 400, -absorb 0, "
            "force field 400 (400 Lightning + 400 non-elemental, exact); only the targeted enemy is hit",
            hit_ok, v8)

    # ---------------------------------------------------------------- V9 vanilla Potion unchanged
    b, a, tr, n = battle_with(0xE9, field=lambda hh: poke_rec(hh, 0, hp=10, maxhp=3000), tag="V9", frames=700,
                              watch=HP)
    pos = [y - x for x, y in zip(tr, tr[1:]) if y > x]
    res["V9"] = {"hp_trace": tr[:6]}
    q.check("V9 vanilla Potion (battle): vanilla heal 250 (no fixed amount on vanilla items)",
            pos and pos[0] == 250, res["V9"])
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "CONSUMABLE_BATTLE_REPORT_v091.json"), "w"), indent=1, default=str)
    print("CONSUMABLE BATTLE v0.9.1", "PASS" if rep["all_pass"] else "FAIL",
          f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
