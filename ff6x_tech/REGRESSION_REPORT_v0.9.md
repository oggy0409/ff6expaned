# TECH v0.9 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

All results are on the **final** v0.9 build: production `99cd74df…`, celes-tech `e4c07031…`, consumable / rare QA
`e1136805…` (`HASHES_v0.9.txt`). Emulator = snes9x core via stable-retro, driving the real game through its menus, event
engine, shops and battles. **POKE** marks test-only RAM writes (setup, identical in every compared run). This is **not**
user runtime QA. Logs, JSON reports and screenshots: `out/emulator_v09/`; contact sheets:
`out/CONSUMABLE_V09_MENUS_SHEET.png`, `out/CONSUMABLE_V09_BATTLE_SHEET.png`, `out/RARE_ITEMS_V09_SHEET.png`,
`out/STRESS_V09_SHEET.png`.

## 1. Static
| Check | Result |
|---|---|
| Clean input asserted (SHA-1 `057ADA1C…`, CRC32 `C0FA0464`); master ROM never written | PASS |
| 24/24 targets build; frozen accepted baselines byte-exact (SHA-1 asserted): **v0.8 production / celes-tech / equipment QA** (`1091d077…`, `e8a96146…`, `498d62c4…`), v0.7.2 / v0.7.3 and every older baseline | PASS |
| Determinism: two full builds into separate directories, every output file compared | PASS (0 differences) |
| Selftest | **114/114 PASS** (new: 47 v0.9 definitions, 48 v0.9 vs accepted v0.8 delta, 49 rare event opcodes only in v0.9 targets, 50 v0.9 validators fail closed in 21 cases, 51 saved-RAM allocations inside the audited free bytes) |
| v0.9 validators (`patches/consumables_v09.py`): 8 consumables at `$127-$12E` once, locked codes CN-01..08, exclusions (no steal / drop / throw / wager / equip), sellable = sold, known statuses, revive restores HP, derived-field lists, no battle-usable vanilla alias; 5 key items KI-01..05, no combat stats, ids / names, QA fillers only 25-51; shops `$80-$8F` sell only defined consumables + vanilla | PASS (build refuses otherwise) |
| BPS and IPS of the three v0.9 ROMs re-applied to clean Rev 1 → byte-identical ROMs | PASS |
| Delta v0.8 → v0.9 (`PATCH_TABLE_v0.9.md`, `out/DELTA_v0.8_to_v0.9.csv`): production 8769 B = FA engine + tables + metadata + checksum + stub claims + 57 hook sites + moved-stub operands; QA 18468 B (+ QA-only hub / fillers) | PASS |
| B-accumulator static audit (`devtools/b_leak_audit_v09.py`, every B-producing hook incl. the v0.9 ones): **1 finding, the known unreachable v0.8 one** (I304, no static caller) | PASS |
| Item consumer audit (`ITEM_CONSUMER_AUDIT_v0.9.md`): every Rev 1 consumer the extended ids can reach accounted for (118 relocated operands, 152 unchanged hooks, 2 replaced Sell routines, 57 new v0.9 hooks; Rev 1 bytes re-asserted at build) | PASS |

## 2. Emulator — v0.9 suites (new)
### `tools/emu_cons_v09.py` (field, shops, Sell, exclusions) → **28/28 PASS**
| Check | Result |
|---|---|
| T1 all 8 consumables: ItemProp record (every byte from the source), blank icon + name, description, XExtFlags, item animation entry | PASS |
| T2 the 39 v0.8 equipment records unchanged · T3 vanilla `$00-$FF` ItemProp / ItemName and vanilla shops `$00-$7F` byte-identical in the relocated tables | PASS |
| T4 the katanas `$27-$2E` (same low bytes) are never Item-command usable and their names differ (no ambiguity) | PASS |
| G1 / G2 QA grant all 8 ×5 / remove all | PASS |
| K1-K3 event API on all 8 (HAS / TAKE / GIVE stacking / emptying), vanilla `$27` give/take never merges with Gaia Tonic, no stale high bit | PASS |
| F1-F7 field use: Remedy+ (Blind/Poison/Imp), Phoenix Ash (revive ½ HP, refused on the living), Iron Ration (+200, Poison), Gaia Tonic (+240, refused at full HP – no unit lost), Aether Flask (+250 MP), battle-only items have no field target, last unit empties the slot + high bit | PASS |
| F8 Arrange with 8 consumables + 39 equipment + katana aliases: every 9-bit id and quantity kept | PASS |
| S1-S6 extended shops `$80` / `$81`: lists, prices, owned counts, buy (stack, GP), Equipped count 0, inventory full → refused, vanilla shop `$00` katanas show no alias count | PASS |
| L1-L3 Sell: exactly the 4 sellable consumables, ½ price, selling all empties the slot + high bit | PASS |
| X1 Colosseum offers no consumable · X2 Equip / Relic lists never offer a consumable | PASS |

