#!/usr/bin/env python3
"""TECH v0.7.2 emulator check: Colosseum battle entry / win / reward / return (stable-retro / snes9x).

Every combination runs twice with identical inputs from the same New Game state:
  * QA ROM: through the vanilla receptionist branch CB:78D9 with the opening party (v0.7.2: the QA menu "Fight"
    called exactly this; v0.7.3: the QA menu first normalizes the party - tested by tools/emu_colosseum_visual.py)
  * clean Rev 1:     through the vanilla receptionist sequence CB:78D9 itself
and the results are compared (battle id, opponent, fighter, rendered frames, inventory after the battle, return).

POKE (test setup only, identical in both ROMs): for "win" combinations the opponent's HP is set to 1 after the battle
starts and held at 1 while the battle runs (some opponents, e.g. Woolly, heal themselves), so the low-level opening
party can win and the reward path runs. Before every combination the game clock
$021B-$021E is set to the same value (0:30:00, frame 0) in both ROMs: the battle seeds its random number generator from
the clock's frame byte (C2:2440 `lda $021e / asl / asl / sta $be`), and the test setup (New Game boot, the four event
`$80` item gives) does not take the same number of frames in v0.7.x as in Rev 1 (event `$80` scans the 256 slots through
the extended-slot mask: one more frame per newly given item), so without this the un-POKEd fight (C1) would compare
two different random seeds instead of the two ROMs.
Optionally (--v071 <rom>) the v0.7.1 QA harness path is run once to document the original black screen.

Part R (real Colosseum, every ROM): the party is moved to the Colosseum map $19D at (23,5) below the receptionist
(event command $6A; NPC switch $558 set with $DA so the receptionist exists, as in the World of Ruin), the player talks
to the receptionist (NPC event CB:78C3), chooses "(With pleasure.)" and plays three wager/fighter combinations without
any POKE (natural outcome). Every ROM must enter the battle, render and end it exactly as Rev 1 and return to $19D.

usage: emu_colosseum.py <qa.sfc> <qa.manifest.json> <clean_rev1.sfc> <out> [<v0.7.1 qa.sfc> <v0.7.1 manifest>]
env FF6X_COLO_EXTRA="name=rom.sfc,..." also runs C1-C3 on these ROMs through the vanilla receptionist sequence CB:78D9
(e.g. the accepted v0.6.0 production and the v0.7.2 production ROM) and compares them with Rev 1 the same way.
A name starting with "v07" marks a ROM with the extended-item engine.
writes <out>/COLOSSEUM_EMULATOR_REPORT.json
"""
import hashlib, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, equip_slot
from emu_item_battle import labels
from emu_menu_nav import Nav, ST
from emu_celes_suite import talk
import emu_monster_tech as MT

COLO_PROP_PC = 0x1FB600          # ColosseumProp DF:B600, 4 bytes per item: monster, $40, prize, hide
WAGERS = [0xE9, 0x04, 0x08, 0x09]  # Potion, ThiefKnife, Graedus, ValiantKnife -> inventory slots 0-3
FIGHTERS = {0: "Terra", 1: "Wedge", 2: "Vicks"}
VANILLA_COLO = 0xCB78D9
BATTLE_ID = 0x23F


def screen(h):
    return np.asarray(h.em.get_screen())


def bright(h):
    return float(screen(h).mean())


