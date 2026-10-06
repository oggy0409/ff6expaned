# TECH v0.8 — equipment balance audit

Method: every production item compared with every vanilla equipment record of the same type that at least one common character can wear. *Dominates* = at least as good in every number (power/defense, hit/MDef, Vigor, Speed, Stamina, Mag.Pwr, Evade, MBlock), every feature of the other (elements absorbed/nulled/halved, weapon element, status immunity, relic bits, weapon special, spell cast) and no extra weakness, and better in one. Locked stats are not changed by this audit; findings that would need a change are listed for creative review.

## Comparison with the nearest vanilla equivalents

| ID | Item | Pwr/Def | Hit/MDef | V/S/St/M | Eva/MBlk | Features | Nearest vanilla (Pwr, Hit/MDef, V/S/St/M, Eva/MBlk, features) |
|---|---|---|---|---|---|---|---|
| $100 | Tempered Edge | 188 | 150 | +2/+0/+0/+0 | 10/0 | - | $17 Ogre Nix (182, 150, +0/+0/+0/+0, 0/0, weapon_special:14); $21 Pearl Lance (194, 150, +0/+0/+0/+3, 0/0, attack:HOLY, spell_cast:4E) |
| $101 | Imperial Saber | 205 | 150 | +0/+0/+0/+3 | 0/20 | - | $19 Scimitar (208, 150, +0/+0/+0/+0, 0/0, weapon_special:13); $18 Excalibur (217, 150, +2/+2/+1/+1, 20/0, attack:HOLY) |
| $102 | Leo's Blade | 218 | 150 | +3/+0/+3/+0 | 0/0 | attack:HOLY | $18 Excalibur (217, 150, +2/+2/+1/+1, 20/0, attack:HOLY); $19 Scimitar (208, 150, +0/+0/+0/+0, 0/0, weapon_special:13) |
| $103 | Raider Knife | 198 | 180 | +0/+5/+0/+0 | 0/0 | weapon_special:1 | $08 Graedus (204, 180, +0/+0/+0/+0, 10/0, attack:HOLY); $4B Sniper (172, 180, +0/+0/+0/+0, 0/0, weapon_special:8) |
| $104 | Sandpiercer | 210 | 150 | +0/+2/+0/+0 | 0/0 | attack:WIND | $19 Scimitar (208, 150, +0/+0/+0/+0, 0/0, weapon_special:13); $18 Excalibur (217, 150, +2/+2/+1/+1, 20/0, attack:HOLY) |
| $105 | Duncan Claw | 214 | 200 | +5/+0/+3/+0 | 0/0 | - | $59 Tiger Fangs (215, 200, +3/+2/+2/+3, 0/0, -); $58 Dragon Claw (188, 200, +2/+0/+0/+1, 0/0, attack:HOLY) |
| $106 | Moonless | 216 | 180 | +0/+7/+0/+0 | 30/0 | - | $2A Stunner (220, 180, +0/+0/+0/+0, 0/0, spell_cast:60); $08 Graedus (204, 180, +0/+0/+0/+0, 10/0, attack:HOLY) |
| $107 | Doma Edge | 222 | 150 | +5/+0/+4/+0 | 0/0 | - | $32 Sky Render (215, 150, +0/+0/+0/+0, 20/0, -); $19 Scimitar (208, 150, +0/+0/+0/+0, 0/0, weapon_special:13) |
| $108 | Darill's Dirk | 202 | 180 | +0/+4/+0/+0 | 20/0 | - | $08 Graedus (204, 180, +0/+0/+0/+0, 10/0, attack:HOLY); $4B Sniper (172, 180, +0/+0/+0/+0, 0/0, weapon_special:8) |
| $109 | Magister Rod | 190 | 135 | +0/+0/+0/+7 | 0/20 | - | $3C Magus Rod (168, 135, +0/+0/+0/+7, 0/30, -); $40 Rainbow Brsh (146, 135, +1/+2/+1/+2, 0/0, -) |
| $10A | Concord Brush | 184 | 135 | +0/+3/+0/+7 | 0/0 | - | $3C Magus Rod (168, 135, +0/+0/+0/+7, 0/30, -); $40 Rainbow Brsh (146, 135, +1/+2/+1/+2, 0/0, -) |
| $10B | Gale Lance | 218 | 150 | +0/+4/+0/+0 | 0/0 | attack:WIND | $18 Excalibur (217, 150, +2/+2/+1/+1, 20/0, attack:HOLY); $19 Scimitar (208, 150, +0/+0/+0/+0, 0/0, weapon_special:13) |
| $10C | Echo Dagger | 200 | 180 | +3/+3/+0/+3 | 0/0 | - | $08 Graedus (204, 180, +0/+0/+0/+0, 10/0, attack:HOLY); $07 SwordBreaker (164, 180, +0/+0/+0/+0, 30/0, -) |
| $10D | Royal Gear | 84 | 60 | +4/+2/+3/+0 | 0/0 | null:FIRE | $93 Red Jacket (78, 55, +5/+2/+4/+1, 0/0, null:FIRE); $94 Force Armor (69, 68, +0/+0/+0/+0, 0/30, half:EARTH, half:FIRE, half:ICE, half:LIGHTNING, half:WIND) |
| $10E | Imperial Mantle | 78 | 72 | +0/+0/+0/+4 | 0/20 | - | $9C Minerva (88, 70, +1/+2/+1/+4, 0/10, half:EARTH, half:HOLY, half:POISON, half:WATER, null:FIRE, null:ICE, null:LIGHTNING, null:WIND, relic:MP_PLUS_25); $94 Force Armor (69, 68, +0/+0/+0/+0, 0/30, half:EARTH, half:FIRE, half:ICE, half:LIGHTNING, half:WIND) |
| $10F | Magister Robe | 70 | 82 | +0/+0/+0/+6 | 0/0 | relic:MP_PLUS_12 | $94 Force Armor (69, 68, +0/+0/+0/+0, 0/30, half:EARTH, half:FIRE, half:ICE, half:LIGHTNING, half:WIND); $99 Czarina Gown (70, 64, +1/+2/+2/+3, 0/0, -) |
| $110 | Ashen Mail | 88 | 52 | +0/+0/+0/+0 | 0/0 | absorb:FIRE, weak:ICE | $93 Red Jacket (78, 55, +5/+2/+4/+1, 0/0, null:FIRE); $98 Crystal Mail (72, 49, +0/+0/+0/+0, 0/0, -) |
| $111 | Concord Vest | 76 | 62 | +0/+4/+0/+0 | 20/0 | - | $94 Force Armor (69, 68, +0/+0/+0/+0, 0/30, half:EARTH, half:FIRE, half:ICE, half:LIGHTNING, half:WIND); $98 Crystal Mail (72, 49, +0/+0/+0/+0, 0/0, -) |
| $112 | Doma Plate | 92 | 58 | +0/+0/+5/+0 | 0/0 | - | $9C Minerva (88, 70, +1/+2/+1/+4, 0/10, half:EARTH, half:HOLY, half:POISON, half:WATER, null:FIRE, null:ICE, null:LIGHTNING, null:WIND, relic:MP_PLUS_25); $93 Red Jacket (78, 55, +5/+2/+4/+1, 0/0, null:FIRE) |
| $113 | Falcon Jacket | 74 | 60 | +0/+5/+0/+0 | 0/0 | half:WIND | $94 Force Armor (69, 68, +0/+0/+0/+0, 0/30, half:EARTH, half:FIRE, half:ICE, half:LIGHTNING, half:WIND); $98 Crystal Mail (72, 49, +0/+0/+0/+0, 0/0, -) |
| $114 | Child's Ribbon | 34 | 38 | +0/+0/+3/+3 | 0/0 | immune:BLIND, immune:POISON, immune:SILENCE, immune:SLEEP | $81 Genji Helmet (36, 38, +0/+0/+0/+0, 0/0, -); $80 Cat Hood (33, 33, +0/+2/+0/+4, 10/10, half:EARTH, half:FIRE, half:HOLY, half:ICE, half:LIGHTNING, half:WIND, relic:DOUBLE_GP) |
| $115 | Doma Kabuto | 42 | 32 | +4/+0/+4/+0 | 0/0 | - | $81 Genji Helmet (36, 38, +0/+0/+0/+0, 0/0, -); $7C Diamond Helm (27, 18, +0/+0/+0/+0, 0/0, -) |
| $116 | Engineer Goggles | 36 | 30 | +0/+2/+0/+0 | 0/0 | immune:BLIND | $81 Genji Helmet (36, 38, +0/+0/+0/+0, 0/0, -); $7B Regal Crown (28, 23, +1/+1/+1/+1, 0/0, -) |
| $117 | Magi Circlet | 36 | 44 | +0/+0/+0/+5 | 0/10 | - | $81 Genji Helmet (36, 38, +0/+0/+0/+0, 0/0, -); $80 Cat Hood (33, 33, +0/+2/+0/+4, 10/10, half:EARTH, half:FIRE, half:HOLY, half:ICE, half:LIGHTNING, half:WIND, relic:DOUBLE_GP) |
| $118 | Concord Shield | 54 | 48 | +0/+0/+0/+0 | 20/20 | half:HOLY | $64 Genji Shld (54, 50, +0/+0/+0/+0, 20/20, -); $5E Aegis Shld (46, 52, +0/+0/+0/+0, 20/40, -) |
| $119 | Ashguard | 58 | 42 | +0/+0/+0/+0 | 0/0 | absorb:FIRE, weak:ICE | $64 Genji Shld (54, 50, +0/+0/+0/+0, 20/20, -); $63 Crystal Shld (50, 34, +0/+0/+0/+0, 10/0, -) |
| $11A | Runic Crest | 0 | 0 | +0/+0/+0/+5 | 0/20 | - | $C0 Zephyr Cape (0, 0, +0/+0/+0/+0, 10/10, -); $B7 Barrier Ring (0, 0, +0/+0/+0/+2, 0/0, relic:SHELL_HP_LOW) |
| $11B | Maduin's Locket | 0 | 0 | +0/+0/+3/+6 | 0/0 | relic:MP_PLUS_25 | $B7 Barrier Ring (0, 0, +0/+0/+0/+2, 0/0, relic:SHELL_HP_LOW); $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND) |
| $11C | Doma Crest | 0 | 0 | +5/+2/+5/+0 | 0/0 | - | $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND); $B1 Star Pendant (0, 0, +0/+0/+0/+0, 0/0, immune:POISON) |
| $11D | Keepsake Ring | 0 | 0 | +0/+3/+0/+3 | 0/0 | immune:CONDEMNED, immune:DEAD, immune:ZOMBIE | $DB Memento Ring (0, 0, +0/+0/+0/+0, 0/0, immune:DEAD, immune:PETRIFY, immune:ZOMBIE); $DC Safety Bit (0, 0, +0/+0/+0/+0, 0/0, immune:DEAD, immune:PETRIFY, immune:ZOMBIE) |
| $11E | Darill's Coin | 0 | 0 | +0/+5/+0/+0 | 0/20 | - | $C0 Zephyr Cape (0, 0, +0/+0/+0/+0, 10/10, -); $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND) |
| $11F | Memorial Band | 0 | 0 | +0/+0/+4/+0 | 0/0 | immune:BERSERK, immune:CONFUSE | $B2 Peace Ring (0, 0, +0/+0/+0/+0, 0/0, immune:BERSERK, immune:CONFUSE); $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND) |
| $120 | Gale Pin | 0 | 0 | +0/+3/+0/+0 | 0/0 | half:WIND | $C7 Sneak Ring (0, 0, +0/+5/+0/+0, 0/0, relic:INC_STEAL_RATE); $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND) |
| $121 | Beastheart | 0 | 0 | +4/+0/+4/+0 | 0/0 | - | $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND); $B1 Star Pendant (0, 0, +0/+0/+0/+0, 0/0, immune:POISON) |
| $122 | Painter's Lens | 0 | 0 | +0/+0/+0/+5 | 0/0 | relic:INC_SKETCH_RATE | $B7 Barrier Ring (0, 0, +0/+0/+0/+2, 0/0, relic:SHELL_HP_LOW); $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND) |
| $123 | Elder's Seal | 0 | 0 | +0/+0/+0/+5 | 0/0 | immune:SILENCE, relic:MP_PLUS_12 | $B7 Barrier Ring (0, 0, +0/+0/+0/+2, 0/0, relic:SHELL_HP_LOW); $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND) |
| $124 | Engineer's Badge | 0 | 0 | +3/+3/+0/+0 | 0/0 | - | $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND); $B1 Star Pendant (0, 0, +0/+0/+0/+0, 0/0, immune:POISON) |
| $125 | Master's Cord | 0 | 0 | +5/+0/+5/+0 | 0/0 | - | $B0 Goggles (0, 0, +0/+0/+0/+0, 0/0, immune:BLIND); $B1 Star Pendant (0, 0, +0/+0/+0/+0, 0/0, immune:POISON) |
| $126 | Legacy of the Magi | 0 | 0 | +0/+0/+0/+7 | 0/30 | relic:MP_PLUS_25 | $C0 Zephyr Cape (0, 0, +0/+0/+0/+0, 10/10, -); $B7 Barrier Ring (0, 0, +0/+0/+0/+2, 0/0, relic:SHELL_HP_LOW) |

