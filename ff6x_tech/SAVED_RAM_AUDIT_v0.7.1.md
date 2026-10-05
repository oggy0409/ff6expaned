# TECH v0.7.1 — saved WRAM / SRAM audit

Scope (NEXT_TASK §1): `$1E1D-$1E3F` and `$1CF8-$1D27`, cross-referenced against every Rev 1 instruction in banks
C0 (field/events/init/save), C1 (battle graphics/menus), C2 (battle), C3 (menus/save/load) and every other bank,
plus the save/load/checksum paths.

Method: the everything8215/ff6 disassembly built with `ROM_VERSION=1` reproduces the clean Rev 1 ROM byte-for-byte
(SHA-1 `057ADA1C…`). `devtools/rev1_insn_index.py` resolves every emitted instruction through the ld65 `.dbg` file
(103 948 instructions, 0 byte mismatches vs the clean ROM). `devtools/saved_ram_audit_v071.py` scans that index;
its output is `audits/saved_ram_audit_v071.json`.

## 1. `$1CF8-$1D27` (48 bytes) — chosen for the extension metadata

| Evidence | Result |
|---|---|
| Direct data accesses (abs/abs,X/abs,Y/long in bank $7E) to `$1CF8-$1D27` | **1**: `C0:BDE8 STA $1CF8,X` in `InitNewGame` (field/init.asm:132), the New Game copy of `BushidoName` → `$1CF8`, 48 bytes. The disassembly comments it "load swdtech names (unused in English version)", `cpx #$0030 ; carried over from japanese version`. |
| Readers | **0**. The English menus and battle take SwdTech names from ROM, never from `$1CF8`. |
| Indexed accesses whose base is within 256 bytes below | `C0:BDD9 STZ $1CF6,X` (X < `$57`: New Game clear of `$1CF6-$1D4C`, runs *before* the Bushido copy); `E5:FA47/FA53 STA $1C04,Y` (Y ≤ `$40`, ends at `$1C44`, ending cutscene). Neither reaches past `$1CF7` except the New Game clear, which v0.7.1 keeps. |
| Neighbours | `$1A6E-$1CF5` spells learned (`$288` bytes, ends 2 bytes below); `$1D28` SwdTech known, `$1D29-$1D2B` lores, `$1D2C-$1D4B` rages — all start after `$1D27`. |
| JMP/JSR `abs` operands with values `$1D0E/$1D24/$1D26` | code addresses in their own bank (`InvertCarry`, `TfrBG1BtmTiles`, `MovePlayer`) — not RAM. |
| Save / load / checksum | The whole `$1600-$1FFF` block is copied to/from the SRAM slot by the vanilla save and load code and covered by the vanilla slot checksum; nothing in that path treats `$1CF8` specially. |

**Layout used (asm/item_v071/core.s):**

| Bytes | Name | Meaning |
|---|---|---|
| `$1CF8-$1D17` (32) | inventory bitmap | bit n (byte `$1CF8+(n>>3)`, mask `1<<(n&7)`) = inventory slot n holds `$100 | $1869[n]` |
| `$1D18-$1D23` (12) | equipment bitmap | bit `256+rec*6+slot` = character record rec (0-15), slot 0-5 (R-hand, L-hand, helmet, armor, relic 1, relic 2) holds `$100 | $161F[rec*37+slot]` |
| `$1D24-$1D27` (4) | signature / version | `58 49 01 FE` = 'X' 'I' version 1, ~version. A genuine vanilla save always holds the Bushido-name bytes `A5 9A A6 FF` here (New Game copy, never modified). |

This is exactly the preferred layout of NEXT_TASK §1 (32-byte inventory bitmap + 12-byte equipment bitmap +
signature/version) and uses a bitmap instead of quantity bit 7. The quantity byte keeps its vanilla meaning (0-99).

**New Game (I220, C0:BDE2):** the `$1CF6-$1D4C` clear still runs; the Bushido copy loop (`C0:BDE2-C0:BDF0`) is
replaced by `JSL XJ_NewGame` + `BRA $C0BDF1` → 44 bytes zero + signature. The copy's only effect was writing data no
code reads.

## 2. `$1E1D-$1E3F` (35 bytes) — audited free

