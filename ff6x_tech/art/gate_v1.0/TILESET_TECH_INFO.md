# TILESET TECH INFO — map $1A2 (ART ASSET GATE v1.0)

Map `$1A2` is the Vector Outer Ward, the QA enabler map of the accepted TECH v0.9.3. Every value below was decoded from
the accepted QA ROM (`FF6X_Rev1_TECH_v0.9.3_VISUAL_STATE_VRAM_HOTFIX_QA.sfc`, SHA-1 `15af77fe…`) by `ff6x/fieldgfx.py`.
It was then checked against the running game on bsnes with the accurate PPU, in all four E8 states:
* VRAM, CGRAM, tileset WRAM and BG1 buffer: identical;
* E8 region pixels: exact.

Details: `VERIFICATION_v1.0.json`. **No ROM byte was written by this gate.**

## 1. Map property row (33 bytes, relocated table F7:4000 + 33 × $1A2)
`00 00 1B 00 24 00 00 B6 1B 4E E7 88 86 63 A9 04 00 00 00 00 00 00 00 55 57 30 00 0E 21 00 1F 1F 00`

| field (engine decode) | value | meaning |
|---|---|---|
| tile property set (byte 4) | `$24` | collision of every metatile id (vanilla, shared with 12 Magitek-lab maps) |
| BG1/BG2 graphics sets (bytes 7-10, 7 bits each) | `$36 $37 $38 $3A` | FACTORY_1 / 2 / 3 / 5 (vanilla, shared) |
| BG3 graphics (byte 10-11) | `$0E` | unused: no BG3 layout |
| BG1 tileset (byte 11) | `$22` | MAGITEK_LAB_1_BG1 (vanilla, shared with 13 maps) |
| BG2 tileset (byte 12) | `$43` | MAGITEK_LAB_BG2 |
| BG1 / BG2 / BG3 layout (bytes 13-16, 10 bits each) | `$163` / `$12A` / `$000` | `$163` = new layout (F5:1208, from `maps/celes_outer_v092/layout_bg1.txt`); `$12A` = vanilla all-transparent filler |
| BG1/BG2 size (byte 23) | `$55` | 32 × 32 metatiles each |
| palette (byte 25) | `$30` | new QA palette (F7:A000 + 256 × $30 = F7:D000), derived from vanilla `$18` |
| BG animation (byte 27) | `$0E` | BG1/BG2 animation index 14 (Magitek-lab); BG3 animation none |

