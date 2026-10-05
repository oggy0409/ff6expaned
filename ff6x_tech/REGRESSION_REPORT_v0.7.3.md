# TECH v0.7.3 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

ROMs: QA `FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA` `3a784e0d…`; production `FF6X_Rev1_TECH_v0.7.2_PRODUCTION` `f8f92c81…`
and celes-tech `FF6X_Rev1_TECH_v0.7.2_CELES_TECH` `2789edb5…` (**unchanged**, rebuilt byte-identical). Emulator:
snes9x via stable-retro, not user runtime QA. Logs: `out/emulator_v073/`.

## 1. Static
| Check | Result |
|---|---|
| 18/18 targets build; all frozen baselines reproduced, **now including production / celes-tech v0.7.2** (SHA-1 asserted) | PASS |
| Determinism: two full builds, 90 output files identical | PASS |
| Selftest | **71/71 PASS** |
| QA delta v0.7.2 → v0.7.3: 977 bytes, only QA event block FF:0087–FF:01AB, QA dialogue (FF:080A, FF:0A39–FF:0CF4, pointers F3:0068–F3:0084), QA event operands, version byte F0:000B, checksum; **no engine byte** (C0–C3, FA unchanged) | PASS (`out/DELTA_v0.7.2_to_v0.7.3.csv`, `PATCH_TABLE_v0.7.3.md`) |
| BPS / IPS re-applied to clean Rev 1 reproduce each ROM | PASS |

## 2. Emulator — v0.7.3 visual / QA-state validation
`tools/emu_colosseum_visual.py` → `COLOSSEUM_VISUAL_REPORT.json`: **32/32 PASS** (details: `COLOSSEUM_QA_STATE_v0.7.3.md` §5).

| Group | Result |
|---|---|
| A/B: v0.7.2 QA opening party = clean Rev 1 (Terra Magitek mode on; Wedge/Vicks record pointer $FFFF), identical frames | reproduced, vanilla |
| C: Rev 1 Terra with only Magitek cleared → no extra sprite | cause isolated |
| E: v0.7.3 QA normalized party: Terra / Locke / Celes / Edgar visible, wins pay prizes, return + party/Magitek restore; Terra with the 3 QA items keeps them | PASS |
| E′: same normalized party on clean Rev 1, identical frames / state / inventory | PASS |
| F: real Colosseum (map $19D receptionist), Terra / Locke / Celes, production v0.7.2 + v0.7.3 QA = clean Rev 1 | PASS |

## 3. Emulator — regressions rerun on the v0.7.3 QA ROM
| Suite | Result |
|---|---|
| `emu_colosseum.py` (Colosseum entry / win / reward / loss / return / cancel, real receptionist on Rev 1, v0.6.0 production, v0.7.1 QA, v0.7.2 production, v0.7.3 QA; v0.7.1 black-screen reference) | **60/60** |
| `emu_item_tech.py` (GIVE/TAKE/HAS, signature) | **10/10** |
| `emu_item_qa.py` (equip ×3, Arrange, Optimum, save/load, shops/Sell, legacy saves, QA save in production) | **33/33** |
| `emu_item_battle.py` (battle hand logic, animations, Rev 1 differential) | **17/17** |
| `emu_enemy_tech.py` save / load / cmds (v0.6.1 QA) | **18/18 · 11/11 · 6/6** |
| Celes Annex suite | celes-tech is byte-identical to the v0.7.2 ROM tested **24/24** (not rerun) |
| Map / formation differential | production byte-identical to v0.7.2 (carry-over of the v0.7.1 412/412 and 576/576 results) |

Test-tool changes (no ROM effect): `emu_colosseum.run_combo` records the fighter's battle-graphics state, takes two
later screenshots, and stops pressing A once the battle has faded out (on map $19D the returning party otherwise
talked to the receptionist again: identical on Rev 1 and production). `emu_colosseum.py` now runs its opening-party
groups through CB:78D9 directly (the v0.7.2 harness path); the new harness path is covered by `emu_colosseum_visual.py`.

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.**
