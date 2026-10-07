# PALETTE AUDIT — map `$1A2` (V1), TECH v0.9.3

Tools:
* `tools/palette_audit_v093.py`, bsnes accurate PPU: ROM → RAM → CGRAM for both QA ROMs. Output
  `out/emulator_v093/PALETTE_AUDIT_v093.json`.
* `tools/emu_visual_v093.py` S1: the rendered frame, on bsnes and snes9x.

## 1. Render path (identical in v0.9.2 and v0.9.3, verified on bsnes)
| step | where | v0.9.2 ROM | v0.9.3 ROM |
|---|---|---|---|
| map property byte 25 (palette) | map `$1A2` properties (`maps/celes_outer_v092/map.json`) | `$30` | `$30` |
| palette index in RAM | `$0539` after the map load | `$30` | `$30` |
| table read | LoadMapPal C0:265C `LDA f:MapPal,X`, operand retargeted by V9210 to the relocated table F7:A000 | entry `$30` (F7:D000) | entry `$30` (F7:D000) |
| table entry vs source | `CE.derive(vanilla $18, transform)` | equal (v0.9.2 transform) | equal (v0.9.3 transform) |
| field palette buffers | `$7E7200` (current) and `$7E7400` (fade target), 256 B | = table, except the 10 engine-managed colours | = table, except the 10 engine-managed colours |
| PPU CGRAM rows 0-7 (BG1 / BG2) | NMI transfer from `$7E7200` | = table (0 differing colours) | = table (0 differing colours) |
| CGRAM rows 8-15 (sprites) | MapSpritePal F7:E000 (relocated, V9211 / V9212) | vanilla 0-6 + Vale `$20` in slot 7 | unchanged (S1c: slots 0-6 = vanilla MapSpritePal) |

* The engine-managed colours are BG colours 1-3 and 121-127: text and window colours. The field engine overwrites them
  on every map, including vanilla `$013`.
* The map tiles use BG palette rows 0-7, so every BG row is the `$30` palette.

**Conclusion:**
* There is no render-path, ordering or row-index defect. The modified palette is loaded, it is not overwritten by a
  vanilla reload, and it is not applied to sprites.
* The defect was the palette **data**: the v0.9.2 transform produced colours almost equal to vanilla.

## 2. The v0.9.2 transform and why it read as unchanged
v0.9.2 `palettes/v092/palettes.json` `$30`: desaturate 0.45 → tint (R 1.08, G 0.97, B 0.88) → gain 0.92.

The warm tint pushed the half-desaturated colours back toward red/brown. Measured on the lit BG pixels of the RESET
room frame (bsnes, raw colours, player / NPC masked, reference = the same frame with vanilla `$18` poked into the
buffers):

| | lit-pixel mean RGB distance to vanilla | lit-pixel saturation (max-min, 8-bit) | BG luma std |
|---|---|---|---|
| vanilla `$18` | 0 | 31.8 | 62.0 |
| v0.9.2 `$30` | 13.5 | **42.1** (more saturated than vanilla) | 56.7 |
| v0.9.3 `$30` | 15.7 | **10.5** (-67%; vanilla in the same run 31.9) | 65.1 |

In palette-table terms (5-bit, colours with r+g+b ≥ 24): vanilla 14.3, v0.9.2 9.97, v0.9.3 3.73.

## 3. v0.9.3 palette `$30` (`palettes/v093/palettes.json`)
* desaturate **0.75** toward luma → tint **0.95 / 1.00 / 1.08** (slightly cool steel) → gain **1.04** (+4%, keeps
  the walls readable). Colour 0 of each row is kept (backdrop / transparent).
* Result: muted ash grey / steel, visibly distinct from the vanilla Magitek-lab palette (screenshots
  `S1_1A2_reset.png` vs `S1_reference_vanilla18.png`), not monochrome (a faint cool tint remains), contrast kept.
* Sprite palette `$20` (Vale) and the Praetor overload palette are unchanged: same transform, byte-identical to
  v0.9.2.

## 4. Checks
* S1a, rendered frame: lit distance ≥ 12, saturation ≤ 50% of vanilla, contrast ≥ 60% of vanilla. **PASS on bsnes and
  snes9x** (v0.9.2: FAIL).
* S1b, colour RAM = the v0.9.3 palette (bsnes CGRAM / snes9x buffer). **PASS** (v0.9.2: FAIL).
* S1c, sprite palettes 0-6 = vanilla. **PASS** on both ROMs: no sprite or Celes / NPC palette corruption.
* Selftest 59: the ROM table entry equals the documented transform; table saturation ≤ 50% of vanilla.