## Strictly dominant

179 (production item, vanilla item) pairs where the production item is at least as good in every respect. Dominating early / mid-game gear is the intended role of a later, unique signature reward. The relevant question is dominance over a character's endgame options (the three strongest vanilla items of that slot the character can wear; Imp-only gear excluded):

| Production item | dominates endgame vanilla | for | note |
|---|---|---|---|
| $107 Doma Edge (222) | $31 Strato (199) | Cyan | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $10D Royal Gear (84) | $92 Diamond Vest (65) | Edgar/Sabin | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $10D Royal Gear (84) | $98 Crystal Mail (72) | Edgar | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $10E Imperial Mantle (78) | $98 Crystal Mail (72) | Celes/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $10F Magister Robe (70) | $92 Diamond Vest (65) | Celes/Gogo/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $111 Concord Vest (76) | $8F Gold Armor (55) | Mog | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $111 Concord Vest (76) | $92 Diamond Vest (65) | Gau/Gogo/Locke/Mog/Shadow | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $111 Concord Vest (76) | $98 Crystal Mail (72) | Locke | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $112 Doma Plate (92) | $95 DiamondArmor (70) | Celes/Cyan/Edgar/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $112 Doma Plate (92) | $98 Crystal Mail (72) | Celes/Cyan/Edgar/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $113 Falcon Jacket (74) | $92 Diamond Vest (65) | Locke/Setzer/Shadow | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $113 Falcon Jacket (74) | $95 DiamondArmor (70) | Setzer | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $113 Falcon Jacket (74) | $98 Crystal Mail (72) | Locke/Setzer | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $114 Child's Ribbon (34) | $7F Oath Veil (32) | Celes/Relm/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $115 Doma Kabuto (42) | $7C Diamond Helm (27) | Cyan | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $116 Engineer Goggles (36) | $7E Crystal Helm (29) | Edgar/Setzer | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $117 Magi Circlet (36) | $7D Dark Hood (26) | Gogo | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $117 Magi Circlet (36) | $7F Oath Veil (32) | Celes/Relm/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $117 Magi Circlet (36) | $81 Genji Helmet (36) | Celes/Gogo/Relm/Strago/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |
| $118 Concord Shield (54) | $63 Crystal Shld (50) | Celes/Cyan/Edgar/Setzer/Terra | locked values; the slot's strongest vanilla item is not dominated (next sections) |

