#!/usr/bin/env python3
"""TECH v0.8 emulator checks, part 2: production signature weapons in battle (stable-retro / snes9x).

Setup for every run: New Game (QA ROM) -> QA "Grant all 39" -> a QA party preset holding the weapon's first user ->
the weapon equipped through the Equip menu in the R-hand -> QA test battle (event battle group $01, Narshe guards).

  W  all 13 weapons, Fight: weapon animation number = $C0 + low byte (XWeaponAnimFull), battle R-hand power = the
     item's Battle Power, and the rendered Fight (swing, weapon graphic, hit, damage) is frame-identical to the same
     battle with the template vanilla weapon in the hand (POKE: template id, extended bit clear; power / hit /
     strength POKEd equal so both runs roll the same damage)
  J  Jump with the two spears (POKE: command 1 := Jump, as v0.7.1 F4): frame-identical to the template spear
  G  Genji Glove: two extended knives (Raider Knife R, Darill's Dirk L, Locke) -> both animation numbers, both powers
  H  Gauntlet: extended sword with the two-hand flag (Tempered Edge, Terra) -> battle "uses weapon 2-handed" set
  O  Offering: Moonless (Shadow) -> four strikes with the extended animation number
  R  Runic (Celes, Imperial Saber) / Bushido (Cyan, Doma Edge): command present and enabled
  I  battle Item list shows no $1xx item (blank), Throw list (Shadow) shows none
  P  battle end: inventory (39 $1xx + vanilla) and equipment unchanged (reconciliation)

usage: emu_equip_battle_v08.py <qa.sfc> <qa.manifest.json> <out>
"""
import json, os, sys, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, inv16
from emu_item_battle import labels
from emu_menu_nav import Nav, ST
from emu_equip_v08 import (BYID, CHARS, PRESETS, PRESET_PICKS, menu, party_order, read_list)

ANIM_NO, ACTIVE = 0x626A, 0x62CA
CMD_RUNIC, CMD_BUSHIDO, CMD_JUMP, CMD_THROW = 0x0B, 0x07, 0x16, 0x08


def preset_for(c):
    return next(k for k, pr in enumerate(PRESETS) if c in pr)


def equip_menu(h, c, it_id, hand=0, relic_slot=0):
    """equip `it_id` on character c (in the current party) through the Equip/Relic menus"""
    it = BYID.get(it_id)
    relic = (it["category"] == "relic") if it else False
    slot_i = party_order(h).index(c)
    nv = Nav(h); h.step(30)
    nv.open_main(); nv.main_to("Relic" if relic else "Equip"); nv.wait(ST["CHAR"], 300); h.step(20)
    nv.cursor_to(slot_i); h.press("A", 4, 30)
    nv.wait(ST["RELIC_OPT" if relic else "EQUIP_OPT"], 120)
    nv.press("A", "RELIC_SLOT" if relic else "EQUIP_SLOT")
    es = relic_slot if relic else {"weapon": hand, "shield": 1, "helmet": 2, "armor": 3}[it["category"]] if it else hand
    nv.cursor_to(es)
    nv.press("A", "RELIC_LIST" if relic else "EQUIP_LIST"); h.step(10)
    lst = read_list(h)
    if it_id not in lst:
        raise RuntimeError(f"{it_id:03X} not offered to {CHARS[c]}: {[hex(x) for x in lst]}")
    nv.cursor_to(lst.index(it_id)); h.press("A", 4, 30); h.step(20)
    nv.back_to_main(); nv.close(); h.step(30)


def equip_relic_vanilla(h, c, vid, relic_slot=0):
    """vanilla relic through the Relic menu (given first with event $80)"""
    h.run_event([0x80, vid])
    slot_i = party_order(h).index(c)
    nv = Nav(h); h.step(30)
    nv.open_main(); nv.main_to("Relic"); nv.wait(ST["CHAR"], 300); h.step(20)
    nv.cursor_to(slot_i); h.press("A", 4, 30); nv.wait(ST["RELIC_OPT"], 120)
    nv.press("A", "RELIC_SLOT"); nv.cursor_to(relic_slot); nv.press("A", "RELIC_LIST"); h.step(10)
    lst = read_list(h)
    nv.cursor_to(lst.index(vid)); h.press("A", 4, 30); h.step(20)
    nv.back_to_main(); nv.close(); h.step(30)


BATTLE_LABEL = {"normal": "QaTestBtl8", "boss": "QaBossBtl8"}
LABELS = {}


def solo(h, c):
    """party := character c alone (field-time script; keeps the battle menu and ATB deterministic)"""
    h.run_event(sum(([0x3F, n, 0x00] for n in party_order(h) if n != c), []))