### `tools/emu_cons_battle_v09.py` (battle Item command) → **13/13 PASS**
| Check | Result |
|---|---|
| B1 battle Item list: the 8 consumables (quantity, targeting, usable), no signature equipment · B1b battle end with everything: inventory unchanged | PASS |
| B2-B9 each consumable in battle: effect (Gaia Tonic party heal ~105-120 each, Aether Flask MP, Phoenix Ash revive, Null Dust strips Haste/Shell/Safe/Reflect/Float, Iron Ration HP + Poison, Remedy+ Blind/Imp/Mute, Beacon Flare Fire on all enemies, Magitek Cell party MP), list quantity −1 at the command, extended name window + animation, exactly one unit used after the battle | PASS |
| BH chosen item held when the user is petrified before acting: returns as Gaia Tonic at battle end (no katana) | PASS |
| BT Shadow's Throw: the Throw list holds only the katana Blossom (×1); throwing it never touches Gaia Tonic | PASS |
| BR no stale high bit on an empty slot | PASS |

### `tools/emu_rare_v09.py` (rare / key items) → **21/21 PASS**
| Check | Result |
|---|---|
| R0a 52 names / descriptions (0-19 vanilla copies, 20-24 key items, 25-51 QA fillers) · R0b XRareDef QA 20-51, production 20-24 only | PASS |
| R1 New Game: rare block zero + signed | PASS |
| R2a GIVE / HAS / TAKE for all 52 ids · R2b no other event bit changes · R2c ids ≥ 52 ignored · R2d id 3 = vanilla bit `$1D3` · R2e one-time states | PASS |
| R3a-d QA hub: grant all 5, check Triune, remove all, toggle each | PASS |
| R4a / R4a' Rare Items menu: 5 key items + Pendant, count 6, descriptions by cursor · R4b / R4c 52 owned: 3 pages, Down / Up / R / L paging | PASS |
| R5 save → power cycle → Continue: all 52 kept, signature valid | PASS |
| R6a Rev 1 save with garbage at `$1E1D-$1E22` / R6b v0.8 save without rare signature: no phantom | PASS |
| R7a QA save in production: 20 vanilla + 5 key items kept, QA fillers dropped · R7b production ignores undefined ids | PASS |

### `tools/emu_stress_v09.py` (everything at once, migration) → **20/20 PASS**
| Check | Result |
|---|---|
| A1 grant everything · B1 19 signature items worn · C1 battle with everything (list, one Gaia Tonic used, reconciliation) | PASS |
| D1 Arrange with 164 item kinds · E1 Empty + Optimum with consumables present (no loss / duplication, none equipped) | PASS |
| F1 extended shop buy n / sell m with everything owned · G1 Colosseum with signature gear + consumables | PASS |
| H1 save → power cycle → Continue: inventory, worn gear, key items, bitmaps identical | PASS |
| I1 v0.9 QA save → v0.9 production · J1 genuine Rev 1 save (katanas + Potions) · K1 v0.7.3 QA save · L1 v0.8 QA save → v0.9 QA and production: nothing cleared · M1 (informative) v0.9 save → v0.8 production: consumables dropped cleanly | PASS |
| O1 120 GIVEs cap at 99 · P1 inventory full → GIVE changes nothing · T1 vanilla `$80/$81` with `$27` / `$2B` separate from the consumables | PASS |
| Q1 / R1 vanilla Potion / Fenix Down (battle), Potion / Antidote (field) · S1 vanilla shop `$48` buy + Sell | PASS |
| N1 bitmap consistency at the end | PASS |

