# TECH v0.8 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

All results are on the **final** v0.8 build: production `1091d077…`, celes-tech `e8a96146…`, equipment QA `498d62c4…`
(`HASHES_v0.8.txt`). Emulator = snes9x core via stable-retro, driving the real game through its menus, event engine
and battles. **POKE** marks test-only RAM writes (setup, identical in every compared run). This is **not** user
runtime QA. Reports, logs and screenshots: `out/emulator_v08/`; contact sheets: `out/EQUIPMENT_V08_WEAPONS_SHEET.png`,
`out/EQUIPMENT_V08_MENUS_STRESS_SHEET.png`.

## 1. Static
| Check | Result |
|---|---|
| Clean input asserted (SHA-1 `057ADA1C…`, CRC32 `C0FA0464`); master ROM never written | PASS |
| 21/21 targets build; frozen accepted baselines byte-exact (SHA-1 asserted): production / celes-tech v0.7.2, item-bank QA v0.7.3, and every older baseline (v0.1-v0.6.1) | PASS |
| Determinism: two full builds, 110 output files + formation previews | PASS (0 differences) |
| Selftest | **88/88 PASS** (new: 43b v0.8 vs v0.7.2 delta, 43c all 39 records decode to source, 43d engine source = v0.7.1 + B-reset exits only, 44 defined/spear flags exactly `$100-$126`, 46 v0.8 validators fail closed in 13 cases) |
| v0.8 validators (`patches/equipment_v08.py`): 39 items, ids `$100-$126` once, locked codes, category counts, unique names/symbols/reward ids/event symbols, users permanent, Gau/Umaro rule, power envelope 184-222, stat ranges, spear flag, one-time acquisition, GP only for smith, BAL-18 fallback for every optional-ASM relic, text limits (12-char name, 2×28 description) | PASS (build refuses otherwise) |
| BPS and IPS of the three v0.8 ROMs re-applied to clean Rev 1 → byte-identical ROMs | PASS |
| Delta v0.7.x → v0.8 (`PATCH_TABLE_v0.8.md`, `out/DELTA_v0.7.x_to_v0.8.csv`): production 3453 B = FA item tables + metadata + checksum + C3 engine fix; QA 7366 B (+ QA-only areas) | PASS |
| B-accumulator static audit (`devtools/b_leak_audit_v08.py`, every B-producing hook): v0.7.1 engine 14 findings incl. the real SortValidEquip defect; **v0.8 engine 1 finding, unreachable** (`ENGINE_FIX_v0.8_B_ACCUMULATOR.md`) | PASS |

## 2. Emulator — the 39 production items (new suites)
### `tools/emu_equip_v08.py` → **21/21 PASS**
| Check | Result |
|---|---|
| T1 all 39: ItemProp record, icon (= template's vanilla icon), 12-char name, description, defined/spear flags, weapon animation and Jump animation (= template weapon's vanilla entries) match the source | PASS |
| T2 vanilla $00-$FF ItemProp / ItemName records unchanged in the relocated tables | PASS |
| T3 no extended name equals its low-byte vanilla alias name (an alias would be visible in every UI) | PASS |
| G1 QA 'Grant all 39': each of $100-$126 exactly once (qty 1), in 39 inventory slots | PASS |
| G2 grant twice: each $1xx stacks to x2 (quantity), still 39 slots | PASS |
| G3 QA 'Remove all 39': no production item left in the inventory | PASS |
| G4 grant by type: weapons = the 13 weapons, armor = the 13 body/helmet/shield, relics = the 13 relics | PASS |
| K1 all 39: HAS=1 -> TAKE -> qty 0, HAS=0 -> GIVE -> qty 1, HAS=1 (event API $68/$67/$66) | PASS |
| K2 vanilla inventory untouched by the event API (only $1xx present) | PASS |
| S1 smith, not enough GP (New Game 3000 GP): nothing given, nothing charged | PASS |
| S2 smith purchase: Tempered Edge $100 given once, 18000 GP charged | PASS |
| S3 smith, already owned (HAS_EXT_ITEM): nothing given, nothing charged | PASS |
| S4 smith, inventory full: GIVE cannot place it -> HAS=0 -> 18000 GP refunded, nothing truncated | PASS |
| N1 nearly full inventory (one free slot): the reward lands in the free slot | PASS |
| E1 equip matrix from the game's own Equip/Relic lists, 14 permanent characters x 39 items, equals the source definitions (Umaro: relic menu only, as vanilla) | PASS |
| E2 vanilla items in the same lists follow their vanilla equip words (no vanilla regression) | PASS |
| A1 all 39 equipped through the menus on a valid character: stats change by exactly the item's power/hit/MDef/Vigor/Speed/Stamina/Mag.Pwr/Evade/MBlock, elements (absorb/null/weak/half/weapon element), status immunity and relic bits; the slot holds the 9-bit id | PASS |
| A2 Remove (event $8D) returns every item to the inventory with its 9-bit id | PASS |
| X1 vanilla shop $05 sells $00/$01/$0A/$0B = low bytes of Tempered Edge $100, Imperial Saber $101, Concord Brush $10A, Gale Lance $10B (all owned): owned counts are 0 (no alias), nothing for sale is $1xx | PASS |
| X2 Sell: production items cannot be selected; inventory unchanged | PASS |
| X3 Colosseum: production items cannot be wagered; inventory unchanged | PASS |