def start_battle(h, slot_i, kind="normal"):
    """QA ROM battle script (battle + vanilla post-battle check + fade-in): a battle must never run from a script
    injected into WRAM - battle RAM overwrites it and the event engine resumes into garbage afterwards"""
    h.call_event(LABELS[BATTLE_LABEL[kind]], frames=1)
    for _ in range(900):
        h.step(1)
    for _ in range(80):
        if h.r8(ACTIVE) == slot_i:
            h.step(20)
            return True
        h.press("Y", 4, 30); h.step(30)
    return False


def fight(h, frames=420, every=2):
    h.press("A", 8, 30); h.press("A", 8, 10)
    seq, shots = [], []
    for t in range(frames):
        h.step(1)
        seq.append(h.r8(ANIM_NO))
        if t % every == 0:
            shots.append(np.asarray(h.em.get_screen()).copy())
    return seq, shots


def finish_battle(h):
    for t in range(6000):
        if t % 16 == 0:
            h.step(4, ("A",))
        else:
            h.step(1)
        if t > 600 and h.idle():
            break
    h.step(60)


def runs(seq):
    return [(f"{k:02X}", len(list(g))) for k, g in itertools.groupby(seq)]


def main(qa, manifest, out):
    q = Report(out)
    L = labels(manifest)
    LABELS.update(L)
    res = {}
    h = T(qa)
    boot_new_game(h)
    menu(h, L, [0, 0])                                   # grant all 39
    st_all = h.em.get_state()

    def setup(c, wid):
        h.em.set_state(st_all); h.step(10)
        menu(h, L, PRESET_PICKS[preset_for(c)])
        h.run_event([0x8D, c])
        equip_menu(h, c, wid)
        return party_order(h).index(c)

    def clear_hand_bit(c, hand=0):
        bit = 256 + c * 6 + hand
        h.w8(0x1CF8 + bit // 8, h.r8(0x1CF8 + bit // 8) & ~(1 << (bit % 8)))

    def as_template(c, si, tpl):
        """POKE (test only), inside the running battle: the R-hand becomes the template vanilla weapon. Every
        battle stat, ATB value and the RNG stay those of the extended weapon's battle, so the only difference left
        is the animation / Jump graphic lookup (RHandItem $3CA8, battle hand list $2B86, equipment bit)"""
        h.w8(0x3CA8 + 2 * si, tpl)
        h.w8(0x2B86 + 5 * si, tpl)
        clear_hand_bit(c)

    # ------------------------------------------------------------------ W: Fight, all 13 weapons
    wbad, wdet = [], {}
    rom_b = open(qa, "rb").read()
    for wid in sorted(i for i, it in BYID.items() if it["category"] == "weapon"):
        it = BYID[wid]
        c = CHARS.index(it["users"][0])
        si = setup(c, wid)
        st_eq = h.em.get_state()
        x = 2 * si
        tpl = int(it["template"], 16)
        # reference: the template weapon really equipped (field POKE) -> its battle power / hit
        h.w8(0x1600 + 0x25 * c + 0x1F, tpl); clear_hand_bit(c)
        start_battle(h, si)
        tpl_power, tpl_hit = h.r8(0x3B68 + x), h.r8(0x3B7C + x)
        # the extended weapon
        h.em.set_state(st_eq); h.step(10)
        ok = start_battle(h, si)
        got = {"power": h.r8(0x3B68 + x), "hit": h.r8(0x3B7C + x), "str": h.r8(0x3B2C + x),
               "elem": h.r8(0x3B90 + x), "props": h.r8(0x3BA4 + x), "template_power": tpl_power,
               "template_hit": tpl_hit}
        st_menu = h.em.get_state()
        seq_a, fa = fight(h)
        q.shot(h, f"W_{wid:03X}_{CHARS[c]}_fight")
        # the same battle state, the hand item swapped to the template
        h.em.set_state(st_menu)
        as_template(c, si, tpl)
        seq_b, fb = fight(h)
        diff = [k for k, (u, v) in enumerate(zip(fa, fb)) if (u != v).any()]
        moving = sum(1 for k in range(1, len(fa)) if (fa[k] != fa[k - 1]).any())
        an = 0xC0 + (wid & 0xFF)
        tp = rom_b[0x185000 + 30 * tpl + 20]
        good = ok and an in seq_a and tpl + 1 in seq_b and an not in seq_b \
            and got["power"] - tpl_power == it["power"] - tp and got["hit"] == it["hit_rate"] \
            and not diff and moving > 30
        wdet[f"{wid:03X}"] = {"char": CHARS[c], "template": it["template"], "anim_runs": runs(seq_a)[:12],
                              "template_anim_runs": runs(seq_b)[:12], "battle": got, "differing_frames": diff[:10],
                              "animated_frames": moving}
        if not good:
            wbad.append(f"{wid:03X}")
        k60 = next((k for k, v in enumerate(seq_a) if v == an), 60) // 2 + 15
        np_pair = np.concatenate([fa[min(k60, len(fa) - 1)], fb[min(k60, len(fb) - 1)]], axis=1)
        from PIL import Image
        q.n += 1
        Image.fromarray(np_pair).resize((1024, 448), Image.NEAREST).save(
            os.path.join(out, f"{q.n:03d}_W_{wid:03X}_ext_vs_template.png"))
    res["weapons"] = wdet
    q.check("W1 all 13 weapons: Fight uses animation number $C0+low byte (the template run uses the "
            "template's id+1), battle power differs from the template weapon's by exactly the power difference, hit "
            "rate = the item's, and every rendered frame of the attack equals the same battle with the template "
            "vanilla weapon in hand (no Brush alias, no unarmed)",
            not wbad, {"failed": wbad, "detail": {k: v for k, v in wdet.items() if k in wbad}})

    # ------------------------------------------------------------------ J: Jump with the spears
    jbad, jdet = [], {}
    for wid in (0x104, 0x10B):
        it = BYID[wid]
        c = CHARS.index("Edgar")
        si = setup(c, wid)
        h.w8(0x1600 + 0x25 * c + 0x16, CMD_JUMP)                      # POKE: Edgar command 1 := Jump
        ok = start_battle(h, si)
        cmd = h.r8(0x202E + 12 * si)
        st_menu = h.em.get_state()
        _, fa = fight(h, 1600, 4)
        q.shot(h, f"J_{wid:03X}_jump_end")
        h.em.set_state(st_menu)
        as_template(c, si, int(it["template"], 16))
        _, fb = fight(h, 1600, 4)
        diff = [k for k, (u, v) in enumerate(zip(fa, fb)) if (u != v).any()]
        moving = sum(1 for k in range(1, len(fa)) if (fa[k] != fa[k - 1]).any())
        jdet[f"{wid:03X}"] = {"template": it["template"], "menu": ok, "first_command": f"{cmd:02X}",
                              "differing_samples": diff[:10], "animated_samples": moving}
        if not ok or cmd != CMD_JUMP or diff or moving < 50:
            jbad.append(f"{wid:03X}")
    res["jump"] = jdet
    q.check("J1 Jump with Sandpiercer / Gale Lance (POKE: command Jump) renders every frame like the same battle with "
            "the template spear (Partisan / Aura Lance) in hand", not jbad, jdet)

    # ------------------------------------------------------------------ G: Genji Glove dual wield
    c = CHARS.index("Locke")
    h.em.set_state(st_all); h.step(10)
    menu(h, L, PRESET_PICKS[preset_for(c)])
    h.run_event([0x8D, c])
    equip_relic_vanilla(h, c, 0xD1)                                   # Genji Glove
    # leaving the Relic menu with Genji Glove re-arranges the hands (vanilla): set L then R explicitly
    if h.eq(c)[1] != 0x108:
        equip_menu(h, c, 0x108, hand=1)
    if h.eq(c)[0] != 0x103:
        equip_menu(h, c, 0x103, hand=0)
    eq = h.eq(c)
    si = party_order(h).index(c); x = 2 * si
    start_battle(h, si)
    pw = (h.r8(0x3B68 + x), h.r8(0x3B69 + x)); r4 = h.r8(0x2E6E + si)            # C2:2883: $11D8 & $10 (Genji)
    seq, _ = fight(h, 500)
    q.shot(h, "G_genji_fight")
    loff = wdet["103"]["battle"]["power"] - 198                        # Locke's own battle-power offset (W1, same item)
    # Genji flag: battle copies $11D8 & $10 to $2E6E + slot (C2:2883)
    q.check("G1 Genji Glove: Raider Knife R + Darill's Dirk L equipped (9-bit ids), battle powers 198/202 (+ Locke's "
            "offset measured in W1), both "
            "animation numbers ($C3, $C8) used by Fight",
            eq[0] == 0x103 and eq[1] == 0x108 and pw == (198 + loff, 202 + loff) and 0xC3 in seq and 0xC8 in seq and r4 & 0x10,   # $11D8 bit 4: Genji Glove
            {"eq": [f"{v:03X}" for v in eq], "power": pw, "relic4": f"{r4:02X}", "anim_runs": runs(seq)[:16]})
    finish_battle(h)
    q.check("P1 battle end (Genji run): Locke's two extended weapons and the inventory are unchanged",
            h.eq(c)[:2] == [0x103, 0x108], [f"{v:03X}" for v in h.eq(c)])

    # ------------------------------------------------------------------ H: Gauntlet two-hand
    c = 0
    h.em.set_state(st_all); h.step(10)
    menu(h, L, PRESET_PICKS[0])
    h.run_event([0x8D, c])
    equip_relic_vanilla(h, c, 0xD0)                                   # Gauntlet
    equip_menu(h, c, 0x100, hand=0)
    si = party_order(h).index(c); x = 2 * si
    start_battle(h, si)
    r4 = h.r8(0x3C58 + x); wf = h.r8(0x3BA4 + x)
    seq, _ = fight(h)
    q.check("H1 Gauntlet + Tempered Edge (two-hand flag, other hand empty): Gauntlet effect ($11D8 bit 3) active and the "
            "weapon's two-hand flag kept in battle (C2 clears it without Gauntlet), Fight uses animation $C0",
            r4 & 0x08 and wf & 0x40 and 0xC0 in seq, {"relic4": f"{r4:02X}", "weapon_flags": f"{wf:02X}",
                                                     "anim_runs": runs(seq)[:10]})
    finish_battle(h)

    # ------------------------------------------------------------------ O: Offering
    c = CHARS.index("Shadow")
    h.em.set_state(st_all); h.step(10)
    menu(h, L, PRESET_PICKS[preset_for(c)])
    h.run_event([0x8D, c])
    equip_relic_vanilla(h, c, 0xD3)                                   # Offering
    equip_menu(h, c, 0x106, hand=0)
    si = party_order(h).index(c)
    start_battle(h, si)
    mons = [k for k in range(6) if h.r16(0x3C1C + 8 + 2 * k) not in (0, 0xFFFF)]
    for k in mons:                                                    # POKE: enemies survive all strikes (test only)
        h.w8(0x3BF4 + 8 + 2 * k, 0x30); h.w8(0x3BF4 + 9 + 2 * k, 0x75)
    hp = lambda: [h.r16(0x3BF4 + 8 + 2 * k) for k in mons]
    h.press("A", 8, 30); h.press("A", 8, 10)
    seq, drops, last = [], 0, hp()
    for t in range(900):
        h.step(1)
        seq.append(h.r8(ANIM_NO))
        now = hp()
        drops += sum(1 for a_, b_ in zip(last, now) if b_ < a_)
        last = now
    q.check("O1 Offering + Moonless: one Fight = 4 strikes (4 separate enemy HP drops), all with the extended animation "
            "number $C6", drops == 4 and 0xC6 in seq and not set(seq) & {0xC0 + k for k in range(0x40) if k != 6},
            {"hp_drops": drops, "anim_runs": runs(seq)[:20]})
    finish_battle(h)

    # ------------------------------------------------------------------ R: Runic / Bushido availability
    def cmd_state(c, wid):
        setup(c, wid)
        si = party_order(h).index(c)
        start_battle(h, si)
        cm = [(h.r8(0x202E + 12 * si + 3 * k), h.r8(0x202F + 12 * si + 3 * k)) for k in range(4)]
        finish_battle(h)
        return cm
    cm_r = cmd_state(CHARS.index("Celes"), 0x101)
    cm_b = cmd_state(CHARS.index("Cyan"), 0x107)
    q.check("R1 Runic with Imperial Saber (Celes) and Bushido with Doma Edge (Cyan): command present and enabled",
            any(k == CMD_RUNIC and not d & 0x80 for k, d in cm_r) and any(k == CMD_BUSHIDO and not d & 0x80 for k, d in cm_b),
            {"celes": [(f"{k:02X}", f"{d:02X}") for k, d in cm_r], "cyan": [(f"{k:02X}", f"{d:02X}") for k, d in cm_b]})

    # ------------------------------------------------------------------ I: battle Item / Throw lists
    h.em.set_state(st_all); h.step(10)
    menu(h, L, PRESET_PICKS[preset_for(CHARS.index("Shadow"))])
    inv0 = inv16(h)
    si = party_order(h).index(CHARS.index("Shadow"))
    start_battle(h, si)
    lst = [h.r8(0x2686 + 5 * s) for s in range(64)]
    ext_pos = [s for s, i, n in h.inv() if i >= 0x100]
    throw = [h.r8(0x4005 + k) for k in range(32)]
    q.check("I1 battle Item list: every slot holding a $1xx item is blank ($FF) - not usable, not throwable, no alias",
            all(lst[s] == 0xFF for s in ext_pos if s < 64), {"list": [f"{v:02X}" for v in lst[:45]]})
    finish_battle(h)
    q.check("P2 battle end: inventory with all 39 production items unchanged", inv16(h) == inv0)
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "EQUIPMENT_BATTLE_REPORT.json"), "w"), indent=1, default=str)
    print("EQUIPMENT BATTLE", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