def run_combo(h, start, item, fighter, win, out, tag, q):
    """start(h) begins the Colosseum sequence; wager = first inventory slot holding vanilla `item`"""
    nv = Nav(h)
    ext = getattr(h, "ext_aware", True)        # clean Rev 1: $1CF8 holds Bushido names, no extension bits
    slot = [s for s in range(256) if h.r8(0x1869 + s) == item and not (ext and h.bit(s))][0]
    for i, v in enumerate((0, 30, 0, 0)):     # same RNG seed in every ROM (see module docstring)
        h.w8(0x21B + i, v)
    start(h)
    r = {"tag": tag, "wager_slot": slot, "wager": f"{h.r8(0x1869 + slot):02X}", "fighter": FIGHTERS[fighter]}
    if not nv.wait(ST["COLO_ITEM"], 600):
        r["error"] = "wager list not reached"; return r
    nv.cursor_to(slot)
    h.press("A", 4, 10)
    if not nv.wait(0x76, 600):
        r["error"] = "fighter select not reached"; return r
    q.shot(h, f"{tag}_matchup")
    nv.cursor_lr(fighter)
    h.press("A", 4, 4)
    started, t0 = False, None
    frames = {}
    for t in range(1500):
        h.step(1)
        if MT.in_battle(h) and h.r16(0x3ED4) == BATTLE_ID and any(MT.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)):
            started, t0 = True, t
            break
    r["battle_entered"] = started
    if not started:
        r["brightness"] = bright(h); q.shot(h, f"{tag}_no_battle"); return r
    r["battle_id"] = f"{h.r16(0x3ED4):03X}"
    r["opponent"] = [f"{MT.mon_id(h, k):03X}" for k in range(6) if MT.mon_maxhp(h, k) not in (0, 0xFFFF)]
    for t in range(140):                     # rendered frames after the fade-in (compared with Rev 1)
        h.step(1)
        if t >= 60:
            frames[hashlib.sha1(screen(h).tobytes()).hexdigest()] = t
        if t == 100:
            q.shot(h, f"{tag}_battle")
            # v0.7.3: battle graphics state of the fighter (slot 1): actor chosen in the menu ($0208), record pointer
            # ($3010, $FFFF = no character record found), sprite id / name (wCharGfxDataBuf $2EAE), Magitek mode ($64BA)
            r["slot1"] = {"actor_0208": f"{h.r8(0x208):02X}", "record_ptr_3010": f"{h.r16(0x3010):04X}",
                          "gfx_id": f"{h.r8(0x2EAE):02X}", "name": bytes(h.r8(0x2EAF + i) for i in range(6)).hex(),
                          "magitek_mode": h.r8(0x64BA)}
    q.shot(h, f"{tag}_battle_b")              # v0.7.3: later frames (real-map fade-in, Magitek armor sprite)
    r["battle_frames"] = frames
    r["battle_brightness"] = bright(h)
    hp0 = [MT.mon_hp(h, k) for k in range(6)]
    for b in ("A", "B", "X", "Y"):          # the Colosseum battle is automatic: input must not hang it
        h.press(b, 4, 6)
    if win:
        for k in range(6):
            if MT.mon_maxhp(h, k) not in (0, 0xFFFF) and MT.mon_hp(h, k):
                h.w8(0x3BF4 + 8 + 2 * k, 1); h.w8(0x3BF4 + 9 + 2 * k, 0)
    r["monster_hp_before_poke"] = hp0
    shot_done = False
    r["hp_trace"] = []
    faded = False                            # battle over (screen black): stop pressing A, so the returning
    for t in range(9000):                    # party does not talk to the receptionist again (map $19D)
        if not faded and t % 40 == 0:
            h.press("A", 4, 4)
        else:
            h.step(1)
        if t > 100 and bright(h) < 1:
            faded = True
        if t == 120 and not faded:
            q.shot(h, f"{tag}_battle_c")
        if MT.in_battle(h) and t % 200 == 0:
            if win:
                for k in range(6):
                    if MT.mon_maxhp(h, k) not in (0, 0xFFFF) and MT.mon_hp(h, k) > 1:
                        h.w8(0x3BF4 + 8 + 2 * k, 1); h.w8(0x3BF4 + 9 + 2 * k, 0)
            r["hp_trace"].append([t, [MT.mon_hp(h, k) for k in range(6) if MT.mon_maxhp(h, k) not in (0, 0xFFFF)],
                                  h.r16(0x3BF4), h.r8(0x3EE4)])
        if not shot_done and not MT.in_battle(h) and t > 200:
            shot_done = True
        if t > 600 and h.idle() and bright(h) > 15:
            break
    h.step(90)
    q.shot(h, f"{tag}_after")
    r["returned_idle"] = h.idle()
    r["return_brightness"] = bright(h)
    r["map"] = f"{h.r16(0x82):03X}"
    r["inventory"] = [(s, f"{h.r8(0x1869 + s):02X}", h.r8(0x1969 + s)) for s in range(256) if h.r8(0x1869 + s) != 0xFF]
    return r