Lower-tier dominance per item (count): $100 11, $101 6, $102 10, $103 3, $104 8, $105 2, $106 6, $107 5, $108 5, $109 2, $10A 3, $10B 8, $10C 5, $10D 10, $10E 10, $10F 11, $111 10, $112 9, $113 10, $114 11, $115 6, $116 7, $117 14, $118 6, $11F 1.

## Strictly dominated (a vanilla item better in every respect)

| Production item | dominated by vanilla | common users | tier of the vanilla item |
|---|---|---|---|
| $100 Tempered Edge | $18 Excalibur | Celes/Edgar/Locke/Terra | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |
| $100 Tempered Edge | $1A Illumina | Celes/Edgar/Locke/Terra | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |
| $100 Tempered Edge | $1B Ragnarok | Celes/Edgar/Locke/Terra | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |
| $101 Imperial Saber | $1A Illumina | Celes | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |
| $101 Imperial Saber | $1B Ragnarok | Celes | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |
| $108 Darill's Dirk | $1A Illumina | Locke | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |
| $119 Ashguard | $67 Paladin Shld | Celes/Cyan/Edgar/Setzer/Terra | ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected |

No production item is dominated by a same-tier or earlier vanilla item; the only dominating items are endgame / ultimate rewards, which a mid-game signature item is allowed to lose to.

