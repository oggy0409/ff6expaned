# TECH v0.9.1 / v0.9.2 — regression report (STATIC + Claude-side EMULATOR; USER RUNTIME QA PENDING)

All results are on the **final** build: production v0.9.1 `2dc73bfb…`, celes-tech v0.9.1 `e2192311…`, QA v0.9.2
`697a25e8…` (`HASHES_v0.9.2.txt`), plus the frozen accepted v0.9 ROMs rebuilt byte-exact by the same source.
Emulator = snes9x core via stable-retro, driving the real game through its menus, event engine, shops and battles.
**POKE** marks test-only RAM writes (setup, identical in every compared run). This is **not** user runtime QA.
Driver: `tools/run_regression_v092.sh`. Logs, JSON reports and screenshots: `out/emulator_v092/`; contact sheets:
`out/ITEM_ALIGNMENT_V091_SHEET.png`, `out/CELES_ENABLERS_V092_SHEET.png`.

## 1. Static
| Check | Result |
|---|---|
| Clean input asserted (SHA-1 `057ADA1C…`, CRC32 `C0FA0464`); master ROM never written | PASS |
| 27/27 targets build; **frozen v0.9 production / celes-tech / QA** (`99cd74df…`, `e4c07031…`, `e1136805…`) and every older accepted baseline byte-exact (SHA-1 asserted by `build.py`) | PASS |
| Determinism: second full build into a separate directory, all 142 output files compared | PASS (0 differences) |
| BPS and IPS of the three new ROMs re-applied to clean Rev 1 → byte-identical ROMs | PASS |
| Package self-check: the source extracted from the delivery zip rebuilds all 27 targets (frozen hashes asserted); the three new ROMs are byte-identical to the packaged ones | PASS |
| Selftest | **148/148 PASS** (new 52-56: v0.9.1 definitions and production delta; v0.9.1 validators fail closed in 15 cases incl. hook-site overlap; v0.9.2 AI compiler / formation encodings, refused extension ops, QA twins share the locked AI; v0.9.2 regions / palettes / D-21 bits / QA-write bits refused outside the QA target) |
| Delta v0.9 → v0.9.1 production / celes-tech: 4,594 B in 220 runs = FA engine + tables + metadata + checksum + stub claims + 6 hook sites (`PATCH_TABLE_v0.9.2.md`, `out/DELTA_v0.9_to_v0.9.2.csv`) | PASS |
| Delta v0.9 QA → v0.9.2 QA: 38,912 B in 2,425 runs (v0.9.1 + enablers: AI extension, palette relocation, map `$1A2`, Praetor / Bits, QA hub) | PASS |
| `formation_safety` QA: `$244/$245` 0 errors (2 margin warnings); `$242/$243` = the accepted v0.6.1 isolation formations (unchanged) | PASS |

## 2. Emulator — new suites
### `tools/emu_cons_v091.py` (field, shops, cap, Sell) → **17/17 PASS**
| Check | Result |
|---|---|
| T1 the 8 consumable records = v0.9.1 sources · T2 equipment = frozen v0.9 except Darill's Coin (Mag +2) | PASS |
| F1 Gaia Tonic field +1500 exactly (5 → 1505), refused at full HP · F2 Iron Ration +600 exactly, Poison **not** cured · F3 Aether Flask +100 MP exactly · F4 Remedy+ · F5 Phoenix Ash · F6 battle-only items have no field target | PASS |
| S1 shops `$80`, `$81`, `$82`, `$83`: entries, 9-bit names, prices, owned counts · S2 Rebuilt Mobliz vendor buys (equipment + stack) | PASS |
| S3 `EXP_CELES_DONE` → Foundry `$84` with Magitek Cell 1500 · S4 cap 3 (quantity max 3, "too many" with 3 owned, also after re-entry) · S5 flag cleared → `$83` again | PASS |
| L1 Sell: exactly Gaia Tonic, Iron Ration, Magitek Cell | PASS |

### `tools/emu_cons_battle_v091.py` (battle Item command) → **9/9 PASS**
| Check | Result |
|---|---|
| V1 Gaia Tonic one ally: +1500 exactly, Regen set, later heals are Regen ticks (< 500; the fixed amount never leaks) | PASS |
| V2 Aether Flask +100 MP · V3 Phoenix Ash · V5 Iron Ration +600, Poison kept | PASS |
| V4 Null Dust: the target loses exactly the vanilla Dispel set (12 statuses), keeps Dance; other enemies untouched | PASS |
| V6 Remedy+: Blind, Zombie, Poison, Imp, Mute, Sap cured; Sleep stays | PASS |
| V7 Beacon Flare: Fire on every enemy and Vanish removed in the same action; Image kept | PASS |
| V8 Magitek Cell one enemy: neutral 800, weak 1200, half 600, null 400, absorb 0, force field 400; others untouched | PASS |
| V9 vanilla Potion 250 (no fixed amount on vanilla items) | PASS |

