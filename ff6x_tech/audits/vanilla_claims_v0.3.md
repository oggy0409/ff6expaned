# Vanilla-space claims & table repacks — TECH v0.3 (`celes-tech` target only)

All are declared in `data/allocations.json`; the builder refuses any vanilla write
outside a declared claim/repack and asserts the original bytes first.

## 1. NPC_EVENT_BRIDGES — CC:E5EE–CC:E5FF (PC 0x0CE5EE–0x0CE5FF)
Same 18-byte event-bank padding proven unused in `vanilla_claim_CCE5EE.md` (TECH v0.2,
runtime-accepted). v0.3 uses two 5-byte bridges:
CC:E5EE `B2 1C 00 27 FE` (Vale → F1:001C) and CC:E5F3 `B2 69 00 27 FE` (chest → F1:0069).
8 bytes remain (CC:E5F8–E5FF): room for one more bridge.

## 2. LAYOUT_PTR_SLOT_15F — D9:D1AD–D9:D1AF (PC 0x19D1AD–0x19D1AF)
- SubTilemap pointer table D9:CD90 is `fixed_block $420` = 352 × 3-byte slots.
  Rev 1 uses 350 layouts ($000–$15D) + the END pointer at $15E (D9:D1AA = `42 2E 04`).
  Slot $15F (D9:D1AD) is fixed-block padding: `FF FF FF`.
- Only consumer: `LoadMapTiles` (C0:2883): `LDA.l SubTilemapPtrs,X` + `ADC #SubTilemap`
  with carry into the bank byte → any 24-bit offset reaches F0–FF.
- No vanilla map property row references layout $15E or $15F (all 415 rows scanned;
  max used = $15D). The END pointer $15E is left untouched (editors may use it).
- New value: `50 2E 1B` → D9:D1B0 + $1B2E50 = **F5:0000**.

## 3. MAP_PROPS_0C7 — ED:A8A7–ED:A8C7 (PC 0x2DA8A7–0x2DA8C7)
- Row = ED:8F00 + $0C7 × 33. Rev 1 content: 33 × `00` (truly blank).
- Map $0C7 has 0 NPCs, 0 triggers, 0 entrances, 0 incoming entrances and 0 event
  `load_map` references (`AUDIT_MAP_CAPACITY.md`); startup event = EventReturn.
- Consumer: `LoadMapProp` (C0:1CAD) copies 33 bytes to $0520.

## 4. Table repacks (pointer-relative tables, inserted inside measured $FF slack)
| Table | Range (SNES / PC) | Inserted | Slack before → after |
|---|---|---|---|
| EVENT_TRIGGERS | C4:0000–C4:1A0F / 0x040000–0x041A0F | map $0C7 (16,10)→F1:0040; map $00C (13,46)→F1:0000 | 18 → 8 bytes |
| NPC_PROPS | C4:1A10–C4:6ABF / 0x041A10–0x046ABF | map $0C7: Vale, chest | 85 → 67 bytes |
| SHORT_ENTRANCES | DF:BB00–DF:D9FF / 0x1FBB00–0x1FD9FF | map $0C7 exit (16,29)→$00C (15,47) | 136 → 130 bytes |

Method: parse the whole table from the clean ROM, append records to the target map's
run, shift later runs, rewrite every later 16-bit pointer, assert the entire original
region (pointers + data + $FF slack) before writing. Round-trip of unmodified tables
is byte-identical; the NPC codec reproduces all 2,193 vanilla NPC records exactly.
Consumers address these tables only through their pointer tables (21 / 12 / 19 long
loads, all symbol-based in the Rev 1-verified disassembly).

Capacity left for future work without relocation: 1 trigger, 7 NPCs, 21 short entrances.
**Production volume will require relocating these tables to MAP_EXPANSION (F6–F7).**
