#!/usr/bin/env python3
"""TECH v0.3 Claude-side EMULATOR regression suite (snes9x core via stable-retro).

NOT user runtime QA. Uses RAM pokes only to (a) teleport the opening-game
party to test locations, (b) set vanilla NPC-visibility bits for the vanilla
dialogue regression, and (c) set enemy HP to 1 so the low-level opening party
can finish the test battle. Everything else runs through normal game code.

usage: emu_celes_suite.py <celes_rom> <control_state> <outdir>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H

DIRS = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
R = {"steps": [], "pass": True}


def log(name, ok, **kw):
    R["steps"].append(dict(name=name, ok=bool(ok), **kw))
    if not ok:
        R["pass"] = False
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


def inject(h, pc24):
    lo, hi, bk = pc24 & 0xFF, (pc24 >> 8) & 0xFF, pc24 >> 16
    for a, v in ((0xE5, lo), (0xE6, hi), (0xE7, bk), (0x5F4, lo), (0x5F5, hi), (0x5F6, bk),
                 (0x594, 0), (0x595, 0), (0x596, 0xCA), (0x5C7, 1), (0xE8, 3), (0xE9, 0)):
        h.w8(a, v)
    y = h.r16(0x803)
    h.w8(0x87D + y, h.r8(0x87C + y)); h.w8(0x87C + y, (h.r8(0x87C + y) & 0xF0) | 4)


SCRIPT_RAM = int(os.environ.get("EMU_SCRIPT_RAM", "7FF000"), 16)


def run_script(h, data):
    for i, v in enumerate(data):
        h.gd.memory.assign(SCRIPT_RAM + i, '|u1', v)
    inject(h, SCRIPT_RAM)
    idle(h)


def idle(h, n=800):
    for t in range(n):
        h.step(1)
        if h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and t > 30:
            h.step(10)
            return True
    return False


def teleport(h, m, x, y, d="DOWN", z_upper=False):
    w = m | (DIRS[d] << 12) | (0x400 if z_upper else 0)
    run_script(h, [0x6A, w & 0xFF, w >> 8, x, y, 0x00, 0xFE])
    h.step(30)


def pos(h):
    return ((h.r8(0x867 + 3) | h.r8(0x867 + 4) << 8) // 16, (h.r8(0x867 + 6) | h.r8(0x867 + 7) << 8) // 16)


def walk(h, d, n):
    for _ in range(n):
        h.step(16, (d,)); h.step(2)
    h.step(8)


def bit(h, b):
    return (h.r8(0x1E80 + (b >> 3)) >> (b & 7)) & 1


def setbit(h, b):
    h.w8(0x1E80 + (b >> 3), h.r8(0x1E80 + (b >> 3)) | (1 << (b & 7)))


def item_count(h, item):
    for i in range(256):
        if h.r8(0x1869 + i) == item:
            return h.r8(0x1969 + i)
    return 0


def dialogs(h, out, tag, max_frames=900, choose_down=False):
    """Advance every dialogue box with A; returns list of dialogue IDs seen."""
    seen, last = [], None
    for t in range(max_frames):
        h.step(1)
        if t % 10 == 0:
            ba, d0 = h.r8(0xBA), h.r16(0xD0)
            if ba and (ba, d0) != last:
                h.step(150)
                p = os.path.join(out, f"{tag}_{len(seen)}_dlg{d0:04X}.png"); h.shot(p)
                seen.append(f"{d0:04X}"); last = (ba, d0)
                if choose_down:
                    h.press("DOWN", 4, 10)
                h.press("A", 4, 20)
            if h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and t > 40:
                break
    return seen


def talk(h, facing):
    """Face an adjacent object and press A until a dialogue opens (max 3 tries per phase).
    v0.7.1: the field checks talk targets on a 4-frame object-update cycle (DP $47); a fixed press pattern can
    miss every time for some frame phases (reproduced identically on v0.6.0 and v0.7.1 from one RAM state), so
    retry with a one-frame phase shift (up to 8 phases)."""
    for _phase in range(8):
        h.press(facing, 2, 8)
        for _ in range(3):
            h.press("A", 4, 4)
            for _ in range(40):
                h.step(1)
                if h.r8(0xBA):
                    return True
        h.step(1)
    return False


def obj_visible(h, obj):
    return bool(h.r8(0x867 + obj * 0x29) & 0x80)


def ram_grid_matches(h, expected_grid):
    h.gd.update_ram()
    mem = lambda a: h.gd.memory.extract(a, '|u1')
    bad = []
    for y, row in enumerate(expected_grid):
        for x, ch in enumerate(row):
            t = mem(0x7F0000 + y * 256 + x); p = mem(0x7E7600 + t)
            passable = p != 0xF7 and (p & 3) != 0
            if passable != (ch != "#"):
                bad.append((x, y, t, p))
    return bad


def battle_until_field(h, out, tag, max_frames=9000):
    """Mash A; keep enemies at 1 HP and party HP topped until the field event resumes."""
    won = False
    for t in range(max_frames):
        if t >= 25:                      # battle RAM initialised (~100 frames after event cmd $4D)
            for k in range(6):
                if h.r16(0x3BFC + 2 * k) not in (0, 1, 0xFFFF):
                    h.w8(0x3BFC + 2 * k, 1); h.w8(0x3BFD + 2 * k, 0)
            for k in range(4):
                mx = h.r16(0x3C1C + 2 * k)
                if mx and mx != 0xFFFF and h.r16(0x3BF4 + 2 * k) != mx:
                    h.w8(0x3BF4 + 2 * k, mx & 0xFF); h.w8(0x3BF5 + 2 * k, mx >> 8)
                if mx and mx != 0xFFFF:          # clear Death/Petrify/Zombie (status 1) and Stop/Sleep-type (status 2)
                    h.w8(0x3EE4 + 2 * k, h.r8(0x3EE4 + 2 * k) & 0x3D)
                    h.w8(0x3EE5 + 2 * k, h.r8(0x3EE5 + 2 * k) & 0x00)
                    st = (h.r8(0x3EE4 + 2 * k), h.r8(0x3EE5 + 2 * k))
        if t == 60:
            h.shot(os.path.join(out, f"{tag}_battle_in_progress.png"))
        if os.environ.get("SUITE_DEBUG") and t % 50 == 0:
            print("  battle", t, hex(h.r16(0x82)), hex(h.evpc()), [h.r16(0x3BF4 + 2 * k) for k in range(10)],
                  [hex(h.r8(0x3EE4 + 2 * k)) for k in range(4)], [hex(h.r8(0x3EE5 + 2 * k)) for k in range(4)], flush=True)
        in_battle = h.r16(0x3BF4) != 0xFFFF
        if in_battle and all(h.r16(0x3BFC + 2 * k) in (0, 0xFFFF) for k in range(6)):
            won = True
        if t > 100 and not in_battle and h.r16(0x82) == 0x0C7 and 0xF1005A <= h.evpc() <= 0xF10068:
            return True
        if won:
            h.step(4, ("A",)) if t % 40 == 0 else h.step(4)
        else:
            h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    return False


def main():
    rom, state, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out, exist_ok=True)
    manifest = json.load(open(rom.replace(".sfc", ".manifest.json")))
    grid = (manifest["notes"].get("walkability") or manifest["notes"]["maps"]["0C7"]["walkability"])["grid"]
    h = H(rom)
    h.em.set_state(open(state, "rb").read()); h.step(2)
    STARTED, BATTLE, COMPLETE, VALE, CHEST = 0x14A, 0x14B, 0x14C, 0x6F8, 0x6F9
    log("01 boot to first control (opening Narshe, vanilla dialogue via global hook)", h.evpc() == 0xCA0000)

    # 03 menu open/close
    h.press("X", 4, 60); h.shot(os.path.join(out, "03_menu.png")); h.press("B", 4, 60); idle(h)
    log("03 main menu open/close returns to field", h.evpc() == 0xCA0000 and h.r8(0xBA) == 0)

    # 14 vanilla NPC dialogue regression (South Figaro + Narshe, bits $303/$600 poked visible)
    setbit(h, 0x303); setbit(h, 0x600)
    van = []
    for m, x, y, expect in ((0x04B, 48, 44, 206), (0x014, 43, 34, 932), (0x014, 37, 15, 917)):
        ok = False
        for z in (False, True):
            teleport(h, m, x, y + 1, "UP", z_upper=z)
            h.press("UP", 2, 6); h.press("A", 4, 4)
            d = dialogs(h, out, f"14_vanilla_{m:03X}_{x}_{y}")
            if d:
                ok = int(d[0], 16) == expect
                break
        van.append({"map": f"{m:03X}", "npc": [x, y], "dlg": d, "expected": expect, "ok": ok})
    log("14 unrelated vanilla NPC dialogues through dialogue hook", all(v["ok"] for v in van), detail=van)

    # Falcon interior entry, choose "No" first
    teleport(h, 0x00C, 13, 47, "UP", z_upper=True)
    log("05a Falcon interior (map $00C) reached", h.r16(0x82) == 0x00C, pos=pos(h))
    walk(h, "UP", 1)
    d = dialogs(h, out, "05b_prompt_no", choose_down=True)
    log("05b entry prompt -> 'No' keeps player on Falcon", d == ["1001"] and h.r16(0x82) == 0x00C, dlg=d, pos=pos(h))
    walk(h, "DOWN", 1); walk(h, "UP", 1)
    d = dialogs(h, out, "05c_prompt_yes")
    idle(h); h.step(90)
    h.shot(os.path.join(out, "05d_annex_arrival.png"))
    log("05c entry prompt -> 'Yes' loads map $0C7 at (16,27)", h.r16(0x82) == 0x0C7 and pos(h) == (16, 27),
        dlg=d, map=f"{h.r16(0x82):03X}", pos=pos(h), z=h.r8(0xB2))
    bad = ram_grid_matches(h, grid)
    log("05e runtime BG1/tile-property grid == compiled walkability grid (32x32)", not bad, mismatches=bad[:5])
    log("05f NPC visibility bits set by entry event (Vale $6F8, chest $6F9)", bit(h, VALE) and bit(h, CHEST))
    log("05g Vale (obj $10) and chest (obj $11) visible", obj_visible(h, 0x10) and obj_visible(h, 0x11))

    # 06/07 door before Vale -> sealed + pushed back
    walk(h, "UP", 17)
    d = dialogs(h, out, "06_door_sealed")
    idle(h)
    log("07 door trigger before talking to Vale: sealed + pushed back", d == ["1006"] and pos(h) == (16, 11) and not bit(h, BATTLE),
        dlg=d, pos=pos(h))
    # wall bump probes
    p0 = pos(h); walk(h, "LEFT", 1); p1 = pos(h)
    log("05h wall collision probe (doorway sides impassable)", p0 == p1, before=p0, after=p1)

    # Vale talk x2
    walk(h, "DOWN", 5); walk(h, "LEFT", 3)
    talk(h, "LEFT")
    d1 = dialogs(h, out, "06_vale_first")
    log("06 Vale first talk: expansion dialogue + STARTED 0->1", d1 == ["1002"] and bit(h, STARTED), dlg=d1, pos=pos(h))
    talk(h, "LEFT")
    d2 = dialogs(h, out, "06_vale_again")
    log("07 Vale second talk: state-dependent follow-up", d2 == ["1003"], dlg=d2)

    # 08/09 battle
    walk(h, "RIGHT", 3); walk(h, "UP", 6)
    potions0 = item_count(h, 0xE9)
    seen = []
    for t in range(400):
        h.step(1)
        if h.r8(0xBA):
            h.step(150); h.shot(os.path.join(out, "08_battle_start.png")); seen.append(f"{h.r16(0xD0):04X}")
            h.press("A", 4, 4); break
    ok_b = battle_until_field(h, out, "08")
    d = dialogs(h, out, "09_after_battle")
    idle(h)
    log("08 battle trigger -> event battle group 40 starts", seen == ["1007"], dlg=seen)
    h.step(60)
    log("09 victory returns to $0C7, BATTLE_DONE set, party stepped off trigger",
        ok_b and h.r16(0x82) == 0x0C7 and bit(h, BATTLE) and d == ["1008"] and pos(h) == (16, 9),
        dlg=d, pos=pos(h), map=f"{h.r16(0x82):03X}")
    # no retrigger: step back onto trigger
    walk(h, "DOWN", 1); idle(h)
    log("09b re-entering trigger after victory does nothing (no loop)", h.r8(0xBA) == 0 and pos(h) == (16, 10), pos=pos(h))
    walk(h, "DOWN", 1); walk(h, "UP", 1)
    log("09c player can move freely off/onto the trigger", pos(h) == (16, 10), pos=pos(h))

    # 10 reward once
    walk(h, "UP", 2); h.step(30); h.shot(os.path.join(out, "10a_chest_before.png"))
    talk(h, "UP")
    d = dialogs(h, out, "10_reward")
    p1 = item_count(h, 0xE9)
    log("10 reward chest: +1 Potion, COMPLETE set, chest hidden",
        d == ["1009"] and p1 == potions0 + 1 and bit(h, COMPLETE) and not bit(h, CHEST) and not obj_visible(h, 0x11),
        dlg=d, potions_before=potions0, potions_after=p1)
    h.press("A", 4, 4); d = dialogs(h, out, "10b_reward_again", max_frames=200)
    walk(h, "UP", 1)
    log("10b repeated interaction: no dialogue, no duplicate, chest tile now walkable",
        d == [] and item_count(h, 0xE9) == p1 and pos(h) == (16, 6), pos=pos(h))

    # Vale done text
    walk(h, "DOWN", 10); walk(h, "LEFT", 3); talk(h, "LEFT")
    d = dialogs(h, out, "13_vale_done")
    log("13 Vale after completion shows final state text", d == ["1005"], dlg=d)

    # 11 exit
    walk(h, "RIGHT", 3); walk(h, "DOWN", 13); idle(h)
    h.step(90); h.shot(os.path.join(out, "11_exit_falcon.png"))
    log("11 exit (16,29) returns to Falcon $00C at (15,47) with control", h.r16(0x82) == 0x00C and pos(h) == (15, 47)
        and h.r8(0x87C + h.r16(0x803)) & 0x0F == 2, map=f"{h.r16(0x82):03X}", pos=pos(h))

    # 13 re-enter
    walk(h, "LEFT", 2); walk(h, "UP", 1)
    d = dialogs(h, out, "13_reenter_prompt"); idle(h); h.step(90)
    vis = (obj_visible(h, 0x10), obj_visible(h, 0x11))
    log("13 re-enter: map loads, Vale visible, chest stays gone", h.r16(0x82) == 0x0C7 and vis == (True, False), vis=vis)
    walk(h, "UP", 17); d = dialogs(h, out, "13_door_after", max_frames=200)
    log("13 door after completion: no battle, no text", d == [] and pos(h) == (16, 10), pos=pos(h))
    walk(h, "DOWN", 19); idle(h)
    log("13 second exit OK", h.r16(0x82) == 0x00C, pos=pos(h))

    # park on the WoB world map one tile south of the Narshe entrance (84,33) for the save test
    teleport(h, 0x000, 84, 34, "UP"); h.step(120)
    open(os.path.join(out, "after_suite.state"), "wb").write(h.em.get_state())
    R["final_bits"] = {"STARTED": bit(h, STARTED), "BATTLE_DONE": bit(h, BATTLE), "COMPLETE": bit(h, COMPLETE),
                       "VALE_VISIBLE": bit(h, VALE), "CHEST_VISIBLE": bit(h, CHEST), "TECH_TEST_0FF": bit(h, 0x0FF)}
    json.dump(R, open(os.path.join(out, "emu_suite_result.json"), "w"), indent=1)
    print("SUITE", "PASS" if R["pass"] else "FAIL")


if __name__ == "__main__":
    main()