## 2. VRAM map (BG1/BG2 character data, 4 bpp, 32 B per 8×8 tile)
| VRAM tiles | VRAM words | content | source in ROM |
|---|---|---|---|
| `$000-$0FF` | `$0000-$0FFF` | graphics set `$36` FACTORY_1, tiles 0-255 | E4:0980 |
| `$100-$17F` | `$1000-$17FF` | graphics set `$37` FACTORY_2, tiles 0-127 | E4:22E0 |
| `$180-$1FF` | `$1800-$1FFF` | graphics set `$38` FACTORY_3, tiles 0-127 | E4:32C0 |
| `$200-$27F` | `$2000-$27FF` | graphics set `$3A` FACTORY_5, tiles 0-127 | E4:5240 |
| `$280-$29F` | `$2800-$29FF` | **BG animation**, 8 records × 4 tiles, 4 frames each (engine-driven) | E6:xxxx (`MAP_1A2_LAYERS.json` › animation) |
| `$2A0-$2BF` | `$2A00-$2BFF` | BG animation load area: Frame 1 of 8 more records, not cycled | E6:xxxx |
| `$2C0-$2DF` | `$2C00-$2DFF` | graphics set `$3A`, tiles 192-223 | E4:5240 + $1800 |
| `$2E0-$2FB` | `$2E00-$2FBF` | **dialog window graphics** (TfrWindowGfx, 28 tiles, depends on the player's wallpaper) | — |
| `$300+` | `$3000+` | BG3 | — |

* LoadMapGfx always DMAs `$2000` bytes per set. Sets 2-4 overlap, and a later set overwrites the earlier one. The table
  shows what survives.
* A BG tilemap word is `vhopppcc cccccccc`: tile number (10 bits), palette row (3 bits), priority, h-flip, v-flip.
* `TILESET_1A2_8X8_IDS.png` / `.json` lists every tile with:
  * its source set and index;
  * the palette rows it is drawn with;
  * the metatiles that use it.

## 3. Tilesets (16×16 metatiles)
* BG1 = tileset `$22` (DE:D432, LZSS, 1680 B compressed); BG2 = tileset `$43` (DF:89E4).
* Each tileset has 256 metatiles. Each metatile is 4 BG words (TL, TR, BL, BR).
* The decompressed layout is: lo bytes `[q × 256 + id]`, hi bytes `[$400 + q × 256 + id]`.
* `METATILES_1A2_16X16_IDS.png` (BG1), `METATILES_1A2_BG2_16X16_IDS.png` (BG2) and `METATILES_1A2.json` show every
  id with:
  * its four words decoded;
  * its collision;
  * whether it is on `$1A2`;
  * the vanilla maps that use it.
* $1A2 uses:
  * 21 BG1 ids in its layout;
  * 13 more BG1 ids in its E8 states;
  * BG2 id `$01` only.

## 4. Palette (`PALETTE_1A2.png` / `.json`)
* 8 rows × 16 colours = CGRAM `$00-$7F`. Index 0 of every row is transparent; row 0 colour 0 is the backdrop
  (`$0000`, black).
* **Engine-managed colours:** CGRAM 1-3 and 121-127 (row 0 idx 1-3, row 7 idx 9-15). They are overwritten at runtime.
  Do not use them for map art.
* Rows actually drawn on the $1A2 layout:
  * row 3: wall faces and edges (`$56 $57 $66 $67 $A1 $A2 $C0 $C3 $D0 $D3 $E1 $E2`; priority 0);
  * row 2: floor (`$52/$62`) and wall corners (`$A0 $A3 $E0 $E3`);
  * row 1: the void tile `$02`;
  * rows 1-3: wall sides (`$B0/$B3`).
* The E8 state tiles add rows 1, 2, 3 and 7.
* **Rows 4, 5, 6 and row 0 idx 4-15 are not drawn anywhere on $1A2.** Palette `$30` is used by no other map, so a
  production palette can redefine these rows for new art without affecting any vanilla map.
* Vanilla `$18` filler (magenta `$7C1F`, i.e. unused): row 0 idx 5-7, 10-11 · row 2 idx 12-15 · row 3 idx 12-14 · row 4
  idx 1-3, 15 · row 5 idx 11-15 · row 7 idx 8-10, 14-15.

## 5. Layers (`MAP_1A2_LAYERS.json`)
| layer | content |
|---|---|
| BG1 | layout `$163`, 32 × 32, tileset `$22`. All wall / floor / E8 art is here. Priority bit 0 on every word used by the map. |
| BG2 | vanilla layout `$12A`, tileset `$43`, metatile `$01` everywhere: draws nothing (transparent) |
| BG3 | none |
| OBJ | party, Vale (E7, sprite palette slot 7) and the survivor NPC: sprites, not BG art |

## 6. Collision (tile property set `$24`, D9:C85B, LZSS → 512 B)
* byte1 & 7 == 7 → impassable (shown as `X` on the metatile sheet). Otherwise the z-level / bridge bits apply
  (Rev 1 C0:4E35, `ff6x/mapsrc4.can_move`). byte2 is the direction mask.
* Every wall tile, every E8 state tile and the void tile `$02` are `F7/FF` (impassable). The floor tiles `$52/$62`, the
  trigger tiles, are `02/8F` (walkable, lower z).
* The collision is indexed by metatile id. A new metatile inherits the collision of its id in set `$24`, unless a new
  property set is made (`CUSTOM_ASSET_SPEC.md` §4).

## 7. Sharing (why nothing can be edited in place)
These vanilla assets are shared with other maps:

| asset | maps |
|---|---|
| graphics set `$3A` | `$0FE $109 $10B-$112 $124 $160 $163` |
| tilesets `$22` / `$43` | `$0FE $108 $10B-$112 $124 $160 $163` |
| tile property set `$24` | `$0FE $10B-$112 $124 $160 $163` |

Graphics sets `$36/$37/$38` are also used by the Magitek Factory maps. Overwriting any of them changes vanilla maps.
New art must go into **new** graphics / tileset entries that only `$1A2` points to (`CUSTOM_ASSET_SPEC.md`).

## 8. Capacity (`CAPACITY_1A2.json`)
### Metatile ids (tileset `$22`)
| measure | ids |
|---|---|
| total | 256 |
| on the $1A2 layout | 21 |
| in E8 states only | 13 |
| not on $1A2 | 222 |
| not on $1A2 and already impassable in set `$24` | **145**: usable for wall-mounted art in a cloned tileset with **no new collision data** |
| not on $1A2 and unused by every vanilla map with tileset `$22` | 17 |

### 8×8 tile slots (VRAM)
| graphics slot | VRAM tiles | not referenced by tilesets `$22`/`$43` | free in a clone made for $1A2 (not used on $1A2) |
|---|---|---|---|
| 1 (`$36`) | `$000-$0FF` | 114 | 221 |
| 2 (`$37`) | `$100-$17F` | 10 | 119 |
| 3 (`$38`) | `$180-$1FF` | 15 | 103 |
| 4 (`$3A`) | `$200-$2DF` (without animation `$280-$2BF`) | 35 | 148 |

### Free pointer-table entries (Rev 1, bytes `$FF`)
| table | free entries |
|---|---|
| map graphics (DF:DA00) | `$52-$54` (3) |
| tileset (DF:BA00) | `$4C-$54` (9) |
| tile property (D9:CD10) | `$2B-$3F` (21) |

### ROM space
| space | size | note |
|---|---|---|
| `GRAPHICS_RESERVED_FE` FE:0000-FE:FFFF | 64 KiB | all `$FF` in the accepted QA, production and celes-tech ROMs; reserved, unassigned |
| F5 layout bank | 59 766 B | free tail |
| bank D9 `$FF` runs | 762 / 663 / 196 B | tile properties must live in bank D9; a run must be audited before it is claimed |