### `tools/emu_equip_battle_v08.py` → **9/9 PASS**
W1 / J1 / O1 fork one in-battle state: the extended run and the same state continued with the template vanilla
weapon in hand (only the hand item id differs) must render every sampled frame identically.

| Check | Result |
|---|---|
| W1 all 13 weapons: Fight uses animation number $C0+low byte (the template run uses the template's id+1), battle power differs from the template weapon's by exactly the power difference, hit rate = the item's, and every rendered frame of the attack equals the same battle with the template vanilla weapon in hand (no Brush alias, no unarmed) | PASS |
| J1 Jump with Sandpiercer / Gale Lance (POKE: command Jump) renders every frame like the same battle with the template spear (Partisan / Aura Lance) in hand | PASS |
| G1 Genji Glove: Raider Knife R + Darill's Dirk L equipped (9-bit ids), battle powers 198/202 (+ Locke's offset measured in W1), both animation numbers ($C3, $C8) used by Fight | PASS |
| P1 battle end (Genji run): Locke's two extended weapons and the inventory are unchanged | PASS |
| H1 Gauntlet + Tempered Edge (two-hand flag, other hand empty): Gauntlet effect ($11D8 bit 3) active and the weapon's two-hand flag kept in battle (C2 clears it without Gauntlet), Fight uses animation $C0 | PASS |
| O1 Offering + Moonless: the multi-strike Fight (Offering) is identical to the same battle with the template Hardened in hand - every sampled frame, the number of enemy HP drops and the enemies' HP afterwards - and uses the extended animation number $C6 (template: $29) | PASS |
| R1 Runic with Imperial Saber (Celes) and Bushido with Doma Edge (Cyan): command present and enabled | PASS |
| I1 battle Item list: every slot holding a $1xx item is blank ($FF) - not usable, not throwable, no alias | PASS |
| P2 battle end: inventory with all 39 production items unchanged | PASS |

### `tools/emu_equip_stress_v08.py` → **13/13 PASS**
| Check | Result |
|---|---|
| C1/D1 19 production items worn at once across the party (Terra: 6 extended slots) through the menus | PASS |
| D2 worn items left the inventory; the other 20 production items are still there | PASS |
| B1 Arrange with 136 vanilla kinds + 20 production items: every 9-bit id and quantity kept | PASS |
| L1 Optimum (vanilla + new competing): no duplication or loss of any item, every chosen item equippable | PASS |
| L2 Optimum keeps vanilla where it is stronger: Terra and Locke (optimized first) take Illumina and Ragnarok (255), not a signature sword (<= 222) | PASS |
| L3 Optimum picks, for every slot, the highest attack / defense power among the items the character can equip - extended and vanilla ranked by their own properties (v0.8 fix: equip-list sort keys) | PASS |
| M1 Equip -> Empty: Terra's weapon/shield/helmet/armor ($102/$118/$114/$10F) return with their 9-bit ids; relics stay | PASS |
| H1 normal battle with the extended party: equipment and inventory reconciled unchanged | PASS |
| I1 boss-style battle (vanilla event battle 64: Whelk) with the extended party: battle runs and returns, equipment unchanged | PASS |
| G1 Colosseum with Terra wearing 6 production items: battle entered, return with control, all party equipment unchanged | PASS |
| E1 save -> power cycle -> Continue: 20 production items in the inventory, 19 worn across the party and the extension bitmaps preserved exactly | PASS |
| P1 the v0.8 QA save in the v0.8 PRODUCTION ROM: every production item kept (inventory and worn), nothing truncated | PASS |
| F1 legacy Rev 1 save: no phantom production item on load (Dirk/MithrilKnife/Kodachi stay vanilla); grant all 39; save; power cycle; load: all 39 + the vanilla items preserved | PASS |

