#!/usr/bin/env python3
"""TECH v0.7.1 emulator checks (stable-retro / snes9x): extended item engine.

Boots the QA ROM to the first field control (New Game), then injects event scripts into unused WRAM
($7E:6C00, field-ram.txt "$7E6C00-$7E71FF -") through the event engine's own call mechanism and checks
the saved-RAM state. Writes <out>/ITEM_ENGINE_REPORT.json.

usage: emu_item_tech.py <qa.sfc> <outdir> [<vanilla_rev1.sfc>]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H

SCRIPT = 0x6C00
XBITS, XSIG = 0x1CF8, 0x1D24


class T(H):
    def wbytes(self, a, data):
        for i, b in enumerate(data):
            self.w8(a + i, b)

    def rbytes(self, a, n):
        return bytes(self.r8(a + i) for i in range(n))

    def idle(self):
        return self.evpc() == 0xCA0000 and self.r16(0xE8) == 0

    def run_event(self, data, frames=240):
        """Call `data` (event bytes, auto-terminated with $FE) from the idle field state."""
        data = bytes(data) + b"\xFE"
        self.wbytes(SCRIPT, data)
        return self.call_event(0x7E0000 | SCRIPT, frames)

    def call_event(self, addr, frames=240):
        """Call the event script at 24-bit `addr` (as EventCmd_b2 would) from the idle field state."""
        for _ in range(2400):
            if self.idle():
                break
            self.step(1)
        assert self.idle(), "event engine not idle"
        SCR = addr & 0xFFFF
        x = self.r16(0xE8)
        # mimic EventCmd_b2 (call) issued at CA:0000
        self.w8(0x0594 + x, 0x00); self.w8(0x0595 + x, 0x00); self.w8(0x0596 + x, 0xCA)
        self.w8(0x05F4 + x, SCR & 0xFF); self.w8(0x05F5 + x, SCR >> 8); self.w8(0x05F6 + x, addr >> 16)
        x += 3
        self.w8(0xE8, x & 0xFF); self.w8(0xE9, x >> 8)
        self.w8(0x05C4 + x, 1)
        self.w8(0xE5, SCR & 0xFF); self.w8(0xE6, SCR >> 8); self.w8(0xE7, addr >> 16)
        for _ in range(frames):
            self.step(1)
            if self.idle():
                break
        self.step(4)
        return self.idle()

    def bit(self, n):
        return (self.r8(XBITS + (n >> 3)) >> (n & 7)) & 1

    def inv(self):
        out = []
        for s in range(256):
            i = self.r8(0x1869 + s)
            if i != 0xFF:
                out.append((s, (self.bit(s) << 8) | i, self.r8(0x1969 + s)))
        return out

    def ext_inv(self):
        return [(s, i, q) for s, i, q in self.inv() if i >= 0x100]

    def eq(self, rec):
        return [(self.bit(256 + rec * 6 + k) << 8) | self.r8(0x161F + rec * 37 + k) for k in range(6)]


def ev_give(i): return [0x66, i & 0xFF, i >> 8]
def ev_take(i): return [0x67, i & 0xFF, i >> 8]
def ev_has(i, sw): return [0x68, i & 0xFF, i >> 8, sw & 0xFF, sw >> 8]


def main(rom, out, vanilla=None):
    os.makedirs(out, exist_ok=True)
    rep = {"rom": os.path.basename(rom), "checks": []}

    def check(name, ok, detail=None):
        rep["checks"].append({"check": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name, "" if detail is None else detail)

    h = T(rom)
    # ---- boot to first control (New Game) ----------------------------------------------------
    idle = 0
    for t in range(60000):
        if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
        else: h.step(1)
        if t % 10 == 0:
            idle = idle + 1 if h.evpc() == 0xCA0000 else 0
            if idle >= 30: break
    for _ in range(120): h.step(1)
    st0 = h.em.get_state()
    check("A0 New Game: signature written", h.rbytes(XSIG, 4) == bytes([0x58, 0x49, 0x01, 0xFE]), h.rbytes(XSIG, 4).hex())
    check("A0 New Game: extended metadata zero", h.rbytes(XBITS, 44) == bytes(44))
    van_inv0 = [(s, i, q) for s, i, q in h.inv()]
    rep["new_game_inventory"] = [(s, f"{i:03X}", q) for s, i, q in van_inv0]

    # ---- A: give the three QA items --------------------------------------------------------
    h.run_event(ev_give(0x13D) + ev_give(0x13E) + ev_give(0x13F))
    ext = h.ext_inv()
    check("A1 GIVE_EXT_ITEM x3 -> 3 extended slots", sorted(i for _, i, _ in ext) == [0x13D, 0x13E, 0x13F], [(s, f"{i:03X}", q) for s, i, q in ext])
    h.run_event(ev_give(0x13D))
    q = [q for s, i, q in h.ext_inv() if i == 0x13D]
    check("A2 second GIVE stacks quantity", q == [2], q)
    # vanilla alias: Chocobo Brsh ($3D) must get its own slot, never stack onto $13D
    h.run_event([0x80, 0x3D])
    inv = h.inv()
    v3d = [(s, f"{i:03X}", qq) for s, i, qq in inv if i == 0x03D]
    e3d = [(s, f"{i:03X}", qq) for s, i, qq in inv if i == 0x13D]
    check("M1 vanilla give $3D does not merge into $13D", len(v3d) == 1 and v3d[0][2] == 1 and e3d[0][2] == 2, {"van": v3d, "ext": e3d})
    # vanilla take $81 $3D removes the vanilla brush only
    h.run_event([0x81, 0x3D])
    inv = h.inv()
    check("M2 vanilla take $3D leaves $13D intact", not [1 for s, i, qq in inv if i == 0x03D] and [qq for s, i, qq in inv if i == 0x13D] == [2])
    # ---- K: TAKE via extended API ---------------------------------------------------------------
    h.run_event(ev_take(0x13D))
    check("K1 TAKE_EXT_ITEM decrements", [qq for s, i, qq in h.inv() if i == 0x13D] == [1])
    h.run_event(ev_take(0x13D))
    slots = [s for s, i, qq in h.inv() if i == 0x13D]
    check("K2 TAKE_EXT_ITEM last copy empties slot and clears bit", slots == [] and all(h.bit(s) == 0 or h.r8(0x1869 + s) != 0xFF for s in range(256)))
    h.run_event(ev_give(0x13D))
    # ---- HAS ---------------------------------------------------------------------------------------
    SW = 0x6F0          # scratch switch for the injected test only (state restored afterwards)
    old = h.r8(0x1E80 + (SW >> 3))
    h.run_event(ev_has(0x13E, SW))
    has1 = (h.r8(0x1E80 + (SW >> 3)) >> (SW & 7)) & 1
    h.run_event(ev_take(0x13E) + ev_has(0x13E, SW))
    has0 = (h.r8(0x1E80 + (SW >> 3)) >> (SW & 7)) & 1
    h.w8(0x1E80 + (SW >> 3), old)
    check("HAS_EXT_ITEM sets / clears the switch", has1 == 1 and has0 == 0, (has1, has0))
    h.run_event(ev_give(0x13E))
    # undefined extended id: ignored
    before = h.inv()
    h.run_event(ev_give(0x13C) + ev_give(0x140) + ev_give(0x03D | 0x200))
    check("undefined / out-of-bank ids are ignored", h.inv() == before)
    rep["after_give"] = [(s, f"{i:03X}", qq) for s, i, qq in h.ext_inv()]
    json.dump(rep, open(os.path.join(out, "ITEM_ENGINE_REPORT.json"), "w"), indent=1)
    open(os.path.join(out, "after_give.state"), "wb").write(h.em.get_state())
    print("ITEM ENGINE", "PASS" if all(c["pass"] for c in rep["checks"]) else "FAIL")


if __name__ == "__main__":
    main(*sys.argv[1:])
