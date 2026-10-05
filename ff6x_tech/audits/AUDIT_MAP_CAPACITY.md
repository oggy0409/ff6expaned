# Audit B — Map capacity (Rev 1)

Machine-readable: `map_capacity_audit.json` (per-map counts, properties, startup
event, incoming entrances, event `load_map` references). Generator: `tools/map_audit.py`.

## Engine facts (verified in Rev 1 code/data)
| Item | Format / capacity | Reaches F0–FF? |
|---|---|---|
| Map index | 9 bits (`and #$01FF`); `$1FF` = return-to-parent; `$000–$002` world maps | — |
| Map properties ED:8F00 | 33 bytes × **415** (`fixed_block $3580`) → IDs `$000–$19E`; map `$19F` has no row | 1 consumer (`LoadMapProp`, `LDA.l MapProp,X`) → easy to relocate |
| NPC pointers C4:1A10 / data C4:1D52 | 16-bit relative, **417** pointers (0x1A0 maps + end) · 9 bytes/NPC · **85 bytes slack** (9 NPCs) | 21 long-address consumers (all in `obj.asm`) |
| NPC event pointer | **18-bit** (+$CA) → CA:0000–CD:FFFF only | No → needs CA–CD bridge (see Phase 2) |
| Event triggers C4:0000 / C4:0342 | 417 pointers · 5 bytes · 24-bit event pointer · **18 bytes slack** (3 triggers) | Yes (24-bit) · 12 consumers |
| Short entrances DF:BB00 | **513** pointers (512 maps) · 6 bytes · **136 bytes slack** | 19 consumers |
| Long entrances ED:F480 | **513** pointers · 7 bytes · **342 bytes slack** | 19 consumers |
| Map startup events D1:FA00 | 24-bit × **512** slots | **Yes** — new startup events can live in F1 |
| Map battle groups CF:5600 / prob. CF:5880 | 512 entries | — |
| Treasure ED:82F4 | 416 pointers · 5 bytes | — |
| Layout assets | map formations (350, D9:D1B0), tile formations (75), tilesets/graphics (82), tile properties (42), palettes (48) | per-layout, shared by many maps |

## The 9 community "free" IDs — Rev 1 evidence
`0C7, 0DE, 0DF, 0E0, 0E3, 0E4, 0E5, 0E6, 11E`: all have **0 NPCs, 0 triggers,
0 short/long entrances, 0 incoming entrances from any map, 0 `load_map`
references in the event script**, and the shared `EventReturn` startup event.
- `0C7`: properties row is **all zero** (truly blank).
- The other 8: properties rows contain leftover data (dummy maps) — usable, but
  the row must be rewritten, not assumed.

Beyond those 9, the audit found 24 more structurally unreferenced IDs
(`01D 01F 028 02D 02E 04F 052 063 076 07A 0C0 0C1 0DC 101 109 113 14D 17B 17C 183 184 193 19E 19F`).
They are **not** proposed for use: being unreferenced by tables is necessary but
not sufficient (no ASM/cutscene audit yet).

## Important constraint — adding content to an empty map
NPC / trigger / entrance tables are **packed with delta pointers**. Giving map
`0C7` one NPC means inserting 9 bytes at its offset and adding +9 to every later
map's pointer. The slack above allows that for the vertical slice:
1 NPC + 1–3 triggers + a few entrances fit **without relocating any table**.

## Proposal
1. **Vertical slice (Phase 3):** use **map `0C7` only**; insert records into
   the existing tables using the measured slack; startup event pointer
   (D1:FA00 + 3×0xC7) points straight to F1; layout reuses an existing map
   formation/tileset. No table relocation.
2. **Physical-map consolidation (production):** the 28 logical environments
   should map onto far fewer IDs — reconstruction states via event-bit-driven
   `mod_bg_tiles` / NPC switches on existing maps (Mobliz, Doma, Figaro,
   Vector, etc.), multi-room interiors packed into one map ID with internal
   short entrances. Target: ≤ 9 new IDs (the audited free set).
3. **Table expansion:** necessary for production NPC/trigger volume (85 + 18
   bytes of slack is ~12 records). Recommended: relocate NPC data + pointers and
   event triggers to `MAP_EXPANSION` (F5–F7) by repointing the 21 + 12 audited
   long-address consumers. Map IDs above `$19E` are **not** needed if
   consolidation works; they would additionally require relocating MapProp and
   the 417-entry NPC/trigger pointer tables.

## Tool-vs-engine limits
The engine supports 512 entrance/startup slots; editors (FF3usME, FF6LE)
assume vanilla table locations/sizes. After relocation those editors can no
longer edit NPCs/triggers safely — project data must be authored in the builder.
