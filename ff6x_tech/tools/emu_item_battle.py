#!/usr/bin/env python3
"""TECH v0.7.1 emulator checks, part 2: the QA harness item menu and battle (stable-retro / snes9x).

Drives the QA access event of the item-tech ROM through its real dialogue choices (give / HAS / TAKE),
equips the three QA items through the real menus, fights the harness test battle (Terra without Magitek)
and checks battle RAM, the battle Item menu, the weapon animation number, battle-end reconciliation and
event command $8D (remove all equipment). Writes <out>/ITEM_BATTLE_EMULATOR_REPORT.json + screenshots.

usage: emu_item_battle.py <qa.sfc> <qa.manifest.json> <out> [<clean_rev1.sfc>]   (clean ROM: B3c differential)
"""
import itertools, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, equip_slot, bits_consistent
from emu_menu_nav import Nav

ITEMLIST, RHAND, LHANDLIST, RHANDLIST = 0x2686, 0x3CA8, 0x2B9A, 0x2B86
RHAND_POWER, ANIM_NO, CMD_CURSOR = 0x3B68, 0x626A, 0x2C
QA_BIT = 0x14E


def labels(manifest):
    """QA event label addresses from the build manifest's event listing (never hard-coded)."""
    m = json.load(open(manifest))
    out = {}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "qa_access_v071" and isinstance(v, str):
                    for a, lab in re.findall(r"^([0-9A-F]{2}:[0-9A-F]{4})\s+@(\w+)", v, re.M):
                        out[lab] = int(a.replace(":", ""), 16)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(m)
    return out


def talk(h, picks, frames=3000):
    """advance the running field dialogue; at each multiple-choice prompt pick the next index in `picks`"""
    picks, last, stable, t = list(picks), -1, 0, 0
    while t < frames:
        h.step(1); t += 1
        n = h.r8(0x56F)                 # number of choices of the current prompt (field text.asm)
        if n and picks:
            stable = stable + 1 if n == last else 0
            last = n
            if stable >= 30:
                k = picks.pop(0)
                for _ in range(10):
                    if h.r8(0x56E) == k:  # current choice
                        break
                    h.press("DOWN" if h.r8(0x56E) < k else "UP", 4, 8)
                h.press("A", 4, 8); t += 12; stable, last = 0, -1
        elif h.idle():
            return True
        elif t % 40 == 0 and not n:
            h.press("A", 4, 4); t += 8
    return h.idle()


def to_terra(h):
    """Make Terra's command menu the active one: $62CA = active battle menu character (valid once a menu has
    opened, i.e. after the 900-frame wait); Y cycles between ready characters (ATB keeps running meanwhile)."""
    for _ in range(80):
        if h.r8(0x62CA) == 0:
            h.step(20)
            return True
        h.press("Y", 4, 30)
        h.step(30)
    raise RuntimeError("Terra's battle menu never became active")


def b3c_run(romfile, state, knife):
    """POKE: vanilla Epee ($10) in Terra's R-hand (bit clear); harness-equivalent battle (status clear Magitek +
    group $01); hand-first exchange R <-> inventory Mithril Knife; back out with B; fight to the end.
    Returns (equipment low bytes, inventory (slot, low byte, qty), battle list after the exchange)."""
    h = T(romfile)
    h.em.set_state(state); h.step(30)
    h.w8(0x161F, 0x10); h.w8(0x1CF8 + 32, h.r8(0x1CF8 + 32) & 0xFE)
    h.run_event([0x88, 0x00, 0xF7, 0xFF, 0x4D, 0x01, 0x3F], frames=1)
    for _ in range(900):
        h.step(1)
    to_terra(h)
    h.step(30)
    for _ in range(6):
        if h.r8(CMD_CURSOR) == 3:
            break
        h.press("DOWN", 8, 24)
    h.press("A", 8, 60); h.press("UP", 8, 40); h.press("A", 8, 40)
    for _ in range(knife + 1):
        h.press("DOWN", 8, 20)
    h.press("A", 8, 60)
    lst = [bslot(h, s)[0] for s in range(16)]
    hands = (h.r8(RHANDLIST), h.r8(LHANDLIST))
    for _ in range(3):
        h.press("B", 8, 30)
    for t in range(6000):
        if t % 16 == 0:
            h.step(4, ("A",))
        else:
            h.step(1)
        if t > 600 and h.idle():
            break
    h.step(60)
    eq = [h.r8(0x161F + k) for k in range(6)]
    inv = [(s, h.r8(0x1869 + s), h.r8(0x1969 + s)) for s in range(256) if h.r8(0x1869 + s) != 0xFF]
    ext = h.ext_inv() if romfile.endswith("QA.sfc") else []
    h.close()
    return eq, inv, lst, hands, ext


