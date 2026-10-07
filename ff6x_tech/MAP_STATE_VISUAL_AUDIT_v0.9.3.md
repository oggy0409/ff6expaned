# MAP STATE VISUAL AUDIT — E8 outer-map states of `$1A2` (V4), TECH v0.9.3

These are still TECH placeholders (D-14): vanilla Magitek-lab tiles under the v0.9.3 ash palette, not final art. The
purpose is to prove the state-change architecture with states that are impossible to miss.

## 1. Mechanism (unchanged since v0.9.2, re-verified)
| item | value |
|---|---|
| when | map startup event `EvOuterInit`: MapInitEvent table D1:FA00 entry for `$1A2`, code in the claim `MAP_INIT_EVENTS_NEW`. It runs on **every** load of `$1A2`: hub walk-in (load_map + startup flag), the World of Ruin short entrance, re-entry after leaving, Continue |
| what | event command `$73` (change BG tiles, immediate). It writes the BG1 map buffer `$7F:0000` (256 tiles per row) and redraws the visible tilemap |
| layer / palette | BG1; the tiles carry their own palette bits from the tileset (rows 0-7, palette `$30`) |
| order | after the map layout is decompressed, before the screen fades in. Nothing is drawn from the old tiles: S4 frames are taken right after the fade-in, and re-entry / Continue frames match the in-session frames |
| map redraw needed? | no. `$73` updates the buffer and the visible tilemap. Off-screen rows (the memorial wall is 15 rows above the arrival tile) are drawn from the buffer when they scroll in |

## 2. What was wrong in v0.9.2
* v0.9.2 changed **one row**: memorial (10-12, 10), archive (19-20, 10).
* It used tiles of the same machinery wall: wall-face edges `B0 B3`, lower-wall pieces `C0 66 C3`, wall pillars
  `D0 D3`, the void tile `02`. The sealed state used the plain wall tiles `57 56`.
* The bytes and pixels did change: 31-47% of the region pixels differ (`out/E8_STATES_bsnes.png`, top row). But the
  result read as more wall, and "sealed" looked exactly like the wall. Only the event text told the states apart.

## 3. v0.9.3 states (`maps/celes_outer_v092/states.json`, event `EvOuterMem*` / `EvOuterArc*`)
Regions:
* memorial: x 9-12, y 10-11, 4 × 2 tiles, above the memorial trigger (10,12);
* archive: x 19-20, y 10-11, 2 × 2 tiles, above the archive trigger (20,12).

| state | bits | memorial tiles (row 10 / row 11) | archive tiles | look |
|---|---|---|---|---|
| 0 RESET | `EXP_CELES_DONE` = 0 | `57 56 57 56` / `67 66 67 66` (= layout) | sealed `12 12` / `13 13` | plain machinery wall, **no memorial**; archive **closed framed grate door** |
| 1 ARC DONE, PRESERVE | DONE, CHOSEN, PRESERVED | `91 92 91 92` / `90 93 90 93` | kept `BB BB` / `CB CB` | **temporary memorial**: lit panel of hanging name tags; archive **open, record shelves intact** (BG-animated highlight) |
| 2 ARC DONE, BURN | DONE, CHOSEN, PRESERVED = 0 | tags (same as 1) | burned `02 02` / `96 97` | tag memorial; archive **black burned-out opening above rubble** |
| 3 GRAVES WITHOUT NAMES | `EXP_GRAVES_DONE` | `F1 F2 F1 F2` / `11 11 11 11` | keeps its branch | **permanent stone memorial**: four pale stone pillars on a heavy riveted base, replaces the tags |

Builder guard (`patches/celes_enablers_v092.py map_states()`, selftest 57). The build fails if any of these holds:
* an event `set_tiles` line differs from `states.json`;
* the RESET memorial differs from the compiled layout;
* two states of a region use the same tiles;
* any of the 9 memorial × archive combinations changes the reachable floor of the base map.

The last check runs the movement model with direction masks and z-levels, 138 reachable cells. The first stone
candidate (`C4 C5 / D4 D5`) was refused this way, because those plates are walkable and would have opened the wall.

## 4. Verification (`tools/emu_visual_v093.py` S4, bsnes accurate PPU and snes9x)
| check | v0.9.2 ROM | v0.9.3 ROM (bsnes / snes9x) |
|---|---|---|
| S4a BG1 map buffer after each state = states.json | FAIL (old tiles) | PASS / PASS |
| S4b memorial region (64 × 32 px) pairwise difference RESET / tags / stone ≥ 60%; tags identical in both branches | FAIL (34-35%) | PASS (91% / 91% / 95%; identical on snes9x) |
| S4c archive region (32 × 32 px) sealed / kept / burned ≥ 60%; Graves keeps the retained archive | FAIL (31-47%) | PASS (98% / 99% / 79%) |
| S4d Preserve + Graves via the World of Ruin entrance; exit to the world map; re-entry. Pixels = one frame of the in-session 64-frame series (the shelf highlight is BG-animated), tiles equal | FAIL | PASS / PASS |
| S4e save → power cycle → Continue → walk in: stone memorial + retained archive, pixels and tiles as in session | FAIL (old tiles) | PASS / PASS |

Event flags, trigger texts and persistence of the bits are unchanged from v0.9.2 (you already passed them). The en92
E8 checks now read the regions and tiles from `states.json`.

Screenshots: `out/emulator_v093/visual_bsnes/S4_*.png` (full frames and 4× crops), `out/E8_STATES_bsnes.png`,
`out/E8_STATES_snes9x.png`.
