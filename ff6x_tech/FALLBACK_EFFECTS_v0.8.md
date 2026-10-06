# TECH v0.8 — BAL-18 fallback effects (D5)

Relics whose locked line names an optional custom-ASM effect ship with their BAL-18 stat fallback: the locked stat line only (plus a vanilla flag where the v0.7 audit named one). No new relic ASM in v0.8. The item identity (name, users, slot, source) is unchanged.

| ID | Relic | Users | Deferred effect (later module) | Running now |
|---|---|---|---|---|
| $11A | Runic Crest | Celes | enhanced Runic (custom ASM) | BAL-18 stat fallback: the locked stat line only |
| $11B | Maduin's Locket | Terra | longer Trance (custom ASM) | BAL-18 stat fallback: the locked stat line only + MP +25% (vanilla bit) |
| $11C | Doma Crest | Cyan | faster Bushido charge (custom ASM) | BAL-18 stat fallback: the locked stat line only |
| $11E | Darill's Coin | Setzer | improved Slots (custom ASM) | BAL-18 stat fallback: the locked stat line only |
| $121 | Beastheart | Gau | Rage enhancement (custom ASM) | BAL-18 stat fallback: the locked stat line only |
| $124 | Engineer's Badge | Edgar | Tools damage +10% (custom ASM) | BAL-18 stat fallback: the locked stat line only |
| $125 | Master's Cord | Sabin | Blitz damage +10% (custom ASM) | BAL-18 stat fallback: the locked stat line only |

Implemented with existing vanilla flags (not fallbacks): Raider Knife steal-on-hit (ThiefKnife special), Painter's Lens Sketch rate (Beret bit), Elder's Seal / Magister Robe MP +1/8 (Bard's Hat bit), Legacy of the Magi MP +1/4 (Minerva bit), Keepsake Ring Doom/Zombie/death immunity (Memento Ring mechanism), Memorial Band Berserk/Muddle immunity (Peace Ring mechanism), spears' Jump x2 (extended spear flag).
