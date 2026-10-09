# maps/celes_annex_tech — TECH v0.3 source package

Source of truth for map **$0C7** in the `celes-tech` build. Nothing here is edited
in a ROM tool; `build.py` compiles these files from the clean Rev 1 ROM every time.

| File | Content |
|---|---|
| `map.json` | map id, size, legend (char → tile id/role), BG2/BG3 choice, tile-property set, explicit 33-byte property row, entry point, room list |
| `layout_bg1.txt` | 32×32 BG1 layout, one character per 16×16 tile |
| `npcs.json` | NPC records (order = object number) |
| `triggers.json` | step-on event triggers (incl. the Falcon-interior entry trigger on map $00C) |
| `exits.json` | short/long entrances |
| `encounters.json` | random-battle setting + the event battle used |
| `preview.png` | walkability preview generated from the source |
| `screenshot_*.png` | emulator captures of the compiled map |

Event scripts and dialogue live in `events/celes_annex_tech/`.

## Build-time validation (fails the build)
- every floor cell uses a tile whose property byte 1 is passable; every non-floor cell is impassable ($F7);
- no floor on the map border; all floor reachable from the arrival tile;
- NPCs, triggers and the exit sit on floor; NPCs don't isolate any floor and are talkable;
- runtime check (emulator suite): BG1 + tile properties read back from WRAM match this grid exactly.

## Placeholder status
Tiles/palette come from the vanilla Magitek Research Facility tileset (map $112 settings).
This is technical placeholder art — **not** the locked Annex art direction.
