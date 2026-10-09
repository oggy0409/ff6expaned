# TECH v0.5 — Monster-ID dependency audit (Rev 1)

Machine-readable version: `audits/MONSTER_DEPENDENCY_TABLE_v0.5.json` (32 dependencies, 71 consumer patch points,
expected + new operand bytes for each). Raw consumer scan: `audits/monster_consumers_v0.5.json`,
builder input: `data/monster_relocation_v05.json`.

**Method.** Every symbol of every monster/formation table was resolved in the ca65 `.dbg` of the
everything8215 disassembly (`ROM_VERSION=1`, code banks match Rev 1), every referencing instruction
(long `BF/DF` operands, `#^bank` and `#near` immediates) was listed, and each instruction is
asserted byte-for-byte against the clean Rev 1 ROM by the builder before its operand is retargeted.
RAM structs whose names collide with table names were excluded by hand (`wTargetProp…`).
Non-table dependencies (bounds, hard-coded IDs, Rage/Veldt, SRAM) were audited by reading the Rev 1
code paths listed below. The disassembly is a dev oracle only; no GPL text is in the builder.

## 1. Result in one line
Monster IDs are **already 9-bit in the engine** (formation msb byte, 16-bit IDs in battle RAM,
`$1FF` = empty slot). What limits the count is that every monster-indexed table stops at 384
entries (and formation tables at 576). v0.5 relocates those tables to 512 / 1024 entries in
F8–F9, retargets 71 operands, and adds 3 small hooks (graphics slot ×2, colosseum bound).

## 2. Relocated tables (vanilla entries byte-identical)

| Table | Vanilla (Rev 1) | Rec | Vanilla n | 9-bit in place? | New (production) | New n | Consumers |
|---|---|---|---|---|---|---|---|
| MonsterProp (stats, HP/MP, exp, gil, level, elements, status, metamorph id, flags) | CF:0000–CF:2FFF | 32 | 384 | no | F8:0000 | 512 | 25 |
| MonsterName | CF:C050–CF:D0CF | 10 | 384 | no | F8:4000 | 512 | 6 (4 long, 1 `#near`, 1 `#^bank`) |
| MonsterSpecialName | CF:D0D0–CF:DFDF | 10 | 384 | no | F8:5400 | 512 | 2 (`#^bank`, `#near`) |
| MonsterItems (steal rare/common, drop rare/common) | CF:3000–CF:35FF | 4 | 384 | no | F8:6800 | 512 | 2 |
| MonsterControl | CF:3D00–CF:42FF | 4 | 384 | no | F8:7000 | 512 | 3 |
| MonsterSketch | CF:4300–CF:45FF | 2 | 384 | no | F8:7800 | 512 | 1 |
| MonsterSpecialAnim | CF:37C0–CF:393F | 1 | 384 | no | F8:7C00 | 512 | 2 |
| MonsterOverlap (sprite y-priority) | CF:3600–CF:377F | 1 | 384 | no | F8:7E00 | 512 | 1 |
| MonsterGfxProp (gfx offset, bpp, palette, size/stencil) | D2:7000–D2:781F | 5 | 416 slots | no (slots $180–$19F = espers/Imp) | F8:8000 | 543 slots | 15 |
| AIScriptPtrs | CF:8400–CF:86FF | 2 | 384 | no | F9:0000 | 512 | 1 |
| AIScript (blob, ptrs relative to start) | CF:8700–CF:C04F | — | 0x3950 B | — | F9:0400 (64 512 B window) | — | 4 |
| BattleProp (formation aux, 4 B) | CF:5900–CF:61FF | 4 | 576 | no | F8:9000 | 1024 | 2 |
| BattleMonsters (formation, 15 B, loader copies 16) | CF:6200–CF:83FF | 15 | 576 | no | F8:A000 | 1024 (+16 pad) | 7 |

Every consumer's PC/SNES address, expected instruction bytes and new operand bytes: JSON table
above and `PATCH_TABLE_v0.5.md` (patch IDs `N200_RETARGET_*`).

## 3. Hooked engine paths

| Dependency | Rev 1 site | Expected | New | Why |
|---|---|---|---|---|
| Graphics-property slot (battle loader) | C1:2058 / PC 012058 | `BD 01 20 0A 0A 18 7D 01 20` | `22 00 12 F0 EA×5` | slots $180–$19F are esper/summon + Imp graphics; `slot(id) = id<$180 ? id : id+$20` |
| Graphics-property slot (Sketch) | C2:F5F1 / PC 02F5F1 | `BD 01 20 AA` | `22 13 12 F0` | same remap for Sketch drawing |
| Colosseum bound | C2:2F75 / PC 022F75 | `AE D4 3E E0 3E 02` | `22 20 12 F0 EA EA` | vanilla treats every battle ≥ $23E as colosseum; now only $23E/$23F |
| Router code | F0:1200–F0:1230 / PC 301200 | FF fill | 49 B | `MonsterGfxSlot5`, `MonsterGfxSlotSketch`, `ColosseumRangeCheck` |

