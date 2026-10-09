"""P100/P101 - Expansion dialogue namespace ($1000-$1FFF) served from F3/F4.

Vanilla consumer (Rev 1, verified bytes):
  GetDlgPtr  C0:7FBF  (PC 0x007FBF)
      A9 CD        LDA #^Dlg        ; bank $CD
      85 CB        STA $CB
      C2 20        REP #$20
      A5 D0        LDA $D0          ; dialogue index (13-bit, from event $4B/$48)
      0A AA        ASL / TAX
      BF 02 E6 CC  LDA $CCE602,X    ; DlgPtrs
      85 C9        STA $C9
      A5 D0        LDA $D0
      CF 00 E6 CC  CMP $CCE600      ; DlgBankInc (first index in bank $CE)
      90 05        BCC +5
      7B E2 20     TDC / SEP #$20
      E6 CB        INC $CB
   C0:7FDC:
      7B E2 20     TDC / SEP #$20
      A9 01        LDA #$01
      8D 68 05     STA $0568        ; enable dialogue display
      60           RTS
  Callers (JSR $7FBF): C0:A49A (event cmd $48), C0:A4E1 (event cmd $4B),
                       C0:D493 (debug code, unreachable in retail).
  DlgPtrs is read ONLY by GetDlgPtr (disassembly cross-reference).
  The text renderer reads [$C9] with bank $CB and carries into $CB, so any
  24-bit address is valid for string data.

Patch: overwrite the first 4 bytes (LDA #$CD / STA $CB) with JML to the hook.
  index <  $1000 : hook re-executes the 2 displaced instructions and JMLs to
                   C0:7FC3 -> vanilla path is byte-for-byte the original logic.
  index >= $1000 : n = index & $0FFF (clamped to 0 if n >= count); load 24-bit
                   pointer from DIALOGUE_PTRS[n] into $C9/$CB; JML C0:7FDC
                   (vanilla epilogue: $0568 = 1, RTS to the C0 caller).
Vanilla dialogue indices max out at DLG_3083 ($0C0B); the vanilla pointer
table can hold at most $0CFF entries, so $1000+ never aliases vanilla data.
"""
from ff6x.asm65816 import Asm
from ff6x.text import encode_dialogue

GETDLGPTR = 0xC07FBF
GETDLGPTR_ORIG4 = bytes.fromhex("A9 CD 85 CB")
VANILLA_CONT = 0xC07FC3      # REP #$20 (after displaced instructions)
VANILLA_EPILOGUE = 0xC07FDC  # TDC / SEP #$20 / LDA #1 / STA $0568 / RTS
EXP_DLG_BASE = 0x1000
EXP_DLG_MAX = 0x1000         # entries reserved in DIALOGUE_PTRS (4 bytes each)


def build_dialogue_table(rom, messages, patch_id="P101_EXP_DLG_TABLE"):
    """messages: list of (label, text). Index 0 is reserved for the
    out-of-range diagnostic string. Returns {label: dialogue_id}."""
    if len(messages) > EXP_DLG_MAX:
        raise ValueError("too many expansion messages")
    ptrs = bytearray()
    ids = {}
    from ff6x.text import line_widths, FONT_WIDTH_SNES, LINE_LIMIT_PX
    from ff6x.hirom import snes_to_pc
    fw = rom.clean[snes_to_pc(FONT_WIDTH_SNES):snes_to_pc(FONT_WIDTH_SNES) + 256]
    for n, (label, text) in enumerate(messages):
        data = encode_dialogue(text)
        lw = line_widths(data, fw)
        if max(lw) > LINE_LIMIT_PX or len(lw) > 4 and "{page}" not in text:
            raise ValueError(f"dialogue '{label}' would wrap/overflow: line widths {lw} px (limit {LINE_LIMIT_PX}, 4 lines)")
        snes = rom.place("DIALOGUE_TEXT", data, f"dlg_{EXP_DLG_BASE + n:04X}_{label}", patch_id,
                         reason=f"Expansion dialogue ${EXP_DLG_BASE + n:04X}: {text!r}",
                         consumer="field text renderer via $C9/$CB set by P100 hook")
        if (snes >> 16) != ((snes + len(data) - 1) >> 16):
            raise ValueError("dialogue string crosses bank")
        ptrs += bytes([snes & 0xFF, (snes >> 8) & 0xFF, snes >> 16, 0x00])
        ids[label] = EXP_DLG_BASE + n
    table = rom.place("DIALOGUE_PTRS", bytes(ptrs), "exp_dlg_ptr_table", patch_id,
                      reason=f"{len(messages)} x 4-byte pointers for dialogue IDs "
                             f"${EXP_DLG_BASE:04X}-${EXP_DLG_BASE + len(messages) - 1:04X}",
                      consumer="P100 hook (LDA.l table,X)", at=0xF30000)
    return table, len(messages), ids


