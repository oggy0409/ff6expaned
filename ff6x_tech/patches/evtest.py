"""T200 - Phase 2 test branch: event + dialogue in expansion space.

Trigger : Figaro Castle (WoB), map $037, NPC #9 at (44,21), switch $030B,
          vanilla text DLG $0052 "Weapons and items manufactured here are
          sent to South Figaro."  Vanilla NPC script CA:75D8 = 4B 52 00 FE.
Path    : NPC record C4:26F4 event pointer (18-bit, CA-CD only)
            CA:75D8  ->  CC:E5EE  (trampoline in end-of-event-bank padding)
          CC:E5EE  B2 00 00 27   call F1:0000 (bank = $27 + $CA)
          CC:E5F2  FE            return (ends NPC event)
          F1:0000  new event (below); returns to CC:E5F2.
Test bit: event bit $0FF ($1E9F bit 7) - audited unreferenced; reserved
          permanently as TECH_TEST (never reused for production content).
"""
from ff6x.hirom import event_offset, npc_event_reachable, snes_to_pc

NPC_REC_SNES = 0xC426F4
NPC_REC_ORIG = bytes.fromhex("D8 75 C8")       # ptr $075D8, pal/scroll/switch bits in byte 2
VANILLA_NPC_SCRIPT = (0xCA75D8, bytes.fromhex("4B 52 00 FE"))
TRAMPOLINE = 0xCCE5EE
TEST_BIT = 0x0FF


class EventAsm:
    """Tiny event-script emitter with label fixups for 24-bit event operands."""
    def __init__(self, org):
        self.org, self.b, self.labels, self.fix, self.lst = org, bytearray(), {}, [], []
    def _e(self, text, data):
        self.lst.append((self.org + len(self.b), bytes(data), text)); self.b += bytes(data)
    def label(self, n): self.labels[n] = self.org + len(self.b); self.lst.append((self.labels[n], b"", n + ":"))
    def dlg(self, i): self._e(f"dlg ${i:04X}", [0x4B, i & 0xFF, (i >> 8) & 0x1F])
    def set_switch(self, s):
        assert s <= 0x6FF
        self._e(f"set_switch ${s:03X}", [0xD0 + (s >> 8) * 2, s & 0xFF])
    def if_switch_set(self, s, lab):
        self.fix.append((len(self.b) + 3, lab))
        self._e(f"if_switch ${s:03X}=1, {lab}", [0xC0, s & 0xFF, ((s >> 8) & 0x7F) | 0x80, 0, 0, 0])
    def ret(self): self._e("return", [0xFE])
    def assemble(self):
        for pos, lab in self.fix:
            off = event_offset(self.labels[lab])
            self.b[pos:pos + 3] = off.to_bytes(3, "little")
        out, o = [], 0
        for a, d, t in self.lst:
            out.append((a, bytes(self.b[o:o + len(d)]), t)); o += len(d)
        self.lst = out
        return bytes(self.b)
    def listing(self):
        return "\n".join(f"{a >> 16:02X}:{a & 0xFFFF:04X}  {d.hex(' ').upper():<20} {t}" for a, d, t in self.lst)


def build(rom, dlg_ids):
    pc = snes_to_pc(VANILLA_NPC_SCRIPT[0])
    if rom.clean[pc:pc + 4] != VANILLA_NPC_SCRIPT[1]:
        raise SystemExit("T200: vanilla NPC script mismatch")
    vanilla_dlg = 0x0052

    # --- new event in EVENT_EXPANSION
    org = 0xF10000
    e = EventAsm(org)
    e.label("EvTest")
    e.if_switch_set(TEST_BIT, "EvTest_Seen")
    e.dlg(dlg_ids["evtest_first"])
    e.set_switch(TEST_BIT)
    e.dlg(vanilla_dlg)
    e.ret()
    e.label("EvTest_Seen")
    e.dlg(dlg_ids["evtest_again"])
    e.dlg(vanilla_dlg)
    e.ret()
    code = e.assemble()
    rom.place("EVENT_EXPANSION", code, "EvTest", "T200_EVTEST_EVENT", at=org,
              reason="Phase 2 proof event: new dialogue, test bit $0FF, vanilla dialogue, return",
              consumer="event interpreter via $B2 call from trampoline CC:E5EE")

    # --- trampoline in vanilla padding (claimed in allocations.json)
    call = bytes([0xB2]) + event_offset(org).to_bytes(3, "little") + bytes([0xFE])
    rom.patch(TRAMPOLINE, b"\xFF" * 5, call, "T201_EVTEST_TRAMPOLINE",
              consumer="field NPC activation (C0 obj code) -> event interpreter",
              reason="B2 call F1:0000 then FE; needed because NPC pointers are 18-bit (CA:0000-CD:FFFF)",
              claim="EVTEST_NPC_TRAMPOLINE")

    # --- NPC event pointer repoint
    assert npc_event_reachable(TRAMPOLINE)
    off = TRAMPOLINE - 0xCA0000
    b2 = (NPC_REC_ORIG[2] & 0xFC) | (off >> 16)
    new = bytes([off & 0xFF, (off >> 8) & 0xFF, b2])
    rom.patch(NPC_REC_SNES, NPC_REC_ORIG, new, "T202_EVTEST_NPC_REPOINT",
              consumer="C0 NPC loader (obj.asm: NPCProp::EventPtr -> $0889-$088B, &3 on hi byte)",
              reason="Map $037 NPC #9 event pointer CA:75D8 -> CC:E5EE (byte 2 upper 6 bits preserved)")
    return e.listing(), call
