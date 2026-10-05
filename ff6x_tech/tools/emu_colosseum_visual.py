#!/usr/bin/env python3
"""TECH v0.7.3 emulator check: Colosseum VISUAL / QA-state validation (stable-retro / snes9x).

A  before: v0.7.2 QA ROM, QA menu Colosseum with the opening Narshe party (Terra in Magitek, Wedge, Vicks)
B  the same opening state on the clean Rev 1 ROM (vanilla receptionist branch CB:78D9): same artifacts?
C  cause isolation on Rev 1: Terra with only her Magitek status cleared; record/actor data of Wedge/Vicks
E  after: v0.7.3 QA ROM, QA menu "Fight: Terra/Locke/Celes/Edgar" (normalized party, restored afterwards):
   every fighter renders, win/reward/loss/return, Terra wearing the three extended QA items keeps them
E' the same normalized party on Rev 1 (the QA ROM's own normalization bytes run as a WRAM event): identical frames
F  real production path: production v0.7.2 and Rev 1, normalized party, Colosseum map $19D, real receptionist

Fighter state is read from battle RAM 100 frames after the battle starts (see emu_colosseum.run_combo):
$0208 actor chosen in the menu, $3010 record pointer of slot 1 ($FFFF = no record found -> no sprite / no name),
$2EAE sprite id + name (wCharGfxDataBuf), $64BA battle Magitek mode (wMagitekModeEnabled).
POKE (test setup only, identical in compared ROMs): game clock aligned before each entry; "win" combinations hold
the opponent at 1 HP.

usage: emu_colosseum_visual.py <v073 qa.sfc> <v073 qa.manifest> <v072 qa.sfc> <v072 qa.manifest>
                               <production v072.sfc> <clean_rev1.sfc> <out>
writes <out>/COLOSSEUM_VISUAL_REPORT.json and screenshots
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_colosseum as C
from emu_colosseum import T, run_combo, to_colosseum_map, talk_receptionist, prize_of, KIT, VANILLA_COLO
from emu_item_qa import Report, boot_new_game, equip_slot
from emu_item_battle import labels
from emu_menu_nav import Nav, ST

OPENING = {0: "Terra", 1: "Wedge", 2: "Vicks"}
NORMAL = {0: "Terra", 1: "Locke", 2: "Celes", 3: "Edgar"}
EXPECT_ACTOR = {"Terra": 0x00, "Locke": 0x01, "Celes": 0x06, "Edgar": 0x04}
CALL_CB78D9 = bytes.fromhex("B2 D9 78 01")


def norm_bytes(rom, L):
    """the QA ROM's own normalization / restore bytes around `call CB:78D9` in QaColoFight7"""
    a = L["QaColoFight7"] - 0xC00000
    blk = rom[a:a + 0x80]
    i = blk.index(CALL_CB78D9)
    j = blk.index(bytes.fromhex("31 82 81 FF"), i)      # party_step RIGHT 1
    return list(blk[:i]), list(blk[i + 4:j])


def boot(rom, ext, kit=True):
    h = T(rom); h.ext_aware = ext; boot_new_game(h)
    if kit:
        h.run_event(sum(([0x80, i] for i in KIT), []))
    return h


def combo(h, start, item, fighter, win, out, tag, q, names):
    C.FIGHTERS = names
    r = run_combo(h, start, item, fighter, win, out, tag, q)
    r.pop("hp_trace", None)
    return r


def visible(r):
    s = r.get("slot1", {})
    return s.get("record_ptr_3010") != "FFFF" and s.get("gfx_id") == s.get("actor_0208")


