# FF6 Expanded Edition — TECH v0.7.2: COLOSSEUM HOTFIX

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING** — v0.7.2 is a QA build for review, not an accepted baseline.

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`,
CRC32 `C0FA0464` (the builder aborts on any other input). Accepted baselines through v0.6.2 are reproduced byte-exact.

## What v0.7.2 changes
Only the Colosseum entry in the **QA harness** of the item-tech QA ROM. The v0.7.1 signature-equipment-bank engine is
unchanged byte for byte. Production and celes-tech differ from v0.7.1 only in the build-metadata version byte and
the SNES checksum.

* **Root cause** (`COLOSSEUM_ROOT_CAUSE_v0.7.2.md`): the v0.7.1 QA menu's Colosseum entry ran event command `$9A`
  (Colosseum menu) alone. `$9A` disables the next map fade-in and reloads the map. The vanilla receptionist script
  then starts the battle (`$AF`) or fades back in. The harness did neither, so the screen stayed black for every
  wager and fighter. The same bytes black-screen on the clean Rev 1 ROM too. The real receptionist (map $19D)
  worked in v0.7.1 and works in v0.7.2.
* **Fix:** QA menu → `Colosseum (full battle)` → `Fight (wager list)` calls the vanilla receptionist branch
  **CB:78D9** itself (its Rev 1 bytes are asserted by the builder, not modified). `Get wager kit` gives vanilla wagers
  (Elixir ×3, Fenix Down ×3, ThiefKnife, ValiantKnife), because a New Game has no items.
* No new allocation, hook, retarget or engine byte. Exact delta: `PATCH_TABLE_v0.7.2.md` and
  `out/DELTA_v0.7.1_to_v0.7.2.csv`.

Not done (out of scope): the final 39 equipment items, consumables, and everything else listed as out of scope in
v0.7.1.

## Outputs
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.sfc` | `1e2604acd9f0fc3d358a1bb4b40dc099d195dccc` | `3D05456C` | `F5FF` | **user QA ROM** |
| `FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.bps` | `6befd92d21f916785a77964e7282ca153e2ba482` | | | patch vs clean Rev 1 |
| `FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc` | `f8f92c81475e14e90adecd541aec19fd251e7e45` | `91346FF2` | `1A8E` | production branch: engine, **no** QA content |
| `FF6X_Rev1_TECH_v0.7.2_CELES_TECH.sfc` | `2789edb5621954421c1f2819d0b8a7f54739ce90` | `7399F9CA` | `2DB9` | production + accepted Celes Annex slice |

Each ROM has `.bps`, `.ips`, `.manifest.json` (every patch row: PC/SNES, original/new bytes, consumer, reason) and
`.diff.csv` (byte diff vs clean Rev 1). `BUILD_SUMMARY.json` lists all 18 targets. `out/HASHES_v0.7.2.txt` has SHA-1
and CRC32 for every file in `out/`. BPS and IPS were re-applied to clean Rev 1 and reproduce each ROM byte-exact.

## Build
```
python3 build.py "<clean Rev 1>.sfc" --target all --out out
python3 tools/selftest.py "<clean Rev 1>.sfc"
```
Colosseum emulator test (stable-retro / snes9x):
```
FF6X_COLO_EXTRA="v060prod=<v0.6.0 production>.sfc,v072prod=out/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc,v071qa=<v0.7.1 QA>.sfc" \
python3 tools/emu_colosseum.py out/FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.sfc out/FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.manifest.json \
  "<clean Rev 1>.sfc" <outdir> [<v0.7.1 QA>.sfc <v0.7.1 QA>.manifest.json]
```

## Status
| | Result |
|---|---|
| STATIC | **PASS**: 18/18 targets build, frozen hashes match, two full builds byte-identical (90 files), selftest 71/71, BPS/IPS re-apply byte-exact |
| EMULATOR (Claude-side, snes9x via stable-retro; not user QA) | **PASS**: Colosseum and all v0.7.1 regressions, see `REGRESSION_REPORT_v0.7.2.md` |
| USER RUNTIME QA | **PENDING**: `USER_QA_TECH_v0.7.2_VI.md` (Colosseum C1–C8 + v0.7.1 regression list) |

Known risks: `KNOWN_RISKS_v0.7.2.md` (v0.7.1 list + R16 event `$80` timing, R17 harness/Shadow switch).
