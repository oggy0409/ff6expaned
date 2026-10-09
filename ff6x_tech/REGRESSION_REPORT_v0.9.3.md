# TECH v0.9.3 — regression report (STATIC + Claude-side EMULATOR; USER RUNTIME QA PENDING)

All results are on the **final** build:
* QA v0.9.3 `15af77fe…` (CRC32 `02DA7373`);
* production v0.9.1 `2dc73bfb…` and celes-tech v0.9.1 `e2192311…`, unchanged and pinned;
* the frozen v0.9 ROMs (`HASHES_v0.9.3.txt`).

Emulators: snes9x (stable-retro), and **bsnes with the accurate PPU** (new: `tools/emu_bsnes.py`, core built by
`tools/build_bsnes_core.sh`). **POKE** marks test-only RAM writes. This is not user runtime QA.

Evidence: `out/emulator_v093/` (logs, JSON, screenshots, crops, VRAM / OAM dumps). Contact sheets:
`out/VISUAL_BEFORE_AFTER_bsnes.png`, `out/VISUAL_BEFORE_AFTER_snes9x.png`, `out/E8_STATES_bsnes.png`,
`out/E8_STATES_snes9x.png`. Driver: `tools/run_regression_v093.sh`.

## 1. Static
| Check | Result |
|---|---|
| Clean input asserted; master ROM never written | PASS |
| 27/27 targets build; frozen v0.9 production / celes-tech / QA byte-exact; **v0.9.1 production / celes-tech byte-exact (SHA-1 now pinned in `build.py`)** | PASS |
| Determinism: second full build into a separate directory, all 142 output files compared | PASS (0 differences) |
| Selftest | **156/156 PASS**. New 57: E8 state validator fails closed (walkable stone, look-alike states, RESET ≠ layout, event / state mismatch). 58: every Celes-enabler hub entry calls the party normaliser first, plus the `obj_vehicle` guard. 59: palette `$30` = documented transform with saturation ≤ 50% of vanilla; production byte-identical |
| Builder E8 check: 9 memorial × archive combinations keep the reachable floor (138 cells) | PASS |
| Delta v0.9.2 QA → v0.9.3 QA (`PATCH_TABLE_v0.9.3.md`, `out/DELTA_v0.9.2_to_v0.9.3.csv`): 934 B in 56 runs. No hook, engine routine or vanilla-space patch changed except the header checksum. Changed regions: map palette `$30` (223 B, F7:D002-D0FF), enabler events (E8 tiles) and the trigger / NPC vector tables pointing into them, QA hub events (normaliser) and root dialogue, build metadata | PASS |

## 2. Emulator — visual hotfix (`tools/emu_visual_v093.py`, New Game without a party preset)
| suite | v0.9.3 QA ROM | v0.9.2 QA ROM (BEFORE) |
|---|---|---|
| bsnes (accurate PPU) | **15/15 PASS** | **FAIL 1/15** (expected) |
| snes9x | **15/15 PASS** | **FAIL 1/15** (expected) |

