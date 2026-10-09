#!/usr/bin/env python3
"""TECH v0.9.2 emulator suite: Celes enablers E1-E9 on the QA ROM (stable-retro / snes9x).

POKEs are test setup only and are listed per check (party HP top-up so the locked-stat Praetor can be fought by an
opening-level party, Suppressor Bits made untargetable so the party's action reaches the Praetor, Praetor HP placed
just above a threshold). Everything else goes through the real QA hub, menus, battle menu and field movement.

  E1  hub 'WoR aboard the Falcon' -> airship over the World of Ruin (146,204) -> land (B) -> walk 2 tiles north ->
      map $1A2 loaded by the world short entrance, parent = (map 1, 146,202) -> walk out south -> back on the world
      map at (146,203) beside the parked airship -> step onto it, A -> airborne again
  E2  locked Praetor battle (group $FA / formation $244): Praetor alone at the start (Bits loaded, hidden, full HP),
      opening barrier (Safe + Shell); a hit that takes it to <= 70% shows both Bits
  E3  a hit that takes it to <= 40%: Defense 165 -> 80, Haste, overload palette in the battle palette buffer, HP
      unchanged except the hit's damage (no monster swap)
  E4  Magitek Cell (Lightning) x3 on the Praetor: hits 1-2 counted, hit 3 = Grounding Field (Lightning null, not weak,
      3 turns); a Lightning hit during the field does only the non-elemental half and is not counted; the field
      expires after 3 Praetor turns (weak again, null cleared, count restarts); a new battle starts from the ROM
      record again (nothing persists)
  E5  party-conditional survivor on $1A2: Locke line (P1), Edgar fallback (Celes/Edgar/Sabin), Sabin fallback (P2),
      line dropped (Terra + Celes)
  E6  map $1A2 palette buffer = derived palette $30; vanilla map palettes intact in the relocated table (ROM)
  E7  Vale visible only with NPC_CELES_VALE_OUTER; sprite palette slot 7 = new palette $20 (relocated table entry)
  E8  outer-map state presentation for none / BURN / PRESERVE / Graves (BG1 tiles in WRAM, regions / tiles from
      maps/celes_outer_v092/states.json since v0.9.3; rendered frames: tools/emu_visual_v093.py S4) + state survives a
      save -> power cycle -> load
  E9  formation $244 / $245 bytes: front attack only (aux $E3), hidden slots; 12 battle starts are all front attacks;
      build formation_safety report: 0 errors for $244 / $245 (hidden slots included)

usage: emu_enablers_v092.py <qa.sfc> <qa.manifest.json> <out>   -> <out>/ENABLERS_EMULATOR_REPORT_v092.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import numpy as np
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, dump_sram, write_sram, continue_slot1
from emu_item_battle import labels, talk, to_terra, bslot
from emu_cons_battle_v09 import choose_item, CMD_CURSOR
from emu_celes_suite import walk, pos, talk as face_talk, obj_visible
from patches import celes_enablers_v092 as CE
from emu_menu_nav import Nav, ST

HP, MAXHP, DEF, WEAK, NULL, ST12, ST34 = 0x3BF4, 0x3C1C, 0x3BB8, 0x3BE0, 0x3BCD, 0x3EE4, 0x3EF8
VAR = 0x3EB0
PRAETOR = 4                                   # battle target index 4 = monster slot 0
EXP = {"EXP_HOPE_EMPIRE": 0x0E0, "EXP_CELES_STARTED": 0x0E8, "EXP_CELES_DONE": 0x0E9, "PRESERVED": 0x0EA,
       "CHOSEN": 0x0EB, "GRAVES": 0x0EC, "VALE": 0x6F0}


def evlabels(manifest):
    """labels of every event package (QA hub + enabler map package) from the manifest listings"""
    import re
    m = json.load(open(manifest))
    out = {}
    for txt in m["notes"]["event_listings"].values():
        for a, lab in re.findall(r"^([0-9A-F]{2}:[0-9A-F]{4})\s+@(\w+)", txt, re.M):
            out[lab] = int(a.replace(":", ""), 16)
    return out


def bit(h, n):
    return (h.r8(0x1E80 + (n >> 3)) >> (n & 7)) & 1


def hub(h, L, picks):
    h.call_event(L["QaRoot92"], frames=1)
    return talk(h, picks)


def older(h, L, picks):
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def sky(h):
    """mean colour of the top 24 lines (orange WoR sky when the airship is flying, ground when on foot)"""
    s = np.asarray(h.em.get_screen())[8:32].reshape(-1, 3).mean(axis=0)
    return [round(float(v)) for v in s]


def heal(h):
    for t in range(4):
        if h.r16(MAXHP + 2 * t) not in (0, 0xFFFF):
            h.w8(MAXHP + 2 * t, 0x0F); h.w8(MAXHP + 2 * t + 1, 0x27)
            h.w8(HP + 2 * t, 0x0F); h.w8(HP + 2 * t + 1, 0x27)
            h.w8(ST12 + 2 * t, 0); h.w8(ST12 + 2 * t + 1, 0)


def run(h, n):
    for i in range(n):
        h.step(1)
        if i % 20 == 0:
            heal(h)


def pstate(h):
    return {"hp": [h.r16(HP + 2 * t) for t in range(4, 7)], "def": [h.r8(DEF + 2 * t) for t in range(4, 7)],
            "weak": [h.r8(WEAK + 2 * t) for t in range(4, 7)], "null": [h.r8(NULL + 2 * t) for t in range(4, 7)],
            "var5": h.r8(VAR + 0), "var6": h.r8(VAR + 1), "var7": h.r8(VAR + 2),
            "global_vars": h.rbytes(VAR + 4, 20).hex(),
            "st34": [h.r16(ST34 + 2 * t) for t in range(4, 7)], "shown": h.r8(0x2F2F),
            "pal": h.rbytes(0x7F00, 32).hex(), "type": h.r8(0x201F)}


def set_hp(h, v):
    h.w8(HP + 2 * PRAETOR, v & 0xFF); h.w8(HP + 2 * PRAETOR + 1, v >> 8)


def notarget_bits(h):
    h.w8(0x2F46, h.r8(0x2F46) & ~0x06)


def terra_fight(h):
    heal(h); notarget_bits(h); to_terra(h)
    for _ in range(8):
        if h.r8(CMD_CURSOR) == 0:
            break
        h.press("UP", 8, 24)
    h.press("A", 8, 40); h.press("A", 8, 10)
    run(h, 480)


def terra_cell(h):
    heal(h); notarget_bits(h); to_terra(h)
    e = next(s for s in range(256) if bslot(h, s)[0] == 0x2E and bslot(h, s)[1] & 1)
    choose_item(h, e)
    run(h, 480)


def start_battle(h, L, label):
    h.call_event(L[label], frames=1)
    run(h, 900)


def finish_battle(h):
    for t in range(6000):
        if t > 30:
            for k in range(6):
                if h.r16(HP + 8 + 2 * k) not in (0, 1, 0xFFFF):
                    h.w8(HP + 8 + 2 * k, 1); h.w8(HP + 9 + 2 * k, 0)
        heal(h) if t % 20 == 0 else None
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
        if t > 200 and h.idle():
            break
    h.step(60)


STATES = json.load(open(os.path.join(HERE, "maps", "celes_outer_v092", "states.json")))   # TECH v0.9.3 E8 regions / states


def tiles(h):
    """BG1 map layout buffer ($7F:0000, 256 per row) over the E8 memorial / archive regions (states.json)"""
    out = {}
    for reg, r in STATES["regions"].items():
        out[reg] = [h.r8(0x10000 + (r["y"] + j) * 256 + r["x"] + i) for j in range(r["h"]) for i in range(r["w"])]
    return out


def state_tiles(region, state):
    return [int(t, 16) for row in STATES["states"][region][state]["rows"] for t in row.split()]


def main(qa, manifest, out):
    q = Report(out)
    L = evlabels(manifest)
    man = json.load(open(manifest))
    rom = open(qa, "rb").read()
    res = {}
    h = T(qa)
    boot_new_game(h)
    older(h, L, [0, 0])                                   # 8 consumables x5 (Magitek Cells for E4)
    older(h, L, [0, 2, 2, 1, 0])                          # preset P1 Terra Locke Celes Edgar (QaReady8 + P1)
    st_p1 = h.em.get_state()

    # ------------------------------------------------------------------ E1 world landing / parent return / Falcon
    h.em.set_state(st_p1); h.step(10)
    h.call_event(L["QaWor92"], frames=1)                  # hub 'WoR aboard the Falcon' (no A presses: A flies)
    h.step(700)
    e1 = {"loaded": (h.r16(0x1F64) & 0x1FF, h.r8(0x1F60), h.r8(0x1F61)), "sky_flying": sky(h)}
    q.shot(h, "E1_flying")
    h.step(20, ("B",)); h.step(400)
    e1["landed_airship"] = (h.r8(0x1F62), h.r8(0x1F63)); e1["sky_landed"] = sky(h)
    q.shot(h, "E1_landed")
    for _ in range(2):
        h.step(16, ("UP",)); h.step(20)
    h.step(700)
    e1["entered"] = (h.r16(0x82), pos(h), h.r16(0x1F69), h.r8(0x1F6B), h.r8(0x1F6C))
    q.shot(h, "E1_outer_map")
    for _ in range(3):
        h.step(16, ("DOWN",)); h.step(20)
    h.step(700)
    e1["back"] = (h.r16(0x1F64) & 0x1FF, h.r8(0x1F60), h.r8(0x1F61), h.r8(0x1F62), h.r8(0x1F63))
    q.shot(h, "E1_back_on_world")
    h.step(16, ("DOWN",)); h.step(60)
    h.step(10, ("A",)); h.step(500)
    e1["boarded_sky"] = sky(h)
    q.shot(h, "E1_boarded")
    res["E1"] = e1
    orange = lambda c: c[0] > 120 and c[0] > c[2] + 40
    q.check("E1 WoR: aboard the airship at (146,204); land; 2 steps north = short entrance -> map $1A2 at (16,27) "
            "with parent (map 1, 146,202); south exit -> world map (146,203) next to the parked airship (146,204); "
            "step on it + A -> airborne again",
            e1["loaded"] == (1, 146, 204) and orange(e1["sky_flying"]) and e1["landed_airship"] == (146, 204)
            and not orange(e1["sky_landed"]) and e1["entered"][0] == 0x1A2 and e1["entered"][1] == (16, 27)
            and e1["entered"][2:] == (1, 146, 202) and e1["back"] == (1, 146, 203, 146, 204)
            and orange(e1["boarded_sky"]), e1)

    # ------------------------------------------------------------------ E2-E4 locked Praetor
    h.em.set_state(st_p1); h.step(10)
    start_battle(h, L, "QaPraetorL92")
    s0 = pstate(h)
    q.shot(h, "E2_start")
    q.check("E2 Praetor alone at the start: monster 1 shown, Bits loaded hidden with full HP (2200), opening "
            "Magitek Barrier = Safe + Shell on the Praetor, front attack",
            s0["shown"] == 0x01 and s0["hp"] == [47800, 2200, 2200] and s0["st34"][0] & 0x0060 == 0x0060
            and s0["var7"] & 1 and s0["type"] == 0, s0)
    set_hp(h, 33470)                                      # POKE: 10 HP above 70% (33,460)
    terra_fight(h)
    s1 = pstate(h)
    q.shot(h, "E2_bits")
    q.check("E2 a Fight hit taking the Praetor from 33,470 to <= 70% launches both Suppressor Bits (shown mask $07)",
            s1["hp"][0] <= 33460 and s1["shown"] == 0x07 and s1["var7"] & 2, s1)
    set_hp(h, 19130)                                      # POKE: 10 HP above 40% (19,120)
    hp_before = h.r16(HP + 2 * PRAETOR)
    terra_fight(h)
    s2 = pstate(h)
    q.shot(h, "E3_overload")
    dmg = hp_before - s2["hp"][0]
    q.check("E3 a hit taking it to <= 40%: Defense 165 -> 80, Haste set, overload palette written to the battle "
            "palette buffer, HP = previous HP - that hit's damage only (no record swap)",
            s2["hp"][0] <= 19120 and 0 < dmg < 400 and s2["def"][0] == 80 and s2["st34"][0] & 0x0008
            and s2["pal"] != s1["pal"] and s2["var7"] & 4, {"dmg": dmg, **s2})
    cells = []
    for k in range(4):
        b = h.r16(HP + 2 * PRAETOR)
        terra_cell(h)
        s = pstate(h)
        cells.append({"dmg": b - s["hp"][0], "weak": s["weak"][0], "null": s["null"][0], "count": s["var5"],
                      "turns": s["var6"]})
    q.check("E4 Magitek Cell (Lightning) on the Praetor: 1st / 2nd counted (1200 dmg, weak); 3rd -> Grounding Field "
            "(Lightning null, not weak, field turns 3, count reset); 4th during the field: 400 (non-elemental half "
            "only), not counted",
            [c["dmg"] for c in cells[:3]] == [1200, 1200, 1200] and cells[0]["count"] == 1 and cells[1]["count"] == 2
            and cells[2]["weak"] == 0 and cells[2]["null"] == 0x0C and cells[2]["count"] == 0
            and cells[2]["turns"] in (2, 3) and cells[3]["dmg"] == 400 and cells[3]["count"] == 0, cells)
    trace, last = [], h.r8(VAR + 1)
    for t in range(6000):
        h.step(1)
        if t % 20 == 0:
            heal(h)
        v = h.r8(VAR + 1)
        if v != last:
            trace.append((t, v, h.r8(WEAK + 2 * PRAETOR), h.r8(NULL + 2 * PRAETOR)))
            last = v
        if v == 0:
            break
    sa = pstate(h)
    b = h.r16(HP + 2 * PRAETOR)
    terra_cell(h)
    sb = pstate(h)
    q.check("E4 the field drops one turn per Praetor turn and expires: weak Lightning again, null Lightning cleared "
            "(Poison null kept); the next Lightning hit does 1200 and counts 1",
            sa["var6"] == 0 and sa["weak"][0] == 0x04 and sa["null"][0] == 0x08 and b - sb["hp"][0] == 1200
            and sb["var5"] == 1, {"trace": trace, "after": sa, "next_dmg": b - sb["hp"][0], "count": sb["var5"]})
    res["E2_E4"] = {"start": s0, "70": s1, "40": s2, "cells": cells, "expiry": trace}
    finish_battle(h)
    start_battle(h, L, "QaPraetorL92")
    s3 = pstate(h)
    q.check("E4 nothing persists: a new Praetor battle starts weak Lightning / null Poison / Defense 165, "
            "count 0, field 0, palette = vanilla Guardian palette, opening barrier again; SRAM-saved global battle vars "
            "4-23 untouched", s3["weak"][0] == 4 and s3["null"][0] == 8 and
            s3["def"][0] == 165 and s3["var5"] == 0 and s3["var6"] == 0 and s3["var7"] & 1 and s3["pal"] == s0["pal"]
            and s3["st34"][0] & 0x0060 == 0x0060 and s3["global_vars"] == s0["global_vars"], s3)
    finish_battle(h)

    # ------------------------------------------------------------------ E9 front only
    types = []
    for k in range(12):
        h.em.set_state(st_p1); h.step(10 + 7 * k)          # different RNG phase each start
        start_battle(h, L, "QaPraetorL92")
        types.append(h.r8(0x201F))
    fs = json.load(open(os.path.join(os.path.dirname(qa), os.path.basename(qa).replace(".sfc", ".formation_safety.json"))))
    rep = {r["formation"]: r for r in fs["formations"]}
    form = lambda f: rom[0x38A000 + 15 * f:0x38A000 + 15 * f + 15]
    aux = lambda f: rom[0x389000 + 4 * f:0x389000 + 4 * f + 4]
    ok_bytes = all(aux(f)[0] & 0xF0 == 0xE0 and form(f)[1] & 0x3F == 0x01 for f in (0x244, 0x245))
    e9 = {"battle_types": types, "aux": {f"{f:03X}": aux(f).hex() for f in (0x244, 0x245)},
          "form": {f"{f:03X}": form(f).hex() for f in (0x244, 0x245)},
          "safety": {k: (rep[k]["status"], [i["msg"] for i in rep[k]["issues"]]) for k in ("244", "245")},
          "hidden_checked": [s["slot"] for s in rep["244"]["slots"] if s.get("hidden_at_start")]}
    res["E9"] = e9
    q.check("E9 formations $244 / $245: front attack only (aux high nibble $E = side / pincer / back disabled), "
            "only slot 0 present at the start; 12 battle starts at different RNG phases are all normal (front) "
            "battles; formation_safety: no ERROR for $244 / $245 with the hidden Bit slots checked",
            ok_bytes and set(types) == {0} and all(v[0] != "ERROR" for v in e9["safety"].values())
            and e9["hidden_checked"] == [1, 2], e9)

    # ------------------------------------------------------------------ E5 party-conditional survivor
    surv = {}
    texts = {k: v for k, v in man["notes"]["dialogue_ids"].items() if k.startswith("cel92_surv")}

    def survivor(picks, tag):
        h.em.set_state(st_p1); h.step(10)
        if picks is not None:
            hub(h, L, picks)
        hub(h, L, [1, 2, 2, 0])                           # walk into the outer map
        h.step(400)
        walk(h, "UP", 13); walk(h, "RIGHT", 4)
        seen = []
        if face_talk(h, "RIGHT"):
            for t in range(1500):
                h.step(1)
                if t % 10 == 0 and h.r8(0xBA):
                    d = h.r16(0xD0)
                    if not seen or seen[-1] != d:
                        seen.append(d)
                        h.step(60)
                        q.shot(h, f"E5_{tag}_{len(seen)}")
                        h.press("A", 4, 20)
                if h.idle() and t > 60:
                    break
        return [f"${d:04X}" for d in seen], pos(h)
    surv["P1_locke"] = survivor(None, "locke")
    surv["edgar"] = survivor([1, 2, 1, 1], "edgar")
    h.em.set_state(st_p1); h.step(10)
    older(h, L, [0, 2, 2, 1, 1])                          # preset P2 Terra Sabin Cyan Shadow
    st_p2 = h.em.get_state()
    h.em.set_state(st_p2); h.step(10)
    hub(h, L, [1, 2, 2, 0]); h.step(400)
    walk(h, "UP", 13); walk(h, "RIGHT", 4)
    seen = []
    if face_talk(h, "RIGHT"):
        for t in range(1500):
            h.step(1)
            if t % 10 == 0 and h.r8(0xBA):
                d = h.r16(0xD0)
                if not seen or seen[-1] != d:
                    seen.append(d); h.step(60); q.shot(h, f"E5_sabin_{len(seen)}"); h.press("A", 4, 20)
            if h.idle() and t > 60:
                break
    surv["P2_sabin"] = ([f"${d:04X}" for d in seen], pos(h))
    surv["celes_only"] = survivor([1, 2, 1, 2], "dropped")
    res["E5"] = {"seen": surv, "ids": texts}
    exp = {"P1_locke": "cel92_surv_locke", "edgar": "cel92_surv_edgar", "P2_sabin": "cel92_surv_sabin",
           "celes_only": "cel92_surv_dropped"}
    ok5 = all(surv[k][0][:1] == [texts["cel92_surv_base"]] and texts[v] in surv[k][0] and
              sum(1 for x in surv[k][0] if x in texts.values()) == 2 for k, v in exp.items())
    q.check("E5 survivor: base line + exactly one reaction - Locke (P1) / Edgar fallback (Terra Celes Edgar Sabin) / "
            "Sabin fallback (P2, no Locke / Edgar) / line dropped (Terra + Celes) - via event cmd $DE + CASE_CHAR bits",
            ok5, res["E5"])

    # ------------------------------------------------------------------ E6 / E7 / E8 outer map
    pals = man["notes"]["celes_enablers"]["palettes"]
    newspr = bytes.fromhex(pals["new_sprite"]["0x20"])
    src = CE.load_palettes()
    clean = open(os.path.join(HERE, "..", "Final Fantasy III (USA) (Rev 1).sfc"), "rb").read()
    base = 0x2DC480 + 256 * 0x18
    derived = CE.derive(clean[base:base + 256], src["map_palettes"][0]["transform"])

    def enter(picks_list):
        h.em.set_state(st_p1); h.step(10)
        for p in picks_list:
            hub(h, L, p)
        hub(h, L, [1, 2, 2, 0])
        h.step(500)
    h.em.set_state(st_p1); h.step(30)
    van_idx = clean[0x2D8F00 + 33 * 0x013 + 25]           # vanilla map $013 palette index (map properties ED:8F00)
    vbuf, vsrc = h.rbytes(0x7200, 256), clean[0x2DC480 + 256 * van_idx:0x2DC480 + 256 * van_idx + 256]
    vdiff = [i // 2 for i in range(2, 256, 2) if vbuf[i:i + 2] != vsrc[i:i + 2]]
    enter([])
    h.gd.update_ram()
    mpal = h.rbytes(0x7200, 256)
    spal7 = h.rbytes(0x7300 + 7 * 32, 32)
    spal06 = h.rbytes(0x7300, 7 * 32)
    vale0 = obj_visible(h, 0x10)
    q.shot(h, "E6_E7_outer_default")
    diff = [i // 2 for i in range(2, 256, 2) if mpal[i:i + 2] != derived[i:i + 2]]
    q.check("E6 map $1A2 uses the new map palette $30: field palette buffer = derived Imperial Ruins palette for every "
            "BG colour except the colours the field engine manages itself (the same colours differ on vanilla map $013 "
            "vs its vanilla palette: text / window colours); ROM table: 48 vanilla map palettes byte-identical at F7:A000",
            set(diff) <= set(vdiff) and len(diff) <= 12
            and rom[0x37A000:0x37A000 + 48 * 256] == clean[0x2DC480:0x2DC480 + 48 * 256],
            {"differing_colours": diff, "vanilla_013_engine_colours": vdiff, "buffer": mpal[:16].hex(),
             "derived": derived[:16].hex()})
    q.check("E7 sprite palette slot 7 = new sprite palette $20 (relocated MapSpritePal entry, loaded by the startup "
            "event); slots 0-6 = vanilla MapSpritePal 0-6; vanilla 32 entries byte-identical at F7:E000",
            spal7 == newspr and spal06 == clean[0x268000:0x268000 + 7 * 32] and
            rom[0x37E000:0x37E000 + 32 * 32] == clean[0x268000:0x268000 + 32 * 32], {"slot7": spal7.hex()})
    enter([[1, 2, 2, 1]])                                 # Vale on
    vale1 = obj_visible(h, 0x10)
    q.shot(h, "E7_vale_visible")
    q.check("E7 Vale (NPC object $10) hidden by default, visible after NPC_CELES_VALE_OUTER is set",
            not vale0 and vale1, {"default": vale0, "set": vale1})
    states = {}
    for tag, picks in (("none", []), ("burn", [[1, 2, 0, 0]]), ("preserve", [[1, 2, 0, 1]]),
                       ("graves", [[1, 2, 0, 1], [1, 2, 0, 2, 0]])):
        enter(picks)
        states[tag] = tiles(h)
        q.shot(h, f"E8_{tag}")
    res["E8"] = states
    expect = {"none": (state_tiles("memorial", "none"), state_tiles("archive", "sealed")),
              "burn": (state_tiles("memorial", "tags"), state_tiles("archive", "burned")),
              "preserve": (state_tiles("memorial", "tags"), state_tiles("archive", "kept")),
              "graves": (state_tiles("memorial", "stone"), state_tiles("archive", "kept"))}
    q.check("E8 outer-map presentation from the persistent bits (BG1 tiles of the 4 x 2 memorial / 2 x 2 archive regions, "
            "maps/celes_outer_v092/states.json): none = machinery wall / sealed door; BURN = tag memorial / burned archive; "
            "PRESERVE = tag memorial / retained archive; Graves = stone memorial (archive keeps its branch)",
            all((states[k]["memorial"], states[k]["archive"]) == (list(m), list(a)) for k, (m, a) in expect.items()),
            states)
    # persistence: PRESERVE + Graves state saved, power cycle, loaded, map re-entered
    h.em.set_state(st_p1); h.step(10)
    hub(h, L, [1, 2, 0, 1]); hub(h, L, [1, 2, 0, 2, 0])
    pre = {k: bit(h, v) for k, v in EXP.items()}
    for _ in range(600):
        if h.idle():
            break
        h.step(1)
    h.step(60)
    h.w8(0x1EB7, h.r8(0x1EB7) | 0x80)                     # POKE (test only): "on a save point"
    nv = Nav(h)
    for _ in range(6):
        h.step(60); nv.open_main()
        if nv.state() == ST["MAIN"]:
            break
    nv.main_to("Save")
    nv.wait(ST["SAVE_SELECT"], 400)
    h.press("A", 4, 60)
    h.press("A", 4, 200)
    q.shot(h, "E8_saved")
    blk, sram = dump_sram(h)
    h.close()
    h2 = T(qa)
    write_sram(h2, blk, sram)
    continue_slot1(h2)
    q.shot(h2, "E8_after_continue")
    for t in range(3000):
        if h2.idle():
            break
        h2.step(1)
        if t % 200 == 199:
            h2.press("B", 4, 10)
    post = {k: bit(h2, v) for k, v in EXP.items()}
    h2.step(30)
    h2.call_event(L["QaOuter92"], frames=1); h2.step(600)
    t2 = tiles(h2)
    q.shot(h2, "E8_after_load")
    q.check("E8 save -> power cycle -> load: the Celes state bits survive and $1A2 re-entered shows the stone "
            "memorial + retained archive", pre == post and post["GRAVES"] == 1 and post["PRESERVED"] == 1 and
            (t2["memorial"], t2["archive"]) == (state_tiles("memorial", "stone"), state_tiles("archive", "kept")),
            {"pre": pre, "post": post, "tiles": t2})
    h2.close()
    out_rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(out_rep, open(os.path.join(out, "ENABLERS_EMULATOR_REPORT_v092.json"), "w"), indent=1, default=str)
    print("ENABLERS v0.9.2", "PASS" if out_rep["all_pass"] else "FAIL",
          f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