COLO_MAP = 0x19D
RECEPTION = [(0x04, 1, "R1_thiefknife_wedge"), (0x08, 2, "R2_graedus_vicks"), (0xE9, 0, "R3_potion_terra")]


def to_colosseum_map(h):
    """switch $558 := 1 (Colosseum NPCs), load map $19D at (23,5) facing UP (receptionist NPC at (23,4))"""
    w = COLO_MAP | (0 << 12)
    h.run_event([0xDA, 0x58, 0x6A, w & 0xFF, w >> 8, 23, 5, 0x00], frames=400)
    h.step(120)


def talk_receptionist(h):
    """talk to the receptionist; choice "(With pleasure.)" is the default cursor position"""
    talk(h, "UP")
    h.step(200)
    h.press("A", 4, 10)


def run_reception(h, out, name, q):
    to_colosseum_map(h)
    res = {"map_loaded": f"{h.r16(0x82):03X}"}
    for item, fighter, tag in RECEPTION:
        res[tag] = run_combo(h, talk_receptionist, item, fighter, False, out, f"{name}_{tag}", q)
        h.step(60)
    return res


KIT = [0xEE, 0xEE, 0xEE, 0xF0, 0xF0, 0xF0, 0x04, 0x09]      # QaColoKit7 (give_item order)
KIT_COMBOS = [(0xEE, 2, "K1_elixir_vicks"), (0xF0, 1, "K2_fenixdown_wedge"), (0xEE, 0, "K3_elixir_terra"),
              (0x04, 2, "K4_thiefknife_vicks")]


def run_kit(h, start, out, name, q):
    """natural outcomes (no POKE) with the QA wager kit; Elixir / Fenix Down face Cactrot"""
    res = {}
    for item, fighter, tag in KIT_COMBOS:
        res[tag] = run_combo(h, start, item, fighter, False, out, f"{name}_{tag}", q)
        # revive the three fighters (clear Wounded, HP := max) so the next combination starts the same way
        h.run_event([0x88, 0x00, 0x7F, 0xFF, 0x8B, 0x00, 0xFF, 0x88, 0x0E, 0x7F, 0xFF, 0x8B, 0x0E, 0xFF,
                     0x88, 0x0F, 0x7F, 0xFF, 0x8B, 0x0F, 0xFF])
    return res


def run_cancel(h, start):
    """open the wager list and leave it with B (no wager): the screen must fade back in with field control"""
    nv = Nav(h)
    start(h)
    if not nv.wait(ST["COLO_ITEM"], 600):
        return {"error": "wager list not reached"}
    h.press("B", 4, 10)
    for t in range(900):
        h.step(1)
        if t > 120 and h.idle() and bright(h) > 15:
            break
    h.step(60)
    return {"returned_idle": h.idle(), "return_brightness": bright(h), "map": f"{h.r16(0x82):03X}"}


def prize_of(rom_bytes, item):
    rec = rom_bytes[COLO_PROP_PC + 4 * item:COLO_PROP_PC + 4 * item + 4]
    return rec[0], rec[2]