| check | what it proves | v0.9.3 | v0.9.2 |
|---|---|---|---|
| N1a-d | WoR / Praetor / walk-in entries: no Magitek in the party, Wedge / Vicks out, P1 when nobody but Terra; Terra on foot | PASS | FAIL (party 0, 14, 15 with Magitek) |
| S1a | `$1A2` RESET frame vs the same frame in vanilla `$18`, lit BG pixels: distance ≥ 12, saturation ≤ 50%, contrast ≥ 60% | PASS (bsnes 15.7, 10.5 vs 31.9, 65 vs 62; snes9x 15.3, 10.2 vs 30.9, 63 vs 60) | FAIL (bsnes 13.5, 42.1 vs 31.8; snes9x 13.0, 40.8 vs 30.8) |
| S1b | colour RAM BG rows = v0.9.3 palette `$30` (bsnes CGRAM / snes9x buffer) | PASS | FAIL |
| S1c | sprite palettes 0-6 = vanilla (no sprite / NPC corruption) | PASS | PASS |
| S2 | WoR Lunaris encounter (temp ROM copy points the landing sector's groups at `$CB` / `$CA`): Magitek mode off, every monster pixel-exact vs ROM data in 12 sampled frames | PASS | FAIL (Magitek mode 1; Lunaris not exact in 12/12 frames on both emulators; on snes9x the Osprey is also not exact in 12/12 because the Magitek-mode party sprites overlap it) |
| S3 245 / 244 | after the 70% reveal and a bounded settle (≤ 600 frames, for the Bits' white cast flash): both Bits pixel-exact vs ROM data in every window-free sample (≥ 10 of 16), the two Bit crops identical, Magitek mode off | PASS / PASS (settled after 20 frames, then 16/16 exact) | FAIL / FAIL (never settles; slot 2 not exact in 16/16, slot 1 exact) |
| S4a | BG1 map buffer = states.json for RESET / PRESERVE / BURN / GRAVES | PASS | FAIL |
| S4b / S4c | memorial / archive crops differ pairwise ≥ 60% | PASS (91-95% / 79-99%) | FAIL (34-35% / 31-47%) |
| S4d | Preserve + Graves via the WoR entrance, exit, re-entry: same pixels and tiles | PASS | FAIL (old tiles) |
| S4e | save → power cycle → Continue → walk in: same pixels and tiles | PASS | FAIL (old tiles) |

## 3. Audits
| audit | result |
|---|---|
| `tools/vram_audit_v093.py` (bsnes) | v0.9.2: Bit slot 2 **12/46** tiles overwritten (all in the Magitek area), Lunaris **10/29** (all in the Magitek area); slots outside the area exact. v0.9.3: 0 overwritten in every slot. `VRAM_AUDIT_v0.9.3.md` |
| `tools/palette_audit_v093.py` (bsnes) | both ROMs: `$0539` = `$30`, table entry = documented transform, `$7E7200` / `$7E7400` / CGRAM = table (0 differing colours). Table saturation: vanilla 14.3, v0.9.2 9.97, v0.9.3 3.73. `PALETTE_AUDIT_v0.9.3.md` |

## 4. Emulator — v0.9.1 / v0.9.2 / v0.9 regression on the v0.9.3 ROMs (snes9x)
| suite | result |
|---|---|
| `emu_cons_v091` (consumables, shops `$80-$84`, cap 3, Sell) | **17/17 PASS** |
| `emu_cons_battle_v091` (battle effects incl. Magitek Cell hybrid) | **9/9 PASS** |
| `emu_savecompat_v092` (v0.9 save → production v0.9.1 / QA v0.9.3) | **5/5 PASS** |
| `emu_enablers_v092` (E1-E9: WoR / Falcon, Praetor 70% / 40% / Grounding Field, E5, E6, E7, E8 logic + persistence; E8 tiles from states.json) | **14/14 PASS** |
| `emu_rare_v09` | **21/21 PASS** |
| `emu_item_tech` / `emu_item_qa` / `emu_item_battle` | **PASS / 33/33 / 17/17** |
| `emu_enemy_tech` v0.6.1 save / load / commands (monster graphics regression) | **PASS / PASS / PASS** |
| `emu_celes_suite` (celes-tech v0.9.1) | **SUITE PASS** |
| `emu_colosseum` (+ production v0.6.0 / v0.7.2 / v0.8 / v0.9 / v0.9.1 receptionist differential) | **72/72 PASS** |
| `emu_equip_v08` / `emu_equip_battle_v08` / `emu_equip_stress_v08` | **21/21 / 9/9 / 13/13 PASS** |
| frozen v0.9 ROMs: `emu_equip_battle_v08` / `emu_cons_v09` / `emu_cons_battle_v09` / `emu_stress_v09` | **9/9 / 28/28 / 13/13 / 20/20 PASS** |
| formation safety (QA): `$244/$245` 0 errors (2 margin warnings), `magitek_possible: false`; `$242/$243` = accepted v0.6.1 isolation formations (unchanged) | PASS |

## 5. Notes
1. **Test-tool changes this cycle:**
   * `emu_enablers_v092` E8 now reads its regions and tiles from `states.json`.
   * `emu_bsnes` gives every core load a fresh save directory, and fully re-initialises the core on every reload (R77: a reload of a different ROM after a field-map session segfaulted in the SMP; found by the palette audit). One intermediate bsnes run had loaded a stale
     `.srm`; all bsnes results here (visual, VRAM and palette audits) are from runs after both fixes.
   * `emu_visual_v093` S3 excludes frames where the battle message window ("Rflect", cast by the Bits right at the
     reveal) covers the Bits. It requires ≥ 10 such frames out of 16.
   * `emu_visual_v093` S3 also waits, at most 600 frames, until both Bits are exact before sampling. On bsnes the first
     frame after the window caught Bit 2 in the vanilla white-silhouette flash, the one a monster shows when it casts
     (`S3_*_transient_before_settle.png`). On v0.9.3 the flash ends after 20 frames, and all 16 samples are then exact.
     On v0.9.2 the armor tiles never settle, so S3 still fails 16/16 there. A first full bsnes run without the settle
     failed S3 on that one frame; it was stopped and rerun.
2. **E5 / E7** were not re-tested by hand: their bytes are unchanged, the en92 suite re-passed, and the E7 sprite
   palette is byte-identical.
3. **No ROM change for the item / shop / save / boss logic** in v0.9.3 (`PATCH_TABLE_v0.9.3.md`).
