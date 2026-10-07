# CUSTOM ASSET SPEC — E8 memorial / archive art (ART ASSET GATE v1.0)

This is the implementation spec only, not artwork. The E8 state / persistence architecture is **accepted** and stays as
it is:
* event bits `$0E9-$0EC`;
* startup-event selection;
* `states.json` as the single source;
* the builder validation.

Only the tiles drawn for each state change. All numbers come from the decoded ROM (`TILESET_TECH_INFO.md`,
`CAPACITY_1A2.json`).

## 1. Common technical rules (all five assets)
| item | rule |
|---|---|
| layer | BG1 of map `$1A2` |
| unit | 16 × 16 px metatile = 2 × 2 tiles of 8 × 8 |
| bit depth | SNES 4 bpp (16 colour indices per 8 × 8 tile) |
| colours per 8 × 8 tile | max **15 visible + index 0**. Every 8 × 8 tile uses **one** palette row (3-bit row in the BG word). Different 8 × 8 tiles of one object may use different rows. |
| palette | map palette `$30` (`PALETTE_1A2.png`): 8 rows × 16 |
| palette rows free for new art (drawn nowhere on $1A2) | **rows 4, 5, 6** (45 colours) and row 0 idx 4-15 |
| palette rows to reuse so the object sits in the wall | **row 3** (wall) and row 2 (floor / corners) |
| colours that must not be used | CGRAM 1-3 (row 0 idx 1-3) and 121-127 (row 7 idx 9-15): engine-managed, overwritten at runtime |
| index 0 / transparency | index 0 is transparent. Behind BG1 there is nothing (BG2 empty, backdrop = `$0000` black), so **every index-0 pixel shows as pure black**. Use real dark colours (not index 0) for dark areas. This is the mistake the v0.9.3 "burned" placeholder made: it reused the void tile `$02` and read as a missing tile. |
| 8 × 8 tile order | row-major inside each metatile: TL, TR, BL, BR (the order of the tileset words) |
| metatile order | row-major inside the region, as in `states.json` (`rows`, left → right, top → bottom) |
| flips | per 8 × 8 tile, h and/or v (BG word bits 14 / 15); mirrored 8 × 8 tiles are stored once |
| priority | 0 (like every wall tile of $1A2). No sprite ever stands on these rows; priority 1 is not needed. |
| animation | static. The current "kept" placeholder (`$BB/$CB`) uses animated VRAM tiles of the vanilla Magitek-lab animation; custom art will not animate unless a new BG animation table entry is approved (out of scope). |
| collision | **every tile of every state impassable** (tile property byte1 & 7 == 7). The floor row below (trigger row 12) stays walkable. The builder runs the movement model for all 9 memorial × archive combinations and rejects any change of the reachable floor. |
| source size | PNG exactly the pixel size below, indexed (≤ 16 colours per 8 × 8 tile, one row each), on an 8 × 8 grid aligned to the region origin |

## 2. The five assets
Regions: `MEMORIAL_REGION.json`, `ARCHIVE_REGION.json` (coordinates in metatiles of BG1).

| asset | region (x, y, w × h) | px | 8 × 8 tiles (max, before dedupe) | metatiles | reads as | must not |
|---|---|---|---|---|---|---|
| **TEMPORARY MEMORIAL** (state `tags`: Celes done, Graves not done) | (9,10) 4 × 2 | 64 × 32 | 32 | 8 | name plaques / tags / records of the dead hung on the machinery wall; improvised, light, many small items | read as wall machinery; be pure black |
| **PERMANENT STONE MEMORIAL** (state `stone`: Graves done) | **A:** (9,10) 4 × 2 · **B:** (9,9) 4 × 3 | 64 × 32 · 64 × 48 | 32 · 48 | 8 · 12 | heavier, permanent: carved stone, a base, inscription; clearly more solid than the temporary memorial | look like the temporary one re-coloured |
| **ARCHIVE PRESERVE** (state `kept`) | (19,10) 2 × 2 | 32 × 32 | 16 | 4 | intact shelves / cabinet / records storage behind the doorway | be the sealed door |
| **ARCHIVE BURN** (state `burned`) | (19,10) 2 × 2 | 32 × 32 | 16 | 4 | burned shelves, rubble, soot, charred frame | be empty black / missing tiles (no index-0 areas, no void tile `$02`) |
| **ARCHIVE SEALED** (state `sealed`) | (19,10) 2 × 2 | 32 × 32 | 0 if reused | 2 (`$12`, `$13`) | closed grate door | — the v0.9.3 gate may be reused if approved |