## 3. Emulator — v0.6.1 / v0.7.x / v0.8 regressions rerun on the v0.9 ROMs
| Suite | ROM | Result | Covers |
|---|---|---|---|
| `tools/emu_item_tech.py` | v0.9 QA | **10/10** | New Game signature/zero, GIVE/TAKE/HAS, vanilla `$80/$81` never merge with extended ids, undefined ids ignored |
| `tools/emu_item_qa.py` | v0.9 QA + v0.9 production | **33/33** | names/icons/descriptions, equip + stats, Remove/Empty, Optimum, Arrange, shop/Sell/Colosseum lists, save → power cycle → load, garbage + genuine Rev 1 saves, QA save in production |
| `tools/emu_item_battle.py` | v0.9 QA (+ clean Rev 1 differential) | **17/17** | battle hand logic, weapon / Jump animation, hand exchange, battle end, `$8D` |
| `tools/emu_equip_v08.py` | v0.9 QA | **21/21** | all 39 v0.8 items: records, grant/remove, event API, smith, equip matrix, stats, Remove, shop alias, Sell / Colosseum exclusion |
| `tools/emu_equip_battle_v08.py` | v0.9 QA | **9/9** | weapon animations / power frame-exact vs template, Jump, Genji, Gauntlet, Offering, Runic / Bushido, battle Item list, battle end |
| `tools/emu_equip_stress_v08.py` | v0.9 QA + v0.9 production | **13/13** | 19 worn, Arrange, Optimum, Empty, battles, boss, Colosseum, save / load, v0.8 save in production, legacy save |
| `tools/emu_enemy_tech.py save` | v0.9 QA | **18/18** | v0.6.1 custom monsters, AI, MP, Dark Wind isolation, enemy graphics pixel-exact, save |
| `tools/emu_enemy_tech.py load` | v0.9 QA | **11/11** | Continue, custom battle after load, map test A, routed NPC, Celes Annex, vanilla Guard battle |
| `tools/emu_enemy_tech.py cmds` | v0.9 QA | **6/6** | Steal / Sketch / Control on custom monsters (POKE) |
| `tools/emu_celes_suite.py` | v0.9 celes-tech | **24/24** | Celes Annex dialogue hook, map / NPC / door / battle / reward / exit |
| `tools/emu_colosseum.py` (+ v0.6.0 / v0.7.2 / v0.8 / **v0.9 production** differential, v0.7.1 harness reference) | v0.9 QA, Rev 1 | **COLO_RESULT** | Colosseum fight / cancel / win / loss, real receptionist on map $19D: frames, inventory, return identical to Rev 1 |

The QA hub moved (Consumables / Rare / More → v0.8 equipment tools / older tests); the older suites reach their menus
through the root override environment variables (`FF6X_QA_V08_ROOT`, `FF6X_QA_ITEM_ROOT`, `FF6X_QA_PREFIX`,
`FF6X_QA_SAVE_PICKS`) — the test logic itself is unchanged.

## 4. Map / formation / Magitek VRAM
Not rerun as a full differential: no map, formation, monster or graphics byte changed between v0.8 and v0.9 (the
delta is FA item tables / engine, C0/C1/C2/C3 hook sites and stubs, metadata, checksum; `PATCH_TABLE_v0.9.md`), so
the v0.7.1 differential results carry over (412/412 maps, 576/576 formations). Emulator evidence on v0.9: custom
monsters / enemy graphics pixel-exact (save 09b), formation MP, map test, Celes Annex, Colosseum, Whelk boss battle.
The QA build regenerates its formation-safety report (`FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.formation_safety.json`).

## 5. Findings during v0.9 QA
| Finding | Disposition |
|---|---|
| **Engine:** battle Item command took the spell path for every consumable (the C2:18B0 hook's `CPX` destroyed `InitTarget`'s carry) | **fixed** (`XB_Consume` / `XB_StaHeldVan` preserve P); B2-B9 |
| **Engine:** the battle list drew `DIRK` after a consumable's quantity (EN template byte +12 drawn as a text code) | **fixed** (`$FF` for marker rows); B1 screenshots |
| **Engine:** Rare Items description drawn over the old one after an L / R page flip | **fixed** (BigTextTask restarted on a page change); R4c |
| A vanilla katana in the battle list (Throw / Item) shows `DIRK` after its quantity | **vanilla behaviour, not v0.9**: identical on the accepted v0.8 ROM (R37) |
| Test harness only (no ROM change): field use needs A twice; empty equip lists don't open; the opening's Pendant (rare 19) is owned at New Game; a Rev 1 inventory must be read without the bitmap; shop `$48` first item too expensive (buy the cheapest); Locke's Raider Knife steals a Tonic on hit; the v0.6.1 save step needed `FF6X_QA_SAVE_PICKS`; a WRAM-script shop cannot exit cleanly (the tests call the ROM label) | fixed in the test tools |
| Colosseum suite first run used the v0.7.3 ROM (already fixed) as the "v0.7.1 harness" reference → its 2 reference checks could not reproduce the original black screen | runner corrected (v0.7.1 QA ROM from the v0.7.1 package); rerun above |

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING** (`USER_QA_TECH_v0.9_VI.md`).