Summon (C1:24FC…) and Imp (`LDX #5*$19E`) loaders keep vanilla slot numbers. btlgfx colosseum
checks (`CPX #$023E/#$023F` with `BEQ/BNE`) are exact compares and need no change.

## 4. Engine-native (no change needed)

| Dependency | Where | Note |
|---|---|---|
| Formation monster IDs | byte 14 bits 0–5 = msb per slot; C2:2EE1 InitMonsters, C1:0ED1/0EDF | `$1FF` = empty; builder writes empty slots as `$1FF` |
| Battle RAM IDs | `$2001+2·slot` (btlgfx), `$33A8+y`, 16-bit | — |
| LoadMonsterProp | C2:2C30, 16-bit A = id | only the tables were too short |
| Encounter packs | RandBattleGroup CF:4800, World CF:5400, Sub CF:5600 — 16-bit formation ids (bit 15 = +rand 0–3) | can reference $240–$3FF directly |
| Event battle groups | EventBattleGroup CF:5000, 256 × 2 × 16-bit, event cmd `$4D` 8-bit group | groups $9A–$FF are `00 00 00 00` and unreferenced; QA uses $FE |
| Hard-coded IDs | Ghost Train $106 (btlgfx, exact); battles $1CF, $1D7, $1E5, $23E, $23F (exact) | unaffected |
| Loops | InitMonsters / LoadBattleProp / btlgfx loop over 6 slots | not over IDs |
| Metamorph | MetamorphProp C4:7F40 indexed by metamorph id in MonsterProp | per-monster record relocated |
| Monster dialogue | CF:DFE0 / CF:E1E0 indexed by message id | — |
| SRAM | `$1600–$1FFF` stores no monster id; rage bits `$1D2C` (256), Veldt formation bits `$1DDD` (battle < $200) | no change |

## 5. Not relocated (with reason)

| Dependency | Address | Indexed by | Decision |
|---|---|---|---|
| MonsterPal | D2:7820 (768 × 16 B) | 10-bit palette index in gfx prop | new monsters reference vanilla palettes (QA). New custom palettes = later step (relocation or audited free units). |
| MonsterGfx tile data, stencils | E9:7000…ED:6FF8, D2:A824, D2:AC24 | gfx offset / stencil | final art needs a graphics allocation (FB–FE reserved) — out of scope |
| MonsterRage / InitRage | CF:4600 (256 × 2), C4:7AA0 | rage id (8-bit) | excluded (section 6) |
| ColosseumProp / MonsterAlign | DF:B600, EC:E800 (256) | item → 8-bit monster | new monsters cannot be colosseum opponents (not needed) |
| BattleMagicPoints | DF:B400 (512), C2:5D94 `LDX wBattleID` / C2:5D97 `CPX #$0200` / `BCS` | battle id | **limitation:** formations ≥ $200 give 0 magic points (vanilla behaviour for $200–$23F) — see KNOWN_RISKS |
| Editors | third-party | 384 / 576 at vanilla addresses | project sources are authoritative; vanilla-address edits have no effect after v0.5 |

## 6. Rage / Veldt policy (implemented = vanilla behaviour, asserted)

* New monsters ($180+) **never** become Gau Rages: LearnRage C2:4A09 `BD 02 20 D0 0F`
  skips IDs ≥ $100 (asserted, untouched).
* New monsters never register Veldt formations: C2:49E9 `BD 02 20 D0 14` (id ≥ $100) and battle
  id ≥ $200 both skip; the builder **also** forces formation aux byte 3 bit 1 (C2:49E3
  `89 02 D0 1F`, "can't appear on Veldt") for every formation that uses an id ≥ $100 and refuses
  a formation source without `no_veldt`.
* No vanilla Rage changed; no SRAM change.

**Low-risk Rage expansion — report only, NOT implemented.** No zero-risk path exists:
rage ids are 8-bit end to end (bits `$1D2C` = 256 in SRAM, rage list C2:5837–5863 iterates
0–$FE, MonsterRage 256 entries, LearnRage uses the low byte). The least invasive option would be
(a) a 256-byte rage-id → 9-bit monster-id indirection table used by LearnRage, LoadRageProp (C2:2DC1)
and the rage name list, (b) re-pointing only rage slots that are *proven unlearnable* in vanilla, and
(c) placing the new monster in a formation < $200 that can appear on the Veldt (re-using a vanilla
formation id) or extending the Veldt formation bits (SRAM). (b) and (c) change vanilla data/SRAM
meaning, so this needs explicit approval and its own audit.

## 7. Formation implications
* 1024 formations; vanilla $000–$23F unchanged; **$240–$3FF = 448 new**.
* New formations: no Veldt (engine + flag), not colosseum (N303), **0 magic points** (engine bound
  `$200`), reachable from encounter packs (16-bit) and event battle groups.
* Formation sources use a vanilla template formation for byte 0 (vram/bg mode) and positions.