| Evidence | Result |
|---|---|
| Direct data accesses | **0** (the 11 hits are JMP/JSR `abs` code addresses `$1E1F/$1E2D/$1E2F/$1E37/$1E38/$1E3C` in their own banks). |
| Indexed accesses with base ≤ 256 bytes below | 29 rows, all bounded tables that end below `$1E1D`: `$1D29,X` lores (3 B), `$1D2C,X` rages (32 B), `$1D55-$1D57,X/Y` config/window colours (≤ `$1DC8`), `$1DC9,X/Y` event words (`$54` B → `$1E1C`), `$1DDD,X` Veldt formations (8 B). Listed in `audits/saved_ram_audit_v071.json`. |
| Initialisation | **None**: `ClearRAM` clears `$0000-$11FF` only; `InitNewGame` clears up to `$1E1C` (event words) and from `$1E80` (switches). In SRAM saves these bytes are whatever the cartridge held → may be garbage. |

Consequently v0.7.1 stores **nothing persistent** here; two bytes are used as transient scratch that is always
written before it is read and never read across a save/load:

| Byte | Name | Use | Written / read |
|---|---|---|---|
| `$1E3F` | `XSCRATCH` | equip-menu stat preview: high bit of the item temporarily removed from the slot | written by `XC3_PrevSave` (I330), read by `XC3_PrevRestore` (I333) in the same preview call |
| `$1E3E` | `XBTLNAME` | battle Item menu: queue of "extended name" flags for the two hand names | cleared at battle start (`XC2_HandL`, I510), written by `XC1_HandNames` (I540) and consumed by `XC1_NameIdx` (I541) while drawing the same header |

`$1E1D-$1E3D` remain free and unallocated.

## 3. Load paths that must validate the metadata

| Path | Site | v0.7.1 |
|---|---|---|
| Title → Continue → slot | load menu `LoadSaveSlot` C3:29EB | I222: `XC3_LoadSlotSan` → `XJ_Sanitize` after the vanilla copy |
| Game-over → restart from last save | `LoadSavedGame` C3:14FE, after the checksum passed (`JSR PopTimers` C3:150E) | I221: `XC3_LoadOK` → `XJ_Sanitize`, then the displaced `PopTimers` |
| New Game | C0:BDE2 | I220: zero + signature |
| Save | vanilla copy of `$1600-$1FFF` + checksum | unchanged (metadata travels inside the slot) |

The sanitizer's rules and the legacy/garbage cases are in `SAVE_COMPATIBILITY_v0.7.1.md`.

## 4. Vanilla padding claims (ITEMX_C0/C2/C3_STUBS)

`devtools/vanilla_claims_v071.py` → `audits/vanilla_claims_v071.json`:

| Claim | Gap (between linker segments) | All `$FF` | Segments overlapping | Instructions inside | JMP/JSR/long refs |
|---|---|---|---|---|---|
| `ITEMX_C0_STUBS` C0:D620-C0:DF8F | C0:D613-C0:DF9F (`field_code` ends C0:D612, `dte_tbl` starts C0:DFA0) | yes | none | 0 | none |
| `ITEMX_C2_STUBS` C2:6470-C2:67FF | C2:6469-C2:67FF (`battle_code` ends C2:6468, `cutscene_code` starts C2:6800) | yes | none | 0 | none |
| `ITEMX_C3_STUBS` C3:F0A0-C3:FFEF | C3:F091-C3:FFFF (`menu_code` ends C3:F090, `event_triggers` starts C4:0000) | yes | none | 0 | none |

Data `abs` operands are DB-relative (WRAM banks `$7E/$7F` in these engines) and cannot address ROM padding. Each
claim is registered in `data/allocations.json` (`vanilla_space_claims`, `original_fill: FF`) and the builder
asserts the `$FF` fill before writing.

Bank C1 has no comparable gap; its three hooks are `JSL` to the far table in FA (`XJ_HandNames`, `XJ_NameIdx`,
`XJ_SwapGuard`).

## 5. Status

STATIC PASS (audit evidence regenerated from the Rev 1 index) · EMULATOR PASS (New Game signature, legacy/garbage
load, save→power-cycle→load: `ITEM_QA_EMULATOR_REPORT.json`) · USER RUNTIME QA PENDING.
