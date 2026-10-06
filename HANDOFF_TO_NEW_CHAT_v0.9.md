# FFVI Expanded Edition — HANDOFF TO NEW CHAT (TECH v0.9 ACCEPTED)

> Self-contained handoff. A new model/session can continue from this file alone. **Do not start any milestone
> automatically** — follow §J, then propose the next milestone and wait for the user.
> Machine-readable twin: `PROJECT_STATE_v0.9.json`. Git / zip facts: `HANDOFF_GIT_STATE.txt`, `HANDOFF_ZIP_MANIFEST.txt`
> (both inside `FF6X_PROJECT_HANDOFF_v0.9_ACCEPTED.zip`).

---------------------------------------------------------------------------------------------------------------------

## A. Project identity

| | |
|---|---|
| Project | **FFVI Expanded Edition** ("FF6X") — an expansion ROM hack of Final Fantasy VI built from source by a deterministic Python builder. All work so far is the **TECH foundation** (engine capacity + proof slices); no final story content exists. |
| Target ROM | **Final Fantasy III (USA) (Rev 1)** = FFVI US v1.1, unheadered, `0x300000` bytes, FastROM HiROM, internal revision `0x01` |
| Clean ROM hash | **SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`**, **CRC32 `C0FA0464`** (the builder aborts on anything else; copier header → abort) |
| Clean ROM in this package | `Final Fantasy III (USA) (Rev 1).sfc` at the package root (it is also tracked in the repository root) |
| Output | 4 MiB HiROM image: Rev 1 (`$000000-$2FFFFF`) + expansion `$300000-$3FFFFF` = SNES banks F0-FF; SNES checksum recomputed |
| Build requirements | **Python 3.8+ stdlib only** for `build.py` and `tools/selftest.py` (verified with Python 3.11.15). Emulator suites (`tools/emu_*.py`) additionally need `stable-retro` (1.0.1, snes9x core), `numpy`, `Pillow`. Devtools that regenerate audits need the everything8215/ff6 disassembly built with `make ROM_VERSION=1` (external, not in the package) and cc65 for `devtools/asm_oracle.py`. |
| Repository | `https://github.com/oggy0409/ff6expaned` (private), branch **`claude/festive-mayer-i6uurp`**; `main` holds only the initial "Start" commit. PR `oggy0409/ff6expaned#1` (branch → main) exists; do not open another. |
| Source-freeze commit | **`2d44bb23ccb1eaa2e6998dd85f479c93ea952970`** — exact source tree of this handoff (builder pins the v0.9 hashes). The next commit on the branch only adds this file, `PROJECT_STATE_v0.9.json` and the handoff zip; see `HANDOFF_GIT_STATE.txt` for the final SHA. |
| Workspace root | `ff6x_tech/` (everything below is relative to it unless it starts with the package root files) |

Engineering rules (binding, from the original model handoff, `FFVI_Expanded_Edition_MODEL_HANDOFF_START_v0.7.1.zip`):
build only from clean Rev 1 · abort on hash mismatch · never edit the master ROM in place · assert original bytes
before every vanilla write · record PC and SNES addresses · no blind opcode-pattern patching · every patch has an
identified consumer/reason · no US v1.0 offsets without Rev 1 verification · ONE allocation manifest
(`ff6x_tech/data/allocations.json`), overlaps rejected · recompute checksum, output SHA-1 + CRC32 + diff/patch
manifest · keep **STATIC / EMULATOR / USER RUNTIME** separate · never claim user-runtime success without the user ·
accepted runtime builds become named, hash-pinned baselines · minimal reversible patches · never overwrite vanilla data
just because it looks unused · QA placeholders allowed, production content must follow the Creative Lock · builder
sources are the source of truth (no manual editor changes).

Creative canon (locked; do not change silently): Kefka remains the final antagonist; magic/Espers disappear in the
ending; Leo, Rachel, Darill stay dead; Shadow stays dead if not saved; Shadow/Relm connection implied, not confessed;
Vael is not the mastermind behind Kefka; no multiverse, time travel, fourth god, resurrection retcons or new permanent
playable character.

---------------------------------------------------------------------------------------------------------------------

## B. Current accepted baseline

**TECH v0.9 — ACCEPTED / USER RUNTIME QA PASS** (consumable + rare/key item expansion). Do not alter these outputs;
`build.py` asserts their SHA-1 (`expect_sha1`) on every build.

| Accepted v0.9 ROM | SHA-1 | CRC32 |
|---|---|---|
| QA `FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc` (target `item-tech`) | `e1136805cc792e11dbffab15e87df0f327a6a12e` | `D8183069` |
| Production `FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc` (target `production`) | `99cd74dfac5b91756120992dd1560534b40c66c3` | `FF753A76` |
| Celes-tech `FF6X_Rev1_TECH_v0.9_CELES_TECH.sfc` (target `celes-tech`) | `e4c0703189fbde9b2df4ca972bfc801778aa6899` | `3067CF9B` |

BPS / IPS / manifest / diff hashes: `ff6x_tech/HASHES_v0.9.txt`.

### Milestone history (every accepted baseline is rebuilt byte-exact and SHA-1-asserted by `build.py --target all`)