### `tools/emu_enablers_v092.py` (Celes enablers, QA ROM) → **14/14 PASS**
E1 WoR airship → land → `$1A2` (parent stored) → south exit → beside the Falcon → board · E2 Praetor alone, Bits hidden with
full HP, opening barrier, front attack · E2 ≤ 70 % → Bits shown · E3 ≤ 40 % → Defense 80, Haste, overload palette, HP not
swapped · E4 Grounding Field (3rd Lightning hit → null / not weak 3 turns; 400 during it) · E4 expiry · E4 nothing persists
(SRAM-saved battle vars untouched) · E9 front only (12 RNG phases), formation safety · E5 four parties (Locke / Edgar /
Sabin / dropped) · E6 map palette `$30` · E7 sprite palette `$20` in slot 7 · E7 Vale switch · E8 four outer-map states ·
E8 save → power cycle → load. Details: `CELES_ENABLERS_v0.9.2.md`.

### `tools/emu_savecompat_v092.py` (v0.9 save → v0.9.1 / v0.9.2) → **5/5 PASS**
A v0.9 QA save (39 equipment, 8 consumables ×10, key items, an equipped extended relic, GP) loaded after a power cycle
in production v0.9.1 and in QA v0.9.2: inventory, all 16 equipment records, extended bitmap + signature, rare block +
signature and GP identical; `$1E23-$1E26` = 0; a carried-over Gaia Tonic heals exactly 1500.

## 3. Emulator — accepted v0.9 suites on the new QA ROM
| Suite | Result |
|---|---|
| `emu_rare_v09` (sources `items/production_v091/rare_items.json`) | **21/21 PASS** |
| `emu_item_tech` (v0.7.1 engine) | PASS |
| `emu_item_qa` (v0.7.1 item bank, QA save in production v0.9.1) | **33/33 PASS** |
| `emu_item_battle` | **17/17 PASS** |
| `emu_enemy_tech` v0.6.1 save / load / commands | **SAVE / LOAD / CMDS PASS** (see note 1) |
| `emu_celes_suite` (celes-tech v0.9.1) | **SUITE PASS** |
| `emu_colosseum` (+ v0.6.0 / v0.7.2 / v0.8 / v0.9 / **v0.9.1** production receptionist differential) | **72/72 PASS** |
| `emu_equip_v08` (sources `items/production_v091/equipment.json`) | **21/21 PASS** |
| `emu_equip_battle_v08` | **9/9 PASS** (J1 / O1 method changed, see note 2) |
| `emu_equip_stress_v08` | **13/13 PASS** |

## 4. Emulator — v0.9 suites on the frozen v0.9 ROMs (toolchain check)
`emu_cons_v09` **28/28 PASS**, `emu_cons_battle_v09` **13/13 PASS**, `emu_stress_v09` **20/20 PASS**,
`emu_equip_battle_v08` (frozen v0.9 QA, with the v0.9.2 J1 / O1 method) **9/9 PASS**.

## 5. Notes (test-tool changes, each justified by evidence)
1. **v0.6.1 suite menu path.** It enters through the QA tile; the v0.9.2 root adds one level, so the driver passes
   `FF6X_QA_PREFIX=2,2,2,0,1` / `FF6X_QA_SAVE_PICKS=2,2,2,1` (the first run with the v0.9 path failed at step 02 for that
   reason). Its check 14b (the two custom monsters' AI was seen casting Mute and Slow) depends on the RNG and therefore on
   input timing; the suite now fights `$240` again (at most 3 times) until both were observed. The AI bytes are unchanged.
2. **Equipment battle J1 / O1 (lag-frame timing, KNOWN_RISKS R67).** The first v0.9.2 run failed J1 (Sandpiercer Jump)
   and O1 (Offering) on frame-exact equality with the template weapon. Diagnosis (`out/emulator_v092/timing_probe/`):
   the first differing RAM after the expected hand bytes is the weapon animation number, then ATB / timer bytes one tick
   apart - the extended-weapon path took one more frame while a guard's animation was running, so that overlapping
   animation is drawn one frame apart. The same probe on the **frozen v0.9 ROM** also diverges (Offering, 2 of 16 start
   phases), so the effect predates v0.9.1; the v0.9 run was phase luck. With the guards' ATB held (POKE, identical in
   both runs) the Offering comparison is frame-identical. J1 / O1 now hold the monster ATB and compare every frame.
3. Gameplay data are unaffected in both cases; no ROM change was made for them.

## 6. Not covered by the emulator (user runtime QA)
Real hardware / other emulators, audio, the feel of the 70 % / 40 % / Grounding Field sequence in hand play, the
readability of the placeholder palettes. Checklist: `USER_QA_TECH_v0.9.2_VI.md`.
