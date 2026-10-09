# VRAM AUDIT — WoR dog (V2) and Suppressor Bits (V3), TECH v0.9.3

Tool: `tools/vram_audit_v093.py`, bsnes accurate PPU. Raw dumps and report: `out/emulator_v093/vram_audit/` (VRAM, OAM,
frame, `VRAM_AUDIT_v093.json`).

Method:
* Both QA ROMs, New Game **without** a party preset (the guide path), then the hub entry. The WoR case uses a temp ROM
  copy whose landing-sector battle groups point at the Lunaris formations `$CB` / `$CA` (test only).
* After the battle has drawn the monsters, the 32-byte 4bpp tile of every used stencil cell of every slot is compared
  with that monster's ROM tile, at the cell's VRAM address.

Monster tile layout:
* Cell (row, col) of the 16 × 16 monster cell grid lives at VRAM **byte `$6000 + (row * 16 + col) * 32`**. This was
  measured: the Praetor's cell (0,4) is at `$6080`, Bit slot 1 cell (8,0) at `$7000`. It matches
  `data/vram_safety.json`.
* A slot's cells are its VRAM-map box origin (`ff6x/enemygfx.VRAM_MAP_POS`, from MonsterVRAMMapPtrs C2:D01A) plus the
  stencil cells of its graphics.
* With any party member in Magitek armor, the armor graphics occupy **rows 0-11, cols 12-15** (48 cells).

## Results
| case | ROM | formation / VRAM map | party (records) | Magitek battle mode `$7E64BA` | slot | monster | box origin (col,row) / size | stencil | tiles used | **overwritten** | of which in the armor area |
|---|---|---|---|---|---|---|---|---|---|---|---|
| V3 Praetor + Bits after the 70% reveal | v0.9.2 | `$245` / 4 | 0, 14, 15 (Wedge, Vicks: Magitek) | **1** | 0 | `$186` Praetor | (0,0) 12×8 | 12×8 | 67 | 0 | 0 |
| | | | | | 1 | `$187` Bit | (0,8) 8×8 | 7×8 | 46 | 0 | 0 |
| | | | | | 2 | `$187` Bit | (8,8) 8×8 | 7×8 | 46 | **12** (`$7180`, `$71A0`, `$71C0`, `$7380` …) | 12 |
| | v0.9.3 | `$245` / 4 | 0, 1, 4, 6 (P1) | **0** | 0 / 1 / 2 | Praetor / Bit / Bit | as above | | 67 / 46 / 46 | **0 / 0 / 0** | — |
| V2 WoR Lunaris | v0.9.2 | `$CA` / 0 | 0, 14, 15 | **1** | 1 | `$0CA` Lunaris | (8,0) 8×8 | 6×6 | 29 | **10** (`$6380`, `$63A0`, `$6580`, `$65A0` …) | 10 |
| | | | | | 2 | `$0E6` Osprey | (0,8) 8×8 | 8×8 | 41 | 0 | 0 |
| | v0.9.3 | `$CA` / 0 | 0, 1, 4, 6 | **0** | 1 / 2 | Lunaris / Osprey | | | 29 / 41 | **0 / 0** | — |

Reading:
* **Bits.** Slot 1 and slot 2 load the same graphics from the same source, but slot 2's box (cols 8-15) overlaps the
  armor area in cols 12-15. The 7-column Bit uses cols 12-14 in rows 8-11 there: 12 cells. All 12 are overwritten by
  armor tiles, and nothing else is. This explains why one Bit is correct and the other shows garbage.
* **Lunaris.** Box cols 8-15, rows 0-7. Its 6×6 stencil uses cols 12-13 in rows 0-5. Those are the 10 overwritten
  cells, on the right of the sprite: the dog's head.
* **Ruled out.** Wrong stencil, size or tile-count metadata, graphics-router routing, palette pairing, slot layout and the
  phase-spawn loading path are all fine:
  * every non-armor cell holds the exact ROM tile, in both ROMs;
  * the v0.9.3 run (same ROM data, same routing, only the party state differs) is exact in every cell;
  * the same pixel results come from snes9x (`emu_visual_v093` S2 / S3).

## Classification and fix
* **Cause:** VRAM overlap, caused by an invalid party state, specific to the QA harness.
* **Why it happened:** after New Game the QA hub left Wedge / Vicks (Magitek armor) in the party. The v0.9.2 Celes
  entries cleared Terra's Magitek only.
* **What it is not:** an engine, graphics-router or formation-data defect.
  * `$244` / `$245` are declared `magitek_possible: false` with the reason (VRAM map 4 slot 2 overlaps the armor cells;
    no vanilla VRAM map fits Praetor + 2 Bits). The Celes arc has no Magitek party.
  * Lunaris's formation is vanilla. No Magitek party reaches the World of Ruin in the real game.
* **Fix:** QA routine `QaCelParty93`, run first by `WoR aboard the Falcon`, both Praetor battles and `Walk into the
  outer map`. Selftest 58 asserts this for every path that starts battle `$FA` / `$F9`, loads `$1A2` or loads the WoR
  aboard the airship.
* **Regression:** `emu_visual_v093.py` S2 / S3 run on bsnes and snes9x:
  * every monster pixel-exact vs ROM data in all sampled frames;
  * the two Bit crops identical;
  * Magitek mode off.
