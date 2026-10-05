# Audit A — Event-bit allocator (Rev 1)

Machine-readable outputs:
- `eventbit_audit.json` — one row per bit `$000–$6FF` with reference counts and status.
- `asm_eventbit_refs.json` — every hard-coded ASM reference to `$1E80–$1F5F`.
- `eventbit_allocation_PROPOSED.json` — proposed project allocation (needs approval).
- Generator: `tools/eventbit_audit.py` (+ `tools/asm_refs.py`).

## Method (cross-reference, no guessing)
A bit is **FREE_CANDIDATE** only if ALL are zero:

| Source | How it was enumerated |
|---|---|
| Event / world / vehicle / object scripts | every `switch`, `if_switch`, `set_switch`, `clr_switch`, `loop_until` operand in `src/event/*.asm` (the event bank reassembles byte-identically to Rev 1; raw `.byte` blocks were classified — none are switch commands) |
| NPC visibility switches | every `npc_prop` switch in `npc_prop.asm` (2,193 NPCs) |
| World-map modification table | `world_mode_ptr` entries (CE:F600 data) |
| Hard-coded ASM | every `$1E80–$1F5F` operand in all non-event modules (field, world, battle, btlgfx, menu, cutscene…). Indexed accesses on group bases (`$1E80,y` etc.) are the generic script-driven accessors; all *direct* byte accesses reserve the whole byte **and the next byte** (possible 16-bit access) |
| Initial values | event bits `$000–$2FF` are zeroed at New Game (`InitEventSwitches`, 0x60 bytes from `$1E80`); NPC bits use the init table at C0:E0A0 — a bit with initial value 1 is never free |

Persistence: the save routine copies `$1600–$1FFF` to SRAM (`CopyGameDataToSRAM`,
`cpy #$0a00`), so all event bits survive save/reset/load.

## Results
| Range | Used | Free candidates |
|---|---:|---:|
| Event bits `$000–$2FF` (`$1E80–$1EDF`) | 655 | **113** |
| NPC bits `$300–$6FF` (`$1EE0–$1F5F`) | 668 | 356 |

Notable: `$0E0–$0FF` (RAM `$1E9C–$1E9F`) is a fully unreferenced 32-bit block.
ASM-reserved bytes include `$1EB4/5` (case word), `$1EB6–$1EBF`, `$1EBA–$1EBC`
(rare-item bits), `$1ED7–$1EDF` (party/battle/character-availability), etc.

## Bit used by this round
`$0FF` (`$1E9F` bit 7) = **TECH_TEST**, used only by the `evtest` branch.
It is permanently reserved and will never be reused for production content,
so a save that touched the test cannot pollute production flags.

## Proposed production allocation (NOT yet in use)
`eventbit_allocation_PROPOSED.json`:
- `$0E0–$0E7` EXP_HOPE_01..08 — one packed byte (`$1E9C`), so "≥4 / ≥6 / all 8
  Hope Flags" checks can be a single popcount routine.
- `$0E8–$0FD` per-arc STARTED/DONE, Terra reconstruction states, Celes branch.
- `$11A–$11C` WoB seed flags; `$0FE`, `$11D–$122` spare.
- 72 further free event bits remain unallocated.

All proposed bits are never touched by vanilla, so they are 0 in every existing
Rev 1 save → loading old saves is safe.

## Open items
- New NPCs on new maps need NPC-switch bits (`$300+`). 356 are unreferenced, but
  NPC bits whose required initial state is 1 would need the init table
  (C0:E0A0) changed — that is a vanilla-data patch and will be proposed separately.
- Debug-only code (C0:D386–D612) references `$1E81–$1E83`; treated as reserved anyway.
