# TECH v0.8 — acquisition map

Every production item has exactly one one-time binding. Story events / maps for these sources are not implemented yet; they bind to `future_event_symbol` later and must use the extended event API (`give_ext_item`, `has_ext_item`). Signature equipment is excluded from vanilla shops, Sell, Steal, Drop, Metamorph, Colosseum wager and Throw (Option C engine: 1-byte sources cannot hold $1xx).

| reward_id | item | source type | planned source | future_event_symbol | conditions | one-time | GP |
|---|---|---|---|---|---|---|---|
| RW_100 | $100 Tempered Edge | smith_purchase | Narshe forge quest | `EV_SMITH_NARSHE_TEMPERED_EDGE` | PREREQ_NARSHE_FORGE_QUEST | yes | 18000 |
| RW_101 | $101 Imperial Saber | event_chest | Vector Annex chest | `EV_CHEST_VECTOR_ANNEX_IMPERIAL_SABER` | PREREQ_VECTOR_ANNEX | yes |  |
| RW_102 | $102 Leo's Blade | quest_reward | Celes arc rare branch | `EV_REWARD_CELES_ARC_LEOS_BLADE` | PREREQ_CELES_ARC_RARE_BRANCH | yes |  |
| RW_103 | $103 Raider Knife | quest_reward | Reconstruction chain | `EV_REWARD_RECONSTRUCTION_RAIDER_KNIFE` | PREREQ_RECONSTRUCTION_CHAIN | yes |  |
| RW_104 | $104 Sandpiercer | smith_purchase | Figaro Foundry | `EV_SMITH_FIGARO_SANDPIERCER` | PREREQ_FIGARO_FOUNDRY | yes | 20000 |
| RW_105 | $105 Duncan Claw | quest_reward | Master's Echo | `EV_REWARD_MASTERS_ECHO_DUNCAN_CLAW` | PREREQ_MASTERS_ECHO | yes |  |
| RW_106 | $106 Moonless | event_chest | Bandit's Hollow | `EV_CHEST_BANDITS_HOLLOW_MOONLESS` | PREREQ_BANDITS_HOLLOW | yes |  |
| RW_107 | $107 Doma Edge | smith_purchase | Doma rebuilt smith | `EV_SMITH_DOMA_DOMA_EDGE` | PREREQ_DOMA_SMITH_REBUILT | yes | 24000 |
| RW_108 | $108 Darill's Dirk | event_chest | Sky Graveyard | `EV_CHEST_SKY_GRAVEYARD_DARILLS_DIRK` | PREREQ_SKY_GRAVEYARD | yes |  |
| RW_109 | $109 Magister Rod | event_chest | Forgotten Age | `EV_CHEST_FORGOTTEN_AGE_MAGISTER_ROD` | PREREQ_FORGOTTEN_AGE | yes |  |
| RW_10A | $10A Concord Brush | event_chest | Sanctuary of Concord | `EV_CHEST_SANCTUARY_CONCORD_BRUSH` | PREREQ_SANCTUARY_OF_CONCORD | yes |  |
| RW_10B | $10B Gale Lance | quest_reward | Beacon quest | `EV_REWARD_BEACON_GALE_LANCE` | PREREQ_BEACON_QUEST | yes |  |
| RW_10C | $10C Echo Dagger | event_chest | Cradle of Silence | `EV_CHEST_CRADLE_OF_SILENCE_ECHO_DAGGER` | PREREQ_CRADLE_OF_SILENCE | yes |  |
| RW_10D | $10D Royal Gear | boss_reward | Brass Colossus (Figaro arc) | `EV_BOSS_BRASS_COLOSSUS_ROYAL_GEAR` | PREREQ_FIGARO_ARC | yes |  |
| RW_10E | $10E Imperial Mantle | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_IMPERIAL_MANTLE` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_10F | $10F Magister Robe | boss_reward | Archive Guardian (First Magi) | `EV_BOSS_ARCHIVE_GUARDIAN_MAGISTER_ROBE` | PREREQ_FIRST_MAGI_ARC | yes |  |
| RW_110 | $110 Ashen Mail | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_ASHEN_MAIL` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_111 | $111 Concord Vest | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_CONCORD_VEST` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_112 | $112 Doma Plate | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_DOMA_PLATE` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_113 | $113 Falcon Jacket | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_FALCON_JACKET` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_114 | $114 Child's Ribbon | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_CHILDS_RIBBON` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_115 | $115 Doma Kabuto | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_DOMA_KABUTO` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_116 | $116 Engineer Goggles | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_ENGINEER_GOGGLES` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_117 | $117 Magi Circlet | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_MAGI_CIRCLET` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_118 | $118 Concord Shield | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_CONCORD_SHIELD` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_119 | $119 Ashguard | arc_reward_tbd | arc design (Armor sheet: not specified) | `EV_ARC_REWARD_ASHGUARD` | PREREQ_TBD_ARC_DESIGN | yes |  |
| RW_11A | $11A Runic Crest | boss_reward | Celes arc (Magitek Praetor) | `EV_BOSS_MAGITEK_PRAETOR_RUNIC_CREST` | PREREQ_CELES_ARC | yes |  |
| RW_11B | $11B Maduin's Locket | boss_reward | Terra arc (Magi-Eater) | `EV_BOSS_MAGI_EATER_MADUINS_LOCKET` | PREREQ_TERRA_ARC | yes |  |
| RW_11C | $11C Doma Crest | boss_reward | Cyan arc (Miasma Regent) | `EV_BOSS_MIASMA_REGENT_DOMA_CREST` | PREREQ_CYAN_ARC | yes |  |
| RW_11D | $11D Keepsake Ring | boss_reward | Shadow/Relm arc (Guiltshade) | `EV_BOSS_GUILTSHADE_KEEPSAKE_RING` | PREREQ_SHADOW_RELM_ARC | yes |  |
| RW_11E | $11E Darill's Coin | boss_reward | Setzer arc (Sky Reaver) | `EV_BOSS_SKY_REAVER_DARILLS_COIN` | PREREQ_SETZER_ARC | yes |  |
| RW_11F | $11F Memorial Band | quest_reward | Vector memorial | `EV_REWARD_VECTOR_MEMORIAL_BAND` | PREREQ_VECTOR_MEMORIAL | yes |  |
| RW_120 | $120 Gale Pin | quest_reward | Coast beacon | `EV_REWARD_COAST_BEACON_GALE_PIN` | PREREQ_COAST_BEACON | yes |  |
| RW_121 | $121 Beastheart | quest_reward | Gau side content | `EV_REWARD_GAU_SIDE_BEASTHEART` | PREREQ_GAU_SIDE_CONTENT | yes |  |
| RW_122 | $122 Painter's Lens | quest_reward | Relm extension | `EV_REWARD_RELM_EXTENSION_PAINTERS_LENS` | PREREQ_RELM_EXTENSION | yes |  |
| RW_123 | $123 Elder's Seal | quest_reward | Ancient lore | `EV_REWARD_ANCIENT_LORE_ELDERS_SEAL` | PREREQ_ANCIENT_LORE | yes |  |
| RW_124 | $124 Engineer's Badge | quest_reward | Figaro | `EV_REWARD_FIGARO_ENGINEERS_BADGE` | PREREQ_FIGARO_ENGINEERS | yes |  |
| RW_125 | $125 Master's Cord | quest_reward | Duncan | `EV_REWARD_DUNCAN_MASTERS_CORD` | PREREQ_DUNCAN | yes |  |
| RW_126 | $126 Legacy of the Magi | boss_reward | Vael Unbound (superboss) | `EV_BOSS_VAEL_UNBOUND_LEGACY_OF_THE_MAGI` | PREREQ_VAEL_UNBOUND | yes |  |

