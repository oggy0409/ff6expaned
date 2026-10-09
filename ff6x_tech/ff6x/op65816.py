"""Complete 65816 opcode table (256 opcodes) shared by the assembler (ff6x/asm816.py)
and the Rev 1 instruction-index / consumer-audit devtools.

mode names:
  imp   implied            acc  accumulator (ASL A ...)
  imm8  #$nn (always 8-bit: REP/SEP/BRK/COP/WDM)
  immm  #imm, width follows M  (LDA/ADC/AND/BIT/CMP/EOR/ORA/SBC)
  immx  #imm, width follows X  (LDX/LDY/CPX/CPY)
  dp dpx dpy dpi dpil dpix dpiy dpily   direct-page forms
  abs absx absy absl abslx absi absix absil
  sr sriy  stack relative
  rel8 rel16 (branches / BRL / PER)    blk (MVN/MVP: dst, src)
"""

_T = """
00 BRK imm8   01 ORA dpix  02 COP imm8  03 ORA sr    04 TSB dp    05 ORA dp    06 ASL dp    07 ORA dpil
08 PHP imp    09 ORA immm  0A ASL acc   0B PHD imp   0C TSB abs   0D ORA abs   0E ASL abs   0F ORA absl
10 BPL rel8   11 ORA dpiy  12 ORA dpi   13 ORA sriy  14 TRB dp    15 ORA dpx   16 ASL dpx   17 ORA dpily
18 CLC imp    19 ORA absy  1A INC acc   1B TCS imp   1C TRB abs   1D ORA absx  1E ASL absx  1F ORA abslx
20 JSR abs    21 AND dpix  22 JSL absl  23 AND sr    24 BIT dp    25 AND dp    26 ROL dp    27 AND dpil
28 PLP imp    29 AND immm  2A ROL acc   2B PLD imp   2C BIT abs   2D AND abs   2E ROL abs   2F AND absl
30 BMI rel8   31 AND dpiy  32 AND dpi   33 AND sriy  34 BIT dpx   35 AND dpx   36 ROL dpx   37 AND dpily
38 SEC imp    39 AND absy  3A DEC acc   3B TSC imp   3C BIT absx  3D AND absx  3E ROL absx  3F AND abslx
40 RTI imp    41 EOR dpix  42 WDM imm8  43 EOR sr    44 MVP blk   45 EOR dp    46 LSR dp    47 EOR dpil
48 PHA imp    49 EOR immm  4A LSR acc   4B PHK imp   4C JMP abs   4D EOR abs   4E LSR abs   4F EOR absl
50 BVC rel8   51 EOR dpiy  52 EOR dpi   53 EOR sriy  54 MVN blk   55 EOR dpx   56 LSR dpx   57 EOR dpily
58 CLI imp    59 EOR absy  5A PHY imp   5B TCD imp   5C JML absl  5D EOR absx  5E LSR absx  5F EOR abslx
60 RTS imp    61 ADC dpix  62 PER rel16 63 ADC sr    64 STZ dp    65 ADC dp    66 ROR dp    67 ADC dpil
68 PLA imp    69 ADC immm  6A ROR acc   6B RTL imp   6C JMP absi  6D ADC abs   6E ROR abs   6F ADC absl
70 BVS rel8   71 ADC dpiy  72 ADC dpi   73 ADC sriy  74 STZ dpx   75 ADC dpx   76 ROR dpx   77 ADC dpily
78 SEI imp    79 ADC absy  7A PLY imp   7B TDC imp   7C JMP absix 7D ADC absx  7E ROR absx  7F ADC abslx
80 BRA rel8   81 STA dpix  82 BRL rel16 83 STA sr    84 STY dp    85 STA dp    86 STX dp    87 STA dpil
88 DEY imp    89 BIT immm  8A TXA imp   8B PHB imp   8C STY abs   8D STA abs   8E STX abs   8F STA absl
90 BCC rel8   91 STA dpiy  92 STA dpi   93 STA sriy  94 STY dpx   95 STA dpx   96 STX dpy   97 STA dpily
98 TYA imp    99 STA absy  9A TXS imp   9B TXY imp   9C STZ abs   9D STA absx  9E STZ absx  9F STA abslx
A0 LDY immx   A1 LDA dpix  A2 LDX immx  A3 LDA sr    A4 LDY dp    A5 LDA dp    A6 LDX dp    A7 LDA dpil
A8 TAY imp    A9 LDA immm  AA TAX imp   AB PLB imp   AC LDY abs   AD LDA abs   AE LDX abs   AF LDA absl
B0 BCS rel8   B1 LDA dpiy  B2 LDA dpi   B3 LDA sriy  B4 LDY dpx   B5 LDA dpx   B6 LDX dpy   B7 LDA dpily
B8 CLV imp    B9 LDA absy  BA TSX imp   BB TYX imp   BC LDY absx  BD LDA absx  BE LDX absy  BF LDA abslx
C0 CPY immx   C1 CMP dpix  C2 REP imm8  C3 CMP sr    C4 CPY dp    C5 CMP dp    C6 DEC dp    C7 CMP dpil
C8 INY imp    C9 CMP immm  CA DEX imp   CB WAI imp   CC CPY abs   CD CMP abs   CE DEC abs   CF CMP absl
D0 BNE rel8   D1 CMP dpiy  D2 CMP dpi   D3 CMP sriy  D4 PEI dpi   D5 CMP dpx   D6 DEC dpx   D7 CMP dpily
D8 CLD imp    D9 CMP absy  DA PHX imp   DB STP imp   DC JML absil DD CMP absx  DE DEC absx  DF CMP abslx
E0 CPX immx   E1 SBC dpix  E2 SEP imm8  E3 SBC sr    E4 CPX dp    E5 SBC dp    E6 INC dp    E7 SBC dpil
E8 INX imp    E9 SBC immm  EA NOP imp   EB XBA imp   EC CPX abs   ED SBC abs   EE INC abs   EF SBC absl
F0 BEQ rel8   F1 SBC dpiy  F2 SBC dpi   F3 SBC sriy  F4 PEA abs   F5 SBC dpx   F6 INC dpx   F7 SBC dpily
F8 SED imp    F9 SBC absy  FA PLX imp   FB XCE imp   FC JSR absix FD SBC absx  FE INC absx  FF SBC abslx
"""

