# TECH v0.6 — Enemy graphics audit (Rev 1)

Machine-readable: `data/enemy_relocation_v06.json` (builder input, 15 consumer patch points),
`audits/enemy_consumers_v0.6.json` (evidence incl. source lines), `out/gfx_isolation_v06/GFX_ISOLATION_RESULT.json`.

## 1. Phase A — TESTMOB B ("garbled bird") isolation

**Result: palette-only. The graphics router / metadata / tile routing is correct.**

v0.5 TESTMOB B used gfx-prop `1B 17 00 4A 1F` = Dark Wind's exact record (`1B 17 00 46 1F`) with only the
palette changed from `$046` (Dark Wind) to `$04A` (Vulture). Vulture is a *different* 4bpp graphic
(index `$17C7`), so its 16-colour palette is ordered for Vulture's art, not Dark Wind's. Dark Wind uses all
16 colour indices; with Vulture's palette its dark ramp (indices 2–7) becomes light tan in non-monotonic order
→ speckled, "garbled" look.

Controlled tests (same start RAM, battle injected; vanilla formation `$008` = 2 Leafer + 2 Dark Wind):

| Test | Monster in slot 5 | Tiles in btlgfx buffer | Palette | Size | Battle screen after 600 frames vs vanilla `$008` |
|---|---|---|---|---|---|
| vanilla Rev 1 `$008` | Dark Wind `$028` | reference | `$046` | 4×4 | — |
| A1 QA `$242` | `$182` exact clone (graphics `$171B`, palette `$046`, stencil `$1F`, overlap of `$028`) | **identical** (SHA-1 equal to vanilla slot 4 and 5) | `$046`, bytes identical | identical | **pixel-identical (full screen)** |
| A2 QA `$243` | `$183` = Dark Wind graphics + palette `$04A` (v0.5 TESTMOB B) | **identical** | `$04A` | identical | differs only inside the bird's box (256×224 coords 86,24–111,56) |
| v0.6 QA ROM `$008` | Dark Wind | identical | `$046` | identical | pixel-identical |

