# FF6 Expanded Edition — TECH v0.5: MONSTER EXPANSION FOUNDATION

**STATIC PASS · EMULATOR PASS (576-formation differential + QA battle suite + save/reset/load + Steal/Sketch/Control poke test) · USER RUNTIME QA PENDING**

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`.
Accepted baselines reproduced byte-exact in the same run: v0.1, v0.2, v0.3, v0.3.1 QA, **v0.4 (accepted: production / celes-tech / map-tech)**.
Not done (by instruction): final monster art, Rust Hound / Annex Guard / Magitek Praetor, vanilla rebalance, new Rages, SRAM change, item architecture, Celes story, other arcs.

## Outputs (`out/`)
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.5.0_PRODUCTION.sfc` | `34ad5625ed08f791ca98ccde6a1dbf4ba4744cec` | `844CC192` | `E399` | production branch v0.5 (engine only, **no QA content**, new IDs/formations null) |
| `FF6X_Rev1_TECH_v0.5.0_CELES_TECH.sfc` | `3805944217af91e7b360225d3e73dd2afdd714a7` | `239DD0DF` | `F6C4` | production v0.5 + accepted Annex slice |
| `FF6X_Rev1_TECH_v0.5.0_MONSTER_TECH_QA.sfc` | `416d5d9fbd88751e8fbd5ab4290dbb51fff3e69f` | `381E6EE5` | `AC44` | **user QA ROM** = celes-tech v0.5 + v0.4 proof maps + TESTMOB A/B + formation $240 + QA access (Q5xx) |
| v0.4.0 production / celes-tech / map-tech | `0181dbaa…` / `51587eae…` / `e1d5387a…` | `2EB2033F` / `B4E71558` / `EE846BD5` | | accepted v0.4 (regression rebuild, identical) |
| v0.3.0 celes-tech / production, v0.3.1 QA, v0.2, v0.1 | as ACCEPTED_BASELINES | | | regression rebuilds (identical) |

BPS SHA-1: production `35e345f9833de05dc30c2de043d0a5309d82ca02`, celes-tech `b5be52098b752a6821e7276c7750be85fba940d1`,
monster-tech `64cd9548203bc44d96d48af1224870a246fdc5c4`. Each ROM also has `.ips`, `.manifest.json` (machine-readable diff/patch manifest), `.diff.csv`.

```
python build.py "Final Fantasy III (USA) (Rev 1).sfc"              # all 11 targets, deterministic
python build.py "<rom>" --target monster-tech
python tools/selftest.py "<rom>"                                    # 40 fail-closed guard tests
python devtools/monster_dependency_table.py                         # regenerate the dependency table
```

## 1. What changed (all v0.5 targets) — exact rows in `PATCH_TABLE_v0.5.md`
| ID | What | PC | SNES |
|---|---|---|---|
| N101 | MonsterProp 512 × 32 B | 380000–383FFF | F8:0000–F8:3FFF |
| N102 | MonsterName 512 × 10 | 384000–3853FF | F8:4000–F8:53FF |
| N103 | MonsterSpecialName 512 × 10 | 385400–3867FF | F8:5400–F8:67FF |
| N104 | MonsterItems 512 × 4 | 386800–386FFF | F8:6800–F8:6FFF |
| N105 | MonsterControl 512 × 4 | 387000–3877FF | F8:7000–F8:77FF |
| N106 | MonsterSketch 512 × 2 | 387800–387BFF | F8:7800–F8:7BFF |
| N107 | MonsterSpecialAnim 512 | 387C00–387DFF | F8:7C00–F8:7DFF |
| N108 | MonsterOverlap 512 | 387E00–387FFF | F8:7E00–F8:7FFF |
| N109 | MonsterGfxProp 543 slots × 5 | 388000–388A9A | F8:8000–F8:8A9A |
| N110 | BattleProp 1024 × 4 | 389000–389FFF | F8:9000–F8:9FFF |
| N111 | BattleMonsters 1024 × 15 (+16) | 38A000–38DC0F | F8:A000–F8:DC0F |
| N112 | AIScriptPtrs 512 × 2 | 390000–3903FF | F9:0000–F9:03FF |
| N113 | AIScript (vanilla blob at same offsets + default empty script; QA scripts appended) | 390400– | F9:0400– |
| N200 | 71 consumer operands retargeted (operand bytes only; each instruction asserted) | see patch table | |
| N300 | router: `MonsterGfxSlot5`, `MonsterGfxSlotSketch`, `ColosseumRangeCheck` (49 B) | 301200–301230 | F0:1200–F0:1230 |
| N301 | `BD 01 20 0A 0A 18 7D 01 20` → `22 00 12 F0 EA EA EA EA EA` | 012058 | C1:2058 |
| N302 | `BD 01 20 AA` → `22 13 12 F0` | 02F5F1 | C2:F5F1 |
| N303 | `AE D4 3E E0 3E 02` → `22 20 12 F0 EA EA` | 022F75 | C2:2F75 |