def bslot(h, s):
    return [h.r8(ITEMLIST + 5 * s + k) for k in range(5)]


def main(rom, manifest, out, clean=None):
    q = Report(out)
    L = labels(manifest)
    h = T(rom)
    boot_new_game(h)

    # ---------------------------------------------------------------- harness: give x2, HAS, TAKE
    h.call_event(L["QaAccess6"], frames=1)
    q.shot(h, "QA_menu_top")
    talk(h, [0, 0])
    inv = {i: n for s, i, n in h.inv()}
    q.check("Q1 QA menu 'Get QA items' gives $13D/$13E/$13F + vanilla $3D/$3E/$3F",
            all(inv.get(i) == 1 for i in (0x13D, 0x13E, 0x13F, 0x03D, 0x03E, 0x03F)),
            {f"{i:03X}": n for i, n in inv.items()})
    h.call_event(L["QaAccess6"], frames=1)
    talk(h, [0, 0])
    inv = {i: n for s, i, n in h.inv()}
    q.check("Q2 second grant stacks (each x2, extended and vanilla kept apart)",
            all(inv.get(i) == 2 for i in (0x13D, 0x13E, 0x13F, 0x03D, 0x03E, 0x03F)),
            {f"{i:03X}": n for i, n in inv.items()})
    h.call_event(L["QaAccess6"], frames=1)
    talk(h, [0, 1, 0])
    inv = {i: n for s, i, n in h.inv()}
    q.check("K3 QA menu HAS_EXT_ITEM sets the QA bit, TAKE_EXT_ITEM removes one $13D (vanilla $3D untouched)",
            h.r8(0x1E80 + (QA_BIT >> 3)) >> (QA_BIT & 7) & 1 == 1 and inv.get(0x13D) == 1 and inv.get(0x03D) == 2,
            {f"{i:03X}": n for i, n in inv.items()})

    # ---------------------------------------------------------------- equip through the menus
    nv = Nav(h)
    h.step(120)
    nv.open_main(); nv.main_to("Equip"); nv.press("A", "EQUIP_OPT"); nv.press("A", "EQUIP_SLOT")
    equip_slot(nv, h, 0, 0); equip_slot(nv, h, 3, 0)
    field_power = h.r8(0x11AC) + h.r8(0x11AD)        # equip menu: battle power after UpdateEquip
    nv.back_to_main(); nv.main_to("Relic"); nv.press("A", "RELIC_OPT"); nv.press("A", "RELIC_SLOT")
    nv.cursor_to(0); nv.press("A", "RELIC_LIST"); nv.cursor_to(0); h.press("A", 4, 30); h.step(60)
    nv.back_to_main(); nv.close(); h.step(60)
    eq0 = h.eq(0)
    inv0 = h.inv()
    q.check("Q3 equipped R-hand $13D, body $13E, relic $13F", eq0[0] == 0x13D and eq0[3] == 0x13E and eq0[4] == 0x13F,
            [f"{x:03X}" for x in eq0])
    ext_pos = [s for s, i, n in inv0 if i >= 0x100]
    st_equipped = h.em.get_state()

    # ---------------------------------------------------------------- battle (harness: Terra without Magitek)
    h.call_event(L["QaBtl7"], frames=1)
    for _ in range(900):
        h.step(1)
    q.shot(h, "F_battle_start")
    empty = bslot(h, 200)
    q.check("B1 extended inventory slots are presented to the battle exactly like empty slots",
            all(bslot(h, s) == empty for s in ext_pos) and empty[0] == 0xFF and empty[3] == 0,
            {"ext_slots": ext_pos, "slot": [f"{x:02X}" for x in bslot(h, ext_pos[0])],
             "empty": [f"{x:02X}" for x in empty]})
    rl = [h.r8(RHANDLIST + k) for k in range(5)]
    q.check("B2 Terra's R-hand in battle = $3D low byte, attack power = field battle power (extended props)",
            h.r8(RHAND) == 0x3D and h.r8(RHAND_POWER) == field_power and rl[0] == 0x3D and rl[1] & 0x20 == 0,
            {"RHandItem": f"{h.r8(RHAND):02X}", "power": h.r8(RHAND_POWER), "field_power": field_power,
             "hand_list": [f"{x:02X}" for x in rl]})
    to_terra(h)
    q.shot(h, "F_battle_terra_menu")
    st_battle = h.em.get_state()

    # battle Item menu: hand names, swap guard (hand-first exchange) and R <-> L exchange
    def item_menu():
        h.step(30)
        for _ in range(6):
            if h.r8(CMD_CURSOR) == 3:
                break
            h.press("DOWN", 8, 24)
        h.press("A", 8, 60)

    def hand_first(hand, slot):
        """UP to the hand row, (RIGHT for L), A, then down to inventory row `slot`, A"""
        h.press("UP", 8, 40)
        if hand:
            h.press("RIGHT", 8, 40)
        h.press("A", 8, 40)
        for _ in range(slot + 1):
            h.press("DOWN", 8, 20)
        h.press("A", 8, 60)

    def hands():
        return h.r8(RHANDLIST), h.r8(LHANDLIST)
    knife = [s for s in range(8) if bslot(h, s)[0] == 0x01][0]
    item_menu()
    h.press("UP", 8, 40)
    q.shot(h, "F_battle_item_menu_hands")
    h.press("DOWN", 8, 40)
    b0 = (hands(), [bslot(h, s) for s in range(8)], h.rbytes(0x1CF8, 44))
    hand_first(0, knife)
    b1 = (hands(), [bslot(h, s) for s in range(8)], h.rbytes(0x1CF8, 44))
    q.check("B3 hand-first exchange of the extended R-hand with an inventory weapon (Mithril Knife) is refused",
            b0 == b1 and b1[0] == (0x3D, 0x5A), {"hands": [f"{x:02X}" for x in b1[0]]})
    h.em.set_state(st_battle)
    item_menu()
    h.press("UP", 8, 40); h.press("A", 8, 40); h.press("RIGHT", 8, 40); h.press("A", 8, 60)
    q.shot(h, "F_battle_hands_exchanged")
    hx = hands()
    bx = [h.bit(256 + k) for k in range(2)]
    for _ in range(3):
        h.press("B", 8, 30)
    for t in range(6000):
        if t % 16 == 0:
            h.step(4, ("A",))
        else:
            h.step(1)
        if t > 600 and h.idle():
            break
    h.step(60)
    q.check("B3b R-hand <-> L-hand exchange in battle: equipment bits follow the items (after battle: R = Buckler "
            "$05A, L = QA Blade $13D; no truncation, no invalid id)",
            hx == (0x5A, 0x3D) and bx == [0, 1] and h.eq(0)[:2] == [0x05A, 0x13D] and not bits_consistent(h),
            {"hands_in_battle": [f"{x:02X}" for x in hx], "bits": bx, "eq_after": [f"{x:03X}" for x in h.eq(0)]})
    # Terra's Fight: weapon animation number and damage
    h.em.set_state(st_battle)
    h.step(30)
    hp0 = [h.r16(0x3BF4 + x) for x in range(8, 20, 2)]
    h.press("A", 8, 30); h.press("A", 8, 10)
    seq = []
    for t in range(400):
        h.step(1)
        seq.append(h.r8(ANIM_NO))
        if t in (70, 90, 110, 140):
            q.shot(h, f"F_terra_attack_{t}")
    hp1 = [h.r16(0x3BF4 + x) for x in range(8, 20, 2)]
    runs = [(f"{k:02X}", len(list(g))) for k, g in itertools.groupby(seq)]
    q.check("F1 weapon animation number for the extended weapon = $C0+$3D = $FD (XWeaponAnimFull)",
            0xFD in seq, runs)
    rom_b = open(rom, "rb").read()
    q.check("F2 XWeaponAnimFull[$FD] = vanilla WeaponAnimProp entry of the base weapon (Epee $10 -> index $11)",
            rom_b[0x3A0000 + 0x3800 + 8 * 0xFD:0x3A0000 + 0x3800 + 8 * 0xFE] == rom_b[0x2CE400 + 8 * 0x11:0x2CE400 + 8 * 0x12])
    q.check("F3 Terra's hit took a guard's HP (damage from the extended weapon)", sum(hp1) < sum(hp0),
            {"hp_before": hp0, "hp_after": hp1})

    # synthetic steal: vanilla items placed where the battle sees empty slots (= extended field slots)
    for s, (i, n) in zip(ext_pos, ((0xE9, 3), (0x01, 1))):
        for k, v in enumerate((i, 0x80, 0x41, n, 0xFF)):
            h.w8(ITEMLIST + 5 * s + k, v)
    for t in range(6000):
        if t % 16 == 0:
            h.step(4, ("A",))
        else:
            h.step(1)
        if t > 600 and h.idle():
            break
    h.step(120)
    q.shot(h, "F_after_battle")
    inv1 = h.inv()
    d0 = {s: (i, n) for s, i, n in inv0}
    d1 = {s: (i, n) for s, i, n in inv1}
    exp_knife = dict((i, n) for s, i, n in inv0).get(0x01, 0) + 1
    q.check("B4 battle end: extended slots preserved at their positions",
            all(d1.get(s) == d0[s] for s in ext_pos), {"before": str(d0), "after": str(d1)})
    q.check("B5 battle end: vanilla items the battle put at extended positions are re-homed (new slot / merged)",
            dict((i, n) for s, i, n in inv1).get(0xE9) == 3 and dict((i, n) for s, i, n in inv1).get(0x01) == exp_knife,
            str(d1))
    q.check("B6 battle end: equipment unchanged, Magitek restored by the harness, bit field consistent",
            h.eq(0) == eq0 and h.r8(0x1614) & 0x08 and not bits_consistent(h), [f"{x:03X}" for x in h.eq(0)])
    st_battle_end = h.em.get_state()

    # ---------------------------------------------------------------- Jump animation (XJumpAnim)
    import numpy as np

    STATS = [0x3B68, 0x3B69, 0x3B7C, 0x3B7D, 0x3B2C, 0x3B2D]   # attack power, hit rate, strength (R/L, Terra)

    def jump_run(epee, stats=None):
        h.em.set_state(st_equipped); h.step(30)
        h.w8(0x1616, 0x16)                                   # POKE (test only): Terra command 1 := Jump
        if epee:                                             # POKE: vanilla Epee ($10) in the R-hand, bit clear
            h.w8(0x161F, 0x10); h.w8(0x1CF8 + 32, h.r8(0x1CF8 + 32) & 0xFE)
        h.call_event(L["QaBtl7"], frames=1)
        for _ in range(900):
            h.step(1)
        to_terra(h)
        got = [h.r8(a) for a in STATS]
        if stats:                                            # POKE: same power/hit/strength -> same damage roll
            for a, v in zip(STATS, stats):
                h.w8(a, v)
        h.press("A", 8, 30); h.press("A", 8, 10)
        frames = []
        for t in range(1600):
            h.step(1)
            if t % 4 == 0:
                frames.append(np.asarray(h.em.get_screen()).copy())
        return frames, got
    fa, sa = jump_run(False)
    fb, _ = jump_run(True, sa)
    diff = [i for i, (x, y) in enumerate(zip(fa, fb)) if (x != y).any()]
    moving = sum(1 for i in range(1, len(fa)) if (fa[i] != fa[i - 1]).any())
    from PIL import Image
    for k in (175, 180, 190):
        q.n += 1
        Image.fromarray(np.concatenate([fa[k], fb[k]], axis=1)).resize((1024, 448), Image.NEAREST).save(
            os.path.join(out, f"{q.n:03d}_F_jump_ext_vs_epee_{k}.png"))
    q.check("F4 Jump with the extended weapon (POKE: command Jump) renders every frame (jump, landing pose, damage) "
            "exactly like vanilla Epee, its base weapon, with equal power/hit/strength; the alias Chocobo Brsh has a "
            "different Jump graphic (ItemJumpThrowAnim $01 vs $10)", not diff and moving > 50,
            {"differing_samples": diff[:10], "animated_samples": moving, "stats_ext": sa})
    h.em.set_state(st_battle_end)

    # ---------------------------------------------------------------- event $8D: remove all equipment
    pre = {i: n for s, i, n in h.inv()}
    h.run_event([0x8D, 0x00])
    post = {i: n for s, i, n in h.inv()}
    q.check("E8D event $8D (remove Terra's equipment): extended items return to the inventory as $1xx",
            all(x == 0xFF for x in h.eq(0)) and all(post.get(i, 0) == pre.get(i, 0) + 1 for i in (0x13D, 0x13E, 0x13F))
            and post.get(0x03D) == pre.get(0x03D) and post.get(0x03E) == pre.get(0x03E) and not bits_consistent(h),
            {"eq": [f"{x:03X}" for x in h.eq(0)], "pre": {f"{i:03X}": n for i, n in pre.items()},
             "post": {f"{i:03X}": n for i, n in post.items()}})

    # ---------------------------------------------------------------- B3c differential vs clean Rev 1
    if clean:
        h.close()
        qa = b3c_run(rom, st_equipped, knife)
        van = b3c_run(clean, st_equipped, knife)
        q.check("B3c vanilla hand-first exchange (POKE: R-hand Epee $10) behaves exactly as in the clean Rev 1 ROM "
                "(same equipment and inventory low bytes/quantities after the battle; v0.7.1 additionally keeps "
                "the extended items at their slots)",
                qa[0] == van[0] and qa[1] == van[1] and qa[3] == van[3] and qa[3][0] == 0x01
                and sorted(i for s_, i, n in qa[4]) == [0x13E, 0x13F],
                {"qa_eq": [f"{x:02X}" for x in qa[0]], "rev1_eq": [f"{x:02X}" for x in van[0]],
                 "qa_hands": [f"{x:02X}" for x in qa[3]], "rev1_hands": [f"{x:02X}" for x in van[3]],
                 "qa_inv": [(s_, f"{i:02X}", n) for s_, i, n in qa[1]], "rev1_inv": [(s_, f"{i:02X}", n) for s_, i, n in van[1]],
                 "qa_ext": [(s_, f"{i:03X}", n) for s_, i, n in qa[4]],
                 "note": "Rev 1 itself writes the exchanged hand to $161F when the exchange is made and restores "
                         "the battle list when the menu is left with B (same result in both ROMs)"})

    rep = {"rom": os.path.basename(rom), "checks": q.checks, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "ITEM_BATTLE_EMULATOR_REPORT.json"), "w"), indent=1)
    print("ITEM BATTLE EMULATOR", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