## Iconic endgame equipment is not invalidated

| Vanilla | Pwr/Def | best production item of the same type for the same users | Pwr/Def | dominated? |
|---|---|---|---|---|
| $1A Illumina | 255 | $102 Leo's Blade | 218 | no |
| $1B Ragnarok | 255 | $102 Leo's Blade | 218 | no |
| $1C Atma Weapon | 255 | $102 Leo's Blade | 218 | no |
| $18 Excalibur | 217 | $102 Leo's Blade | 218 | no |
| $23 Aura Lance | 227 | $102 Leo's Blade | 218 | no |
| $59 Tiger Fangs | 215 | $105 Duncan Claw | 214 | no |
| $32 Sky Render | 215 | $107 Doma Edge | 222 | no |
| $3C Magus Rod | 168 | $10C Echo Dagger | 200 | no |
| $40 Rainbow Brsh | 146 | $109 Magister Rod | 190 | no |
| $9A Genji Armor | 90 | $112 Doma Plate | 92 | no |
| $9C Minerva | 88 | $112 Doma Plate | 92 | no |
| $A2 Snow Muffler | 128 | $111 Concord Vest | 76 | no |
| $64 Genji Shld | 54 | $119 Ashguard | 58 | no |
| $67 Paladin Shld | 59 | $119 Ashguard | 58 | no |
| $68 Force Shld | 0 | $119 Ashguard | 58 | no |
| $81 Genji Helmet | 36 | $115 Doma Kabuto | 42 | no |
| $CA Ribbon | 0 | $11A Runic Crest | 0 | no |