Why: every monster-indexed table stops at 384 entries (formations at 576), although monster IDs are
already 9-bit in the engine. Vanilla records are copied unchanged; the vanilla tables remain as dead
data (reversible: restoring the 71 operands + 3 hook sites returns vanilla behaviour).
Production v0.5 vanilla-space diff = 379 bytes, all declared. Details: `MONSTER_DEPENDENCY_AUDIT_v0.5.md`.

**ID policy:** vanilla `$000–$17F` untouched · new `$180–$1FE` · `$1FF` null. Formations: vanilla `$000–$23F`, new `$240–$3FF`.
**Graphics slots:** monster `$180+` → MonsterGfxProp slot `id + $20` (vanilla slots `$180–$19F` belong to espers/Imp).
**Rage/Veldt:** new monsters never become Rages and never appear on the Veldt (vanilla guards asserted + builder forces the no-Veldt flag). No SRAM change.

## 2. Monster source format
`monsters/<name>/`: `monster.json` (id, name, special name, special anim, policies) · `stats.json` (vanilla base record + named fields) ·
`ai.txt` (`random A B C`, `use A`, `wait`, `end` ×2) · `graphics.json` (graphics + overlap resource) · `palette.json` (palette index + bpp check) ·
`loot.json` · `control.json` · `sketch.json` · `README.md`. Graphics and palette are separate resources from the ID, so final art can replace them later.
`formations/<name>.json`: template vanilla formation, slots (monster, optional position), `no_veldt` (required for IDs ≥ $100).

## 3. QA monsters (monster-tech only)
| | TESTMOB A `$180` | TESTMOB B `$181` |
|---|---|---|
| Graphics / palette | Leafer gfx ($017) / Leafer palette $027 | Dark Wind gfx ($028) / **Vulture palette $04A** (not Dark Wind's) |
| gfx-prop slot | $1A0 | $1A1 |
| Lv / HP / speed / atk | 4 / 90 / 50 / 8 | 5 / 140 / 40 / 6 |
| AI (F9) | random Battle, Battle, **Mute** | random Battle, Battle, **Slow** |
| Steal (rare/common) | Potion / Tonic | Fenix Down / Antidote |
| Drop (rare/common) | Eyedrop / Antidote | Potion / Tonic |
| Control / Sketch | Battle, Mute / Battle, Mute | Battle, Slow / Battle, Slow |
| Exp / Gil | 12 / 30 | 20 / 45 |
Formation `$240` (template $002): slot 2 = $180, slot 3 = $181, no-Veldt. Event battle group `$FE` → `$240` (CF:53F8 `00 00 00 00` → `40 02 40 02`, Q501).

QA access (opening Narshe, as v0.4): New Game → **up 6, left 4** → `TECH v0.5 QA ACCESS` → Monster test battle / Map/Annex tests / No (Save Point).

## 4. Status
* **STATIC PASS** — builds, baselines byte-exact, 40/40 selftests, determinism.
* **EMULATOR PASS** — `REGRESSION_REPORT_v0.5.md` (576/576 vanilla formations identical engine data; QA battle; save/reset/load; poke test Steal/Sketch/Control).
* **USER RUNTIME QA PENDING** — `USER_QA_TECH_v0.5_VI.md`.

Other docs: `CAPACITY_REPORT_v0.5.md`, `KNOWN_RISKS_v0.5.md`, `PATCH_TABLE_v0.5.md`, `audits/MONSTER_DEPENDENCY_TABLE_v0.5.json`, `data/allocations.json` (manifest v5).
