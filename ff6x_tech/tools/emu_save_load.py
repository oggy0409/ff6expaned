#!/usr/bin/env python3
"""Save/reset/load persistence check (Claude emulator side).
phase 'save': from a state on the world map, save to slot 1 via the menu and dump SRAM.
phase 'load': fresh emulator process, write the dumped SRAM, boot, Continue -> slot 1,
              then report project bits from the loaded game."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
BLOCK = None

def sram_block(h):
    h.gd.update_ram()
    for k, v in h.gd.memory.blocks.items():
        if k not in (0x7E0000,) and len(v) == 0x2000:
            yield k

def bits(h):
    b = lambda n: (h.r8(0x1E80 + (n >> 3)) >> (n & 7)) & 1
    return {"STARTED_14A": b(0x14A), "BATTLE_DONE_14B": b(0x14B), "COMPLETE_14C": b(0x14C),
            "VALE_VISIBLE_6F8": b(0x6F8), "CHEST_VISIBLE_6F9": b(0x6F9), "TECH_TEST_0FF": b(0x0FF)}

def potions(h):
    for i in range(256):
        if h.r8(0x1869 + i) == 0xE9:
            return h.r8(0x1969 + i)
    return 0

if __name__ == "__main__":
    phase, rom, out = sys.argv[1], sys.argv[2], sys.argv[3]
    h = H(rom)
    if phase == "save":
        h.em.set_state(open(sys.argv[4], "rb").read()); h.step(120)
        before = bits(h); pot = potions(h)
        h.press("X", 4, 60)
        for _ in range(6): h.press("DOWN", 3, 8)
        h.press("A", 4, 60); h.press("A", 4, 120)
        h.shot(os.path.join(out, "12_saved_slot.png"))
        h.press("B", 4, 30); h.press("B", 4, 30); h.press("B", 4, 60)
        dumps = {}
        for k in sram_block(h):
            data = bytes(h.gd.memory.extract(k + i, "|u1") for i in range(0x2000))
            dumps[k] = data
        # identify SRAM: slot 1 copy of $1600.. has event bytes at +$08A9 / +$0927
        sel = [k for k, d in dumps.items() if d[0x08A9] == h.r8(0x1EA9) and d[0x0927] == h.r8(0x1F27) and d[0x1FF0 if False else 0] is not None]
        k = sel[-1]
        open(os.path.join(out, "sram_slot1.bin"), "wb").write(dumps[k])
        json.dump({"block": k, "bits_in_ram_before_save": before, "potions": pot,
                   "sram_event_byte_1EA9": dumps[k][0x08A9], "sram_npc_byte_1F5F": dumps[k][0x095F]},
                  open(os.path.join(out, "save_phase.json"), "w"), indent=1)
        print("saved", k, before)
    else:
        sram = open(os.path.join(out, "sram_slot1.bin"), "rb").read()
        k = json.load(open(os.path.join(out, "save_phase.json")))["block"]
        for i, v in enumerate(sram): h.gd.memory.assign(k + i, "|u1", v)
        for t in range(1400):              # title -> menu
            if t % 30 == 0 and t > 300: h.press("A" if t > 900 else "START", 4, 4)
            else: h.step(1)
            if t == 1100: h.shot(os.path.join(out, "12_title_continue.png"))
            if h.r16(0x82) and h.evpc() == 0xCA0000 and t > 1000: break
        for t in range(1200):
            h.step(1)
            if t % 40 == 0: h.press("A", 4, 4)
            if h.r8(0x1EA9) == sram[0x08A9] and h.r16(0x82) == 0: break
        h.step(120); h.shot(os.path.join(out, "12_after_load.png"))
        res = {"map_after_load": f"{h.r16(0x82):03X}", "bits_after_load": bits(h), "potions_after_load": potions(h)}
        # post-load: re-enter the Annex and re-talk
        import emu_celes_suite as S
        S.walk(h, "UP", 1)                      # world map (84,34) -> Narshe entrance (84,33)
        for t in range(600):
            h.step(1)
            if h.r16(0x82) == 0x014 and h.evpc() == 0xCA0000 and t > 120: break
        h.step(60); res["field_after_load"] = f"{h.r16(0x82):03X}"
        S.teleport(h, 0x00C, 13, 47, "UP", z_upper=True); h.step(60)
        S.walk(h, "UP", 1); d = S.dialogs(h, out, "12_postload_prompt"); S.idle(h); h.step(90)
        res["postload_map"] = f"{h.r16(0x82):03X}"
        res["postload_vale_visible"] = S.obj_visible(h, 0x10); res["postload_chest_visible"] = S.obj_visible(h, 0x11)
        S.walk(h, "UP", 11); S.walk(h, "LEFT", 3); S.talk(h, "LEFT")
        res["postload_vale_dlg"] = S.dialogs(h, out, "12_postload_vale")
        S.walk(h, "RIGHT", 3); S.walk(h, "UP", 6); res["postload_door_dlg"] = S.dialogs(h, out, "12_postload_door", max_frames=200)
        res["postload_potions"] = potions(h)
        # 04 vanilla random encounter on the WoB world map + return to world-map control
        S.teleport(h, 0x000, 84, 34, "UP"); h.step(120)
        h.w8(0x11E0, 0xFF); h.w8(0x11E1, 0xFF)
        got = False
        for k in range(80):
            S.walk(h, "DOWN" if k % 2 == 0 else "UP", 2)
            if h.r16(0x11E0) != 0xFFFF:
                got = True; break
        res["random_battle_index"] = f"{h.r16(0x11E0):04X}" if got else None
        if got:
            for t in range(900):
                if t == 150: h.shot(os.path.join(out, "04_random_battle.png"))
                if t % 10 == 0:
                    for kk in range(4):
                        mx = h.r16(0x3C1C + 2 * kk)
                        if mx and mx != 0xFFFF: h.w8(0x3BF4 + 2 * kk, mx & 0xFF); h.w8(0x3BF5 + 2 * kk, mx >> 8)
                h.step(4, ("A",)) if t % 2 == 0 else h.step(4)
            h.step(200)
            for k in range(8):
                S.walk(h, "UP", 1); h.step(30)
                if h.r16(0x82) == 0x014: break
            h.step(60); h.shot(os.path.join(out, "04_after_battle_narshe.png"))
        res["after_random_battle_entered_narshe"] = h.r16(0x82) == 0x014
        res["pass"] = (res["after_random_battle_entered_narshe"] and res["bits_after_load"]["COMPLETE_14C"] == 1 and res["potions_after_load"] == 1 and
                       res["postload_map"] == "0C7" and res["postload_vale_visible"] and not res["postload_chest_visible"]
                       and res["postload_vale_dlg"] == ["1005"] and res["postload_door_dlg"] == [] and res["postload_potions"] == 1)
        json.dump(res, open(os.path.join(out, "load_phase.json"), "w"), indent=1)
        print(res)