| Milestone | Status | What it proved | Pinned ROM(s) (target → SHA-1 / CRC32) |
|---|---|---|---|
| TECH v0.1 | ACCEPTED | 4 MiB expansion + F0 data reads; save/reset/load OK | `legacy-v0.1` → `c412f12938f9f4bd9c7e3f857572d3b773bab649` / `DA88A7DE` |
| TECH v0.2 | ACCEPTED | expansion dialogue + event hook/bridge + persistent event bit (`$0FF` reserved for TECH_TEST forever) | `evtest` → `0258a0fc122bb109e7ca343dda61c58af2e921fb` / `32725A65` |
| TECH v0.3 | ACCEPTED | new map / NPC / dialogue / event / battle / reward / save-load pipeline (Celes "Echoes of the Empire" tech slice, Annex map `$0C7`) | `celes-tech-v0.3.0` → `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` / `3E6B68E2`; `production-v0.3.0` → `0eda0bab925f8b6f1c840c20523f9413cb586ec3` / `8D05263F` |
| TECH v0.3.1 | QA harness (accepted with a documented QA-only issue) | QA access menu | `celes-qa-v0.3.1` → `bf443c85dc448c0a86169f58dce43d77684c36f5` / `B982BC11` |
| TECH v0.4 | ACCEPTED | expanded map foundation: relocated map tables, map ids up to `$1FD`, scalable NPC event routing, short/long entrances, persistent map state | `production-v0.4.0` `0181dbaa133b679e04bfa4fd7349292fc2e5f32a` / `2EB2033F`; `celes-tech-v0.4.0` `51587eaef3837d797e05cc58b8f535f6369fb8c3` / `B4E71558`; `map-tech-v0.4.0` `e1d5387a819e3db87ce572d35ca51a5f5c91b6f1` / `EE846BD5` |
| TECH v0.5 | ACCEPTED / RUNTIME VERIFIED | monster ids above `$17F` (QA `$180/$181`), 512 monsters / 1024 formations | `production-v0.5.0` `34ad5625ed08f791ca98ccde6a1dbf4ba4744cec` / `844CC192`; `celes-tech-v0.5.0` `3805944217af91e7b360225d3e73dd2afdd714a7` / `239DD0DF`; `monster-tech-v0.5.0` `416d5d9fbd88751e8fbd5ab4290dbb51fff3e69f` / `381E6EE5` |
| TECH v0.6.0 | NOT ACCEPTED (superseded) | QA isolation battle used VRAM map 1 slot 5 (Magitek conflict) | `monster-tech-v0.6.0` `14d179cfa61e720aa81ea9c4be518df1e13212fa` / `F13B490B` (regression only) |
| TECH v0.6.1 | ACCEPTED / RUNTIME VERIFIED (`TECH_v0.6.1_ENEMY_ASSET_MP`) | custom enemy graphics + palettes (banks FB/FC), new-formation Magic Points | `monster-tech-v0.6.1` `8a55707ff2b4cd1364fdabf75e91422ba90ff8bb` / `289BD3B9`; `production-v0.6.0` `26ebd7d3b1a16bfae94625cead054edc34a1a5b6` / `C9DB005B`; `celes-tech-v0.6.0` `a7ae5d4c1c49ce5cfcbca65de943678b86923fce` / `E2BDA3B1` |
| TECH v0.6.2 | tooling only (no ROM byte) | formation-safety validator, Magitek VRAM matrix, previews | — |
| TECH v0.7 | audit / decision | item architecture: **Option C Signature Equipment Bank** approved (D1-D6) | — |
| TECH v0.7.1 | superseded by v0.7.2 (user found the QA Colosseum black screen) | extended item ids `$100-$13F`, engine, event API, save signature | not pinned (QA ROM `c6ea2b30…` in the v0.7.1 package) |
| TECH v0.7.2 | ACCEPTED (production engine) | Colosseum hotfix of the QA harness; engine unchanged | `production-v0.7.2` `f8f92c81475e14e90adecd541aec19fd251e7e45` / `91346FF2`; `celes-tech-v0.7.2` `2789edb5621954421c1f2819d0b8a7f54739ce90` / `7399F9CA` |
| TECH v0.7.3 | ACCEPTED (QA harness) | Colosseum visual reports = vanilla behaviour; QA party normalisation | `item-tech-v0.7.3` `3a784e0d3df817dd47d796f8b50b8ac34b143b31` / `EB2923BA` |
| TECH v0.8 | ACCEPTED / USER RUNTIME PASS | all 39 signature equipment items `$100-$126`; B-accumulator engine fix | `production-v0.8` `1091d0779c5278f40c6e74648dbfb8cb2ce6818b` / `2F5FB45A`; `celes-tech-v0.8` `e8a96146507f4587f75344f5cea2781ed02e6b72` / `332238AF`; `item-tech-v0.8` `498d62c47477a91d6df7b4619f76bb03e7a1fbb5` / `4A8A7533` |
| **TECH v0.9** | **ACCEPTED / USER RUNTIME PASS** | 8 consumables `$127-$12E`, extended shops + Sell, rare/key items (52 ids), GIVE/TAKE/HAS_RARE, save compat, QA hub | table above |

