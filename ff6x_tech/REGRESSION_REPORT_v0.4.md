# TECH v0.4 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

## Static
| Check | Result |
|---|---|
| Accepted baselines rebuilt byte-exact (v0.1, v0.2, v0.3 celes-tech, v0.3 production, v0.3.1 QA) | PASS (SHA-1 asserted by the builder) |
| Determinism (41 output files, two full builds) | PASS |
| Selftests | 28/28 PASS |
| Event assembler vs disassembly macros | 24/24 PASS |
| Relocated tables decode identical to vanilla for every map (triggers, NPCs, short/long entrances, treasure), 415 property rows, 351 layout pointers | PASS (selftest 21) |
| Production v0.4 vanilla-space diff = 237 bytes, all declared (90 operands, accepted dialogue hook, router site, checksum) | PASS (selftest 22) |
| Every consumer instruction asserted against the clean ROM before retargeting | PASS (builder) |
| Map packages: engine movement model (direction masks, counters, z-levels, bridges) reaches exactly the authored floor (Annex, Map A); compose map B: no leak, NPCs talkable, exits reachable | PASS |

## Emulator (snes9x core via stable-retro) — NOT user runtime QA
### 1. Differential map-load test (vanilla Rev 1 vs production v0.4)
Same start state, same injected `load_map` for every map $003–$19E (412 maps), 150 frames, then fingerprint:
map index, property RAM $0520–$0540, NPC object event pointers, static NPC fields
(visibility, speed, gfx, palette, event pointer, map index, tile position of non-moving NPCs),
full BG RAM 7F:0000–7F:FFFF, tile-property RAM.

| Field | Maps identical |
|---|---|
| map index, properties, BG tilemaps, tile properties, NPC event pointers, static NPC fields | **412 / 412** |
| raw object block (incl. animation counters) | 367 / 412 |

The 45 raw-object differences are only sprite animation-frame bytes (`$0876/$0877`, values 32↔33)
and the sub-tile position of one walking NPC on map $06D: a one-frame phase shift
(production v0.4 reaches first control at frame 8641 vs 8642), not data. The map
load does slightly different work per NPC (router JSL), which can shift NPC animation phase.

### 2. Celes slice on the v0.4 pipeline (celes-tech v0.4, teleport suite, Falcon route, group 40 with HP pokes)
24/24 PASS — Falcon trigger (relocated trigger table), Annex map/grid, Vale + chest via NPC vectors,
sealed door, battle 40 return, no loop, one-time Potion, exit to Falcon (15,47), re-entry.

### 3. map-tech QA ROM from New Game, no RAM pokes
Save phase 21/21, load phase 13/13 (new process, SRAM reload):
QA tile → map $1A0 (grid == source), routed NPC pointers in RAM = F1 vectors, trigger, A1/A3 dialogue,
short entrance → $1A1 (composed grid == source), B1 sets $14D/$6FA, long entrance → $1A0, A2 appears,
A1 second state, door round trip, long strip → $013 (35,43), SavePoint + menu Save → Continue: flags
restored, no prompt loop, A2 still visible, Annex via QA (vectors, battle group $01, reward), vanilla
opening guard event $000D + battle.

Observed (known QA issue): after Continue at the opening QA tile the party is drawn with the walking
sprite instead of Magitek (KNOWN_QA_ISSUE_v0.3.1), consistent with the user report.

Evidence: `out/emu_map_tech/`, `out/emu_celes_v04/`, `out/emu_production_v04/`, `out/TECH_v0.4_emulator_contact_sheet.png`,
`audits/map_diff_vanilla_vs_v04.json`.
