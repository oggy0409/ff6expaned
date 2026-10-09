# MAP EXPANSION FOUNDATION (TECH v0.4) — architecture & authoring

## Design choices
| Decision | Chosen | Why / alternatives |
|---|---|---|
| Table relocation method | Copy vanilla table to MAP_EXPANSION, **same record format and relative-pointer convention**, retarget only the 24-bit operand of each consumer | Minimal + reversible: consumer logic untouched; 90 audited 3-byte operand edits. Alternative (rewriting loaders for 24-bit pointers/new formats) rejected: larger engine rewrite, no capacity need yet. |
| Pointer count | 513 for all packed tables | Map index is 9-bit; covers every legal ID. Unused maps get empty runs (start == end), the engine's own "no records" path. |
| Sub-region sizes | 16/32/16/8/8 KiB | ≥ 2.6× vanilla record counts each; 16-bit relative pointers allow up to 64 KiB per table if ever needed (move table, grow region). |
| Map properties | 512 rows (vanilla 415) | Single consumer (LoadMapProp, X = map·33 ≤ $41DF). |
| Layout pointers | 1024 entries, same offset format (from D9:D1B0) | Layout index in map properties is 10-bit; offsets are 24-bit with carry → any F0–FF bank. Unassigned entries = entry $000 value (deterministic, valid stream). |
| NPC event routing | Router hook in InitNPCs + vector table | Alternatives: (a) more CA–CD bridge stubs — limited free space in event banks, one 5-byte stub per NPC; (b) widen NPC record to 24-bit — changes a 9-byte format used by 2,193 records + 21 consumers + editors. The router costs 5 vanilla bytes + 71 bytes and keeps every vanilla record valid. |
| Map IDs beyond vanilla | $19F–$1FD | $1FE/$1FF have engine meaning (event cmd $6A, entrances). MapInitEvent (512 slots, $19F+ = EventReturn) and battle tables (512) already cover them. |
| Vanilla tables after relocation | left in place (dead) | Reversibility and zero risk of overwriting something that still reads them. Reclaiming that space would need a separate audit. |

## Consumers (Rev 1, from the disassembly debug info)
`audits/MAP_CONSUMERS_v0.4.md` (machine-readable: `data/map_relocation_v04.json`, evidence:
`audits/map_consumers_v0.4.json`). Field code: entrance.asm (long/short), event.asm (triggers),
obj.asm (NPCs), scroll.asm + player.asm (treasure), map.asm (props, layout pointers);
world-map code: move.asm (short entrances, triggers). No other code references these tables
(symbol cross-reference + source grep for raw addresses).

## Authoring a new map (production workflow)
1. Pick an unused ID from `$1A2–$1FD` (or an audited blank vanilla ID) and a layout index from `$163–$3FF`.
2. `maps/<name>/map.json`: size, `tile_property_set`, property bytes, `bg1` (legend text **or** `compose`), optional `bg2`,
   `entry.arrive`. `npcs.json` (≤ 32 per map; switch by name; `event` label), `triggers.json`, `exits.json`
   (`short_entrances`, `long_entrances` with `length`/`vertical`), `encounters.json`.
3. `events/<package>/package.json` (event org/region, patch IDs, list of maps), `events.evt`, `dialogue.json`.
4. Allocate any new flag in `data/allocations.json` (must be FREE_CANDIDATE in the audit).
5. `python build.py <rom> --target ...` — the builder validates walkability with the engine movement rule
   (direction masks, counter tiles, z-levels, bridges), refuses leaks / unreachable NPCs / >32 NPCs,
   assigns NPC vectors, places layouts, writes all records into the relocated tables.

Compose example (`maps/map_tech_b/map.json`): canvas filled with a void tile, a 12×12 room copied from
vanilla layouts $06F/$070 into new BG1/BG2 layouts. Use it to consolidate logical environments into
existing art without new graphics.

## Limits that remain
- ≤ 32 NPCs per map, ≤ 128×64 tiles per layout, 9-bit map IDs (512), 10-bit layout IDs (1024).
- Event scripts addressed with 24-bit offsets from CA:0000 (reach CA:0000–FF:FFFF).
- Treasure chests on new maps need chest-bit allocation (not done; item architecture is a later module).
- External editors (FF3usME, FF6LE) cannot edit relocated tables; the builder is the only authoring path.
