# FF6 Expanded Edition — TECH v0.7.3: COLOSSEUM VISUAL / QA-STATE VALIDATION

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING** — QA build for review, not an accepted baseline.

## Result
Both v0.7.2 visual reports (Terra extra sprite; Wedge / Biggs-Vicks invisible) are **vanilla Rev 1 behaviour** in the
opening-Narshe QA state. Clean Rev 1 renders the same frames. They are not FF6X engine or item-bank defects
(`COLOSSEUM_QA_STATE_v0.7.3.md`).
* **Production unchanged:** `FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc` and `…_CELES_TECH.sfc` are rebuilt byte-identical;
  the builder now asserts their v0.7.2 SHA-1.
* **QA ROM updated:** the QA menu's Colosseum "Fight" normalizes the party (Terra out of Magitek; Wedge/Vicks out;
  Locke/Celes/Edgar in, using the vanilla recruit commands). It then calls the vanilla receptionist branch and
  restores the opening party.
* The item engine is not modified. The QA ROM delta from v0.7.2 is limited to the QA event/dialogue areas, the
  version byte and the checksum (`out/DELTA_v0.7.2_to_v0.7.3.csv`).

## Outputs
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.sfc` | `3a784e0d3df817dd47d796f8b50b8ac34b143b31` | `EB2923BA` | `AD8D` | **user QA ROM** |
| `FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.bps` | `8cab577cd0072e1495c42a61e5db60bcbd5daee6` | | | patch vs clean Rev 1 |
| `FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc` | `f8f92c81475e14e90adecd541aec19fd251e7e45` | `91346FF2` | `1A8E` | production, **unchanged** |
| `FF6X_Rev1_TECH_v0.7.2_CELES_TECH.sfc` | `2789edb5621954421c1f2819d0b8a7f54739ce90` | `7399F9CA` | `2DB9` | unchanged |

Before/after screenshots: `out/COLOSSEUM_VISUAL_v0.7.3_before_after.png` (rows: v0.7.2 QA opening party · same
state on clean Rev 1 + Terra without Magitek · v0.7.3 QA normalized party · real Colosseum on production).
User QA: `USER_QA_TECH_v0.7.3_VI.md`. Regression: `REGRESSION_REPORT_v0.7.3.md`. Risks: `KNOWN_RISKS_v0.7.3.md`
(new R18–R20).

## Build / test
```
python3 build.py "<clean Rev 1>.sfc" --target all --out out
python3 tools/emu_colosseum_visual.py out/FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.sfc out/FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.manifest.json \
  <v0.7.2 QA>.sfc <v0.7.2 QA>.manifest.json out/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc "<clean Rev 1>.sfc" <outdir>
python3 tools/colosseum_visual_sheet.py <outdir> sheet.png
```

Not started (out of scope): the final 39 equipment items.