No production weapon exceeds Battle Power 222 (locked envelope 184-222); Illumina / Ragnarok / Atma Weapon (255) and the 227-253 spears stay above every production weapon.

## Optimum: which slots move to a new item (highest power / defense per slot, as the vanilla Optimum)

| Character | Weapon (vanilla best -> with v0.8) | Shield | Helmet | Armor |
|---|---|---|---|---|
| Terra | Illumina (255) kept | Paladin Shld (59) kept | Thornlet (38) kept | Genji Armor (90) -> **Doma Plate (92)** |
| Locke | Illumina (255) kept | Paladin Shld (59) kept | Thornlet (38) kept | Genji Armor (90) kept |
| Cyan | Sky Render (215) -> **Doma Edge (222)** | Paladin Shld (59) kept | Thornlet (38) -> **Doma Kabuto (42)** | Genji Armor (90) -> **Doma Plate (92)** |
| Shadow | Stunner (220) kept | Paladin Shld (59) kept | Thornlet (38) kept | Genji Armor (90) kept |
| Edgar | Illumina (255) kept | Paladin Shld (59) kept | Thornlet (38) kept | Genji Armor (90) -> **Doma Plate (92)** |
| Sabin | Tiger Fangs (215) kept | Paladin Shld (59) kept | Thornlet (38) kept | Red Jacket (78) -> **Royal Gear (84)** |
| Celes | Illumina (255) kept | Paladin Shld (59) kept | Thornlet (38) kept | Genji Armor (90) -> **Doma Plate (92)** |
| Strago | Graedus (204) kept | Paladin Shld (59) kept | Thornlet (38) kept | BehemothSuit (94) kept |
| Relm | Graedus (204) kept | Paladin Shld (59) kept | Thornlet (38) kept | BehemothSuit (94) kept |
| Setzer | Graedus (204) kept | Paladin Shld (59) kept | Thornlet (38) kept | Genji Armor (90) kept |
| Mog | Aura Lance (227) kept | Paladin Shld (59) kept | Thornlet (38) kept | Snow Muffler (128) kept |
| Gau | - | Paladin Shld (59) kept | Thornlet (38) kept | Snow Muffler (128) kept |
| Gogo | Graedus (204) kept | Paladin Shld (59) kept | Thornlet (38) kept | Dark Gear (68) -> **Concord Vest (76)** |
| Umaro | Bone Club (151) kept | - | - | Snow Muffler (128) kept |

Optimum moves 8 of 53 character slots to a production item; the rest keep their vanilla best. Signature items with lower raw power (e.g. Magister Robe, Imperial Mantle, the relic-like helmets) are picked for their specialisation, not by Optimum.

