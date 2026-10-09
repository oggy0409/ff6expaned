# TECH v0.5 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

## Static
| Check | Result |
|---|---|
| Accepted baselines rebuilt byte-exact (v0.1, v0.2, v0.3 celes-tech/production, v0.3.1 QA, **v0.4 production / celes-tech / map-tech**) | PASS (SHA-1 asserted by the builder) |
| Determinism (56 output files, two full builds) | PASS (0 differences) |
| Selftests | **40/40 PASS** (15 new v0.5 guards) |
| Relocated tables: 384 monster records ×9 tables, 416 gfx slots, 384 AI scripts + pointers, 576 formations ×2 tables **byte-identical** to vanilla; production new IDs/formations null | PASS (builder assert + selftest 26) |
| Production v0.5 vanilla-space diff = 379 bytes, all declared (v0.4 set + 71 monster operands + 3 hook sites + checksum) | PASS (selftest 27) |
| Rage/Veldt guards C2:4A09, C2:49E9, C2:49E3 unchanged | PASS (builder assert + selftest 27) |
| QA content (Q500–Q503, monsters $180/$181, formation $240, group $FE) only in monster-tech | PASS (selftest 28) |
| Source guards (id range, $1FF, name length, palette range/bpp, AI ends, formation no-Veldt, unassigned monster, undeclared retarget) | PASS (selftests 29–30) |

## Emulator (snes9x core via stable-retro) — NOT user runtime QA

### 1. Differential formation test — vanilla Rev 1 vs production v0.5 (all 576 vanilla formations)
Same start RAM state, same injected `battle` event; `$11E0` set to the formation during the battle
mosaic. Fingerprint at battle start: formation aux `$2F48–$2F4B`, btlgfx monster IDs `$2001–$200C`,
monster entries of every TargetProp1/2 block (`$3204–$35EB`, `$3AA0–$3EAF`: HP/MP, stats, level,
elements, status, steal/drop items, AI script pointers, control, special anim…), and the screen.

| Field | Formations identical |
|---|---|
| Battle-engine data loaded from monster/formation tables | **576 / 576** |
| Screen at +90 frames | 574 / 576 |

The 2 screen differences ($03D, $10F) are a 1-frame fade-in phase shift (production frame N+1 ==
vanilla frame N), not data. Colosseum formations $23E/$23F included. Report:
`audits/formation_diff_vanilla_vs_v05_production.json`.

### 2. Differential map test — vanilla vs production v0.5 (412 maps, as v0.4)
map index, properties, BG tilemaps, tile properties, NPC event pointers, static NPC fields:
**412 / 412** identical; raw object block 391/412 (animation-frame counters only).
`audits/map_diff_vanilla_vs_v05.json`.

### 3. Celes slice on v0.5 (celes-tech v0.5)
24/24 PASS (Falcon trigger, Annex grid, Vale, sealed door, battle 40 + return, no loop, Potion once, exit, re-entry).

### 4. monster-tech QA ROM from New Game, no RAM pokes — save phase 10/10, load phase 11/11, poke phase 6/6
| Step | Result |
|---|---|
| New Game → vanilla opening dialogue → QA tile prompt `TECH v0.5 QA ACCESS` | PASS |
| Monster test battle: event group $FE → formation $240; slot 2 = **$180**, slot 3 = **$181** | PASS |
| Max HP from relocated stats: A = 90, B = 140 | PASS |
| Custom AI from F9: Mute (only in A's script) and Slow (only in B's script) land on the party; party HP ≥ 54 | PASS |
| Target names in menu `TESTMOB A` / `TESTMOB B`; one monster dies first (B), the other keeps acting; victory | PASS |
| Return to map $013 (35,43), message, control, no battle loop | PASS |
| Gold +75 (30 + 45 from new records); drops only from defined loot (got Tonic + Antidote) | PASS |
| QA Save Point → menu Save → new process → Continue: gil/inventory/map/position restored | PASS |
| QA battle again after load: IDs/HP identical; 2nd victory (A died first this time) + return, +75 gold | PASS |
| Map test A ($1A0) grid + routed NPC A1; south exit | PASS |
| Celes Annex via QA: map $0C7, Vale + chest visible, Vale dialogue, exit (35,43) | PASS |
| Vanilla opening Guard battle (event $000D): Guard IDs $000, HP 40/40, victory, field control | PASS |

### 5. Steal / Sketch / Control — POKE TEST (Terra's Magitek bit cleared, commands set)
| Step | Result |
|---|---|
| Battle steal slots from relocated MonsterItems: A = E9/E8, B = F0/F2 | PASS |
| Terra menu Steal/Sketch/Control/Item | PASS |
| Steal on A and on B (slots consumed, "Stole Antidote ×1!") | PASS |
| Sketch on A → Leafer drawing → **Mute**; Sketch on B → Dark Wind drawing → **Slow** (MonsterSketch + Sketch gfx-slot hook) | PASS |
| Control on A → menu `Battle / Mute`; Control on B → menu `Battle / Slow` | PASS |

Evidence: `out/emu_monster_tech/`, `out/emu_monster_tech_cmds/`, `out/emu_celes_v05/`,
`out/TECH_v0.5_emulator_contact_sheet.png`.

**EMULATOR PASS. USER RUNTIME QA PENDING.**
