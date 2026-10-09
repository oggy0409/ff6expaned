# ROOT CAUSE — TECH v0.9.2 user-runtime visual failures V1–V4 (fixed in TECH v0.9.3)

Status: STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING. Scope: QA ROM only. The production and celes-tech v0.9.1
ROMs are byte-identical; their SHA-1s are now asserted by `build.py`.

## How the failures were reproduced
* Every failure was reproduced on the v0.9.2 QA ROM (`697a25e8…`), starting from **New Game with no party preset**. That
  is the path the v0.9.2 guide gave you, and the one you followed.
* Each case was run on two emulators:
  * snes9x (stable-retro);
  * bsnes with the accurate PPU, driven through a new ctypes libretro frontend (`tools/emu_bsnes.py`). It exposes WRAM,
    VRAM, CGRAM, OAM and SRAM.
* Both emulators show all four failures on the v0.9.2 ROM. The v0.9.2 emulator suite missed V2/V3 because it always
  chose party preset P1 before testing. It missed V1/V4 because it checked RAM and tables but not how the frames
  looked.
* BEFORE / AFTER evidence:
  * `out/emulator_v093/visual_*` and `before_v092_*`;
  * contact sheets `out/VISUAL_BEFORE_AFTER_bsnes.png`, `out/VISUAL_BEFORE_AFTER_snes9x.png`,
    `out/E8_STATES_*.png`.

| # | defect | root cause | class | fix |
|---|---|---|---|---|
| V1 | map `$1A2` looks like the vanilla Magitek-lab palette | **Palette data, not the render path.** The path is correct: map property byte 25 = `$30` → `$0539` → LoadMapPal C0:265C (relocated table F7:A000, operand V9210) → field buffers `$7E7200`/`$7400` → CGRAM. bsnes CGRAM = palette `$30`, byte for byte. But the v0.9.2 transform desaturated by 45% and then **re-warmed** the colours (tint R 1.08 / G 0.97 / B 0.88). On lit pixels the result was *more* saturated than vanilla (42 vs 32) and within ~13 RGB levels of it, so it read as unchanged. | wrong palette parameters | palette `$30` retuned in `palettes/v093/palettes.json`: desaturate 0.75, tint 0.95 / 1.00 / 1.08, gain 1.04. Lit saturation 10.5 vs vanilla 31.9 (-67%, bsnes), contrast kept (luma std 65 vs 62). `PALETTE_AUDIT_v0.9.3.md` |
| V2 | WoR dog (Lunaris, formation `$CA`/`$CB`) has its head replaced by garbage blocks | **QA party state.** After New Game the party is Terra + Wedge + Vicks, all three with Magitek status. The v0.9.2 entry `WoR aboard the Falcon` cleared Magitek on Terra only (`status_clear $00 $FFF7`), so Wedge and Vicks kept the armor. Any battle then runs in Magitek battle mode (`$7E64BA` = 1), and the armor graphics overwrite monster tile cells rows 0-11 × cols 12-15 (VRAM `$6000`-based, `data/vram_safety.json`). Lunaris sits in VRAM map 0, slot 1 (box cols 8-15). Its 6 × 6 stencil reaches cols 12-13: **10 of 29 tiles overwritten, all inside the armor area**, and those are the head cells. The vanilla graphics router and formation data are unchanged. The same happens in Rev 1 with a Magitek party, which never meets this formation in the real game. | QA harness state (not engine) | new QA routine `QaCelParty93`, called first by every Celes-enabler entry (WoR, Praetor locked / QA-scaled, walk-in). It removes Wedge / Vicks, clears Magitek on all 16 records, resets Terra's field sprite, and uses preset P1 if nobody but Terra is in the party. `VRAM_AUDIT_v0.9.3.md` |
| V3 | one Suppressor Bit has garbage tiles | **The same Magitek party state.** Formation `$244`/`$245` uses VRAM map 4. Slot 1 (box origin col 0, row 8) is outside the armor area. **Slot 2 (box origin col 8, row 8) overlaps it in cols 12-15**. The Bit stencil is 7 columns wide, so in slot 2 it reaches cols 12-14: **12 of 46 tiles overwritten (VRAM `$7180`…), all in the armor area**. Slot 1 is untouched, which is why exactly one Bit was corrupt. The formation was already declared `magitek_possible: false`, correctly: the Celes arc has no Magitek party. Only the QA entry broke that assumption. | QA harness state | same normaliser. The locked `$244` and QA-scaled `$245` both render both Bits pixel-exact vs ROM data, and the two Bit crops are identical (bsnes and snes9x) |
| V4 | E8 memorial / archive states do not visibly change | **Tile vocabulary.** The tiles *did* change in the map buffer and in the frame, on both emulators: 31-47% of the region pixels differ. But v0.9.2 swapped one row of wall-edge / wall-panel tiles (`B0 B3`, `C0 66 C3`, `D0 D3`, `57 56`), and those read as part of the machinery wall. The sealed state was identical to the plain wall. | placeholder art too subtle | real map-state objects, data in `maps/celes_outer_v092/states.json`. Memorial 4 × 2 tiles (none / lit name-tag panel / four stone pillars on a riveted base). Archive 2 × 2 tiles (sealed grate door / record shelves / burned-out opening above rubble). 79-99% of the region pixels change between states. The builder checks every state against the startup event and the movement model, so no wall becomes walkable. `MAP_STATE_VISUAL_AUDIT_v0.9.3.md` |

## What did not change
* No engine code, hook, vanilla-space patch, item ID or effect, save layout, boss threshold, AI rule, dialogue
  decision or event-bit meaning.
* The relocated palette tables, the AI extension, the item engine and every v0.9.2 enabler mechanism are unchanged.
* Byte delta v0.9.2 QA → v0.9.3 QA (`PATCH_TABLE_v0.9.3.md`): 934 B in 56 runs, all in QA expansion regions. The
  changed areas are:
  * map palette `$30`;
  * enabler events;
  * the trigger and NPC vector tables pointing into the enabler events;
  * QA hub events and dialogue;
  * build metadata;
  * the header checksum.

## Why the v0.9.2 emulator evidence missed it
| failure | v0.9.2 check | gap | v0.9.3 check |
|---|---|---|---|
| V1 | E6: field buffer = derived palette | it proved the data was installed, not that it looked different | S1: the rendered frame vs the same frame in vanilla `$18`, on lit pixels: distance, saturation ratio, contrast |
| V2 | none (no WoR battle rendered) | — | S2: WoR encounter from the guide path, dog pixel-exact vs ROM data |
| V3 | E2 Bits shown (`$2F2F` = 7), after preset P1 | the test party never had Magitek | S3: both Bits pixel-exact + crops identical, from New Game without a preset |
| V4 | E8: tile bytes in RAM | the bytes changed, the look did not | S4: rendered region crops differ ≥ 60% pairwise, plus persistence by pixels |
