# FF6 Expanded Edition — TECH v0.4: MAP EXPANSION FOUNDATION

**STATIC PASS · EMULATOR PASS (differential vanilla map-load + proof-map suite + save/reset/load) · RUNTIME USER QA PENDING**

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`.
Accepted baselines reproduced byte-exact in the same run: TECH v0.1, v0.2, **v0.3 (accepted)**, v0.3 production branch, v0.3.1 QA harness.
No final Celes art/story, Magitek Praetor, Runic Crest, monster expansion or item architecture.

## Outputs (`out/`)
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.4.0_PRODUCTION.sfc` | `0181dbaa133b679e04bfa4fd7349292fc2e5f32a` | `2EB2033F` | `8A8B` | production branch v0.4 (engine only) |
| `FF6X_Rev1_TECH_v0.4.0_CELES_TECH.sfc` | `51587eaef3837d797e05cc58b8f535f6369fb8c3` | `B4E71558` | `9DB6` | production v0.4 + accepted Annex slice via the v0.4 pipeline |
| `FF6X_Rev1_TECH_v0.4.0_MAP_TECH_QA.sfc` | `e1d5387a819e3db87ce572d35ca51a5f5c91b6f1` | `EE846BD5` | `0087` | **user QA ROM** = celes-tech v0.4 + 2 proof maps + QA access (QA parts = Q4xx) |
| `FF6X_Rev1_TECH_v0.3.0_CELES_TECH.sfc` | `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` | `3E6B68E2` | `0C36` | accepted TECH v0.3 (regression rebuild) |
| `FF6X_Rev1_TECH_v0.3.0_PRODUCTION.sfc` | `0eda0bab925f8b6f1c840c20523f9413cb586ec3` | `8D05263F` | `20F6` | regression |
| `FF6X_Rev1_TECH_v0.3.1_CELES_TECH_QA_ACCESS.sfc` | `bf443c85dc448c0a86169f58dce43d77684c36f5` | `B982BC11` | `CCD9` | regression (QA harness) |
| `FF6X_Rev1_TECH_v0.2.0_EVTEST_REBUILD.sfc` | `0258a0fc122bb109e7ca343dda61c58af2e921fb` | `32725A65` | `96FF` | = accepted v0.2 |
| `FF6X_Rev1_TECH_v0.1_LEGACY_REBUILD.sfc` | `c412f12938f9f4bd9c7e3f857572d3b773bab649` | `DA88A7DE` | `3F4D` | = accepted v0.1 |

BPS SHA-1: production `1a89749c0903da21926270a86c4c3d90c12a96dd`, celes-tech `5a31d9c6a31578f3561b0211ffe173cf092588fe`,
map-tech `7c77d64aaf54b151cf7155fcb0838f3bd4ead880`. Each ROM also has `.ips`, `.manifest.json`, `.diff.csv`.

```
python build.py "Final Fantasy III (USA) (Rev 1).sfc"            # all 8 targets (deterministic)
python build.py "<rom>" --target map-tech
python tools/selftest.py "<rom>"                                  # 28 fail-closed guard tests
```

## 1. What changed (engine, all v0.4 targets)
| ID | What | Where |
|---|---|---|
| M101 | Event-trigger table relocated: 513 ptrs + 5-byte records | F6:0000–F6:3FFF |
| M102 | NPC table relocated: 513 ptrs + 9-byte records | F6:4000–F6:BFFF |
| M103 | Short entrances relocated: 513 ptrs + 6-byte records | F6:C000–F6:FFFF |
| M104 | Long entrances relocated: 513 ptrs + 7-byte records | F7:0000–F7:1FFF |
| M105 | Treasure table relocated: 513 ptrs (data-relative) + 5-byte records | F7:2000–F7:3FFF |
| M106 | Map properties: 512 rows × 33 B (maps $000–$1FF) | F7:4000–F7:81FF |
| M107 | Layout (SubTilemap) pointers: 1024 × 3 B (10-bit index) | F7:8400–F7:8FFF |
| M108 | NPC event vector table (3-byte addresses) | F7:9000–F7:9FFF |
| M200 | 90 consumer operands retargeted (TRIG 12, NPC 21, SHORT 19, LONG 19, TREASURE 12, PROPS 1, LAYOUT PTRS 6) | `audits/MAP_CONSUMERS_v0.4.md` |
| M300 | NPC event router: C0:52E6 `29 03 99 8B 08` → `22 00 11 F0 EA` (JSL F0:1100) + 71-byte routine | F0:1100–F0:1146 |