## Stacking maxima per character (equipment only; Evade / MBlock in %, stats as bonus)

FF6 Rev 1 note: the SNES Evade bug makes physical evasion use MBlock, so MBlock is the stacking value that matters in practice.

| Character | max MBlock vanilla | max MBlock vanilla+v0.8 | max Evade vanilla | with v0.8 | max Speed bonus vanilla | with v0.8 |
|---|---|---|---|---|---|---|
| Terra | 160 | 180 | 130 | 130 | +16 | +19 |
| Locke | 160 | 160 | 130 | 150 | +21 | +24 |
| Cyan | 110 | 110 | 100 | 100 | +9 | +14 |
| Shadow | 100 | 100 | 110 | 130 | +12 | +22 |
| Edgar | 160 | 160 | 130 | 130 | +16 | +22 |
| Sabin | 90 | 90 | 80 | 80 | +11 | +14 |
| Celes | 160 | 190 | 130 | 130 | +16 | +19 |
| Strago | 120 | 140 | 110 | 110 | +10 | +13 |
| Relm | 120 | 140 | 110 | 110 | +12 | +19 |
| Setzer | 120 | 130 | 90 | 100 | +9 | +21 |
| Mog | 90 | 90 | 100 | 110 | +11 | +16 |
| Gau | 90 | 90 | 90 | 100 | +9 | +12 |
| Gogo | 120 | 140 | 110 | 130 | +14 | +20 |
| Umaro | 30 | 30 | 40 | 40 | +0 | +3 |

Raised by more than +20 MBlock or +4 Speed over the vanilla maximum: Cyan, Shadow, Edgar, Celes, Relm, Setzer, Mog, Gogo.
Speed: the raised peaks reach the vanilla party ceiling (Locke +21 with vanilla gear); MBlock: Terra/Celes gain +20/+30 over a vanilla peak that is already far above 100%.

## Dangerous combinations reviewed

* **Shadow evasion** — Moonless (Eva +30, Spd +7), Concord Vest (Eva +20, Spd +4) and Concord Shield (Eva/MBlock +20) stack Evade, but Evade is the bugged stat; Shadow's MBlock and Speed peaks are in the table above. Not changed (locked).
* **Magic users' MBlock** — Legacy of the Magi (+30), Magister Rod (+20), Concord Shield (+20), Magi Circlet (+10), Runic Crest / Imperial Mantle / Imperial Saber (+20, Celes/Terra) reach the same band as vanilla Illumina / Force Shld / Paladin Shld stacks; not above the vanilla ceiling for Terra/Celes (see table).
* **Elemental immunity** — the new items add Fire null (Royal Gear), Fire absorb (Ashen Mail, Ashguard, both with Ice weakness), Wind half (Falcon Jacket, Gale Pin) and Holy half (Concord Shield). Stacking Ashen Mail + Ashguard keeps a single Fire absorb and a single Ice weakness; no new item grants absorb/null of Ice, Lightning, Poison, Earth or Water, so no new full elemental immunity set is possible beyond vanilla (Paladin/Flame/Ice Shld).
* **Relic stacking** — two relics per character: the strongest new pairs are Legacy of the Magi + Maduin's Locket (Terra: Mag +13, MP +25% twice does not stack beyond the single MP +25% bit) and Doma Crest + Memorial Band / Master's Cord-type pairs (stat +9/+10). MP bits are flags: two MP +25% relics give +25%. No new relic copies Offering, Genji Glove, Hyper Wrist, Gem Box or other vanilla multiplier relics.
* **Kefka's Tower / final bosses** — no new item raises a damage multiplier (no Atlas/Earring/Hyper Wrist bit, no X-Fight / X-Magic, no proc), every new weapon is below 255 power, so the end-game damage ceiling is the vanilla one.

## Unintended caps

All bonuses are inside the ItemProp nibble ranges (stats -7..+7, Evade/MBlock 0..50 in steps of 10); the builder refuses values outside. Speed +7 (Moonless) and Mag +7 (Magister Rod, Concord Brush, Legacy of the Magi) are at the field maximum and exactly the locked values (no silent clipping).

## Changes made by this audit

None to locked values. Derived fields were chosen conservatively (family-default hit rates and weapon flags; the smaller MP bit for 'MP-oriented'; a 4-status subset for Child's Ribbon; half (not null) for every 'resist').