def main(qa, qa_man, qa72, qa72_man, prod, clean, out):
    q = Report(out)
    L, L72 = labels(qa_man), labels(qa72_man)
    rom_qa = open(qa, "rb").read()
    NORM, REST = norm_bytes(rom_qa, L)
    res = {"normalize_bytes": bytes(NORM).hex(" "), "restore_bytes": bytes(REST).hex(" ")}
    revive = [0x88, 0x00, 0x7F, 0xFF, 0x8B, 0x00, 0xFF]

    # ---------------- A / B: opening party (v0.7.2 QA harness = call CB:78D9; Rev 1 = CB:78D9)
    for name, rom, ext, start in (("A_v072qa", qa72, True, lambda hh: hh.call_event(L72["QaColoFight7"], frames=1)),
                                  ("B_rev1", clean, False, lambda hh: hh.call_event(VANILLA_COLO, frames=1))):
        h = boot(rom, ext)
        res[name] = {}
        for item, f in ((0x04, 0), (0x04, 1), (0x04, 2)):
            h.run_event([0x80, 0x04])                   # a fresh ThiefKnife wager each time
            res[name][OPENING[f]] = combo(h, start, item, f, False, out, f"{name}_{OPENING[f]}", q, OPENING)
            h.run_event(revive + [0x88, 0x0E, 0x7F, 0xFF, 0x8B, 0x0E, 0xFF, 0x88, 0x0F, 0x7F, 0xFF, 0x8B, 0x0F, 0xFF])
        if name == "B_rev1":
            res["opening_records"] = {n: {"actor_1600": f"{h.r8(0x1600 + 0x25 * n):02X}",
                                          "gfx_1601": f"{h.r8(0x1601 + 0x25 * n):02X}",
                                          "party_1850": f"{h.r8(0x1850 + n):02X}",
                                          "status1_1614": f"{h.r8(0x1614 + 0x25 * n):02X}"} for n in (0, 14, 15)}
        h.close()
    for f, who in OPENING.items():
        a, b = res["A_v072qa"][who], res["B_rev1"][who]
        same = set(a.get("battle_frames", {})) & set(b.get("battle_frames", {}))
        q.check(f"A/B {who} (opening party): v0.7.2 QA shows exactly what clean Rev 1 shows (same fighter state, "
                f"{len(same)} identical rendered frames)", a.get("slot1") == b.get("slot1") and len(same) >= 20,
                {"v072qa": a.get("slot1"), "rev1": b.get("slot1"), "identical_frames": len(same)})
    for who in ("Wedge", "Vicks"):
        s = res["B_rev1"][who].get("slot1", {})
        q.check(f"B Rev 1 {who} (opening party): fighter has no character record (actor {s.get('actor_0208')} chosen, "
                "record pointer $FFFF) -> no sprite, empty name box = the reported invisible fighter, in vanilla",
                s.get("record_ptr_3010") == "FFFF" and s.get("name") == "ffffffffffff", s)
    s = res["B_rev1"]["Terra"].get("slot1", {})
    q.check("B Rev 1 Terra (opening party, Magitek status): battle Magitek mode ON ($64BA=1) = the extra armor sprite, "
            "in vanilla", s.get("magitek_mode") == 1 and s.get("record_ptr_3010") != "FFFF", s)
    rec = res["opening_records"]
    q.check("B cause (Wedge/Vicks): the opening records 14/15 hold actors $20/$21, the menu passes the record number "
            "($0E/$0F) and the battle looks it up as an actor id -> not found",
            rec[14]["actor_1600"] == "20" and rec[15]["actor_1600"] == "21"
            and res["B_rev1"]["Wedge"]["slot1"]["actor_0208"] == "0E"
            and res["B_rev1"]["Vicks"]["slot1"]["actor_0208"] == "0F", rec)

    # ---------------- C: cause isolation on Rev 1 - only Terra's Magitek status cleared
    h = boot(clean, False)
    h.run_event([0x88, 0x00, 0xF7, 0xFF])
    res["C_rev1_terra_no_magitek"] = combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), 0x04, 0, False, out,
                                           "C_rev1_terra_no_magitek", q, OPENING)
    h.close()
    s = res["C_rev1_terra_no_magitek"].get("slot1", {})
    q.check("C Rev 1 Terra with only status-1 bit $08 (Magitek) cleared: Magitek mode OFF, extra sprite gone",
            s.get("magitek_mode") == 0 and s.get("gfx_id") == "00", s)

    # ---------------- E: v0.7.3 QA ROM, normalized QA party (QA menu "Fight")
    E = [(0x04, 0, True, "E1_terra_thiefknife_win"), (0xEE, 1, False, "E2_locke_elixir"),
         (0xF0, 2, False, "E3_celes_fenixdown"), (0x04, 3, True, "E4_edgar_thiefknife_win")]
    EXTRA = [0x80, 0x04]                    # a second ThiefKnife (E4), given the same way in every ROM
    fight = lambda hh: hh.call_event(L["QaColoFight7"], frames=1)
    h = boot(qa, True)
    h.run_event(EXTRA)
    party0 = [h.r8(0x1850 + n) for n in range(16)]
    res["E"] = {}
    for item, f, win, tag in E:
        r = combo(h, fight, item, f, win, out, f"E_v073qa_{tag}", q, NORMAL)
        r["party_after"] = [f"{h.r8(0x1850 + n):02X}" for n in range(16)]
        r["terra_status1_after"] = f"{h.r8(0x1614):02X}"
        res["E"][tag] = r
        h.run_event(revive)
    # E5: Terra wears the three extended QA items
    h.run_event([0x66, 0x3D, 0x01, 0x66, 0x3E, 0x01, 0x66, 0x3F, 0x01, 0x80, 0x04])
    nv = Nav(h); h.step(60)
    nv.open_main(); nv.main_to("Equip"); nv.wait(ST["CHAR"], 300); h.step(30)
    for _ in range(3):
        if nv.state() == ST["EQUIP_OPT"]:
            break
        h.press("A", 4, 30); nv.wait(ST["EQUIP_OPT"], 120)
    nv.press("A", "EQUIP_SLOT")
    equip_slot(nv, h, 0, 0); equip_slot(nv, h, 3, 0)
    nv.back_to_main(); nv.main_to("Relic"); nv.wait(ST["CHAR"], 300); h.step(30)
    for _ in range(3):
        if nv.state() == ST["RELIC_OPT"]:
            break
        h.press("A", 4, 30); nv.wait(ST["RELIC_OPT"], 120)
    nv.press("A", "RELIC_SLOT")
    nv.cursor_to(0); nv.press("A", "RELIC_LIST"); nv.cursor_to(0); h.press("A", 4, 30); h.step(60)
    nv.back_to_main(); nv.close(); h.step(60)
    eq0 = [f"{x:03X}" for x in h.eq(0)]
    r = combo(h, fight, 0x04, 0, True, out, "E_v073qa_E5_terra_QAequipped_win", q, NORMAL)
    r["eq_before"], r["eq_after"] = eq0, [f"{x:03X}" for x in h.eq(0)]
    r["party_after"] = [f"{h.r8(0x1850 + n):02X}" for n in range(16)]
    r["terra_status1_after"] = f"{h.r8(0x1614):02X}"
    res["E"]["E5_terra_QAequipped_win"] = r
    h.close()
    for tag, r in res["E"].items():
        item = r.get("wager") and int(r["wager"], 16)
        mon, prize = prize_of(rom_qa, item)
        s = r.get("slot1", {})
        who = r.get("fighter")
        inv = {int(i, 16): n for _, i, n in r.get("inventory", [])}
        q.check(f"E {tag}: {who} renders normally (actor {EXPECT_ACTOR[who]:02X}, record found, own sprite and name, "
                "Magitek mode off), battle screen bright", visible(r) and s.get("actor_0208") == f"{EXPECT_ACTOR[who]:02X}"
                and s.get("magitek_mode") == 0 and s.get("name") != "ffffffffffff"
                and r.get("battle_brightness", 0) > 20, {"slot1": s, "brightness": r.get("battle_brightness")})
        q.check(f"E {tag}: return to Narshe with fade-in and control; opening party and Terra's Magitek status restored",
                r.get("returned_idle") and r.get("return_brightness", 0) > 20 and r.get("map") == "013"
                and r.get("party_after") == [f"{x:02X}" for x in party0] and bool(int(r.get("terra_status1_after", "0"), 16) & 0x08),
                {k: r.get(k) for k in ("returned_idle", "return_brightness", "map", "party_after", "terra_status1_after")})
        if tag.endswith("_win"):
            q.check(f"E {tag}: win path - prize {prize:02X} received", inv.get(prize, 0) >= 1, r.get("inventory"))
    e5 = res["E"]["E5_terra_QAequipped_win"]
    q.check("E5 Terra wearing QA Blade13D / QA Mail 13E / QA Charm13F: renders normally, equipment unchanged after "
            "the fight", visible(e5) and e5["eq_before"] == e5["eq_after"] and e5["eq_before"][0] == "13D"
            and e5["eq_before"][3] == "13E" and e5["eq_before"][4] == "13F",
            {"before": e5["eq_before"], "after": e5["eq_after"], "slot1": e5.get("slot1")})
    outcomes = {tag: ("win" if any(int(i, 16) == prize_of(rom_qa, int(r["wager"], 16))[1] for _, i, n in r["inventory"])
                      else "loss") for tag, r in res["E"].items() if not tag.endswith("_win")}
    res["E_natural_outcomes"] = outcomes

    # ---------------- E': same normalized party on Rev 1 (QA ROM's own bytes as a WRAM event) - differential
    h = boot(clean, False)
    h.run_event(EXTRA)
    res["E_rev1"] = {}
    for item, f, win, tag in E:
        def start(hh):
            hh.call_event(VANILLA_COLO, frames=1)
        h.run_event(NORM)
        r = combo(h, start, item, f, win, out, f"E_rev1_{tag}", q, NORMAL)
        h.run_event(REST)
        res["E_rev1"][tag] = r
        h.run_event(revive)
    h.close()
    h = boot(qa, True)
    h.run_event(EXTRA)
    res["E_v073qa_split"] = {}
    for item, f, win, tag in E:
        h.run_event(NORM)
        r = combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), item, f, win, out, f"E_v073qa_split_{tag}", q,
                  NORMAL)
        h.run_event(REST)
        res["E_v073qa_split"][tag] = r
        h.run_event(revive)
    h.close()
    for item, f, win, tag in E:
        a, b = res["E_v073qa_split"][tag], res["E_rev1"][tag]
        same = set(a.get("battle_frames", {})) & set(b.get("battle_frames", {}))
        q.check(f"E' {tag}: with the identical normalized party, v0.7.3 QA renders and ends the fight exactly as clean "
                f"Rev 1 ({len(same)} identical rendered frames, same fighter state, same inventory)",
                len(same) >= 20 and a.get("slot1") == b.get("slot1") and a.get("inventory") == b.get("inventory")
                and visible(b), {"identical_frames": len(same), "qa": a.get("slot1"), "rev1": b.get("slot1"),
                                 "qa_inv": a.get("inventory"), "rev1_inv": b.get("inventory")})

    # ---------------- F: real production Colosseum (map $19D, receptionist), normalized party
    F = [(0xEE, 0, "F1_terra_elixir"), (0xF0, 1, "F2_locke_fenixdown"), (0x04, 2, "F3_celes_thiefknife")]
    res["F"] = {}
    for name, rom, ext in (("rev1", clean, False), ("prod_v072", prod, True), ("qa_v073", qa, True)):
        h = boot(rom, ext)
        h.run_event(NORM)
        to_colosseum_map(h)
        res["F"][name] = {}
        for item, f, tag in F:
            res["F"][name][tag] = combo(h, talk_receptionist, item, f, False, out, f"F_{name}_{tag}", q, NORMAL)
            h.step(60)
        h.close()
    for name in ("prod_v072", "qa_v073"):
        for item, f, tag in F:
            a, b = res["F"][name][tag], res["F"]["rev1"][tag]
            same = set(a.get("battle_frames", {})) & set(b.get("battle_frames", {}))
            q.check(f"F {name} {tag} (real receptionist CB:78C3, map $19D, permanent character): fighter renders "
                    f"normally, no extra sprite, identical to Rev 1 ({len(same)} frames), return to $19D",
                    visible(a) and a["slot1"].get("magitek_mode") == 0 and a.get("slot1") == b.get("slot1")
                    and len(same) >= 20 and a.get("inventory") == b.get("inventory") and a.get("returned_idle")
                    and a.get("map") == "19D" and a.get("return_brightness", 0) > 20,
                    {"identical_frames": len(same), "slot1": a.get("slot1"), "inventory": a.get("inventory"),
                     "rev1_inventory": b.get("inventory"), "map": a.get("map")})

    def strip(o):
        if isinstance(o, dict):
            return {k: strip(v) for k, v in o.items() if k != "battle_frames"}
        return o
    rep = {"rom": os.path.basename(qa), "reference": os.path.basename(clean), "checks": q.checks,
           "results": strip(res), "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "COLOSSEUM_VISUAL_REPORT.json"), "w"), indent=1)
    print("COLOSSEUM VISUAL", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:8])