def main(qa, manifest, clean, out, v071=None, v071_manifest=None):
    q = Report(out)
    L = labels(manifest)
    rom_qa = open(qa, "rb").read()
    combos = [(0xE9, 0, False, "C1_potion_terra"), (0x04, 1, True, "C2_thiefknife_wedge_win"),
              (0x08, 2, True, "C3_graedus_vicks_win"), (0x09, 0, True, "C4_valiantknife_terra_QAequipped_win")]

    def setup(romfile, ext_aware=True):
        h = T(romfile)
        h.ext_aware = ext_aware
        boot_new_game(h)
        h.run_event(sum(([0x80, i] for i in WAGERS), []))
        return h

    # ---------------- reference: clean Rev 1, vanilla receptionist sequence
    ref = {}
    h = setup(clean, False)
    for slot, fighter, win, tag in combos[:3]:
        ref[tag] = run_combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), slot, fighter, win, out, "rev1_" + tag, q)
    cancel = {"rev1": run_cancel(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1))}
    h.close()
    # wager kit, natural outcomes: Rev 1 gets the same items with event $80
    h = T(clean); h.ext_aware = False; boot_new_game(h)
    h.run_event(sum(([0x80, i] for i in KIT), []))
    kit_ref = run_kit(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), out, "rev1_kit", q)
    h.close()
    # the exact v0.7.1 QA-harness bytes ($9A, party_step RIGHT 1, return) run on the clean Rev 1 ROM (WRAM event)
    h = setup(clean, False)
    rev1_v071_bytes = run_combo(h, lambda hh: hh.run_event([0x9A, 0x31, 0x82, 0x81, 0xFF], frames=1), 0x04, 1, True,
                                out, "rev1_with_v071_harness_bytes", q)
    h.close()
    recep = {"rev1": None}
    h = setup(clean, False)
    recep["rev1"] = run_reception(h, out, "rev1", q)
    h.close()

    # ---------------- optional: further ROMs through the vanilla receptionist sequence
    extra = {}
    for spec in filter(None, os.environ.get("FF6X_COLO_EXTRA", "").split(",")):
        name, rom = spec.split("=", 1)
        h = setup(rom, name.startswith("v07"))
        extra[name] = {tag: run_combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), slot, fighter, win, out,
                                      f"{name}_{tag}", q) for slot, fighter, win, tag in combos[:3]}
        h.close()
        h = setup(rom, name.startswith("v07"))
        recep[name] = run_reception(h, out, name, q)
        h.close()
    h = setup(qa)
    recep["v072qa"] = run_reception(h, out, "v072qa", q)
    h.close()

    # ---------------- QA ROM: QA harness "Get wager kit" + vanilla branch CB:78D9
    h = T(qa); h.ext_aware = True; boot_new_game(h)
    h.call_event(L["QaColoKit7"], frames=1)
    for _ in range(600):
        h.step(1)
        if h.r8(0xBA):                       # kit dialogue open -> close it
            break
    for _ in range(10):
        h.press("A", 4, 20)
        if h.idle():
            break
    kit_inv = [(sl, f"{h.r8(0x1869 + sl):02X}", h.r8(0x1969 + sl)) for sl in range(256) if h.r8(0x1869 + sl) != 0xFF]
    kit_qa = run_kit(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), out, "qa_kit", q)
    h.close()

    # ---------------- v0.7.2 QA ROM through the QA harness
    res = {}
    h = setup(qa)
    for slot, fighter, win, tag in combos[:3]:
        res[tag] = run_combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), slot, fighter, win, out, "qa_" + tag, q)
    # C4: Terra wears the three extended QA items (given through the QA menu event API, equipped through the menus)
    # Terra lost C1 to Chupon (vanilla outcome, same in Rev 1) and is Wounded: revive with event commands
    # $88 (clear status: Wounded) and $8B (HP := max) so she can be equipped
    h.run_event([0x88, 0x00, 0x7F, 0xFF, 0x8B, 0x00, 0xFF])
    h.run_event([0x66, 0x3D, 0x01, 0x66, 0x3E, 0x01, 0x66, 0x3F, 0x01])
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
    eq_before = h.eq(0)
    slot, fighter, win, tag = combos[3]
    res[tag] = run_combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), slot, fighter, win, out, "qa_" + tag, q)
    res[tag]["eq_before"] = [f"{x:03X}" for x in eq_before]
    res[tag]["eq_after"] = [f"{x:03X}" for x in h.eq(0)]
    res[tag]["ext_inventory"] = [(s, f"{i:03X}", n) for s, i, n in h.ext_inv()]
    cancel["qa_harness_fight"] = run_cancel(h, lambda hh: hh.call_event(L["QaColoFight7"], frames=1))
    h.close()

    # ---------------- checks
    for slot, fighter, win, tag in combos:
        r = res[tag]
        wager = slot
        mon, prize = prize_of(rom_qa, wager)
        inv_after = {int(i, 16): n for s, i, n in r.get("inventory", [])}
        base = f"{tag}: wager {wager:02X} -> opponent {mon:02X}, fighter {FIGHTERS[fighter]}"
        q.check(f"{base}: battle entered (battle id $23F)", r.get("battle_entered") and r.get("battle_id") == "23F",
                {k: r.get(k) for k in ("battle_id", "opponent", "error")})
        q.check(f"{base}: opponent is the ColosseumProp monster", r.get("opponent") and int(r["opponent"][0], 16) & 0xFF == mon,
                r.get("opponent"))
        q.check(f"{base}: battle screen rendered (not black) and input does not hang it",
                r.get("battle_brightness", 0) > 20, {"brightness": r.get("battle_brightness")})
        q.check(f"{base}: returns to the field with control, screen faded in (map $013)",
                r.get("returned_idle") and r.get("return_brightness", 0) > 20 and r.get("map") == "013",
                {k: r.get(k) for k in ("returned_idle", "return_brightness", "map")})
        if tag in ref:
            rr = ref[tag]
            same_frames = set(r.get("battle_frames", {})) & set(rr.get("battle_frames", {}))
            q.check(f"{base}: fighter and opponent render exactly as in Rev 1 (identical battle frames)",
                    len(same_frames) >= 20, {"identical_frames": len(same_frames)})
            q.check(f"{base}: result (inventory after the battle) identical to Rev 1",
                    r.get("inventory") == rr.get("inventory") and r.get("opponent") == rr.get("opponent"),
                    {"qa": r.get("inventory"), "rev1": rr.get("inventory")})
        if win:
            q.check(f"{base}: win path - wager consumed, prize {prize:02X} received",
                    inv_after.get(prize, 0) >= 1 and inv_after.get(wager, 0) == 0, r.get("inventory"))
    for name, er in extra.items():
        for slot, fighter, win, tag in combos[:3]:
            r, rr = er[tag], ref[tag]
            same_frames = set(r.get("battle_frames", {})) & set(rr.get("battle_frames", {}))
            q.check(f"{name} {tag} (receptionist sequence CB:78D9): battle entered, same opponent, same rendered frames, "
                    "same result and return as Rev 1",
                    r.get("battle_entered") and r.get("opponent") == rr.get("opponent") and len(same_frames) >= 20
                    and r.get("inventory") == rr.get("inventory") and r.get("returned_idle") and r.get("map") == "013",
                    {"identical_frames": len(same_frames), "inventory": r.get("inventory"), "map": r.get("map"),
                     "returned_idle": r.get("returned_idle")})
    rr0 = recep["rev1"]
    for item, fighter, tag in RECEPTION:
        q.check(f"Rev 1 {tag} (real receptionist, map $19D): battle entered and returned to the Colosseum map",
                rr0[tag].get("battle_entered") and rr0[tag].get("returned_idle") and rr0[tag].get("map") == "19D",
                {k: rr0[tag].get(k) for k in ("battle_entered", "opponent", "returned_idle", "map", "inventory")})
    for name, rres in recep.items():
        if name == "rev1":
            continue
        for item, fighter, tag in RECEPTION:
            r, rr = rres[tag], rr0[tag]
            same_frames = set(r.get("battle_frames", {})) & set(rr.get("battle_frames", {}))
            mon, prize = prize_of(rom_qa, item)
            q.check(f"{name} {tag} (real receptionist CB:78C3 on map $19D, wager {item:02X} -> opponent {mon:02X}, "
                    f"{FIGHTERS[fighter]}): battle entered, rendered, same opponent / frames / result / return as Rev 1",
                    r.get("battle_entered") and r.get("battle_id") == "23F" and r.get("opponent") == rr.get("opponent")
                    and int(r["opponent"][0], 16) & 0xFF == mon and r.get("battle_brightness", 0) > 20
                    and len(same_frames) >= 20 and r.get("inventory") == rr.get("inventory")
                    and r.get("returned_idle") and r.get("return_brightness", 0) > 20 and r.get("map") == "19D",
                    {"identical_frames": len(same_frames), "opponent": r.get("opponent"), "inventory": r.get("inventory"),
                     "rev1_inventory": rr.get("inventory"), "map": r.get("map"), "returned_idle": r.get("returned_idle"),
                     "return_brightness": r.get("return_brightness")})
    q.check("clean Rev 1 running the v0.7.1 harness bytes `9A 31 82 81 FF FE`: battle NOT entered, screen stays black "
            "(same failure as v0.7.1 -> the failure is the harness script, not the engine)",
            not rev1_v071_bytes.get("battle_entered") and rev1_v071_bytes.get("brightness", 99) < 1,
            {"brightness": rev1_v071_bytes.get("brightness")})
    res["rev1_with_v071_harness_bytes"] = rev1_v071_bytes
    q.check("QA harness 'Get wager kit': Elixir x3, Fenix Down x3, ThiefKnife, ValiantKnife in the inventory",
            kit_inv == [(0, "EE", 3), (1, "F0", 3), (2, "04", 1), (3, "09", 1)], kit_inv)
    for item, fighter, tag in KIT_COMBOS:
        r, rr = kit_qa[tag], kit_ref[tag]
        mon, prize = prize_of(rom_qa, item)
        same_frames = set(r.get("battle_frames", {})) & set(rr.get("battle_frames", {}))
        won = any(int(i, 16) == prize for s_, i, n in r.get("inventory", [])) and prize not in (0xEE,)
        q.check(f"{tag} (QA kit, CB:78D9, natural outcome - no POKE; wager {item:02X} -> opponent {mon:02X}, "
                f"prize {prize:02X}, {FIGHTERS[fighter]}): battle entered and rendered, same frames / result / return as "
                "Rev 1", r.get("battle_entered") and r.get("opponent") == rr.get("opponent")
                and int(r["opponent"][0], 16) & 0xFF == mon and r.get("battle_brightness", 0) > 20
                and len(same_frames) >= 20 and r.get("inventory") == rr.get("inventory") and r.get("returned_idle")
                and r.get("return_brightness", 0) > 20 and r.get("map") == "013",
                {"identical_frames": len(same_frames), "inventory": r.get("inventory"),
                 "rev1_inventory": rr.get("inventory"), "prize_in_inventory": won})
    for name, c in cancel.items():
        q.check(f"{name}: wager list left with B (no wager) -> screen fades back in, field control, map $013",
                c.get("returned_idle") and c.get("return_brightness", 0) > 20 and c.get("map") == "013", c)
    c4 = res[combos[3][3]]
    q.check("C4: fighter wearing QA Blade13D / QA Mail 13E / QA Charm13F keeps the extended equipment; extended "
            "inventory untouched", c4.get("eq_before") == c4.get("eq_after") and c4["eq_before"][0] == "13D"
            and c4["eq_before"][3] == "13E" and c4["eq_before"][4] == "13F",
            {"before": c4.get("eq_before"), "after": c4.get("eq_after"), "ext_inv": c4.get("ext_inventory")})

    # ---------------- optional: the v0.7.1 harness (documents the original failure)
    if v071:
        L1 = labels(v071_manifest)
        h = setup(v071)
        r = run_combo(h, lambda hh: hh.call_event(L1["QaColo7"], frames=1), 0x04, 1, True, out, "v071_C2", q)
        h.close()
        q.check("v0.7.1 harness (reference for the root cause): battle is NOT entered and the screen stays black",
                not r.get("battle_entered") and r.get("brightness", 99) < 1, {"brightness": r.get("brightness")},)
        h = setup(v071)
        c = run_cancel(h, lambda hh: hh.call_event(L1["QaColo7"], frames=1))
        h.close()
        q.check("v0.7.1 harness (reference): wager list left with B -> the screen also stays black (map reloaded "
                "with fade-in disabled by $9A, no fade_in in the harness)", c.get("return_brightness", 99) < 1, c)
        cancel["v071_harness"] = c
        res["v071_C2"] = r
    for v in list(res.values()) + list(ref.values()) + [x for e in list(extra.values()) + list(recep.values())
                                                         + [kit_qa, kit_ref]
                                                         for x in e.values() if isinstance(x, dict)]:
        v.pop("battle_frames", None)
    rep = {"rom": os.path.basename(qa), "reference": os.path.basename(clean), "checks": q.checks,
           "results": res, "rev1": ref, "extra": extra, "reception": recep, "cancel": cancel, "kit_inventory": kit_inv,
           "kit_qa": kit_qa, "kit_rev1": kit_ref, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "COLOSSEUM_EMULATOR_REPORT.json"), "w"), indent=1)
    print("COLOSSEUM EMULATOR", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:7])