`build.py --target all` = **24 targets** (3 current v0.9 + 21 frozen), all STATIC PASS, deterministic.

---------------------------------------------------------------------------------------------------------------------

## C. Architecture summary (accepted implementation)

Addresses: SNES `bank:addr`; expansion banks F0-FF map to PC `$300000-$3FFFFF`. Exact byte tables per milestone:
`ff6x_tech/PATCH_TABLE_v*.md`; every patch row (PC/SNES, original → new, consumer, reason) is in each ROM's
`.manifest.json`.

**C1. Expansion banks / allocation strategy.** `ff6x_tech/data/allocations.json` is the single source of truth for every
claimed byte (regions per target, vanilla-space claims, vanilla table repacks, operand retargets, event bits, saved
RAM). `ff6x/romimage.py` enforces: read-only master, hash guard, expansion writes only inside regions active for the
target and only onto pristine `FF`, no overlaps, every vanilla write asserts original bytes, any changed byte without an
owning patch aborts, checksum + complement recomputed. Bank map: F0 `BUILD_METADATA` (F0:0000), `ENGINE_CODE`
(F0:1000-7FFF: dialogue hook F0:1000, NPC router F0:1100, monster routers F0:1200, enemy-gfx router F0:1240); F1-F2
`EVENT_EXPANSION`; F3 `DIALOGUE_PTRS` (F3:0000-3FFF) + F3:4000-F4 `DIALOGUE_TEXT`; F5 `MAP_LAYOUTS`; F6-F7 relocated map
tables (`MAPX_*`); F8-F9 relocated monster / formation / AI / MP tables (`MONX_*`, `FORMX_*`); FA `ITEMX_TABLES`
(FA:0000-7FFF) + `ITEMX_CODE` (FA:8000-FFFF); FB `ENEMYX_PAL` / `ENEMYX_STENCIL`; FC-FD `ENEMYX_GFX`; FE reserved; FF
`QA_HARNESS` (QA targets only). Same-bank stubs live in audited `$FF` padding claims in C0 / C1 / C2 / C3.

**C2. Event hooks.** Event-command operands (`$B2` call, `$C0-$CF` jumps…) are 24-bit with the interpreter adding `$CA`
to the bank → F0-FF reachable natively (F1 = `$27`). Scripts are written in the project's `.evt` language
(`ff6x/eventasm.py`, encodings verified against the disassembly macros) and placed in `EVENT_EXPANSION`. Unused Rev 1
opcodes were turned into FF6X commands: `$66 give_ext_item`, `$67 take_ext_item`, `$68 has_ext_item` (v0.7.1),
`$69 give_rare`, `$6D take_rare`, `$6E has_rare` (v0.9); the assembler refuses them on targets without the engine.

