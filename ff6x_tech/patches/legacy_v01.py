"""TECH v0.1 smoke test re-expressed through the guarded framework.

Purpose: regression proof that the new framework reproduces the
gameplay-accepted v0.1 ROM byte-for-byte (SHA-1 c412f129...). This target is
NOT a production branch; EXPTEST never enters 'foundation' or 'evtest'.
"""
CMD_TABLE_SNES = 0xD8CEA0          # PC 0x18CEA0, 32 x 7 bytes
CMD_TABLE_LEN = 0xE0
OLD_REF = bytes.fromhex("BF A0 CE D8")   # LDA.l $D8CEA0,X
NEW_REF = bytes.fromhex("BF 00 00 F0")   # LDA.l $F00000,X
CONSUMERS = [  # identified Rev 1 long-load consumers of the command-name table
    (0xC15F2B, "C1 battle menu (btlgfx/menu.asm _c15f13): command list name draw"),
    (0xC169FB, "C1 battle menu text cmd $0D (MenuTextCmd_0d): command name"),
    (0xC35EFB, "C3 Status menu DrawCmdName (menu/status.asm)"),
]


def enc_upper(s):
    return bytes(0xFF if c == " " else 0x80 + ord(c) - 65 for c in s)


def build(rom):
    from ff6x.hirom import snes_to_pc
    pc = snes_to_pc(CMD_TABLE_SNES)
    if rom.clean[pc:pc + 7] != bytes([0x85, 0xA2, 0xA0, 0xA1, 0xAD, 0xFF, 0xFF]):
        raise SystemExit("Fight table signature mismatch")
    table = bytearray(rom.clean[pc:pc + CMD_TABLE_LEN])
    table[0:7] = enc_upper("EXPTEST")                 # cmd $00 Fight
    table[0x1D * 7:0x1D * 7 + 7] = enc_upper("EXPTEST")   # cmd $1D MagiTek
    rom.place("LEGACY_V01_CMDNAMES", bytes(table), "cmd_names_relocated", "L001_CMDNAMES",
              reason="v0.1: relocated command-name table with EXPTEST markers",
              consumer="C1:5F2B, C1:69FB, C3:5EFB (LDA.l table,X)", at=0xF00000)
    sig = b"FFVI_EXPANDED_TECHTEST_V0.1_REV1"
    rom.place("LEGACY_V01_SIGNATURE", sig, "signature", "L002_SIGNATURE",
              reason="v0.1 signature", consumer="none (identification)", at=0xF00100)
    for snes, who in CONSUMERS:
        rom.patch(snes, OLD_REF, NEW_REF, "L003_REPOINT_CMDNAMES", consumer=who,
                  reason="Repoint LDA.l $D8CEA0,X -> $F00000,X")
