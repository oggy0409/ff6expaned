# TECH v0.3 — Regression test report

Scope: **STATIC** (builder + self-tests) and **Claude EMULATOR SMOKE** (snes9x core via stable-retro, headless).
None of this is user runtime QA. Emulator runs use RAM pokes only to teleport the opening-game party, to make vanilla town NPCs visible, and to hold enemy HP at 1 / party alive in the test battle.

## Static

| Check | Result |
|---|---|
| Clean Rev 1 hash guard, header asserts | PASS |
| All 4 targets build; checksum/complement self-check | PASS |
| TECH v0.1 rebuild = accepted `c412f129…` | PASS (byte-identical) |
| TECH v0.2 EVTEST rebuild = accepted `0258a0fc…` | PASS (byte-identical) |
| Deterministic rebuild (21 output files compared) | PASS |
| IPS + BPS round-trip on every target | PASS |
| Negative guard self-tests (`tools/selftest.py`) | 16/16 PASS |
| Event-assembler vs ca65 disassembly macros (`tools/oracle_check.py`) | 24/24 PASS |
| LZSS decoder vs all 350 vanilla layouts + 42 tile-property sets | PASS |
| Packed-table round-trip (triggers / NPCs / short / long entrances) | PASS |
| NPC codec re-encodes all 2,193 vanilla NPC records exactly | PASS |
| Map walkability validator (border, leaks, connectivity, NPC softlock) | PASS (144 floor tiles, all reachable) |
| Dialogue width check vs ROM font table (≤220 px/line, ≤4 lines) | PASS |

## Emulator smoke — required regression list

| Requirement | Evidence | Result |
|---|---|---|
| 1 boot | 01 boot to first control (opening Narshe, vanilla dialogue via global hook) | PASS |
| 2 vanilla opening dialogue | 02 opening dialogue boxes $0006–$0009 rendered through the hook (screenshots 02_opening_*.png) | PASS |
| 3 normal menu | 03 main menu open/close returns to field | PASS |
| 4 normal battle | 04 WoB world-map random encounter (battle index $0006, Leafer) won; world-map control returns and Narshe entrance works | PASS |
| 5 enter new map | 05a Falcon interior (map $00C) reached | PASS |
| 5 enter new map | 05b entry prompt -> 'No' keeps player on Falcon | PASS |
| 5 enter new map | 05c entry prompt -> 'Yes' loads map $0C7 at (16,27) | PASS |
| 5 enter new map | 05e runtime BG1/tile-property grid == compiled walkability grid (32x32) | PASS |
| 5 enter new map | 05f NPC visibility bits set by entry event (Vale $6F8, chest $6F9) | PASS |
| 5 enter new map | 05g Vale (obj $10) and chest (obj $11) visible | PASS |
| 5 enter new map | 05h wall collision probe (doorway sides impassable) | PASS |
| 6 NPC dialogue | 06 Vale first talk: expansion dialogue + STARTED 0->1 | PASS |
| 7 flag transition | 07 door trigger before talking to Vale: sealed + pushed back | PASS |
| 7 flag transition | 07 Vale second talk: state-dependent follow-up | PASS |
| 8 battle trigger | 08 battle trigger -> event battle group 40 starts | PASS |
| 9 victory return | 09 victory returns to $0C7, BATTLE_DONE set, party stepped off trigger | PASS |
| 9 victory return | 09b re-entering trigger after victory does nothing (no loop) | PASS |
| 9 victory return | 09c player can move freely off/onto the trigger | PASS |
| 10 reward once | 10 reward chest: +1 Potion, COMPLETE set, chest hidden | PASS |
| 10 reward once | 10b repeated interaction: no dialogue, no duplicate, chest tile now walkable | PASS |
| 11 exit to vanilla flow | 11 exit (16,29) returns to Falcon $00C at (15,47) with control | PASS |
| 12 save/reset/load | 12 in-game Save (slot 1) → new emulator process with only SRAM → title Continue → bits STARTED/BATTLE_DONE/COMPLETE = 1/1/1, Potion = 1, chest still gone, Vale shows $1005, door inactive | PASS |
| 13 re-enter / re-talk | 13 Vale after completion shows final state text | PASS |
| 13 re-enter / re-talk | 13 re-enter: map loads, Vale visible, chest stays gone | PASS |
| 13 re-enter / re-talk | 13 door after completion: no battle, no text | PASS |
| 13 re-enter / re-talk | 13 second exit OK | PASS |
| 14 unrelated vanilla NPC dialogues | 14 unrelated vanilla NPC dialogues through dialogue hook | PASS |

Final project-bit state after the suite: STARTED=1, BATTLE_DONE=1, COMPLETE=1, VALE_VISIBLE=1, CHEST_VISIBLE=0, TECH_TEST_0FF=0

SRAM evidence: slot-1 byte for $1EA9 = `$1C` (bits $14A/$14B/$14C), byte for $1F5F = `$01` (NPC bit $6F8).

## Not covered by Claude (needs your gameplay QA)
- Real progression route: a genuine World of Ruin save with the Falcon (the emulator used the opening party + teleport).
- A natural (un-assisted) fight with a WoR party, run-away behaviour, defeat → Game Over.
- Other emulators / hardware timing.
- Long free play around the Falcon and unrelated WoR locations.

Artifacts: `out/emu_celes/*.png`, `emu_suite_result.json`, `save_phase.json`, `load_phase.json`, `out/emu_production/` (production boot).
