# FF6 Expanded Edition — TECH v0.7.1: SIGNATURE EQUIPMENT BANK PROOF (Option C)

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING** — v0.7.1 is a QA build for review, not an accepted baseline.

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`,
CRC32 `C0FA0464` (the builder aborts on any other input). Accepted baselines through v0.6.2 are reproduced byte-exact.

## What v0.7.1 adds
An extended item id range **`$100-$13F`** that coexists with vanilla `$00-$FE` without changing any vanilla id:

* **Storage** (`SAVED_RAM_AUDIT_v0.7.1.md`): the low byte stays in the vanilla inventory/equipment byte; the high bit
  lives in a saved bitmap at `$1CF8-$1D23` (32-byte inventory + 12-byte equipment) with signature/version
  `58 49 01 FE` at `$1D24-$1D27` — the 48-byte Bushido-name block that the English game writes at New Game and never
  reads. SRAM slot size/layout unchanged.
* **Save compatibility** (`SAVE_COMPATIBILITY_v0.7.1.md`): every load path sanitizes; legacy/garbage saves get zero
  extended items; undefined ids are removed, never truncated.
* **Tables** (bank FA, `ITEMX_TABLES`): 320-entry copies of ItemProp/ItemName, extended flags, descriptions,
  256-entry weapon-animation and Jump-animation tables. Vanilla tables are copied, never modified.
* **Engine**: 65816 sources in `asm/item_v071/` (assembled by the project's `ff6x/asm816.py`, checked against ca65 by
  `devtools/asm_oracle.py`); far code in `ITEMX_CODE` (FA:8000); same-bank stubs in three audited `$FF` padding claims
  (C0/C2/C3); 154 same-length hook sites and 118 long-operand retargets — every one with original bytes asserted,
  consumer and reason (`patches/item_v071_hooks.py`, `data/item_relocation_v071.json`, `PATCH_TABLE_v0.7.1.md`).
* **Consumers** (`ITEM_CONSUMER_AUDIT_v0.7.1.md`): 287 inventory/equipment/battle-hand instruction sites and 118 table
  operands, each hooked or reviewed (0 unclassified). Shops, Sell, Steal/Drop/Metamorph, Colosseum wager, Throw and
  other 1-byte sources are excluded (extended items are invisible there).
* **Event API** (expanded opcodes, vanilla `$80/$81` unchanged): `$66 GIVE_EXT_ITEM id16`, `$67 TAKE_EXT_ITEM id16`,
  `$68 HAS_EXT_ITEM id16 switch16`; event assembler commands `give_ext_item / take_ext_item / has_ext_item`
  (only accepted when the target carries the engine).
* **QA content (item-tech only)**: `$13D` QA Blade13D (weapon), `$13E` QA Mail 13E (body armor), `$13F` QA Charm13F
  (relic) from `items/qa_v071/qa_items.json`; QA harness menu `events/qa_access_v071/` (grant, HAS/TAKE, shop,
  colosseum, test battle). QA bit `$14E` allocated in `data/allocations.json` (item-tech only).

Not done (out of scope per NEXT_TASK): the 39 production items, consumables, special relic ASM, key-item expansion,
Celes content, foundation redesign.

## Outputs
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc` | `c6ea2b3017e01da7a6049470215e35b962b345da` | `65CF1731` | `7984` | **user QA ROM** |
| `FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.bps` | `b89f86b979d6c16d973148c1fc0494669efb8aff` | | | patch vs clean Rev 1 |
| `FF6X_Rev1_TECH_v0.7.1_PRODUCTION.sfc` | `b03b0973337a7aea7bb6f53ada04d7f93a8a0226` | `BBEC9D4C` | `1A8D` | production branch: engine, **no** QA content, no extended item defined |
| `FF6X_Rev1_TECH_v0.7.1_PRODUCTION.bps` | `50ac325b0008e740295009807048090d6f76919f` | | | |
| `FF6X_Rev1_TECH_v0.7.1_CELES_TECH.sfc` | `ed0398cbcf4ac4d5b074ea7a319b43c1fbe06f92` | `D6634BE6` | `2DB8` | production + accepted Celes Annex slice |
| `FF6X_Rev1_TECH_v0.7.1_CELES_TECH.bps` | `7e11af4dc25b8e078bef815ca4a0df53bfb597f8` | | | |

Each ROM has `.ips`, `.manifest.json` (every patch row: PC/SNES, original/new bytes, consumer, reason) and `.diff.csv`
(byte diff vs clean Rev 1). `BUILD_SUMMARY.json` lists all 18 targets with hashes.

Frozen accepted targets (asserted by SHA-1 at build time): `production-v0.6.0` `26ebd7d3…`, `celes-tech-v0.6.0`
`a7ae5d4c…`, `monster-tech-v0.6.1` `8a55707f…`, and all v0.1-v0.6.0 rebuilds (`REGRESSION_REPORT_v0.7.1.md`).

## Build
```
python3 build.py "<clean Rev 1>.sfc" --target all --out out
python3 tools/selftest.py "<clean Rev 1>.sfc"
```
Devtools (need the everything8215/ff6 disassembly built with `make ROM_VERSION=1`):
`devtools/rev1_insn_index.py` → instruction index; `item_relocation_v071.py`, `gen_hooks_v071.py`,
`saved_ram_audit_v071.py`, `vanilla_claims_v071.py`, `item_consumer_audit_v071.py` regenerate the data and audits.

## Status
| | Result |
|---|---|
| STATIC | **PASS** — 18/18 targets build, frozen hashes match, two full builds byte-identical (90 files), selftest 71/71, vanilla-space diff limited to declared bytes |
| EMULATOR (Claude-side, snes9x via stable-retro; not user QA) | **PASS** — see `REGRESSION_REPORT_v0.7.1.md` |
| USER RUNTIME QA | **PENDING** — `USER_QA_TECH_v0.7.1_VI.md` (A–N + three items equipped at once) |

Known risks: `KNOWN_RISKS_v0.7.1.md`.