## 3. Emulator — regressions rerun on the v0.8 ROMs
| Suite | ROM | Result | Covers |
|---|---|---|---|
| `tools/emu_item_tech.py` | v0.8 QA | **10/10** | New Game signature/zero, GIVE/TAKE/HAS, vanilla `$80/$81` never merge with extended ids, undefined ids ignored |
| `tools/emu_item_qa.py` | v0.8 QA + v0.8 production | **33/33** | names/icons/descriptions, equip + stats, Remove/Empty, Optimum, Arrange, shop/Sell/Colosseum lists, save → power cycle → load, garbage + genuine Rev 1 saves, QA save in production |
| `tools/emu_item_battle.py` (`FF6X_QA_ITEM_ROOT=1,0`) | v0.8 QA (+ clean Rev 1 differential) | **17/17** | battle hand logic, weapon / Jump animation, hand exchange, battle end, `$8D` |
| `tools/emu_enemy_tech.py save` (`FF6X_QA_PREFIX=1,1`) | v0.8 QA | **18/18** | v0.6.1 custom monsters, AI, MP, Dark Wind isolation, enemy graphics pixel-exact, save |
| `tools/emu_enemy_tech.py load` | v0.8 QA | **11/11** | Continue, custom battle after load, map test A, routed NPC, Celes Annex, vanilla Guard battle |
| `tools/emu_enemy_tech.py cmds` | v0.8 QA | **6/6** | Steal / Sketch / Control on custom monsters (POKE) |
| `tools/emu_celes_suite.py` | v0.8 celes-tech | **24/24** | Celes Annex dialogue hook, map / NPC / door / battle / reward / exit |
| `tools/emu_colosseum.py` (+ v0.6.0 / v0.7.2 / **v0.8 production** differential) | v0.8 QA, Rev 1 | **60/60** | Colosseum fight / cancel / win / loss, real receptionist on map $19D: frames, inventory, return identical to Rev 1 (v0.8 production included) |

## 4. Map / formation / Magitek VRAM
Not rerun as a full differential: production v0.8 differs from v0.7.2 only in the FA item tables, the C3 *menu*
engine stubs / C3 hook operands, metadata and checksum. No map, formation, monster, graphics or battle-engine (C2)
byte changed (selftest 43b), so the v0.7.1 differential results carry over: 412/412 maps and 576/576 formations
engine-data identical to v0.6.0 (`REGRESSION_REPORT_v0.7.1.md` §3). Emulator evidence on v0.8: custom monsters /
enemy graphics pixel-exact (save 09b), formation MP, map test, Colosseum. The item-tech build regenerates its
formation-safety / Magitek VRAM report (`FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.formation_safety.json`, unchanged QA formations,
$242 slot 0 the known non-blocking placement).

## 5. Findings during v0.8 QA
| Finding | Disposition |
|---|---|
| **Engine:** extended-id high bit left in B; `SortValidEquip` used it in a 16-bit `TAY` → wrong Equip-list order / Optimum choice with extended items (no loss or duplication) | **fixed** in `asm/item_v08` (B := 0 exits); frozen v0.7.x unchanged; static audit + stress L2/L3 (`ENGINE_FIX_v0.8_B_ACCUMULATOR.md`, R32) |
| Two shortened names had no full locked name in-game ($10A ConcordBrush, $10F MagisterRobe) | descriptions now start with the full locked name |
| Test harness only (no ROM change): save menu pressed too soon after an event (F1); A1 Battle Power expectation (the menu's fist is power 10); X3 started from a shop exit; W1/J1/O1 two separate battles desynchronize (replaced by in-battle fork); solo test characters without armor died before their turn; Genji / Gauntlet flags are `$11D8` bits 4 / 3 ($2E6E+slot / $3C58) | fixed in the test tools |
| Leaving the Relic menu with Genji Glove re-arranges the hands (vanilla) | documented (R28, user guide step 16) |
| The boss test battle (vanilla event battle 64, Whelk) shows its scripted "VICKS: Hold it!" line | vanilla script text, expected |

**STATIC PASS · EMULATOR PASS · USER RUNTIME PASS** (user report: 39 items OK; equip restrictions / stats OK; battle / boss graphics OK; Optimum / Empty / Arrange OK; save / load OK; Sell / Colosseum exclusion OK; smith OK).