Vanilla records are copied **unchanged** (static check: every map's records decode identical to Rev 1); the
vanilla tables stay in place as dead data (reversible: restoring the 90 operands + 5 router-site bytes returns to vanilla behaviour).
Vanilla-space diff of production v0.4 = 237 bytes: 90 operands, C0:7FBF hook (accepted), C0:52E6 router site, checksum.

### NPC event routing (replaces CA–CD bridge stubs)
NPC records keep the vanilla 9-byte format. A **non-special** NPC whose 18-bit event field is `$3xxxx`
(= bank CD, which holds dialogue, never events; audit: 0 of 1,904 vanilla non-special NPCs) is routed:
`index = field & $FFFF` → `F7:9000 + 3·index` → 24-bit event address (any bank C0–FF).
Vanilla NPCs (bits 0–2) and all special NPCs (45 use bits = 3 for master-object data) take the
unchanged path (`AND #$03 / STA $088B,Y`). Out-of-range index → EventReturn (CA:5EB3).
The Annex Vale/chest bridges at CC:E5EE are no longer used in v0.4 (claim not active for v0.4 targets).

## 2. Practical capacity (v0.4 layout)
| Resource | Vanilla | Capacity now | Notes |
|---|---|---|---|
| Map IDs | $000–$19E (415) | **$000–$1FD** | $1FE/$1FF = engine "previous/parent map". New IDs: $19F–$1FD = **95** (+ 9 audited blank vanilla IDs) |
| Event triggers | 1,164 (18 B slack) | **3,071** records | 16 KiB sub-region |
| NPCs | 2,193 (85 B slack) | **3,526** records | 32 KiB |
| Short entrances | 1,129 (136 B slack) | **2,559** | 16 KiB |
| Long entrances | 152 | **1,023** | 8 KiB |
| Treasure | 286 | **1,433** | 8 KiB (chest bits not yet allocated) |
| Layout indices | 350 + END | **673 new** ($15F–$3FF) | data in MAP_LAYOUTS F5 (64 KiB; 4 layouts use 4.6 KiB) |
| NPC event vectors | — | **1,365** | events anywhere in F0–FF |
| Per-map hard limits (unchanged engine) | | ≤ 32 NPCs per map (objects $10–$2F; no engine bound check → enforced by the builder), map ≤ 128×64 tiles | |
Remaining reserve: MAPX_SPARE F7:A000–F7:FFFF (24 KiB), MAP_LAYOUTS free 59 KiB.

## 3. Content pipeline (source-controlled)
`events/<package>/package.json` + `events.evt` + `dialogue.json` (+ `records.json` for cross-map records),
`maps/<map>/map.json`, layout source, `npcs.json`, `triggers.json`, `exits.json` (short + long), `encounters.json`.
New: **compose layers** (canvas + rectangular blits from vanilla layouts + overrides) to reuse/consolidate vanilla
room art; BG2 layers with their own layout index; long entrances; NPC events via vectors (automatic);
walkability proof now models the engine movement rule (tile byte-2 direction masks, counter tiles, z-levels, bridges).

## 4. Proof maps (map-tech)
| Map | Content | Proves |
|---|---|---|
| **$1A0 MAP TECH A** (beyond vanilla range) | Magitek-lab legend layout $160 (F5:0482); NPC A1/A3 always visible (vanilla switch $300, read-only), A2 visible after flag; alcove trigger; door short entrance → $1A1; south long entrance (2 tiles) → map $013 | new map ID, new layout index, relocated props/NPC/trigger/short/long tables, routed NPC events, NPC switch on new map |
| **$1A1 MAP TECH B** | composed from vanilla room art (layouts $06F/$070 → new BG1 $161, BG2 $162); NPC B1 sets flags; door short entrance and stairs long entrance → $1A0 | compose pipeline, BG2 layer, second tileset/palette, flags across maps |
Flags (audited FREE, reserved permanently for TECH): `$14D MAP_TECH_V04_VISITED_B`, NPC `$6FA NPC_MAP_TECH_A2_VISIBLE`.

## 5. QA access (map-tech only — QA HARNESS, Q4xx)
Map $013 tile (34,43), same tile as v0.3.1. Prompt: Map test A / Celes Annex / No (Save Point).
Q400 event FF:0000, Q401 dialogue FF:0800 + pointer slot, Q403 Annex battle group $28→$01, Annex exit → (35,43).
**This opening-Magitek tile is UNSUITABLE for field-sprite persistence testing** (`docs/KNOWN_QA_ISSUE_v0.3.1.md`).

## 6. Verification
- 28/28 selftests (new: relocated tables == vanilla for all maps; vanilla diff limited to declared bytes; undeclared/wrong-target retarget refused; QA parts only in map-tech; celes-tech v0.4 writes no CA–CD bridge/vanilla table; compose-map leak refused).
- Event assembler oracle 24/24. Determinism: two full builds byte-identical.
- Emulator differential test: vanilla Rev 1 vs production v0.4, teleport into maps $003–$19E with identical inputs → map RAM fingerprints (properties, NPC objects incl. event pointers, BG tilemaps, tile properties) compared — see `REGRESSION_REPORT_v0.4.md`.
- Emulator proof-map suite from New Game, no RAM pokes: 21/21 save phase + 13/13 load phase (incl. Annex regression and vanilla opening battle).

Details: `docs/MAP_FOUNDATION_v0.4.md`, `PATCH_TABLE_v0.4.md`, `audits/MAP_CONSUMERS_v0.4.md`,
`KNOWN_RISKS_v0.4.md`, `REGRESSION_REPORT_v0.4.md`, `USER_QA_TECH_v0.4_VI.md`.
