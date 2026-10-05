"""Explicit HiROM address helpers for a 4 MiB (0x400000) FastROM HiROM image.

Only the canonical C0-FF mapping is accepted for ROM data addresses:
    SNES $C0:0000-$FF:FFFF  <->  PC 0x000000-0x3FFFFF
Mirrors (40-7D, 80-BF/00-3F:8000+) are intentionally rejected so that every
recorded address is unambiguous.
"""
ROM_SIZE_EXPANDED = 0x400000
ROM_SIZE_VANILLA = 0x300000

def snes_to_pc(snes: int) -> int:
    if not (0xC00000 <= snes <= 0xFFFFFF):
        raise ValueError(f"SNES address {snes:06X} is not in canonical HiROM range C0:0000-FF:FFFF")
    return snes - 0xC00000

def pc_to_snes(pc: int) -> int:
    if not (0 <= pc < ROM_SIZE_EXPANDED):
        raise ValueError(f"PC offset {pc:06X} outside 4 MiB image")
    return pc + 0xC00000

def fmt_snes(snes: int) -> str:
    return f"{snes >> 16:02X}:{snes & 0xFFFF:04X}"

def event_offset(snes: int) -> int:
    """Event-script address as stored in event operands (relative to $CA:0000).
    Consumers: C0 event interpreter (cmd $B2/$B3/$C0-$CF/$B6/$BD...) do
    `adc #^EventScript` (#$CA) on the high byte."""
    off = snes - 0xCA0000
    if not (0 <= off <= 0x35FFFF):
        raise ValueError(f"{snes:06X} not reachable by 24-bit event pointer")
    return off

def npc_event_reachable(snes: int) -> bool:
    """NPC event pointers are 18-bit (+$CA0000): CA:0000-CD:FFFF only."""
    return 0xCA0000 <= snes <= 0xCDFFFF

if __name__ == "__main__":
    assert snes_to_pc(0xF00000) == 0x300000
    assert pc_to_snes(0x3FFFFF) == 0xFFFFFF
    assert snes_to_pc(0xC0FFC0) == 0xFFC0
    assert event_offset(0xF10000) == 0x270000
    for bad in (0x7E0000, 0x808000, 0x400000):
        try: snes_to_pc(bad); raise SystemExit("FAIL")
        except ValueError: pass
    print("hirom self-test PASS")
