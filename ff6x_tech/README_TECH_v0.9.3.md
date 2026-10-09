# FFVI Expanded Edition — TECH v0.9.3 Visual State / VRAM Hotfix (QA)

**Status: ACCEPTED / USER RUNTIME PASS (2026-10-07; frozen).** STATIC PASS · EMULATOR PASS · USER RUNTIME PASS. See `ACCEPTANCE_v0.9.3.md`. E8 state / persistence accepted; E8 placeholder memorial / archive art rejected for production and deferred to a dedicated art pass.

* Scope: a focused hotfix for the four visual failures of the v0.9.2 user runtime QA (V1-V4). It changes the QA ROM only.
* Baseline: TECH v0.9 (accepted, frozen, rebuilt byte-exact) + TECH v0.9.1 item alignment (production / celes-tech,
  unchanged, SHA-1 now asserted) + TECH v0.9.2 enabler logic (passed in your runtime QA; mechanisms unchanged).

| target | file | SHA-1 | CRC32 | v0.9.3 |
|---|---|---|---|---|
| `item-tech` | `FF6X_Rev1_TECH_v0.9.3_VISUAL_STATE_VRAM_HOTFIX_QA` | `15af77fe9c01f54844fbcbbb0c5f1d65768d55f0` | `02DA7373` | **accepted (pinned in `build.py`)** |
| `production` | `FF6X_Rev1_TECH_v0.9.1_PRODUCTION` | `2dc73bfbbcf4657eb59eec93bd614181ecdc817c` | `01AE6F84` | unchanged (pinned) |
| `celes-tech` | `FF6X_Rev1_TECH_v0.9.1_CELES_TECH` | `e2192311a997ee49315807508d71ca202d4a8d09` | `EA66714A` | unchanged (pinned) |

The package ships only the v0.9.3 QA ROM (`.sfc`, `.ips`, `.bps`). The production and celes-tech ROMs are unchanged, so
they are not included. Use the v0.9.2 package, or rebuild them with `build.py` (the SHA-1s above are asserted).

## The four failures (details: `ROOT_CAUSE_VISUAL_v0.9.3.md`)
| # | cause | fix | proof |
|---|---|---|---|
| V1 map `$1A2` palette | the palette was installed correctly all the way to CGRAM, but the v0.9.2 transform re-warmed the colours, so it looked like vanilla | `palettes/v093/palettes.json`: palette `$30` = 75% desaturated, slightly cool, +4% gain | `PALETTE_AUDIT_v0.9.3.md`; visual S1 |
| V2 WoR dog (Lunaris) | QA party state: after New Game, Wedge / Vicks are in Magitek armor, and v0.9.2 cleared Terra only → Magitek battle mode → armor tiles over the dog's head cells | QA routine `QaCelParty93` at every Celes-enabler entry | `VRAM_AUDIT_v0.9.3.md`; visual S2 |
| V3 second Suppressor Bit | same party state; VRAM map 4 slot 2 overlaps the armor cells (slot 1 does not) | same | `VRAM_AUDIT_v0.9.3.md`; visual S3 (both Bits pixel-exact and identical) |
| V4 E8 states not visible | the tiles changed, but they were wall pieces that read as wall | real 4 × 2 memorial / 2 × 2 archive objects (`maps/celes_outer_v092/states.json`); builder-checked against the event and the movement model | `MAP_STATE_VISUAL_AUDIT_v0.9.3.md`; visual S4 |

Not changed: item IDs or effects, save format, boss thresholds, AI, dialogue decisions, event-bit meanings, engine code,
hooks. Byte delta v0.9.2 QA → v0.9.3 QA: 934 B in 56 runs, all in QA expansion regions plus the header checksum
(`PATCH_TABLE_v0.9.3.md`, `out/DELTA_v0.9.2_to_v0.9.3.csv`).

## New tooling
* `tools/emu_bsnes.py`: a ctypes libretro frontend for **bsnes** (accurate PPU), with the same API as the snes9x
  harness plus WRAM / VRAM / CGRAM / OAM / SRAM access. The core is built locally by `tools/build_bsnes_core.sh`
  (bsnes commit in `tools/bsnes_ff6x/BSNES_COMMIT.txt`, harness patch in `tools/bsnes_ff6x/`).
* `tools/emu_visual_v093.py`: S1-S4 + N1 on rendered frames, from New Game without a preset (the guide path). It runs on
  bsnes and on snes9x, on the v0.9.3 ROM (expected PASS) and on the v0.9.2 ROM (BEFORE evidence, expected FAIL).
* `tools/vram_audit_v093.py`: per-slot VRAM tile audit. `tools/palette_audit_v093.py`: palette ROM → RAM → CGRAM trace.
* `tools/sheet_v093.py`: before / after contact sheets. `tools/docs_v093.py`: hashes, patch table, delta.
* `tools/run_regression_v093.sh`: the full regression behind `REGRESSION_REPORT_v0.9.3.md`.
* Builder: `patches/celes_enablers_v092.map_states()` (E8 state validation). Event assembler: `obj_vehicle` (event
  `$44`).

## Build
* `python3 build.py "<Final Fantasy III (USA) (Rev 1).sfc>" --target all --out out`: 27 targets; the frozen v0.9 and
  the pinned v0.9.1 hashes are asserted.
* Self-tests: `python3 tools/selftest.py <clean>` (156 guards).
* Regression: `tools/run_regression_v093.sh <clean> out <evidence dir> <v0.7.1 QA .sfc>` (needs the bsnes core).

## User QA
`USER_QA_TECH_v0.9.3_VI.md`: 5-10 min, H0-H5, visual hotfix only. E5 / E7 and everything that passed in v0.9.2 need
no retest.

## Not done (by instruction)
No CONTENT v1.0, no Celes ROM Script Pass, no final art. Known risks: `KNOWN_RISKS_v0.9.3.md`.
