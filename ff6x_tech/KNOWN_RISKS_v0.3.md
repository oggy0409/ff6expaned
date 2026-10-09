# TECH v0.3 — Known risks / open items

| # | Risk | Severity | Mitigation / status |
|---|---|---|---|
| R1 | Emulator tests used the opening-game party + RAM teleport, not a real WoR save with the Falcon. | Medium | User QA on a real WoR save is the acceptance gate. |
| R2 | Table repacks shift every NPC / trigger / short-entrance record after maps $00C / $0C7. Any external tool or patch that addresses these records by absolute offset (FF3usME, FF6LE, community IPS for Rev 1/v1.0) is now incompatible with this ROM. | Medium (tooling) | Builder is the only authoring path. Re-run the builder instead of editing the ROM. |
| R3 | Remaining slack: 1 trigger, 7 NPCs, 21 short entrances. Production content will exceed this. | Blocker for production volume (not for v0.3) | Next map-pipeline step: relocate NPC / trigger / entrance tables into MAP_EXPANSION F6–F7 (≈52 audited long-address consumers). |
| R4 | Entry trigger is inside the vanilla Falcon interior at (13,46). Players walking there get a Yes/No prompt; a party-member NPC that randomly wanders onto it would block it. | Low (TECH build only) | "No" returns cleanly (tested). Final entry will be a world-map location per design. |
| R5 | Running away from the test battle also completes the battle step (FF6 event scripts cannot read escape vs win). | Low | Documented. Production boss: no-escape formation. |
| R6 | Map art is placeholder (vanilla Magitek-lab tiles assembled from a legend), so some wall seams look unpolished. | Cosmetic | Final Annex art is a later, separate task. |
| R7 | Layout pointer slot $15F is the last free slot in the 352-entry SubTilemap pointer table. A second new layout needs either the END slot $15E (editor impact) or relocating the pointer table (1 consumer routine, 3 loads). | Medium (next maps) | To be designed in the map-capacity module. |
| R8 | BG2 reuses vanilla layout $12A (unused by any vanilla map) as an "all transparent" layer; it depends on tile $01 being transparent in this tileset. | Low | Visually verified in emulator. A different tileset will need its own empty BG2. |
| R9 | Production branch hook compares against the per-build message count (`CMP #$0001` in production, `#$000B` in celes-tech); the routine is otherwise byte-identical to the runtime-accepted v0.2 hook. | Low | Generated from the same source; listing in each manifest. |
| R10 | The test bits $14A–$14C and NPC bits $6F8/$6F9 stay set in saves used for QA. | Low | They are reserved permanently for the TECH slice and will never be reused by final content. |
| R11 | Save inside the Annex is impossible (no save point). | By design | Same as vanilla dungeons; save on the world map. |
