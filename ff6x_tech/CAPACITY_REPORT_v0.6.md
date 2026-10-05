# TECH v0.6 — Enemy asset + Magic Point capacity (production build)

| Item | Capacity after v0.6 | Used (production / QA) | Notes |
|---|---|---|---|
| Custom enemy tile data | ENEMYX_GFX FC:0000–FD:FFFF = **131 072 B** | 0 / 864 B | index base FB:0000; reserve ENEMYX_SPARE FB:6000–FB:FFEF (40 944 B) and GRAPHICS_RESERVED_FE (65 536 B) can be activated later inside the same index window (FB:0000–FE:FFF8) |
| practical monster count (tile data) | vanilla average 1 174 B, median 864 B, max 6 400 B | | ≈ 110 average-size sprites, or e.g. 35 mobs × 2 KB (70 KB) + 7 full 128×128 bosses (8 KB each) in ENEMYX_GFX alone |
| Palettes | 1024 units; new units `$300–$3FF` = 256 = **128 sixteen-colour palettes** (each new palette takes 2 units) | 0 / 2 palettes | identical palettes are shared automatically |
| Graphics metadata | 1 gfx-prop slot per new ID (543 slots: 416 vanilla + 127) | — | 1:1 with monster IDs `$180–$1FE` |
| Stencils (tile arrangements) | small 256 (128 vanilla, **128 free**), large 191 (48 vanilla, **143 free**) | 128+48 / 130+48 | identical shapes are shared (incl. vanilla shapes) |
| Max graphics size | small stencil 8×8 tiles (64×64 px); large 16×16 tiles (128×128 px), 4bpp or 3bpp | | |
| Per-battle limits (engine) | 3 distinct monster palettes; 16×16-tile VRAM area split by the formation's VRAM map (13 maps, `ff6x/enemygfx.py VRAM_MAPS`) | | builder refuses a custom sprite larger than its slot box |
| Large bosses | need a large stencil and a formation VRAM map with a big box (map 6 = 16×16 solo, map 9 = 12×12, map 3 = 8×16 ×2) | | multi-part bosses = several monster IDs; ≤ 3 palettes per battle |
| Magic Points | 1024 battles; **448 new formations `$240–$3FF` × 0–255 MP** | — / `$241` = 3 | source-controlled per formation |
| F0–FF bytes (this module) | FB:0000–FB:3FFF pal (16 KB, full table), FB:4000–FB:5FFF stencil (8 KB, 3 588 used), FB:FFF0 16 B shadow, FC–FD gfx (128 KB), F8:E000–F8:E3FF MP (1 KB), F0:1240 router 35 B | | MONX_SPARE_3 F8:E400–F8:FFFF (7 KB) reserved |

## Roster verdict
**35 normal mobs + all planned bosses fit comfortably.** IDs: 127 available (v0.5). Tile data: 128 KB active + 104 KB
reserve in the same window. Palettes: 128 new. Stencils: 271 free shapes. MP: every new formation configurable.
Remaining constraints are per-battle engine limits (3 palettes, 16×16-tile VRAM per battle), which affect encounter design
of large multi-part bosses, not capacity.
