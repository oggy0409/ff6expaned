# FF6 Expanded Edition — TECH v0.6: ENEMY ASSET + MAGIC POINT FOUNDATION

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING**

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`.
Accepted baselines rebuilt byte-exact in the same run: v0.1, v0.2, v0.3, v0.3.1 QA, v0.4, **v0.5 (accepted)**.
Not done (by instruction): final monster art (Rust Hound / Annex Guard / Magitek Praetor), vanilla rebalance,
Celes story, item architecture, Rage/Veldt, SRAM change.

## Phase A result first: TESTMOB B was palette-only
v0.5 TESTMOB B = Dark Wind's exact graphics record with **only the palette swapped to Vulture's (`$04A`)**.
Vulture is a different graphic, so its colour order does not fit Dark Wind's pixels → speckled look.
An exact Dark Wind clone (`$182`) renders **pixel-identical** to vanilla Dark Wind (full battle screen, tile buffer,
palette bytes, size); the Vulture-palette variant (`$183`) has identical tiles and differs only in colours.
The v0.5 graphics routing is correct. Details: `ENEMY_GRAPHICS_AUDIT_v0.6.md` §1.

## Outputs (`out/`)
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc` | `26ebd7d3b1a16bfae94625cead054edc34a1a5b6` | `C9DB005B` | `7B38` | production branch v0.6 (engine only, no QA content, no custom assets) |
| `FF6X_Rev1_TECH_v0.6.0_CELES_TECH.sfc` | `a7ae5d4c1c49ce5cfcbca65de943678b86923fce` | `E2BDA3B1` | `8E63` | production v0.6 + accepted Annex slice |
| `FF6X_Rev1_TECH_v0.6.0_ENEMY_ASSET_QA.sfc` | `14d179cfa61e720aa81ea9c4be518df1e13212fa` | `F13B490B` | `FC13` | **user QA ROM** = celes-tech v0.6 + v0.4 proof maps + custom assets `$180/$181` + Dark Wind isolation `$182/$183` + QA formations `$240–$243` + QA access (Q6xx) |
| v0.5.0 production / celes-tech / monster-tech | `34ad5625…` / `38059442…` / `416d5d9f…` | `844CC192` / `239DD0DF` / `381E6EE5` | | accepted v0.5 (regression rebuild, identical) |

BPS SHA-1: production `24a35c62cf3f6f818b462b9932f0b058e6f78675`, celes-tech `8c24d6540bf740486480b5eef791539767ba5eb1`,
QA `afdfee198406f87c98abed18365526cc4d073a85`. Each ROM also has `.ips`, `.manifest.json` (machine-readable diff/patch manifest), `.diff.csv`.

```
python build.py "Final Fantasy III (USA) (Rev 1).sfc"          # all 14 targets, deterministic, no third-party libraries
python tools/selftest.py "<rom>"                                # 50 fail-closed guard tests
python devtools/make_qa_sprites_v06.py                          # (dev, once) regenerates the QA PNG sources
```

## What changed (all v0.6 targets) — exact rows in `PATCH_TABLE_v0.6.md`
| ID | What | PC | SNES | Original → new |
|---|---|---|---|---|
| E101 | MonsterPal relocated (1024 units; vanilla `$000–$2FF` identical) | 3B0000–3B3FFF | FB:0000–FB:3FFF | FF → table |
| E101 | empty-palette-slot shadow (vanilla D3:7810 bytes) | 3BFFF0–3BFFFF | FB:FFF0–FB:FFFF | FF → 16 B |
| E102 | MonsterStencil relocated (header + 256 small + large) | 3B4000–3B4E03 | FB:4000–FB:4E03 | FF → table |
| E103 | custom tile data (QA build only) | 3C0000–3C035F | FC:0000–FC:035F | FF → 864 B |
| E104 | BattleMagicPoints relocated (1024 battles) | 38E000–38E3FF | F8:E000–F8:E3FF | FF → table |
| E105 | MP bound `CPX #$0200` → `#$0400` | 025D98–025D99 | C2:5D98 | `00 02` → `00 04` |
| E200 | 15 operands: 6 MonsterPal, 8 MonsterStencil (incl. colosseum literal C3:AFFD), 1 BattleMagicPoints | see table | | operand bytes only, instruction asserted |
| E300 | router `EnemyGfxBase` (35 B) | 301240–301262 | F0:1240–F0:1262 | FF → code |
| E301 | AddMonsterGfxOffset hook | 0120FF–012103 | C1:20FF | `A5 64 18 69 00` → `22 40 12 F0 60` |

Why: custom enemy graphics need storage outside the vanilla graphics window, new palettes, new tile arrangements
(stencils) and a way to select the expansion bank per monster (MonsterGfxProp byte2 bit5, ignored by vanilla);
new formations need Magic Points. All vanilla records are copied unchanged; reversible by restoring 46 vanilla bytes (15 operands = 39 B, C1:20FF hook 5 B, C2:5D98 bound 2 B).

## Asset pipeline
`monsters/<m>/`: `monster.json`, `stats.json`, `ai.txt`, `loot.json`, `control.json`, `sketch.json` (definition) ·
`sprite.png` (indexed graphics data) · `graphics.json` (bpp, stencil kind, overlap = metadata) · `palette.json` (palette data) ·
battle size derives from the image; position/VRAM box from `formations/<f>.json` (+ `magic_points`).
Builder: `ff6x/png.py` (PNG reader), `ff6x/enemygfx.py` (tiles, stencil, palette, gfx-prop), `patches/enemy_v06.py`
(allocation, relocation, hook, MP, VRAM-box check). Allocation manifest v6: ENEMYX_PAL / ENEMYX_STENCIL / ENEMYX_PAL_EMPTY_SLOT /
ENEMYX_GFX / ENEMYX_SPARE / GRAPHICS_RESERVED_FE, FORMX_MAGIC_POINTS / MONX_SPARE_3.

## QA content (QA ROM only)
| | `$180` TESTCUBE A | `$181` TESTEYE B | `$182` DW CLONE | `$183` DW VULPAL |
|---|---|---|---|---|
| graphics | custom blue gel cube, 4bpp, 32×40 | custom orange spiked eye, **3bpp**, 32×32 | vanilla Dark Wind | vanilla Dark Wind |
| palette | new `$300` | new `$302` | `$046` (Dark Wind) | `$04A` (Vulture) |
| stencil | new `$80` | new `$81` | `$1F` | `$1F` |
| AI | Battle / Mute | Battle / Slow | Battle | Battle |
Formations: `$240` cube+eye **0 MP**, `$241` cube+eye **3 MP**, `$242` = vanilla `$008` with slot 5 = `$182`, `$243` = `$008` with slot 5 = `$183`.
Event groups `$FE/$FD/$FC/$FB` → `$240/$241/$242/$243`.
QA access: New Game → up 6, left 4 → `TECH v0.6 QA ACCESS` (Custom monster battle / More tests / No (Save Point));
More tests → Dark Wind isolation / Magic Point test (gives Ramuh) / Map/Annex tests.

Docs: `ENEMY_GRAPHICS_AUDIT_v0.6.md`, `MAGIC_POINT_AUDIT_v0.6.md`, `CAPACITY_REPORT_v0.6.md`, `REGRESSION_REPORT_v0.6.md`,
`KNOWN_RISKS_v0.6.md`, `USER_QA_TECH_v0.6_VI.md`, `PATCH_TABLE_v0.6.md`.
