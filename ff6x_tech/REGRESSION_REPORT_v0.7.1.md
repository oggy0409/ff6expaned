# TECH v0.7.1 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

All results below are on the **final** build (`item-tech` `c6ea2b30…`, `production` `b03b0973…`, `celes-tech`
`ed0398cb…`). Emulator = snes9x core via stable-retro, driving the real game through its menus and event engine;
POKE marks the few steps that write RAM directly (test setup only). This is **not** user runtime QA.

## 1. Static
| Check | Result |
|---|---|
| Clean input asserted (SHA-1 `057ADA1C…`, CRC32 `C0FA0464`) | PASS |
| 18/18 targets build; frozen accepted baselines reproduced byte-exact (SHA-1 asserted): v0.1, v0.2 evtest, v0.3 ×2, v0.3.1 QA, v0.4 ×3, v0.5 ×3, v0.6.0 production / celes-tech / QA, v0.6.1 QA | PASS |
| Determinism: two full builds, 90 output files (`.sfc/.bps/.ips/.manifest.json/.diff.csv`) | PASS (0 differences) |
| Selftest | **71/71 PASS** (v0.6 sections now address the frozen `*-v0.6.x` targets; new 42-45: table equivalence, vanilla-space diff, QA isolation, item/event-API guards incl. Gau/Umaro rule) |
| v0.7.1 production vanilla-space diff (< 3 MiB) limited to declared bytes: v0.6 set + 154 hook sites + 118 retargets + 3 stub claims | PASS (0 undeclared bytes) |
| Vanilla ItemProp / ItemName / WeaponAnimProp / ItemJumpThrowAnim unchanged; FA copies byte-identical for ids `$00-$FF`; production defines no extended id | PASS |
| Consumer audit: 287 RAM sites + 118 table operands classified, 0 unclassified | PASS (`ITEM_CONSUMER_AUDIT_v0.7.1.md`) |
| Saved-RAM / padding-claim evidence regenerated from the Rev 1 index | PASS (`SAVED_RAM_AUDIT_v0.7.1.md`) |

## 2. Emulator — extended item engine (QA ROM)
| Suite | Result | Covers |
|---|---|---|
| `tools/emu_item_tech.py` → `ITEM_ENGINE_REPORT.json` | **10/10** | New Game signature/zero, GIVE/TAKE/HAS, vanilla `$80/$81` never merge with `$13D`, undefined/out-of-bank ids ignored |
| `tools/emu_item_qa.py` → `ITEM_QA_EMULATOR_REPORT.json` | **33/33** | A receive, B names/icons/descriptions/details (screenshots), C/D three items equipped at once, E stats + preview, D Remove/Empty/relic remove, I Optimum (no duplication), H Arrange + item move, M shop owned count / Sell / Colosseum, J save → power cycle → Continue, L garbage + genuine Rev 1 saves, P QA save in production |
| `tools/emu_item_battle.py` → `ITEM_BATTLE_EMULATOR_REPORT.json` | **17/17** | QA harness menu (grant ×2, HAS/TAKE), battle list = empty slots (byte-identical), hand props/power, hand names, F1/F2 weapon animation `$FD`, F3 damage, F4 Jump animation frame-identical to the base weapon (POKE command), B3 extended hand replacement refused, B3b R↔L exchange with bits, B3c vanilla exchange identical to clean Rev 1 (differential), B4-B6 battle end, `$8D` |

F4 is discriminating: the same test **fails** on a build without the Jump-animation fix (alias graphic).

## 3. Emulator — regression of accepted features
| Check | ROM | Result |
|---|---|---|
| v0.6.1 QA save phase (custom monsters `$180/$181`, AI, MP 3/0, Dark Wind isolation `$242/$243` pixel-exact, save) — `tools/emu_enemy_tech.py save` with `FF6X_QA_PREFIX=1` (v0.6.1 menu is now one level down) | item-tech | **18/18** |
| v0.6.1 QA load phase (Continue, custom battle after load, Map test A `$1A0` grid, routed NPC, Celes Annex, vanilla opening Guard battle) | item-tech | **11/11** |
| Steal / Sketch / Control on custom monsters (POKE) | item-tech | **6/6** |
| Celes Annex suite (dialogue hook, Annex map/NPC/door/battle/reward/exit) | celes-tech | **24/24** (v0.6.0 celes-tech also 24/24 with the same tool) |
| Map differential, 412 vanilla maps ($003-$19E): props, NPC objects, BG tilemaps, tile properties | production v0.6.0 vs v0.7.1 | **412/412 identical** |
| Formation differential, 576 formations ($000-$23F): monster records, battle RAM, btlgfx ids, decoded tiles, palettes, sizes | production v0.6.0 vs v0.7.1 | **576/576 engine data identical**; screen hash 550/576 identical at +94 frames, the other **26 identical one frame later** (`screen_plus1.json`) |

Notes on the regression method:
* The shared start state was made on v0.6.0; for the v0.7.1 run `FF6X_XINIT=1` applies exactly what a v0.7.1 New Game
  writes at `$1CF8-$1D27` (zero metadata + signature). Without it the v0.6.0 Bushido-name bytes there are read as
  extended-equipment bits, which no real v0.7.1 game can have (New Game zeroes them; every load sanitizes them).
* Battle-start timing: with the zero-bitmap fast paths the inventory post-pass, hand and UpdateEquip helpers no longer
  shift typical battles (formation $000: data at frame 35 with identical ATB, as v0.6.0). 26 formations start one frame
  later (KNOWN_RISKS R12).
* `tools/emu_celes_suite.py` `talk()` now retries across the 4-frame object-update phase: from one RAM state the chest
  interaction failed at the same frame phases on v0.6.0 and v0.7.1 (test-driver timing, not ROM behaviour).

## 4. Defects found and fixed during v0.7.1 emulator QA (all before packaging)
| Defect | Fix | Proof |
|---|---|---|
| Battle Item menu showed the alias name ("Chocobo Brsh") for an extended hand: `CharHandN` ended with `PLX`, which overwrote the flags its callers test | `CMP #$0000` before `RTS` | hand-name screenshot |
| Event `$8D` branched on stale flags after `XBitTst` | `CMP #$0000` after the call | E8D |
| Battle R-hand ↔ L-hand exchange (SelectEquipItem, no `check_equip`) left the bits on the old slots → `$15A` / `$03D` after battle | I545 `XC1_HandSwapBits` | B3b |
| `check_equip` guard tested the wrong hand (`w7e7b3b` is the other hand; `w7e7b00` doesn't identify the replaced hand on all paths) → extended hand could be replaced | guard by caller (return address) | B3 |
| Jump animation used the alias's ItemJumpThrowAnim entry | I543/I544 + XJumpAnim (retarget C1:BA4C) | F4 |
| Battle init ~2 frames slower (per-slot bit lookups for 256 inventory slots) → different ATB start | inventory post-pass I516 with zero-byte skip + equipment-bitmap fast paths | §3 timing |
| Masked compare treated extended slots as `$FF` → Empty → Optimum duplicated an item (found earlier in this task) | Z forced 0 for extended slots | I2 |

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.**
