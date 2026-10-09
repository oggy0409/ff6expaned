#!/usr/bin/env python3
"""TECH v0.3.1 QA-ACCESS build - Claude-side EMULATOR check (snes9x via stable-retro).

NOT user runtime QA. No RAM pokes in this script: New Game -> walk -> QA tile ->
Annex -> real battle (no HP edits) -> reward -> exit -> vanilla SavePoint -> menu Save
-> (new process) Continue -> re-entry -> vanilla opening events.

usage:
  emu_qa_access.py save <qa_rom> <outdir>      # boot + full flow + save slot 1 + SRAM dump
  emu_qa_access.py load <qa_rom> <outdir>      # fresh process: load SRAM, continue, re-entry, regression
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
import emu_celes_suite as S
from emu_celes_suite import walk, idle, talk, pos, bit, item_count, obj_visible, ram_grid_matches

R = {"steps": [], "pass": True}
STARTED, BATTLE, COMPLETE, VALE, CHEST = 0x14A, 0x14B, 0x14C, 0x6F8, 0x6F9
LATCH, SAVE_OK = 0x1B5, 0x1BF


def log(name, ok, **kw):
    R["steps"].append(dict(name=name, ok=bool(ok), **kw))
    if not ok:
        R["pass"] = False
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


def dialogs(h, out, tag, max_frames=1500, choose_down=False):
    """Advance every dialogue page with A (DOWN first when choose_down: picks the 2nd option
    of any choice; harmless on plain pages). Returns the list of distinct dialogue IDs seen."""
    seen, last, t = [], None, 0
    while t < max_frames:
        h.step(1); t += 1
        if t % 10:
            continue
        ba, d0 = h.r8(0xBA), h.r16(0xD0)
        if ba:
            h.step(150); t += 150
            if d0 != last:
                h.shot(os.path.join(out, f"{tag}_{len(seen)}_dlg{d0:04X}.png"))
                seen.append(f"{d0:04X}"); last = d0
            if choose_down:
                h.press("DOWN", 4, 10)
            h.press("A", 4, 20); t += 38
        elif h.evpc() == 0xCA0000 and t > 40:
            break
    return seen


def boot_new_game(h, out):
    idle_n = 0; shots = 0; last = None; seen = []
    for t in range(60000):
        if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
        else: h.step(1)
        if t % 10 == 0:
            ba, d0 = h.r8(0xBA), h.r16(0xD0)
            if ba and d0 != last and d0:
                seen.append(f"{d0:04X}"); last = d0
                if shots < 2:
                    for _ in range(240):
                        h.step(1)
                        if h.em.get_screen().mean() > 12: break
                    h.step(60); h.shot(os.path.join(out, f"01_opening_dlg{d0:04X}.png")); shots += 1
            idle_n = idle_n + 1 if h.evpc() == 0xCA0000 else 0
            if idle_n >= 30: break
    return seen


def battle_real(h, out, tag, max_frames=12000):
    """Mash A only (no RAM edits) until the v0.3 post-battle event resumes on $0C7."""
    entered = False
    for t in range(max_frames):
        in_battle = h.r16(0x3BF4) != 0xFFFF
        if in_battle and not entered:
            entered = True
            h.step(120); h.shot(os.path.join(out, f"{tag}_battle.png"))
            R["battle_monster_hp_at_start"] = [h.r16(0x3BFC + 2 * k) for k in range(6)]
        if entered and not in_battle and h.r16(0x82) == 0x0C7 and 0xF1005A <= h.evpc() <= 0xF10068:
            return True
        if h.r16(0x82) != 0x0C7 and h.r16(0x82) != 0xFFFF and not in_battle and entered and t > 2000:
            return False
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    return False


def menu_save(h, out, tag):
    h.press("X", 4, 60); h.shot(os.path.join(out, f"{tag}_menu.png"))
    for _ in range(6): h.press("DOWN", 3, 8)
    h.press("A", 4, 60); h.shot(os.path.join(out, f"{tag}_save_screen.png"))
    h.press("A", 4, 120); h.shot(os.path.join(out, f"{tag}_saved.png"))
    h.press("B", 4, 30); h.press("B", 4, 30); h.press("B", 4, 60); idle(h)


def sram_dump(h):
    h.gd.update_ram()
    for k, v in h.gd.memory.blocks.items():
        if k != 0x7E0000 and len(v) == 0x2000:
            yield k, bytes(h.gd.memory.extract(k + i, "|u1") for i in range(0x2000))


def phase_save(rom, out):
    h = H(rom)
    seen = boot_new_game(h, out)
    log("01 New Game -> first control on map $013 (38,49); vanilla opening dialogue via hook",
        h.r16(0x82) == 0x013 and pos(h) == (38, 49) and len(seen) >= 2, opening_dlg=seen[:6])
    h.press("X", 4, 60); h.shot(os.path.join(out, "02_menu_not_on_tile.png")); h.press("B", 4, 60); idle(h)
    log("02 main menu open/close", h.evpc() == 0xCA0000 and h.r8(0xBA) == 0)
    pot0 = item_count(h, 0xE9)

    walk(h, "UP", 6); walk(h, "LEFT", 3)
    log("03 walk to tile right of QA tile (35,43)", pos(h) == (35, 43), pos=pos(h))
    walk(h, "LEFT", 1)
    d = dialogs(h, out, "04_qa_prompt_no", choose_down=True)   # QA prompt -> No; vanilla save info -> No
    idle(h); h.step(60)
    log("04 QA prompt ($100B) -> No -> vanilla SavePoint (info prompt DLG $0010), stays on map $013",
        d[:1] == ["100B"] and h.r16(0x82) == 0x013 and pos(h) == (34, 43) and bit(h, LATCH) and bit(h, SAVE_OK),
        dlg=d, pos=pos(h), latch=bit(h, LATCH), save_ok=bit(h, SAVE_OK))
    d = dialogs(h, out, "04b_standing", max_frames=300)
    log("04b standing on the QA tile: prompt does not re-open (latch)", d == [] and h.r8(0xBA) == 0, dlg=d)
    h.press("X", 4, 60); h.shot(os.path.join(out, "04c_menu_on_qa_tile.png")); h.press("B", 4, 60); idle(h)

    walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    log("05a step off/on clears latch and re-fires", True)
    d = dialogs(h, out, "05_qa_prompt_yes")
    idle(h); h.step(90); h.shot(os.path.join(out, "05_annex_arrival.png"))
    log("05 QA prompt -> Yes -> map $0C7 at (16,27) (same v0.3 entry branch)",
        d == ["100B"] and h.r16(0x82) == 0x0C7 and pos(h) == (16, 27), dlg=d, map=f"{h.r16(0x82):03X}", pos=pos(h))
    manifest = json.load(open(rom.replace(".sfc", ".manifest.json")))
    bad = ram_grid_matches(h, manifest["notes"]["walkability"]["grid"])
    log("06 runtime collision grid == compiled v0.3 grid", not bad, mismatches=bad[:5])
    log("06b Vale + chest visible (bits $6F8/$6F9 set by v0.3 entry branch)",
        bit(h, VALE) and bit(h, CHEST) and obj_visible(h, 0x10) and obj_visible(h, 0x11))

    walk(h, "UP", 17); d = dialogs(h, out, "07_door_sealed"); idle(h)
    log("07 sealed door before Vale ($1006) + pushed back", d == ["1006"] and pos(h) == (16, 11) and not bit(h, BATTLE),
        dlg=d, pos=pos(h))
    walk(h, "DOWN", 5); walk(h, "LEFT", 3); talk(h, "LEFT")
    d1 = dialogs(h, out, "08_vale_first")
    log("08 Vale first ($1002) + STARTED", d1 == ["1002"] and bit(h, STARTED), dlg=d1)
    talk(h, "LEFT"); d2 = dialogs(h, out, "08_vale_second")
    log("08b Vale second ($1003)", d2 == ["1003"], dlg=d2)

    walk(h, "RIGHT", 3); walk(h, "UP", 6)
    seen = []
    for t in range(400):
        h.step(1)
        if h.r8(0xBA):
            h.step(150); h.shot(os.path.join(out, "09_battle_msg.png")); seen.append(f"{h.r16(0xD0):04X}")
            h.press("A", 4, 4); break
    ok = battle_real(h, out, "09")
    d = dialogs(h, out, "09_after_battle"); idle(h); h.step(60)
    log("09 battle ($1007, QA group $01) won with no RAM edits; returns to $0C7, BATTLE_DONE, stepped up",
        seen == ["1007"] and ok and h.r16(0x82) == 0x0C7 and bit(h, BATTLE) and d == ["1008"] and pos(h) == (16, 9),
        dlg=seen + d, pos=pos(h), monsters_hp=R.get("battle_monster_hp_at_start"))
    walk(h, "DOWN", 1); idle(h)
    log("09b no battle loop on re-entering trigger", h.r8(0xBA) == 0 and pos(h) == (16, 10), pos=pos(h))

    for _ in range(4):
        if pos(h) == (16, 7): break
        walk(h, "UP", 1)
    talk(h, "UP"); d = dialogs(h, out, "10_reward")
    p1 = item_count(h, 0xE9)
    log("10 reward: +1 Potion, COMPLETE, chest hidden", d == ["1009"] and p1 == pot0 + 1 and bit(h, COMPLETE)
        and not bit(h, CHEST) and not obj_visible(h, 0x11), dlg=d, potions=[pot0, p1])
    h.press("A", 4, 4); d = dialogs(h, out, "10b_again", max_frames=200); walk(h, "UP", 1)
    log("10b reward is one-time", d == [] and item_count(h, 0xE9) == p1 and pos(h) == (16, 6), pos=pos(h))
    walk(h, "DOWN", 10); walk(h, "LEFT", 3); talk(h, "LEFT"); d = dialogs(h, out, "11_vale_done")
    log("11 Vale COMPLETE text ($1005)", d == ["1005"], dlg=d)

    walk(h, "RIGHT", 3); walk(h, "DOWN", 13); idle(h); h.step(90)
    h.shot(os.path.join(out, "12_qa_exit_narshe.png"))
    log("12 QA exit -> map $013 (35,43) with control", h.r16(0x82) == 0x013 and pos(h) == (35, 43)
        and h.r8(0xBA) == 0 and h.evpc() == 0xCA0000, map=f"{h.r16(0x82):03X}", pos=pos(h))

    walk(h, "LEFT", 1)
    d = dialogs(h, out, "13_qa_prompt_no_save", choose_down=True); idle(h); h.step(30)
    log("13 QA tile -> No -> SavePoint (no info prompt 2nd time), Save allowed",
        d == ["100B"] and bit(h, LATCH) and bit(h, SAVE_OK), dlg=d)
    R["ram_before_save"] = {"STARTED": bit(h, STARTED), "BATTLE_DONE": bit(h, BATTLE), "COMPLETE": bit(h, COMPLETE),
                            "VALE": bit(h, VALE), "CHEST": bit(h, CHEST), "potions": item_count(h, 0xE9),
                            "map": f"{h.r16(0x82):03X}", "pos": pos(h)}
    menu_save(h, out, "14")
    dumps = dict(sram_dump(h))
    sel = [k for k, dd in dumps.items() if dd[0x08A9] == h.r8(0x1EA9) and dd[0x095F] == h.r8(0x1F5F) and (dd[0x08A9] >> 4) & 1]
    log("14 menu Save on the QA tile wrote slot 1 (SRAM has COMPLETE bit)", bool(sel), blocks=[hex(k) for k in sel])
    if sel:
        open(os.path.join(out, "sram_slot1.bin"), "wb").write(dumps[sel[-1]])
        json.dump({"block": sel[-1], "ram_before_save": R["ram_before_save"]},
                  open(os.path.join(out, "save_phase.json"), "w"), indent=1)
    json.dump(R, open(os.path.join(out, "qa_save_phase_result.json"), "w"), indent=1)
    print("SAVE PHASE", "PASS" if R["pass"] else "FAIL")


def phase_load(rom, out):
    h = H(rom)
    sram = open(os.path.join(out, "sram_slot1.bin"), "rb").read()
    sp = json.load(open(os.path.join(out, "save_phase.json")))
    k = sp["block"]; before = sp["ram_before_save"]
    for i, v in enumerate(sram): h.gd.memory.assign(k + i, "|u1", v)
    for t in range(1400):
        if t % 30 == 0 and t > 300: h.press("A" if t > 900 else "START", 4, 4)
        else: h.step(1)
        if h.r16(0x82) and h.evpc() == 0xCA0000 and t > 1000: break
    for t in range(1500):
        h.step(1)
        if t % 40 == 0: h.press("A", 4, 4)
        if h.r8(0x1EA9) == sram[0x08A9] and h.r16(0x82) == 0x013 and h.evpc() == 0xCA0000 and h.r8(0xBA) == 0: break
    h.step(120); h.shot(os.path.join(out, "15_after_load.png"))
    st = {"STARTED": bit(h, STARTED), "BATTLE_DONE": bit(h, BATTLE), "COMPLETE": bit(h, COMPLETE),
          "VALE": bit(h, VALE), "CHEST": bit(h, CHEST), "potions": item_count(h, 0xE9),
          "map": f"{h.r16(0x82):03X}", "pos": pos(h)}
    log("15 reset/new process -> Continue slot 1 -> map $013 QA tile, flags + Potion restored",
        all(st[x] == before[x] for x in ("STARTED", "BATTLE_DONE", "COMPLETE", "VALE", "CHEST", "potions", "map"))
        and tuple(st["pos"]) == tuple(before["pos"]), loaded=st, saved=before)
    d = dialogs(h, out, "15b_standing", max_frames=300)
    log("15b no prompt loop after load while standing on the QA tile", d == [], dlg=d)

    walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    d = dialogs(h, out, "16_reenter"); idle(h); h.step(90)
    log("16 re-entry after load: map $0C7, Vale visible, chest gone", d == ["100B"] and h.r16(0x82) == 0x0C7
        and obj_visible(h, 0x10) and not obj_visible(h, 0x11), dlg=d, map=f"{h.r16(0x82):03X}")
    walk(h, "UP", 11); walk(h, "LEFT", 3); talk(h, "LEFT"); d = dialogs(h, out, "16b_vale")
    log("16b Vale shows COMPLETE text after load", d == ["1005"], dlg=d)
    walk(h, "RIGHT", 3); walk(h, "UP", 6); d = dialogs(h, out, "16c_door", max_frames=200)
    log("16c door inert after load, Potion count unchanged", d == [] and pos(h) == (16, 10)
        and item_count(h, 0xE9) == before["potions"], dlg=d, pos=pos(h))
    walk(h, "DOWN", 19); idle(h); h.step(60)
    log("16d exit back to map $013 (35,43)", h.r16(0x82) == 0x013 and pos(h) == (35, 43), pos=pos(h))

    # 17 vanilla opening flow regression: continue north along the scripted path
    walk(h, "RIGHT", 3)
    walk(h, "UP", 5)                       # (38,43) -> (38,38): vanilla trigger
    seen, battle = [], False
    for t in range(9000):
        if h.r16(0x3BF4) != 0xFFFF and not battle:
            battle = True; h.step(120); h.shot(os.path.join(out, "17_vanilla_battle.png"))
        if h.r8(0xBA) and (not seen or seen[-1] != f"{h.r16(0xD0):04X}"):
            seen.append(f"{h.r16(0xD0):04X}")
            if len(seen) <= 2: h.step(150); h.shot(os.path.join(out, f"17_vanilla_dlg_{seen[-1]}.png"))
        if t > 300 and h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and h.r16(0x3BF4) == 0xFFFF and (battle or t > 3000):
            break
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    idle(h); h.step(60); h.shot(os.path.join(out, "17_after_vanilla_event.png"))
    log("17 vanilla opening event after QA: vanilla dialogue + vanilla battle, field control returns",
        battle and len(seen) >= 1 and h.evpc() == 0xCA0000 and h.r16(0x82) != 0xFFFF,
        dlg=seen[:8], battle=battle, map=f"{h.r16(0x82):03X}", pos=pos(h))
    json.dump(R, open(os.path.join(out, "qa_load_phase_result.json"), "w"), indent=1)
    print("LOAD PHASE", "PASS" if R["pass"] else "FAIL")


if __name__ == "__main__":
    phase, rom, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    (phase_save if phase == "save" else phase_load)(rom, out)
