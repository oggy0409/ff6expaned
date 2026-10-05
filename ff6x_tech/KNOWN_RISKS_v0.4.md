# TECH v0.4 — known risks / open items

| # | Risk | Severity | Mitigation / status |
|---|---|---|---|
| R1 | Consumer completeness relies on the symbolic Rev 1 disassembly (debug-info cross-reference + source grep). A reference not expressed through a symbol would be missed. | Medium | 90 consumers asserted byte-exact; differential emulator test vanilla vs v0.4 across maps $003–$19E; user runtime QA through the opening + proof maps. |
| R2 | Vanilla tables remain in ROM as dead data; any third-party patch/editor writing them has no effect anymore. | Medium (tooling) | Builder is the only authoring path (as since v0.3). |
| R3 | NPC router changes behaviour only for non-special NPCs with event field $3xxxx (none in vanilla). Event command $7A (set object event pointer) is unaffected. | Low | Audited 0/1,904; special NPCs (45 with bits = 3) keep the vanilla path (tested via differential event-pointer fingerprints). |
| R4 | Added cycles: JSL/RTL + ~20 instructions per NPC at map load only. | Low | Map load only; no per-frame cost. |
| R5 | Long entrances in Rev 1 use a fixed destination (no offset along the strip). | Info | Map A south strip (2 tiles) always arrives at (35,43). |
| R6 | Proof map B reuses vanilla Narshe-house art; some furniture tiles block movement by design (direction masks). | Cosmetic | Walkability modelled with the engine rule; emulator grid check passed. |
| R7 | map-tech QA tile is in the opening Magitek sequence: field sprite reloads as walking sprite after load (KNOWN_QA_ISSUE_v0.3.1). | QA-only | Do not use for field-sprite persistence; flags/inventory persistence is valid. |
| R8 | Map IDs $1FE/$1FF must never be assigned; $19F has an NPC/trigger pointer slot in vanilla but no props row (now valid in the 512-row table). | Info | Builder refuses packages for $000–$002 and $1FE/$1FF. |
| R9 | MapInitEvent slots for new maps are not written (EventReturn). | Info | Builder asserts EventReturn; a vanilla-space claim will be needed when a new map needs a startup event. |
| R10 | Treasure on new maps not exercised (no chest bits allocated). | Info | Deferred to item/treasure architecture. |
| R11 | Celes Annex in celes-tech v0.4 now uses NPC vectors instead of the runtime-accepted CC:E5EE bridges → the accepted slice is re-expressed and must be re-verified. | Medium | Emulator: v0.4 Annex flow passes (map-tech load phase 22–27, celes-tech teleport suite). User QA step in the guide. |
