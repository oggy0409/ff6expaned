# FFVI Expanded Edition — Design Pack v1.2 CREATIVE LOCK

## Baseline correction / lock

The uploaded ROM is an official Squaresoft North American revision of Final Fantasy III:

- Final Fantasy III (USA) (Rev 1) / Revision A / v1.1
- 3,145,728 bytes, unheadered
- SHA-1 `057ada1c641e3e0b3ca34e6e4f4eb1b05a87143a`
- CRC32 `C0FA0464`

It is now the **locked project baseline**.
The only caution is technical compatibility: many community utilities/patches were authored against US v1.0, so they must be checked or ported rather than assumed compatible.

## v1.2 additions

The v1.2 workbook adds:

- `Character_NPC_Prompts`
- `Equipment_Art_Prompts`
- `Key_Props`
- `VFX_Animation_Locks`
- `Audio_Cue_Locks`
- `Voice_Bible`
- `Canon_Lock`
- `Arc_Beat_Lock`
- `Balance_Guardrails`
- `Palette_Families`
- `Creative_Lock_Matrix`
- `Baseline_Revision`

Together with the v1.1 map/mob/boss prompt sheets, this freezes the remaining creative asset families before implementation.

## Narrative status

The narrative baseline is:

1. `Scenario Script v1.0`
2. `Narrative Production Pass v1.1`
3. v1.2 `Voice_Bible`, `Canon_Lock` and `Arc_Beat_Lock`

Major arcs are no longer treated as a handful of key scenes. They are locked to 12–15 meaningful beats, with exploration dialogue, optional party reactions, NPC state changes and quiet aftermath scenes.
Final text-box splitting is technical work and intentionally deferred.

## Next phase

Do **not** start building maps, inserting sprites or rewriting dialogue from scratch yet.
The next work item is the Rev 1 technical audit: ROM map, event bits, free space, map/monster/item slots, text banks, graphics/palette constraints and editor compatibility.