## Smith items (event-driven purchase, D4)

Not in any vanilla shop inventory; no reforge consumption (D6: Tempered Edge, Raider Knife and Doma Edge are independent items).

| item | smith | GP | prerequisite placeholder | already owned | not enough GP | inventory full |
|---|---|---|---|---|---|---|
| $100 Tempered Edge | Narshe forge quest | 18000 | PREREQ_NARSHE_FORGE_QUEST | HAS_EXT_ITEM (inventory + equipment) -> 'already owned' message, no charge, no give | event $85 take_gp sets vanilla switch $1BE -> 'not enough GP' message, nothing given | GIVE then HAS check -> if not received, GP refunded with event $84 and 'no room' message |
| $104 Sandpiercer | Figaro Foundry | 20000 | PREREQ_FIGARO_FOUNDRY | HAS_EXT_ITEM (inventory + equipment) -> 'already owned' message, no charge, no give | event $85 take_gp sets vanilla switch $1BE -> 'not enough GP' message, nothing given | GIVE then HAS check -> if not received, GP refunded with event $84 and 'no room' message |
| $107 Doma Edge | Doma rebuilt smith | 24000 | PREREQ_DOMA_SMITH_REBUILT | HAS_EXT_ITEM (inventory + equipment) -> 'already owned' message, no charge, no give | event $85 take_gp sets vanilla switch $1BE -> 'not enough GP' message, nothing given | GIVE then HAS check -> if not received, GP refunded with event $84 and 'no room' message |

GP costs are derived (the locked sheets give none): tier of the nearest vanilla shop weapon (Falchion 17000, Partisan 13000) scaled to the higher Battle Power — Tempered Edge 18000, Sandpiercer 20000, Doma Edge 24000. The purchase script template is the QA smith demo (`events/qa_access_v08/events.evt` `QaSmithBuy8`), runtime-tested.

Raider Knife ("Reconstruction chain") is bound as a quest reward, not a smith purchase: the locked source names a quest chain, not a smith.

Items whose source the locked Armor sheet leaves to arc design (`arc_reward_tbd`) keep a reserved binding symbol and placeholder prerequisite until the arc content exists.