OPCODES = {}          # opcode -> (mnemonic, mode)
_tok = _T.split()
for i in range(0, len(_tok), 3):
    OPCODES[int(_tok[i], 16)] = (_tok[i + 1], _tok[i + 2])
assert len(OPCODES) == 256

BY_NAME = {}          # (mnemonic, mode) -> opcode
for _op, (_mn, _md) in OPCODES.items():
    BY_NAME[(_mn, _md)] = _op

# operand byte count per mode (immm/immx: resolved by the caller from M/X)
SIZE = {"imp": 0, "acc": 0, "imm8": 1, "dp": 1, "dpx": 1, "dpy": 1, "dpi": 1, "dpil": 1, "dpix": 1,
        "dpiy": 1, "dpily": 1, "sr": 1, "sriy": 1, "rel8": 1, "abs": 2, "absx": 2, "absy": 2, "absi": 2,
        "absix": 2, "absil": 2, "rel16": 2, "blk": 2, "absl": 3, "abslx": 3}

# modes whose operand is a (bank-relative or long) DATA/RAM address
MEM_MODES = {"dp", "dpx", "dpy", "dpi", "dpil", "dpix", "dpiy", "dpily", "abs", "absx", "absy", "absl", "abslx"}


def operand_size(mode, m8=True, x8=True):
    if mode == "immm":
        return 1 if m8 else 2
    if mode == "immx":
        return 1 if x8 else 2
    return SIZE[mode]


def fmt_operand(mode, val, pc_next=None):
    f = {"imp": "", "acc": "A", "imm8": "#${:02X}", "dp": "${:02X}", "dpx": "${:02X},X", "dpy": "${:02X},Y",
         "dpi": "(${:02X})", "dpil": "[${:02X}]", "dpix": "(${:02X},X)", "dpiy": "(${:02X}),Y", "dpily": "[${:02X}],Y",
         "sr": "${:02X},S", "sriy": "(${:02X},S),Y", "abs": "${:04X}", "absx": "${:04X},X", "absy": "${:04X},Y",
         "absi": "(${:04X})", "absix": "(${:04X},X)", "absil": "[${:04X}]", "absl": "${:06X}", "abslx": "${:06X},X"}
    if mode in ("immm", "immx"):
        return f"#${val:0{4 if val > 0xFF else 2}X}"
    if mode == "blk":
        return f"${val & 0xFF:02X},${val >> 8:02X}"
    if mode in ("rel8", "rel16"):
        return f"${pc_next:04X}" if pc_next is not None else f"{val}"
    return f[mode].format(val)