Notes:
* Option B (4 × 3) extends the permanent memorial up into the wall-top row 9 (tiles `$A1/$A2`, impassable). The trigger
  row 12 is not touched.
  * It needs `states.json` to give the `stone` state its own rectangle (`y` 9, `h` 3). The other memorial states would
    then redraw row 9 with the wall top (`A1 A2 A1 A2`).
  * This is a data change to the region rows. The event bits and the selection logic stay unchanged.
  * **Decision for you:** keep 4 × 2 (A) or allow 4 × 3 (B).
* The region size is fixed by the trigger and the wall. Wider art means redefining the region in `states.json` and the
  startup event (both builder-checked).

## 3. Budget and capacity
| resource | worst case for all new art (A or B) | available for $1A2 |
|---|---|---|
| unique 8 × 8 tiles | 32 + 32 / 48 + 16 + 16 = **96 / 112** (fewer after dedupe / flips) | **148** free in a cloned graphics slot 4 (`$3A` copy). Tilesets `$22`/`$43` do not reference 35 of its tiles, but set `$3A` is also loaded by map `$109` with tileset `$2F`, so only the clone is safe. |
| metatile ids | 8 + 8 / 12 + 4 + 4 = **24 / 28** | **145** ids not on $1A2 and already impassable in property set `$24` |
| palette | ≤ 3 rows of new colours | rows 4, 5, 6 free (palette `$30` belongs to $1A2 only) |

## 4. Injection destination (proposed; implementation is a future TECH milestone, not this gate)
Nothing shared with vanilla maps may be overwritten (`TILESET_TECH_INFO.md` §7). The only way to append without
touching vanilla assets is to clone:

| # | what | where | why |
|---|---|---|---|
| 1 | **new graphics set** `$52` = copy of `$3A` (FACTORY_5) with the new 8 × 8 tiles in tiles not used on $1A2 | `GRAPHICS_RESERVED_FE`, e.g. FE:0000-FE:1FFF ($2000 B, uncompressed, DMA'd as-is). Pointer: DF:DA00 + 3 × $52 = DF:DAF6 (Rev 1 bytes `FF FF FF`); value = FE:0000 − DF:DB00 = `$1E2500`. | the vanilla pointer slots `$52-$54` are unused. A 24-bit offset reaches bank FE, and the DMA handles a bank crossing. |
| 2 | **new tileset** `$4C` = copy of `$22` with the new metatiles in ids not used on $1A2 that are impassable in set `$24` | FE:2000-FE:2FFF (LZSS; ≤ $800 B decompressed). Pointer: DF:BA00 + 3 × $4C = DF:BAE4 (Rev 1 `FF FF FF`); value = FE:2000 − DE:0000 = `$202000`. | 9 vanilla tileset slots are unused; 24-bit offset. |
| 3 | **tile properties**: keep set `$24` | — | the chosen ids are already `F7/FF` (impassable), so no collision data is written. A new set would have to live in bank D9 (16-bit offset, fixed bank). The free runs there need an audit first, or the loader needs a hook. Avoid it. |
| 4 | **map `$1A2` property row**: graphics slot 4 → `$52`, BG1 tileset → `$4C` | the relocated MapProp row of $1A2 (F7:4000 + 33 × $1A2), bytes 9-12 re-encoded (7-bit fields packed across byte boundaries, `ff6x/fieldgfx.decode_props`) | $1A2 is a new map, so no vanilla row changes |
| 5 | **`states.json`** rows → new metatile ids; the startup-event `set_tiles` lines are generated from it | `maps/celes_outer_v092/states.json` | the accepted mechanism; the builder asserts event = states.json and the collision model |
| 6 | **palette** rows 4-6 of `$30` (or the production palette that replaces it) | `palettes/v093/palettes.json` (new version) | `$30` is used only by $1A2 |

* Can the tiles be appended without overwriting vanilla assets? **Yes**, through steps 1-2: new entries in unused
  pointer slots, data in reserved bank FE, and only $1A2's own property row pointing at them.
* Vanilla sets `$36/$37/$38/$3A/$22/$43/$24` stay byte-identical. The production / celes-tech builds would be checked
  byte-for-byte as today.
* Before implementing, the allocations manifest needs:
  * new regions in FE (`MAPX_GFX`, `MAPX_TILESET`);
  * vanilla-space claims for the pointer slots DF:DAF6-DAF8 and DF:BAE4-BAE6.
