#!/usr/bin/env python3
"""TECH v0.4 map-tech QA build - Claude-side EMULATOR suite (snes9x via stable-retro).
NOT user runtime QA. No RAM pokes: New Game -> QA tile -> proof maps $1A0/$1A1 -> exits ->
SavePoint -> menu Save -> (new process) Continue -> persistence -> Annex regression ->
vanilla opening event regression.

usage: emu_map_tech.py save|load <map_tech_rom> <outdir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
from emu_celes_suite import walk, idle, talk, pos, bit, item_count, obj_visible
from emu_qa_access import dialogs, boot_new_game, menu_save, sram_dump, battle_real

R = {"steps": [], "pass": True}
VISITED_B, A2_VIS, LATCH, SAVE_OK = 0x14D, 0x6FA, 0x1B5, 0x1BF


def log(name, ok, **kw):
    R["steps"].append(dict(name=name, ok=bool(ok), **kw))
    if not ok: R["pass"] = False
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


def choose(h, out, tag, n_down, max_frames=1500):
    """Wait for a dialogue with a choice, move the cursor n_down times, confirm; then advance."""
    seen = []
    for t in range(max_frames):
        h.step(1)
        if h.r8(0xBA):
            h.step(150); d0 = h.r16(0xD0); seen.append(f"{d0:04X}")
            h.shot(os.path.join(out, f"{tag}_dlg{d0:04X}.png"))
            for _ in range(n_down): h.press("DOWN", 4, 10)
            h.press("A", 4, 20)
            break
    seen += dialogs(h, out, tag + "_after", choose_down=True)
    return seen


def grid_ok(h, grid):
    h.gd.update_ram()
    mem = lambda a: h.gd.memory.extract(a, '|u1')
    bad = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            t = mem(0x7F0000 + y * 256 + x); p = mem(0x7E7600 + t)
            if (p != 0xF7 and (p & 3) != 0) != (ch == "."):
                bad.append((x, y, t, p))
    return bad


def ids(rom):
    m = json.load(open(rom.replace(".sfc", ".manifest.json")))
    return {k: v[1:] for k, v in m["notes"]["dialogue_ids"].items()}, m


def walk_to(h, d, n, target):
    walk(h, d, n)
    return pos(h) == target


def phase_save(rom, out):
    D, man = ids(rom)
    h = H(rom)
    seen = boot_new_game(h, out)
    log("01 New Game -> first control map $013 (38,49), vanilla opening dialogue",
        h.r16(0x82) == 0x013 and pos(h) == (38, 49) and len(seen) >= 2, dlg=seen[:6])
    walk(h, "UP", 6); walk(h, "LEFT", 4)
    d = choose(h, out, "02_qa_mapA", 0)
    idle(h); h.step(90); h.shot(os.path.join(out, "02_mapA_arrival.png"))
    log("02 QA prompt -> 'Map test A' loads NEW map $1A0 at (16,27)", d[:1] == [D["qa4_prompt"]] and h.r16(0x82) == 0x1A0
        and pos(h) == (16, 27), dlg=d, map=f"{h.r16(0x82):03X}", pos=pos(h))
    bad = grid_ok(h, man["notes"]["maps"]["1A0"]["runtime_grid"])
    log("03 map $1A0 runtime BG1+tile-property grid == compiled source (layout $160 via relocated pointer table)",
        not bad, mismatches=bad[:5])
    vis = [obj_visible(h, o) for o in (0x10, 0x11, 0x12)]
    log("04 NPCs from relocated NPC table: A1, A3 visible; A2 hidden (NPC bit $6FA off)", vis == [True, True, False], vis=vis)
    evp = [h.r8(0x0889 + o * 0x29) | h.r8(0x088A + o * 0x29) << 8 | h.r8(0x088B + o * 0x29) << 16 for o in (0x10, 0x11, 0x12)]
    R["npc_event_ptrs_in_ram"] = [f"{(p & 0xFFFF) | (((p >> 16) + 0xCA) & 0xFF) << 16:06X}" for p in evp]
    lab = man["notes"]["labels"]
    exp = [lab["EvA1"].replace(":", ""), lab["EvA3"].replace(":", ""), lab["EvA2"].replace(":", "")]
    log("05 NPC event router: object event pointers resolved from vector table to F1 events",
        R["npc_event_ptrs_in_ram"] == exp, got=R["npc_event_ptrs_in_ram"], expected=exp)
    # trigger alcove
    walk(h, "UP", 2); walk(h, "LEFT", 6)
    d = dialogs(h, out, "06_trigger"); idle(h)
    log("06 event trigger on new map (relocated trigger table): message + pushed back", d == [D["a_trigger"]]
        and pos(h) == (11, 25), dlg=d, pos=pos(h))
    # north room: A1, A3
    walk(h, "RIGHT", 4); walk(h, "UP", 11)
    log("06b corridor to north room", pos(h) == (15, 14), pos=pos(h))
    walk(h, "LEFT", 5); talk(h, "LEFT"); d = dialogs(h, out, "07_A1_first")
    log("07 A1 (vector #) dialogue before VISITED_B", d == [D["a1_first"]], dlg=d, pos=pos(h))
    walk(h, "RIGHT", 11); talk(h, "RIGHT"); d = dialogs(h, out, "08_A3")
    log("08 A3 (second routed NPC) dialogue", d == [D["a3_info"]], dlg=d, pos=pos(h))
    # door -> map B
    walk(h, "LEFT", 5); walk(h, "UP", 5); idle(h); h.step(90)
    h.shot(os.path.join(out, "09_mapB_arrival.png"))
    log("09 short entrance (16,9) on map $1A0 -> NEW map $1A1 (13,18)", h.r16(0x82) == 0x1A1 and pos(h) == (13, 18),
        map=f"{h.r16(0x82):03X}", pos=pos(h))
    bad = grid_ok(h, man["notes"]["maps"]["1A1"]["runtime_grid"])
    log("10 map $1A1 runtime grid == composed source (BG1 $161 + BG2 $162 from vanilla room art)", not bad, mismatches=bad[:5])
    walk(h, "UP", 2); walk(h, "LEFT", 1); talk(h, "LEFT"); d = dialogs(h, out, "11_B1_first")
    log("11 B1 dialogue sets VISITED_B ($14D) and NPC bit $6FA", d == [D["b1_first"]] and bit(h, VISITED_B) and bit(h, A2_VIS),
        dlg=d, pos=pos(h))
    talk(h, "LEFT"); d = dialogs(h, out, "11b_B1_again")
    log("11b B1 second state", d == [D["b1_again"]], dlg=d)
    walk(h, "RIGHT", 1); walk(h, "UP", 3); walk(h, "RIGHT", 6); walk(h, "DOWN", 5); idle(h); h.step(90)
    h.shot(os.path.join(out, "12_mapA_from_stairs.png"))
    log("12 long entrance (19,18) on map $1A1 -> map $1A0 hall (13,26)", h.r16(0x82) == 0x1A0 and pos(h) == (13, 26),
        map=f"{h.r16(0x82):03X}", pos=pos(h))
    log("12b A2 now visible on map $1A0 (NPC switch persisted across maps)", obj_visible(h, 0x12))
    walk(h, "RIGHT", 2); walk(h, "UP", 12); walk(h, "LEFT", 5); talk(h, "LEFT"); d = dialogs(h, out, "13_A1_after")
    log("13 A1 state-dependent dialogue after VISITED_B", d == [D["a1_after"]], dlg=d, pos=pos(h))
    walk(h, "RIGHT", 9); walk(h, "DOWN", 2); talk(h, "RIGHT"); d = dialogs(h, out, "14_A2")
    log("14 A2 dialogue", d == [D["a2_info"]], dlg=d, pos=pos(h))
    # door round trip via short entrances
    walk(h, "UP", 2); walk(h, "LEFT", 3); walk(h, "UP", 5); idle(h); h.step(60)
    ok1 = h.r16(0x82) == 0x1A1
    walk(h, "DOWN", 1); idle(h); h.step(60)
    log("15 short-entrance round trip A->B->A (door)", ok1 and h.r16(0x82) == 0x1A0 and pos(h) == (16, 12),
        map=f"{h.r16(0x82):03X}", pos=pos(h))
    walk(h, "DOWN", 17); idle(h); h.step(90); h.shot(os.path.join(out, "16_exit_narshe.png"))
    log("16 long entrance strip (15-16,29) -> map $013 (35,43)", h.r16(0x82) == 0x013 and pos(h) == (35, 43),
        map=f"{h.r16(0x82):03X}", pos=pos(h))
    walk(h, "LEFT", 1)
    d = choose(h, out, "17_qa_no", 2); idle(h); h.step(30)
    log("17 QA tile -> 'No (Save Point)' -> vanilla SavePoint, Save allowed", d[:1] == [D["qa4_prompt"]]
        and bit(h, LATCH) and bit(h, SAVE_OK) and pos(h) == (34, 43), dlg=d)
    R["before_save"] = {"VISITED_B": bit(h, VISITED_B), "A2": bit(h, A2_VIS), "map": f"{h.r16(0x82):03X}", "pos": list(pos(h))}
    menu_save(h, out, "18")
    dumps = dict(sram_dump(h))
    sel = [k for k, dd in dumps.items() if dd[0x1EA9 - 0x1600] == h.r8(0x1EA9) and dd[0x1F5F - 0x1600] == h.r8(0x1F5F)
           and (dd[0x1EA9 - 0x1600] >> 5) & 1]
    log("18 menu Save wrote slot 1 (SRAM has VISITED_B)", bool(sel))
    if sel:
        open(os.path.join(out, "sram_slot1.bin"), "wb").write(dumps[sel[-1]])
        json.dump({"block": sel[-1], "before": R["before_save"]}, open(os.path.join(out, "save_phase.json"), "w"))
    json.dump(R, open(os.path.join(out, "map_tech_save_phase.json"), "w"), indent=1)
    print("SAVE PHASE", "PASS" if R["pass"] else "FAIL")


def phase_load(rom, out):
    D, man = ids(rom)
    h = H(rom)
    sram = open(os.path.join(out, "sram_slot1.bin"), "rb").read()
    sp = json.load(open(os.path.join(out, "save_phase.json")))
    for i, v in enumerate(sram): h.gd.memory.assign(sp["block"] + i, "|u1", v)
    for t in range(1400):
        if t % 30 == 0 and t > 300: h.press("A" if t > 900 else "START", 4, 4)
        else: h.step(1)
        if h.r16(0x82) and h.evpc() == 0xCA0000 and t > 1000: break
    for t in range(1500):
        h.step(1)
        if t % 40 == 0: h.press("A", 4, 4)
        if h.r16(0x82) == 0x013 and h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and h.r8(0x1EA9) == sram[0x1EA9 - 0x1600]: break
    h.step(120); h.shot(os.path.join(out, "19_after_load.png"))
    st = {"VISITED_B": bit(h, VISITED_B), "A2": bit(h, A2_VIS), "map": f"{h.r16(0x82):03X}", "pos": list(pos(h))}
    log("19 new process -> Continue slot 1: map $013 QA tile, VISITED_B + $6FA restored", st == sp["before"], loaded=st)
    d = dialogs(h, out, "19b_standing", max_frames=300)
    log("19b no prompt loop after load", d == [], dlg=d)
    walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    d = choose(h, out, "20_qa_mapA", 0); idle(h); h.step(90)
    log("20 re-enter map $1A0 after load: A2 visible", h.r16(0x82) == 0x1A0 and obj_visible(h, 0x12), map=f"{h.r16(0x82):03X}")
    walk(h, "UP", 13); walk(h, "LEFT", 6); talk(h, "LEFT"); d = dialogs(h, out, "21_A1_after_load")
    log("21 A1 dialogue after load = VISITED_B state", d == [D["a1_after"]], dlg=d, pos=pos(h))
    walk(h, "RIGHT", 6); walk(h, "DOWN", 15); idle(h); h.step(60)
    log("21b south exit back to map $013", h.r16(0x82) == 0x013, pos=pos(h))
    # Annex regression via QA (vector-routed Vale/chest, relocated tables)
    walk(h, "LEFT", 1)
    if pos(h) != (35, 43): walk(h, "LEFT", 1); walk(h, "RIGHT", 1)
    walk(h, "LEFT", 1)
    d = choose(h, out, "22_qa_annex", 1); idle(h); h.step(90)
    log("22 QA 'Celes Annex' -> map $0C7 (16,27), Vale + chest visible", h.r16(0x82) == 0x0C7 and pos(h) == (16, 27)
        and obj_visible(h, 0x10) and obj_visible(h, 0x11), map=f"{h.r16(0x82):03X}", pos=pos(h))
    bad = grid_ok(h, man["notes"]["maps"]["0C7"]["runtime_grid"])
    log("22b Annex grid unchanged under v0.4 pipeline", not bad, mismatches=bad[:5])
    walk(h, "UP", 17); d = dialogs(h, out, "23_door"); idle(h)
    log("23 Annex sealed door (relocated trigger)", d == [D["door_sealed"]] and pos(h) == (16, 11), dlg=d)
    walk(h, "DOWN", 5); walk(h, "LEFT", 3); talk(h, "LEFT"); d = dialogs(h, out, "24_vale")
    log("24 Vale via NPC event vector (no CA-CD bridge)", d == [D["vale_first"]] and bit(h, 0x14A), dlg=d)
    walk(h, "RIGHT", 3); walk(h, "UP", 6)
    seen = []
    for t in range(400):
        h.step(1)
        if h.r8(0xBA):
            h.step(150); seen.append(f"{h.r16(0xD0):04X}"); h.press("A", 4, 4); break
    ok = battle_real(h, out, "25")
    d = dialogs(h, out, "25_after_battle"); idle(h); h.step(60)
    log("25 Annex battle (QA group $01) + return + BATTLE_DONE", seen == [D["battle_start"]] and ok and bit(h, 0x14B)
        and pos(h) == (16, 9), dlg=seen + d, pos=pos(h))
    for _ in range(4):
        if pos(h) == (16, 7): break
        walk(h, "UP", 1)
    p0 = item_count(h, 0xE9)
    talk(h, "UP"); d = dialogs(h, out, "26_reward")
    log("26 chest via NPC vector: +1 Potion, COMPLETE", d == [D["reward_get"]] and item_count(h, 0xE9) == p0 + 1 and bit(h, 0x14C),
        dlg=d)
    walk(h, "DOWN", 23); idle(h); h.step(60)
    log("27 Annex exit -> map $013 (35,43)", h.r16(0x82) == 0x013 and pos(h) == (35, 43), pos=pos(h))
    # vanilla opening event regression
    walk(h, "RIGHT", 3); walk(h, "UP", 5)
    seen, battle = [], False
    for t in range(9000):
        if h.r16(0x3BF4) != 0xFFFF and not battle:
            battle = True; h.step(120); h.shot(os.path.join(out, "28_vanilla_battle.png"))
        if h.r8(0xBA) and (not seen or seen[-1] != f"{h.r16(0xD0):04X}"):
            seen.append(f"{h.r16(0xD0):04X}")
        if t > 300 and h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and h.r16(0x3BF4) == 0xFFFF and (battle or t > 3000):
            break
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    idle(h); h.step(60); h.shot(os.path.join(out, "28_after_vanilla_event.png"))
    log("28 vanilla opening trigger (38,38) from relocated trigger table: dialogue + battle + control",
        battle and seen[:1] == ["000D"] and h.evpc() == 0xCA0000, dlg=seen[:6], map=f"{h.r16(0x82):03X}", pos=pos(h))
    json.dump(R, open(os.path.join(out, "map_tech_load_phase.json"), "w"), indent=1)
    print("LOAD PHASE", "PASS" if R["pass"] else "FAIL")


if __name__ == "__main__":
    ph, rom, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    (phase_save if ph == "save" else phase_load)(rom, out)