**C3. Dialogue expansion.** Hook `C0:7FBF` (`GetDlgPtr`) → JML F0:1000: dialogue ids `$1000-$1FFF` read 4-byte pointers
from F3:0000 (`lo hi bank 0`), text anywhere in F3-F4 (QA text may use FF via a package's `dlg_org`). `$1000` is the
reserved out-of-range diagnostic. `ff6x/text.py` encodes (DTE-free) and enforces the 219-px line width with the ROM font.

**C4. Map expansion** (v0.4). Trigger / NPC / short + long entrance / treasure tables, map properties (512 rows × 33 B),
layout pointers (1024 × 3 B) relocated to F6-F7; 90 consumer operands retargeted; vanilla records copied unchanged
(old tables left as dead data → reversible). Map ids up to `$1FD` (95 new ids + 9 blank vanilla ids; `$1FE/$1FF` are
engine "parent/previous"). Map packages: `ff6x_tech/maps/<pkg>/` compiled by `ff6x/mapsrc.py` / `mapsrc4.py`
(LZSS `ff6x/lzss.py`, walkability proof). Persistent map state via audited free event / NPC bits.

**C5. NPC routing** (v0.4). Hook `C0:52E6` → JSL F0:1100. A non-special NPC whose 18-bit event field is `$3xxxx` (bank
CD never holds events; 0/1,904 vanilla NPCs use it) is routed through the vector table F7:9000 + 3·index to any 24-bit
address; vanilla and special NPCs take the untouched path; out-of-range → EventReturn CA:5EB3.

**C6. Monster expansion** (v0.5). All monster-indexed tables relocated to F8-F9 for 512 monsters (prop, names, items,
control, sketch, special anim, overlap, gfx prop 543 slots, AI pointers + scripts) and 1024 formations (battle prop,
battle monsters); 71 operands retargeted; routers `MonsterGfxSlot5`, `MonsterGfxSlotSketch`, `ColosseumRangeCheck`
(F0:1200-1230). New monsters are excluded from Rage/Veldt and the Colosseum (8-bit table). Monster sources:
`ff6x_tech/monsters/<id>/`, `ff6x/monsters.py`.

**C7. Enemy graphics / palettes** (v0.6/0.6.1). `MonsterPal` (1024 units) → FB:0000, `MonsterStencil` → FB:4000, custom
4bpp/3bpp tiles → FC (`ff6x/enemygfx.py`, PNG importer); router `EnemyGfxBase` F0:1240 via hook C1:20FF; expansion flag =
MonsterGfxProp byte2 bit5; 16 vanilla bytes shadowed at FB:FFF0 for the empty palette slot. Proven pixel-exact against
vanilla Dark Wind.

**C8. Formation Magic Points** (v0.6). `BattleMagicPoints` (1024 battles) → F8:E000; bound `CPX #$0200` → `#$0400` at
C2:5D98.

**C9. Formation safety / Magitek VRAM matrix** (v0.6.2, tooling). `ff6x/formation_safety.py` validates every EE formation
on the built image (visible field x 8-247 / y 4-150, edge margin <8 px ERROR, <16 px WARNING, window crossing ERROR,
party lane warning); `magitek_possible` mandatory per EE formation; Magitek armor overwrites monster VRAM rows 0-11 ×
cols 12-15 → `data/vram_safety.json` (all-safe maps 2, 8, 9, 10, 11; always unsafe map 1 slot 5, map 7 slot 1, map 12
slot 5). Previews `out/formation_preview/` (`build.py <rom> --preview-only`). Frozen QA formations run in report mode.

**C10. Signature equipment bank** (v0.7.1 engine, v0.8 content). Item ids `$100-$126` = the 39 locked equipment concepts
(13 weapons `$100-$10C`, 7 body `$10D-$113`, 4 helmets `$114-$117`, 2 shields `$118-$119`, 13 relics `$11A-$126`);
`$127-$12E` consumables (v0.9); `$12F-$13C` reserve; `$13D-$13F` QA-only. FA tables: 320-entry ItemProp / ItemName
copies, `XExtFlags` (bit0 defined, bit1 spear, bit2 consumable, bit3 sellable), descriptions, weapon / Jump animation.
Records composed by `patches/equipment_v08.py` from `items/production_v08/equipment.json` (vanilla template supplies
only icon / graphics / animation). Engine source: `asm/item_v09/` (assembled by `ff6x/asm816.py`); 154 v0.7.1 hook sites +
118 long-operand retargets (`patches/item_v071_hooks.py`, `data/item_relocation_v071.json`) + 57 v0.9 sites
(`patches/item_v09_hooks.py`). Never stealable / dropped / metamorphed / thrown / wagered; Gau/Umaro can't equip extended
weapons/shields (validator).

**C11. Item high-bit storage.** Low byte stays in the vanilla inventory/equipment byte; the 9th bit lives in `XBITS`
`$1CF8-$1D23` (32-byte inventory bitmap + 12-byte equipment bitmap) — the Bushido-name block that the EN game writes at
New Game and never reads. SRAM layout unchanged. All producers return the high bit in B; consumers clear it (v0.8 fix:
B := 0 exits; static audit `devtools/b_leak_audit_v09.py`).

**C12. Save signature / version migration.** `XSIG` `$1D24-$1D27` = `58 49 01 FE` (format **version 1**, unchanged in
v0.8 and v0.9). Every load path runs `XSanitize`: legacy/garbage save (no signature) → extended metadata cleared, zero
extended items; signed save → undefined ids removed (never truncated to the low-byte alias), stale bits on empty slots
dropped. Rare block has its own signature (C17). Rev 1, v0.7.x, v0.8 and v0.9 saves load with nothing lost
(`SAVE_MIGRATION_v0.9.md`).

**C13. Extended consumables** (v0.9). `$127-$12E`: Gaia Tonic, Aether Flask, Phoenix Ash, Null Dust, Iron Ration,
Remedy+, Beacon Flare, Magitek Cell (`items/production_v09/consumables.json`, validated by `patches/consumables_v09.py`).
Their records run through the vanilla item-effect code. Low bytes `$27-$2E` are the vanilla katanas, which are never
Item-command usable → in battle `(command == Item && IsCons(lo))` identifies a consumable unambiguously; the battle list
marks consumable rows (UsageFlags bit0) and every C1 id search compares the marker. Field menu: name, usable colour,
use, target, decrement, Arrange — via C3 hooks (`XC3_*`).

**C14. Battle consumable reconciliation.** Battle Item command: target context (`XCURCMD $1E36`), extended attack-name
window + item animation (`XATKX $1E37`, `XBTLNAME $1E3E`, table FA:5000), quantity −1 at the command, held item
(`XHELD $1E38-$1E3B`) returned as the 9-bit id if the user can't act, and `XBattleEndInv` (`asm/item_v09/c1x.s`) merges
the battle list back into the inventory (pass 1 non-equipment slots with the marker bit, pass 2 merge at
extended-equipment positions). C2 logic lives in FA behind small JSL stubs (`XB_*`), C2 stub space is 912 B.

**C15. Extended shops.** `XShopProp` relocated to FA:5400 (144 × 9 B; vanilla shops `$00-$7F` copied unchanged) +
`XShopPropHi` FA:5940 (high bits). Shops `$80` / `$81` defined (`items/production_v09/ext_shops.json`); `$82-$8F` empty.
Owned / equipped counts and prices computed from the 9-bit record (`XSHOPCURHI $1E3C`); purchase refused when no stack
and no empty slot.

**C16. Sell handling.** The two vanilla Sell routines are replaced (overrides I420 / I421 → `XC3_SellLdaX` /
`XC3_SellLdaY`): only items with `XExtFlags` sellable (Gaia Tonic, Null Dust, Iron Ration, Remedy+) are selectable from
the extended range, at ½ price; signature equipment is never sellable; slot + high bit cleared when sold out.

**C17. Rare / key-item storage.** 52 logical rare ids: 0-19 = vanilla event bits `$1D0 + id` (unchanged), 20-51 = FF6X bits
in `XRARE` `$1E1D-$1E20` with signature `XRSIG` `$1E21-$1E22` (`$52`, xor(XRARE)^`$A5`); `XRareDef` FA:5080 masks the
defined ids (QA `FFFFFFFF`, production `1F000000` = ids 20-24). Names `XRareName` FA:5100 (52 × 13), descriptions
`XRareDescPtr` FA:5090 → `XRareDescText` FA:5E80. Locked key items: 20 Darill's Token, 21 Concord Sigil, 22 Cinder
Sigil, 23 Triune Sigil, 24 Broken Seal (`items/production_v09/rare_items.json`); QA fillers 25-51
(`items/qa_v09/qa_rare_items.json`, QA ROM only).

**C18. Rare Item paging.** 20 per page (vanilla buffer), page in `XRAREPAGE $1E3D`; Down on the last row / Up on the first
row / R / L change the page; a page change redraws the list and restarts BigTextTask (state 0) so the description does
not overlap. Opens on page 0.

**C19. GIVE / TAKE / HAS APIs.** Equipment + consumables: `$66 id16` / `$67 id16` / `$68 id16 sw16` (stack to 99, first
free slot, inventory full → nothing; TAKE affects inventory only; HAS counts inventory + equipment). Rare: `$69 id`,
`$6D id`, `$6E id sw16` for ids 0-51 (ids ≥ 52 and undefined FF6X ids ignored; signature rewritten). `.evt` syntax and
examples: `RARE_ITEM_EVENT_API_v0.9.md`.

**C20. QA hub** (QA ROM `item-tech` only; package `events/qa_access_v09/`, dialogue at FF:1000). Top menu:
`Consumables v0.9` / `Rare items v0.9` / `More…` → `Stress / save` / `Equipment v0.8` / `More…` → `Older tests` /
`Save Point` / `Cancel`. Grants, removals, toggles, party presets, test battles (ROM labels, never WRAM-injected
battles), extended shops via ROM label `QaShop80`. Older suites reach the moved menus through env variables
(`FF6X_QA_V08_ROOT`, `FF6X_QA_ITEM_ROOT`, `FF6X_QA_PREFIX`, `FF6X_QA_SAVE_PICKS`; see `tools/run_regression_v09.sh`).

Transient context bytes `$1E36-$1E3F` are cleared at New Game and load (`ClrTrans`); the allocation table is
`saved_ram_allocations` in `allocations.json`.

---------------------------------------------------------------------------------------------------------------------

## D. Source-of-truth files (paths relative to `ff6x_tech/`)

| What | Path |
|---|---|
| Builder (targets, pinned hashes, outputs) | `build.py`, `BUILD.bat` (Windows drag-and-drop) |
| Builder library | `ff6x/` (`romimage.py`, `allocations.py`, `hirom.py`, `asm816.py`, `asm65816.py`, `op65816.py`, `eventasm.py`, `text.py`, `lzss.py`, `tables.py`, `maptables.py`, `mapsrc.py`, `mapsrc4.py`, `monsters.py`, `enemygfx.py`, `formation_safety.py`, `formation_preview.py`, `patchfmt.py`, `png.py`) |
| Patch modules | `patches/` (`core.py`, `dialogue_hook.py`, `map_foundation.py`, `map_v04.py`, `monster_v05.py`, `enemy_v06.py`, `item_v071.py`, `item_v071_hooks.py`, `equipment_v08.py`, `item_v09.py`, `item_v09_hooks.py`, `consumables_v09.py`, `celes_tech.py`, `qa_access.py`, `evtest.py`, `legacy_v01.py`) |
| Allocation manifest | `data/allocations.json` (+ `data/baseline.json` clean-ROM identity) |
| Relocation data | `data/map_relocation_v04.json`, `data/monster_relocation_v05.json`, `data/enemy_relocation_v06.json`, `data/item_relocation_v071.json`, `data/vram_safety.json` |
| Equipment JSON (39 items) | `items/production_v08/equipment.json` |
| Consumable JSON (8) | `items/production_v09/consumables.json` (+ `author_v09.py` that authored the v0.9 JSON files) |
| Rare / key-item JSON | `items/production_v09/rare_items.json`; QA fillers `items/qa_v09/qa_rare_items.json` |
| Extended shops JSON | `items/production_v09/ext_shops.json` |
| QA items | `items/qa_v071/qa_items.json` (`$13D-$13F`) |
| Event sources | `events/<package>/` (`package.json`, `records.json`, `dialogue.json`, `events.evt`): `celes_annex_tech`, `celes_qa_access`, `map_tech_v04`, `qa_access_v04 … qa_access_v09` |
| Map sources | `maps/celes_annex_tech/`, `maps/map_tech_a/`, `maps/map_tech_b/` |
| Monster / formation sources | `monsters/tech_0180/`, `monsters/tech_0181/`, `monsters/tech6_0180/` … `monsters/tech6_0183/`, `formations/*.json`, `formations/examples/` |
| ASM sources | `asm/item_v09/` (**current**: `core.s`, `c0.s`, `c1x.s`, `c2.s`, `c3.s`, `v09.s`), `asm/item_v08/` (frozen v0.8 engine), `asm/item_v071/` (frozen v0.7.x engine); small routers are inline in `patches/*.py` |
| Self-tests | `tools/selftest.py` (114 checks incl. fail-closed guards) |
| Emulator regression | `tools/emu_*.py` (harness `tools/emu_harness.py`, menu nav `tools/emu_menu_nav.py`); v0.9 suites `emu_cons_v09.py`, `emu_cons_battle_v09.py`, `emu_rare_v09.py`, `emu_stress_v09.py`; runner `tools/run_regression_v09.sh` |
| Handoff verification | `tools/handoff_verify_v09.py` |
| Patch tables / docs generators | `tools/patch_table.py`, `tools/patch_table_v09.py`, `tools/consumable_docs_v09.py`, `tools/equipment_docs_v08.py`, `tools/user_qa_v09.py`, `tools/sheet_v09.py`, `tools/equipment_sheet_v08.py` |
| Static audits / devtools | `devtools/` (`b_leak_audit_v09.py`, `item_consumer_audit_v071.py`, `saved_ram_audit_v071.py`, `rev1_insn_index.py`, `asm_oracle.py`, …); outputs in `audits/` |
| Docs (per milestone) | `README_TECH_v*.md`, `REGRESSION_REPORT_v*.md`, `KNOWN_RISKS_v*.md`, `PATCH_TABLE_v*.md`, `USER_QA_TECH_v*_VI.md`; v0.9: `CONSUMABLE_*_v0.9.*`, `RARE_ITEM_*_v0.9.*`, `EXTENDED_SHOP_AUDIT_v0.9.md`, `ITEM_CONSUMER_AUDIT_v0.9.md`, `SAVE_MIGRATION_v0.9.md`; `docs/ACCEPTED_BASELINES_v0.*.md`, `docs/history/` |
| Item architecture decision | `ITEM_ARCHITECTURE_DECISION_v0.7.md` (+ the original `FFVI_Expanded_Edition_MODEL_HANDOFF_START_v0.7.1.zip` at the package root) |
| Accepted ROM manifests / patches | `out/FF6X_Rev1_TECH_v0.9_{PRODUCTION,CELES_TECH,CONSUMABLE_RARE_QA}.{sfc,bps,ips,manifest.json,diff.csv}`, `out/BUILD_SUMMARY.json`, `out/HASHES_v0.9.txt`, `HASHES_v0.9.txt`, `out/DELTA_v0.8_to_v0.9.csv` |
| Emulator evidence | `out/emulator_v09/` (logs, JSON reports, screenshots), contact sheets `out/*_V09_*SHEET.png` |
| Colosseum root-cause reference ROM (4th argument of `tools/run_regression_v09.sh`) | `out/reference_v0.7.1/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc` (+ `.manifest.json`; handoff zip only, `out/` is git-ignored) |

---------------------------------------------------------------------------------------------------------------------

## E. Accepted runtime QA (what the user personally tested)

| Version | User runtime result |
|---|---|
| v0.1 | 4 MiB expansion + F0 reads; save / reset / load OK |
| v0.2 | expansion dialogue, event hook/bridge, persistent bit OK |
| v0.3 / v0.3.1 | Annex slice (map, NPC, dialogue, event battle, reward, save/load) OK. **QA-only issue** (`docs/KNOWN_QA_ISSUE_v0.3.1.md`): saving at the opening-Magitek QA tile reloads the walking field sprite (vanilla never allows a save there); production save engine intentionally not modified |
| v0.4 | relocated tables, new map ids, NPC routing, triggers, short/long entrances, persistent map state OK |
| v0.5 | monster ids `$180/$181` together, names/stats/AI, targeting, victory, return, save/load, vanilla regression OK; TESTMOB B "garbled" look later proven palette-only (placeholder) |
| v0.6.0 → v0.6.1 | v0.6.0 Dark Wind corruption = vanilla Magitek VRAM overlap (map 1 slot 5), not routing → v0.6.1 accepted: graphics routing, custom assets/palettes, Magic Points (`$241` = 3, `$240` = 0), save/load, vanilla regression. Steal/Sketch/Control on custom monsters: emulator poke only (**user NOT TESTED**) |
| v0.7.1 → v0.7.2 | user found the QA Colosseum black screen: the QA harness ran event `$9A` alone (same bytes black-screen on clean Rev 1); v0.7.2 calls the vanilla receptionist branch CB:78D9 → accepted |
| v0.7.2 → v0.7.3 (Colosseum QA-state findings) | Terra extra sprite and invisible Wedge/Vicks in the Colosseum = **vanilla Rev 1 behaviour** in the opening-Narshe QA state (Magitek status, temp characters in records 14/15); QA menu now normalises the party → accepted (`COLOSSEUM_QA_STATE_v0.7.3.md`) |
| v0.8 | **PASS**: 39 items OK; equip restrictions / stats OK; battle / boss graphics OK; Optimum / Empty / Arrange OK; save / load OK; Sell / Colosseum exclusion OK; smith OK |
| v0.9 | **PASS** (user report: "TECH v0.9 has now been USER RUNTIME TESTED and PASSED"). The consolidated checklist it followed, `USER_QA_TECH_v0.9_VI.md`, covers consumables in field / battle / shops / Sell, the Rare Items menu + paging + descriptions, the event API via the QA hub, save / load / migration and the stress steps |

Important fixes along the way: v0.3.1 QA access harness; v0.6.1 Magitek-VRAM-safe QA formations; v0.7.2 Colosseum
harness; v0.8 B-accumulator engine fix (`ENGINE_FIX_v0.8_B_ACCUMULATOR.md`); v0.9 internal fixes before packaging
(consumables took the spell path in battle — carry clobbered; `DIRK` after consumable rows; rare description overlap
after L/R).

---------------------------------------------------------------------------------------------------------------------

## F. Known risks / deferred work (open)

Full lists: `ff6x_tech/KNOWN_RISKS_v0.9.md` (R1-R44), `KNOWN_RISKS_v0.6.2.md` (F1-F5), older `KNOWN_RISKS_v*.md`.

1. **Creative Lock / Tech Gate spreadsheets are not in the workspace.** Only names / locked lines quoted in the
   decision docs exist here. Any production content must wait for the user to supply them.
2. **v0.9 derived values (R33)**: consumable effects, power, targeting, prices, shop placement, rarity, animation;
   key-item arcs, sources, prerequisites (Triune Sigil ← both sigils), descriptions — all DERIVED, listed per item in
   the JSON `derived` fields; need creative confirmation. Also v0.8 derived values (smith GP 18000/20000/24000, smith
   prerequisites R23; 11 armor items with `arc_reward_tbd` R22; 12-char display names R21; balance notes R31).
3. **Deferred custom relic ASM** (R14, `FALLBACK_EFFECTS_v0.8.md`): Runic Crest, Maduin's Locket, Doma Crest, Darill's
   Coin, Beastheart, Engineer's Badge, Master's Cord ship with BAL-18 stat fallbacks.
4. **Formation safety gaps**: back / pincer / side attack placements not validated (F2 — disable those attack types for
   EE formations unless reviewed); only the Magitek party state audited for VRAM conflicts (F3 — other special party
   states unchecked); monster–monster overlap not flagged (F4); transforming bosses not modelled (F5); visible field
   measured in snes9x only (F1).
5. **Vanilla quirks kept on purpose**: katana rows show `DIRK` in battle Item/Throw lists (R37); hand-first exchange +
   B duplicates/loses a hand item (R10, vanilla bug); Colosseum invisible temp characters / Magitek fighter (R18, R19);
   Genji/Gauntlet re-evaluate hands on leaving the Relic menu (R28); `$40` char_prop drops equipment (R25 — future
   story scripts must not re-run `$40` on a character wearing signature gear); Sketch drawn behind Terra.
6. **Non-blocking timing differences**: 26/576 vanilla formations reach the battle screen 1 frame later (R12);
   monster gfx router +1 frame fade-in in 3/576 formations (v0.6 R5); event `$80` give loop up to ~4 frames longer
   (R16). Data identical in every case.
7. **One-way downgrade** (R1): v0.9 saves in older builds lose the consumables (removed cleanly).
8. **Design rules for future work**: consumables rely on katanas `$27-$2E` never being Item-usable (R36); extended
   weapons/shields never for Gau/Umaro (R8); dialogue can't print extended item names (R7); extended shops `$82-$8F`
   empty (R40); TAKE_EXT_ITEM ignores equipped items (R3); full-inventory GIVE / buy silently does nothing (R4, R41).
9. **Test-only assumptions**: emulator evidence = snes9x via stable-retro; POKE marks test-only RAM setup; battles are
   started from ROM labels only (R29); QA presets initialise all permanent characters (R30); QA menus in the frozen
   QA ROMs differ by version (R44); Colosseum harness assumes switch `$1EF` = 0 (R17); the v0.7.1 QA ROM is needed only as
   the Colosseum root-cause reference (copied into the handoff zip as
   `ff6x_tech/out/reference_v0.7.1/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc` + manifest; originally from the v0.7.1 package).
10. Acquisition of all 39 equipment items and 5 key items is **bound, not placed** — no story event gives them yet (R22).

---------------------------------------------------------------------------------------------------------------------

## G. Work NOT started — must remain untouched until the user chooses a milestone

- final Celes production quest (only the TECH Annex slice with a VALE placeholder exists)
- Terra production arc · Cyan production arc · Shadow / Relm production arc · Figaro production arc · Setzer production arc
- Forgotten Age production content · Vael / First Magi production content
- final custom enemy art (Rust Hound, Annex Guard, Magitek Praetor …; only QA placeholder sprites exist)
- final map production (only TECH proof maps)
- deferred special relic ASM (item 3 above)
- ending implementation, post-Kefka content
- any balance redesign beyond the accepted values; new items / maps / enemies / quests

---------------------------------------------------------------------------------------------------------------------

## H. Work in progress / unfinished files

There is **no unfinished feature branch or partial implementation**: everything in the build is accepted v0.9.
Branches: `claude/festive-mayer-i6uurp` (all work), `main` (initial commit only).

| Path | Purpose | Status | Safe to keep / delete | In an accepted build? |
|---|---|---|---|---|
| `ff6x_tech/wip/session_scratch_v07_v09/` | the sessions' debug probes, regression runners, drafts (see its `README_EXPERIMENTAL.md`) | EXPERIMENTAL, hard-coded scratch paths | keep (dead ends documented); deleting is harmless | **no** |
| `ff6x_tech/asm/item_v071/`, `ff6x_tech/asm/item_v08/` | frozen engines of v0.7.x / v0.8 | OBSOLETE for new work, REQUIRED for the frozen targets | **keep** (frozen hashes depend on them) | yes (v0.7.2/0.7.3, v0.8) |
| `ff6x_tech/events/qa_access_v04 … qa_access_v08`, `celes_qa_access` | older QA hubs | QA-only, frozen | keep (frozen QA targets) | yes (QA ROMs only) |
| `ff6x_tech/audits/eventbit_allocation_PROPOSED.json` | proposed pool of event bits for future story arcs | PROPOSAL, unused by any build | keep | no |
| `ff6x_tech/items/production_v09/author_v09.py` | script that authored the v0.9 JSON (derived values) | tooling; JSON is the source of truth | keep | no (its JSON output is) |
| `ff6x_tech/docs/history/` | historical start prompts and early READMEs | history | keep | no |
| `ff6x_tech/tools/emu_*` older suites (`emu_map_*`, `emu_monster_*`, `emu_mp_diff`, `emu_sketch_diff`, `emu_smoke`, `emu_qa_access`, `emu_save_load`) | v0.3-v0.6 differential / proof suites | QA tooling; written for the older QA ROMs | keep | no |
| repository-root `FF6X_TECH_v0.6.2 … v0.9_*.zip` | per-milestone QA packages | released packages (not in the handoff zip; SHA-1s in `HANDOFF_ZIP_MANIFEST.txt`) | keep in repo | — |

Unfinished ideas (notes only, nothing coded): enumerate remaining special party states for VRAM safety; back/pincer
placement validator; relic-ASM module design (BAL-18 fallbacks are the current behaviour); story placement of the 39
equipment + 5 key items via the GIVE APIs.

---------------------------------------------------------------------------------------------------------------------

## I. Recommended next step (do NOT begin it)

**Recommendation:** a no-ROM-change **"Creative source recovery & design confirmation" gate**, then the first
production-content milestone, **TECH/CONTENT v1.0 — Celes "Echoes of the Empire" production quest**, because every
engine capability that quest needs is accepted (maps, NPC routing, dialogue, events, monsters + custom graphics + MP,
formation safety, signature equipment incl. Runic Crest / Imperial Saber, key items, shops).

Prerequisites before any code:
1. User supplies the Creative Lock / Tech Gate spreadsheets (or confirms the derived v0.8/v0.9 values, R23/R33).
2. Locked Celes arc script, map concepts, and boss/monster concepts (Magitek Praetor, Annex Guard, Rust Hound) + art.
3. Decide whether Runic Crest's special effect (deferred relic ASM) is in scope or keeps its BAL-18 fallback.
4. Decide formation rules for the arc's battles (back/pincer/side allowed? special party states?) — F2/F3.
5. Event-bit and dialogue-id budget for the arc from `audits/eventbit_allocation_PROPOSED.json`.

Alternative if creative sources are not ready: a pure TECH gate for the deferred relic ASM module (item 3 in §F).

---------------------------------------------------------------------------------------------------------------------

## J. New-session startup checklist

1. Read this file (and `PROJECT_STATE_v0.9.json`), then `ff6x_tech/README_TECH_v0.9.md` and `ff6x_tech/KNOWN_RISKS_v0.9.md`.
2. Verify the clean ROM: `sha1sum "Final Fantasy III (USA) (Rev 1).sfc"` → `057ada1c641e3e0b3ca34e6e4f4eb1b05a87143a`
   (CRC32 `C0FA0464`).
3. Verify the accepted v0.9 hashes: `cd ff6x_tech && python3 tools/handoff_verify_v09.py "../Final Fantasy III (USA) (Rev 1).sfc" /tmp/ff6x_verify out`
   → must print `HANDOFF VERIFY PASS` (it rebuilds all 24 targets, checks the three accepted SHA-1/CRC32, BPS/IPS,
   and compares with the packaged `out/`).
4. Run the self-tests: `python3 tools/selftest.py "../Final Fantasy III (USA) (Rev 1).sfc"` → `ALL 114 SELF-TESTS PASS`.
5. Reproduce the current build: `python3 build.py "../Final Fantasy III (USA) (Rev 1).sfc" --target all --out out`
   (deterministic; optional emulator regression: `tools/run_regression_v09.sh`, expected counts in
   `REGRESSION_REPORT_v0.9.md`).
6. Only then propose the next milestone (§I) to the user and wait for approval. Keep committing only to the agreed
   branch; never edit the master ROM; keep STATIC / EMULATOR / USER RUNTIME separate.
