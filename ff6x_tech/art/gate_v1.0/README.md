# FF6X ART ASSET GATE v1.0 — map $1A2 E8 memorial / archive source material

This is an **export-only milestone**. It contains no feature, no story code and no ROM change. It hands the visual source
material to a deliberate human / art pass for the E8 memorial and archive states. The E8 placeholder art was rejected for
production in the TECH v0.9.3 user runtime QA; the E8 state / persistence architecture was accepted and is not touched.

* Baseline: **TECH v0.9.3 — ACCEPTED / USER RUNTIME PASS**. QA ROM `15af77fe9c01f54844fbcbbb0c5f1d65768d55f0`; production
  v0.9.1 `2dc73bfb…` and celes-tech v0.9.1 `e2192311…` unchanged. Every export was read from those bytes; nothing was
  written.
* Not started (by instruction): CONTENT v1.0, the Celes ROM Script Pass, new events / bosses / items, VRAM changes.
  This gate creates no final artwork.

## Files
| file | content |
|---|---|
| `MAP_1A2_CURRENT.png` | full map, current (RESET) state, ×2, grid, coordinates, E8 regions + triggers |
| `MAP_1A2_CURRENT_1X.png` | the same render 1:1 (512 × 512), no annotation: paint-over base |
| `MAP_1A2_METATILE_IDS.png` | the map with every BG1 metatile id |
| `MAP_1A2_STATES.png` | E8 regions in RESET / PRESERVE / BURN / GRAVES: ROM render vs bsnes screenshot |
| `MAP_1A2_RUNTIME_*.png` | bsnes screenshots of the four states |
| `REGION_MEMORIAL_*.png`, `REGION_ARCHIVE_*.png` | each state ×6 with ids and the region box |
| `TILESET_1A2_8X8_IDS.png` / `.json` | VRAM BG tiles `$000-$2FF`: id, source graphics set:tile, usage |
| `METATILES_1A2_16X16_IDS.png`, `METATILES_1A2_BG2_16X16_IDS.png`, `METATILES_1A2.json` | tilesets `$22` / `$43`: every metatile id, 4 words, collision, usage |
| `PALETTE_1A2.png` / `.json` | palette `$30`: rows, CGRAM index, BGR555, engine colours; vanilla `$18` for reference |
| `MAP_1A2_LAYERS.json` | property row, layer use (BG1 / BG2 / BG3 / OBJ), BG1 rows, animation records |
| `MEMORIAL_REGION.json`, `ARCHIVE_REGION.json` | rectangle, layer, current tile ids, every state, collision, neighbours, constraints, runtime check |
| `CAPACITY_1A2.json` | free metatile ids, VRAM tile slots, free pointer-table entries, reserved ROM space |
| `TILESET_TECH_INFO.md` | the technical description of all of the above |
| `CUSTOM_ASSET_SPEC.md` | implementation spec for the five assets (sizes, colours, collision, injection destination) |
| `ART_PIPELINE.md` | PNG → indexed palette → 8×8 → dedupe / flips → metatiles → states → builder → screenshot check |
| `ART_RECOMMENDATION_v1.0.md` | best vanilla references per asset (no art created) |
| `VANILLA_REFERENCE/` | 24 candidate crops (×3 with ids, 1:1), per-candidate JSON, `INDEX.md`, contact sheet, full source-map renders (`maps/`) |
| `VERIFICATION_v1.0.json` | ROM decode vs running game (bsnes, accurate PPU) |
| `TOOLS/` | the exporter source (also in the repository) and the candidate list |

## Verification (VERIFICATION_v1.0.json): PASS
Map $1A2 was captured on bsnes in every E8 state (RESET, PRESERVE, BURN, GRAVES):

| check | result |
|---|---|
| VRAM tiles `$000-$2DF` | equal to the ROM decode (animation tiles: one of their 4 frames) |
| tilesets `$22` / `$43` in WRAM | identical |
| CGRAM | equal to palette `$30` except the 10 engine-managed colours |
| BG1 map buffer | layout + `states.json` |
| E8 region pixels | exact |
| visible screen | 99.2 % identical to the static render; every other pixel is in the two sprite cells (party leader, survivor NPC) |