Visual: `out/gfx_isolation_v06/GFX_ISOLATION_SHEET.png` (decoded from the emulator's tile buffer + palette bytes).

### A3 — data involved (Dark Wind `$028`)
| Item | Value |
|---|---|
| MonsterGfxProp (vanilla D2:7000 + 5·$028 → v0.5+ F8:8000 slot $028) | `1B 17 00 46 1F` |
| graphics index / tile-data source | `$171B` → E9:7000 + `$171B`·8 = **EA:28D8** (PC 2A28D8), 4bpp |
| stencil (small) `$1F` | `E0 70 F0 F0 00 00 00 00` → rows `###.` `.###` `####` `####` = **14 tiles** = 448 bytes |
| width × height | 4 × 4 tiles (32×32 px), clipped by formation `$008` VRAM map 1 boxes 4×4 (slots 4/5) |
| position | formation `$008` bytes 8–13 `00 00 AB 4C 44 A3` (slot 4 = `$44`, slot 5 = `$A3`; x/y nibbles) |
| MonsterOverlap | 0 (Dark Wind and Vulture) |
| palette `$046` (D2:7820 + `$46`·16) | `00 00 22 00 B7 46 F1 35 6D 29 0A 21 C7 14 85 0C D6 5A E7 7E BE 73 DC 0E B2 0D EA 04 91 20 4B 18` |
| palette `$04A` (Vulture) | `29 25 84 0C BD 73 3A 53 76 3E D0 35 BC 3E 8E 29 2B 21 C7 14 FA 21 11 19 4A 10 15 7A 4E 65 CA 44` |
| consumers on the path | C1:2058 slot router (N301) → LoadMonsterGfxProp C1:204E reads F8:8000 (5 retargeted operands C1:2062–C1:20AB) → AddMonsterGfxOffset C1:20FF (E301 hook) → InitStencil C1:2153 (stencil table, E200) → LoadMonsterGfx C1:2299 / LoadMonsterGfxTile C1:2227 → LoadMonsterPal C1:22D1 (palette table, E200) |

## 2. Rev 1 battle-sprite format (as used by the v0.6 pipeline)
* **MonsterGfxProp** 5 bytes: word0 bits 0–14 graphics index (data address = base + index·8), bit 15 = 3bpp;
  byte2 bit 7 = large stencil (16×16 tiles), bits 0–1 + byte3 = palette number (10 bit);
  byte2 bit 6 = stencil number bit 8 (reaches `$81AB`, the high byte of the 16-bit stencil read — confirmed by the
  colosseum code `AND #$40 / ROL3`); **byte2 bits 2–5 are ignored by the engine** (vanilla: never set in all 416 records).
  **v0.6 uses byte2 bit 5 = expansion graphics** (lands in `$81AC` bit 4, which is never tested).
* **Stencil**: small = 8 rows × 1 byte, large = 16 rows × 2 bytes, MSB = leftmost tile. Height = rows from the top
  until the first empty row; width = highest set column + 1; both clipped to the formation's VRAM box.
* **Tile data**: only tiles whose stencil bit is set, row-major. 4bpp = SNES 32-byte tile; 3bpp = 16 bytes planes 0/1 + 8 bytes plane 2.
* **Palette**: index·16 bytes into MonsterPal; LoadMonsterPal always copies 32 bytes (16 colours);
  **at most 3 distinct monster palettes per battle**; an unused palette slot reads MonsterPal + `$FFF0`.
* **VRAM**: 16×16 tiles per battle; formation byte 0 bits 4–7 select one of 13 VRAM maps (per-slot boxes, `ff6x/enemygfx.py VRAM_MAPS`).

## 3. Changes (all v0.6 targets) — exact rows in `PATCH_TABLE_v0.6.md`
| ID | What | PC | SNES | Original → new |
|---|---|---|---|---|
| E101 | MonsterPal relocated, 1024 units (`$000–$2FF` vanilla, `$300–$3FF` new) | 3B0000–3B3FFF | FB:0000–FB:3FFF | FF fill → table |
| E101 | empty-palette-slot shadow (16 vanilla bytes from D3:7810) | 3BFFF0–3BFFFF | FB:FFF0–FB:FFFF | FF → `00 00 70 3C 1E 0F 06 04 06 00 0A 00 1A 00 3A 00` |
| E102 | MonsterStencil relocated: header `04 40 04 48` + 256 small + large maps | 3B4000– | FB:4000– | FF → table |
| E103 | custom tile data (QA only in monster-tech) | 3C0000– | FC:0000– | FF → data |
| E200 | 6 MonsterPal operands (C1:233D, C1:D679, C2:BBD4 (+$20), C2:FA7C, C2:FA93, C3:B171) | | | `20 78 D2` → `00 00 FB` |
| E200 | 8 MonsterStencil operands (C1:216E, C1:2178, C1:2194, C1:219E, C3:AFBF, C3:AFC8, C3:AFD3 + **literal bank byte C3:AFFD**) | | | D2/A820 → FB/4000 |
| E300 | router `EnemyGfxBase` (35 B) | 301240–301262 | F0:1240–F0:1262 | FF → code |
| E301 | AddMonsterGfxOffset hook | 0120FF–012103 | C1:20FF–C1:2103 | `A5 64 18 69 00` → `22 40 12 F0 60` |

The colosseum literal (`src/menu/colosseum.asm:456 lda #$d2`) was not reachable through the symbol cross-reference;
it was found by reading every MonsterStencil user and is part of the relocation list (otherwise colosseum sprites would
read their stencil from bank D2 with a FB pointer).

**Not relocated:** MonsterGfx tile window E9:7000 (vanilla graphics stay; colosseum has its own hard-coded `E9/7000`,
fine because new monsters cannot be colosseum opponents).

## 4. Source format (custom assets)
`monsters/<m>/graphics.json` `{"custom": {"image": "sprite.png", "bpp": 3|4, "stencil": "small"|"large"}, "overlap": n}`,
`palette.json` `{"colors": [8 or 16 × "#RRGGBB"]}`, `sprite.png` indexed PNG (index 0 = transparent).
The builder (`ff6x/enemygfx.py`, no third-party libraries) derives tile data, stencil (re-uses an identical vanilla or earlier
stencil, else allocates a new one), size, BGR555 palette; checks PNG palette == palette.json, sizes, colour count, top-edge
alignment, and each formation's VRAM box (`patches/enemy_v06.py check_vram_box`). Graphics index, palette unit, stencil
index are allocated deterministically and written to the monster's gfx-prop slot.

QA assets: `$180` TESTCUBE A (4bpp, 32×40, new stencil `$80`, palette `$300`, FC:0000, 576 B);
`$181` TESTEYE B (3bpp, 32×32, new stencil `$81`, palette `$302`, FC:0240, 288 B).