READONLY_ASSERTS = [  # (snes, bytes) verified in the clean ROM; not modified
    (0xC07FC3, bytes.fromhex("C2 20 A5 D0 0A AA BF 02 E6 CC 85 C9 A5 D0 CF 00 E6 CC 90 05 7B E2 20 E6 CB")),
    (0xC07FDC, bytes.fromhex("7B E2 20 A9 01 8D 68 05 60")),
    (0xC0A49A, bytes.fromhex("20 BF 7F")),   # cmd $48 JSR GetDlgPtr
    (0xC0A4E1, bytes.fromhex("20 BF 7F")),   # cmd $4B JSR GetDlgPtr
    (0xC0D493, bytes.fromhex("20 BF 7F")),   # debug JSR GetDlgPtr
]


def build_hook(rom, table_snes, count, patch_id="P100_DLG_HOOK"):
    from ff6x.hirom import snes_to_pc
    for snes, exp in READONLY_ASSERTS:
        pc = snes_to_pc(snes)
        if rom.clean[pc:pc + len(exp)] != exp:
            raise SystemExit(f"{patch_id}: consumer assert failed at {snes:06X}")
    org = 0xF01000
    a = Asm(org)
    a.label("DlgHook")            # entry: .a8 .i16 (as at vanilla GetDlgPtr)
    a.rep(0x20)
    a.lda_dp(0xD0)
    a.cmp_imm16(EXP_DLG_BASE)
    a.bcs("Expansion")
    a.sep(0x20)
    a.lda_imm8(0xCD)              # displaced: LDA #^Dlg
    a.sta_dp(0xCB)                # displaced: STA $CB
    a.jml(VANILLA_CONT)
    a.label("Expansion")          # .a16
    a.and_imm16(0x0FFF)
    a.cmp_imm16(count)
    a.bcc("InRange")
    a.lda_imm16(0x0000)           # out of range -> reserved diagnostic msg
    a.label("InRange")
    a.asl_a()
    a.asl_a()
    a.tax()
    a.lda_long_x(table_snes)      # 16-bit offset
    a.sta_dp(0xC9)
    a.sep(0x20)
    a.lda_long_x(table_snes + 2)  # bank byte
    a.sta_dp(0xCB)
    a.jml(VANILLA_EPILOGUE)
    code = a.assemble()
    snes = rom.place("ENGINE_CODE", code, "DlgHook", patch_id,
                     reason="Dialogue-pointer hook: vanilla IDs unchanged, IDs $1000+ from expansion table",
                     consumer="JML from C0:7FBF (GetDlgPtr)", at=org)
    assert snes == org
    jml = bytes([0x5C, org & 0xFF, (org >> 8) & 0xFF, org >> 16])
    rom.patch(GETDLGPTR, GETDLGPTR_ORIG4, jml, patch_id,
              consumer="GetDlgPtr C0:7FBF; callers C0:A49A ($48), C0:A4E1 ($4B), C0:D493 (debug)",
              reason="Replace LDA #$CD / STA $CB with JML $F01000 (displaced code re-executed in hook)")
    return a.listing_text()
