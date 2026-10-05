#!/usr/bin/env python3
"""Claude-side EMULATOR SMOKE TEST (snes9x core via stable-retro).
NOT a substitute for user runtime QA. Uses RAM pokes to teleport, so it only
proves engine paths, not normal game progression.

usage: emu_smoke.py <rom> <outdir> [--evtest]
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H

def inject(h, pc24):
    lo, hi, bk = pc24 & 0xFF, (pc24 >> 8) & 0xFF, pc24 >> 16
    for a, v in ((0xE5, lo), (0xE6, hi), (0xE7, bk), (0x5F4, lo), (0x5F5, hi), (0x5F6, bk),
                 (0x594, 0), (0x595, 0), (0x596, 0xCA), (0x5C7, 1), (0xE8, 3), (0xE9, 0)):
        h.w8(a, v)
    y = h.r16(0x803)
    h.w8(0x87D + y, h.r8(0x87C + y)); h.w8(0x87C + y, (h.r8(0x87C + y) & 0xF0) | 4)

def wait_idle(h, n=400):
    for t in range(n):
        h.step(1)
        if h.evpc() == 0xCA0000 and t > 100: return True
    return False

def run_dialogs(h, out, tag, max_frames=1500):
    shots, last = [], None
    for t in range(max_frames):
        h.step(1)
        if t % 15 == 0:
            ba, d0 = h.r8(0xBA), h.r16(0xD0)
            if ba and (ba, d0) != last:
                h.step(90); p = os.path.join(out, f"{tag}_{len(shots)}_dlg{d0:04X}.png"); h.shot(p)
                shots.append({"dlg": f"{d0:04X}", "bank": f"{h.r8(0xCB):02X}", "png": os.path.basename(p)}); last = (ba, d0)
                h.press('A', 4, 20)
            if h.evpc() == 0xCA0000 and t > 60: break
    return shots

def pos(h): return ((h.r8(0x867+3) | h.r8(0x867+4) << 8) // 16, (h.r8(0x867+6) | h.r8(0x867+7) << 8) // 16)

def main():
    rom, out = sys.argv[1], sys.argv[2]; ev = "--evtest" in sys.argv
    os.makedirs(out, exist_ok=True)
    h = H(rom); res = {"rom": os.path.basename(rom)}
    idle = 0
    for t in range(60000):                       # boot -> title -> New Game -> first control
        if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
        else: h.step(1)
        if t % 10 == 0:
            idle = idle + 1 if h.evpc() == 0xCA0000 else 0
            if idle >= 30: break
    res["first_control_frame"] = h.f; h.shot(os.path.join(out, "00_first_control.png"))
    res["boot_to_control"] = idle >= 30
    if ev:
        bit = lambda: (h.r8(0x1E9F) >> 7) & 1
        res["bit255_before"] = bit()
        # teleport to Figaro Castle map $037 at (43,21) facing RIGHT, Z_UPPER
        w = 0x37 | (1 << 12) | 0x0400
        for i, v in enumerate([0x6A, w & 0xFF, w >> 8, 43, 21, 0x00, 0xFE]):
            h.gd.memory.assign(0x7FF000 + i, '|u1', v)
        inject(h, 0x7FF000); wait_idle(h); h.step(40)
        res["map"] = f"{h.r16(0x82):03X}"
        npc = 0x867 + 0x19 * 0x29
        res["npc19_event_ptr_runtime"] = f"{(h.r8(npc+0x22) | h.r8(npc+0x23) << 8 | h.r8(npc+0x24) << 16) + 0xCA0000:06X}"
        h.press('RIGHT', 2, 10); h.press('A', 4, 4)
        res["talk1"] = run_dialogs(h, out, "10_talk1"); res["bit255_after_talk1"] = bit()
        h.step(30); h.press('RIGHT', 2, 10); h.press('A', 4, 4)
        res["talk2"] = run_dialogs(h, out, "20_talk2"); res["bit255_after_talk2"] = bit()
        p0 = pos(h); h.step(24, ('UP',)); h.step(10); p1 = pos(h)
        res["player_moves_after_event"] = p0 != p1
        # out-of-range ID via WRAM test script: dlg $1FFF ; return
        h.step(24, ('DOWN',)); h.step(10)
        for i, v in enumerate([0x4B, 0xFF, 0x1F, 0xFE]): h.gd.memory.assign(0x7FF000 + i, '|u1', v)
        inject(h, 0x7FF000); res["out_of_range"] = run_dialogs(h, out, "30_oor")
        res["returned_to_idle"] = h.evpc() == 0xCA0000
    json.dump(res, open(os.path.join(out, "emu_smoke_result.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    main()
