# TECH v0.8 — equipment master table ($100-$126)

Generated from `items/production_v08/equipment.json` (canonical source). Locked name = the creative lock; display name = the in-game 12-character name (ROM name field = icon + 12 characters, as vanilla; the locked name opens the description where the display name is abbreviated).

## ID map

| ID | Name (locked) | In-game | Type | Acquisition | Notes |
|---|---|---|---|---|---|
| $100 | Tempered Edge | TemperedEdge | weapon (sword) | smith_purchase: Narshe forge quest | smith 18000 GP |
| $101 | Imperial Saber | ImperialSabr | weapon (sword) | event_chest: Vector Annex chest |  |
| $102 | Leo's Blade | Leo's Blade | weapon (sword) | quest_reward: Celes arc rare branch |  |
| $103 | Raider Knife | Raider Knife | weapon (knife) | quest_reward: Reconstruction chain |  |
| $104 | Sandpiercer | Sandpiercer | weapon (spear) | smith_purchase: Figaro Foundry | Jump x2 (spear); smith 20000 GP |
| $105 | Duncan Claw | Duncan Claw | weapon (claw) | quest_reward: Master's Echo |  |
| $106 | Moonless | Moonless | weapon (ninja blade) | event_chest: Bandit's Hollow |  |
| $107 | Doma Edge | Doma Edge | weapon (katana) | smith_purchase: Doma rebuilt smith | smith 24000 GP |
| $108 | Darill's Dirk | Darill'sDirk | weapon (knife) | event_chest: Sky Graveyard |  |
| $109 | Magister Rod | Magister Rod | weapon (rod) | event_chest: Forgotten Age |  |
| $10A | Concord Brush | ConcordBrush | weapon (brush) | event_chest: Sanctuary of Concord |  |
| $10B | Gale Lance | Gale Lance | weapon (spear) | quest_reward: Beacon quest | Jump x2 (spear) |
| $10C | Echo Dagger | Echo Dagger | weapon (knife) | event_chest: Cradle of Silence |  |
| $10D | Royal Gear | Royal Gear | armor (body) | boss_reward: Brass Colossus (Figaro arc) |  |
| $10E | Imperial Mantle | ImperialMntl | armor (body) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $10F | Magister Robe | MagisterRobe | armor (body) | boss_reward: Archive Guardian (First Magi) |  |
| $110 | Ashen Mail | Ashen Mail | armor (body) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $111 | Concord Vest | Concord Vest | armor (body) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $112 | Doma Plate | Doma Plate | armor (body) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $113 | Falcon Jacket | FalconJacket | armor (body) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $114 | Child's Ribbon | ChildsRibbon | helmet (helmet) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $115 | Doma Kabuto | Doma Kabuto | helmet (helmet) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $116 | Engineer Goggles | Eng. Goggles | helmet (helmet) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $117 | Magi Circlet | Magi Circlet | helmet (helmet) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $118 | Concord Shield | Concord Shld | shield (shield) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $119 | Ashguard | Ashguard | shield (shield) | arc_reward_tbd: arc design (Armor sheet: not specified) |  |
| $11A | Runic Crest | Runic Crest | relic (relic) | boss_reward: Celes arc (Magitek Praetor) | BAL-18 fallback: enhanced Runic (custom ASM) deferred |
| $11B | Maduin's Locket | MaduinLocket | relic (relic) | boss_reward: Terra arc (Magi-Eater) | BAL-18 fallback: longer Trance (custom ASM) deferred |
| $11C | Doma Crest | Doma Crest | relic (relic) | boss_reward: Cyan arc (Miasma Regent) | BAL-18 fallback: faster Bushido charge (custom ASM) deferred |
| $11D | Keepsake Ring | KeepsakeRing | relic (relic) | boss_reward: Shadow/Relm arc (Guiltshade) |  |
| $11E | Darill's Coin | Darill'sCoin | relic (relic) | boss_reward: Setzer arc (Sky Reaver) | BAL-18 fallback: improved Slots (custom ASM) deferred |
| $11F | Memorial Band | MemorialBand | relic (relic) | quest_reward: Vector memorial |  |
| $120 | Gale Pin | Gale Pin | relic (relic) | quest_reward: Coast beacon |  |
| $121 | Beastheart | Beastheart | relic (relic) | quest_reward: Gau side content | BAL-18 fallback: Rage enhancement (custom ASM) deferred |
| $122 | Painter's Lens | PaintersLens | relic (relic) | quest_reward: Relm extension |  |
| $123 | Elder's Seal | Elder's Seal | relic (relic) | quest_reward: Ancient lore |  |
| $124 | Engineer's Badge | Eng. Badge | relic (relic) | quest_reward: Figaro | BAL-18 fallback: Tools damage +10% (custom ASM) deferred |
| $125 | Master's Cord | Master'sCord | relic (relic) | quest_reward: Duncan | BAL-18 fallback: Blitz damage +10% (custom ASM) deferred |
| $126 | Legacy of the Magi | LegacyofMagi | relic (relic) | boss_reward: Vael Unbound (superboss) |  |

Reserve $127-$13C: free. QA-only $13D-$13F: QA Blade13D / QA Mail 13E / QA Charm13F (QA ROM only).

## Stats

| ID | Name | Users | Pwr/Def | Hit/MDef | Vig | Spd | Sta | Mag | Eva | MBlk | Elements | Status immunity | Relic bits | Weapon flags / special |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $100 | Tempered Edge | Terra/Locke/Edgar/Celes | 188 | 150 | +2 | +0 | +0 | +0 | 10 | 0 | - | - | - | RUNIC;TWO_HAND;BUSHIDO |
| $101 | Imperial Saber | Celes | 205 | 150 | +0 | +0 | +0 | +3 | 0 | 20 | - | - | - | RUNIC;TWO_HAND;BUSHIDO |
| $102 | Leo's Blade | Terra/Locke/Edgar/Celes | 218 | 150 | +3 | +0 | +3 | +0 | 0 | 0 | attack:HOLY | - | - | RUNIC;TWO_HAND;BUSHIDO |
| $103 | Raider Knife | Locke | 198 | 180 | +0 | +5 | +0 | +0 | 0 | 0 | - | - | - | RUNIC;TWO_HAND / STEAL |
| $104 | Sandpiercer | Edgar/Mog | 210 | 150 | +0 | +2 | +0 | +0 | 0 | 0 | attack:WIND | - | - | RUNIC;TWO_HAND |
| $105 | Duncan Claw | Sabin | 214 | 200 | +5 | +0 | +3 | +0 | 0 | 0 | - | - | - | - |
| $106 | Moonless | Shadow | 216 | 180 | +0 | +7 | +0 | +0 | 30 | 0 | - | - | - | RUNIC;TWO_HAND |
| $107 | Doma Edge | Cyan | 222 | 150 | +5 | +0 | +4 | +0 | 0 | 0 | - | - | - | RUNIC;TWO_HAND;BUSHIDO |
| $108 | Darill's Dirk | Locke/Setzer | 202 | 180 | +0 | +4 | +0 | +0 | 20 | 0 | - | - | - | RUNIC;TWO_HAND |
| $109 | Magister Rod | Strago/Relm | 190 | 135 | +0 | +0 | +0 | +7 | 0 | 20 | - | - | - | TWO_HAND |
| $10A | Concord Brush | Relm | 184 | 135 | +0 | +3 | +0 | +7 | 0 | 0 | - | - | - | TWO_HAND |
| $10B | Gale Lance | Edgar/Mog | 218 | 150 | +0 | +4 | +0 | +0 | 0 | 0 | attack:WIND | - | - | RUNIC;TWO_HAND |
| $10C | Echo Dagger | Gogo | 200 | 180 | +3 | +3 | +0 | +3 | 0 | 0 | - | - | - | RUNIC;TWO_HAND |
| $10D | Royal Gear | Edgar/Sabin | 84 | 60 | +4 | +2 | +3 | +0 | 0 | 0 | null:FIRE | - | - | - |
| $10E | Imperial Mantle | Terra/Celes | 78 | 72 | +0 | +0 | +0 | +4 | 0 | 20 | - | - | - | - |
| $10F | Magister Robe | Terra/Celes/Strago/Relm/Gogo | 70 | 82 | +0 | +0 | +0 | +6 | 0 | 0 | - | - | MP_PLUS_12 | - |
| $110 | Ashen Mail | Cyan/Edgar/Setzer | 88 | 52 | +0 | +0 | +0 | +0 | 0 | 0 | absorb:FIRE;weak:ICE | - | - | - |
| $111 | Concord Vest | Locke/Shadow/Mog/Gau/Gogo | 76 | 62 | +0 | +4 | +0 | +0 | 20 | 0 | - | - | - | - |
| $112 | Doma Plate | Terra/Cyan/Edgar/Celes | 92 | 58 | +0 | +0 | +5 | +0 | 0 | 0 | - | - | - | - |
| $113 | Falcon Jacket | Locke/Shadow/Setzer | 74 | 60 | +0 | +5 | +0 | +0 | 0 | 0 | half:WIND | - | - | - |
| $114 | Child's Ribbon | Terra/Celes/Relm | 34 | 38 | +0 | +0 | +3 | +3 | 0 | 0 | - | BLIND;POISON;SILENCE;SLEEP | - | - |
| $115 | Doma Kabuto | Cyan | 42 | 32 | +4 | +0 | +4 | +0 | 0 | 0 | - | - | - | - |
| $116 | Engineer Goggles | Edgar/Setzer | 36 | 30 | +0 | +2 | +0 | +0 | 0 | 0 | - | BLIND | - | - |
| $117 | Magi Circlet | Terra/Celes/Strago/Relm/Gogo | 36 | 44 | +0 | +0 | +0 | +5 | 0 | 10 | - | - | - | - |
| $118 | Concord Shield | Terra/Locke/Cyan/Shadow/Edgar/Sabin/Celes/Strago/Relm/Setzer/Mog/Gogo | 54 | 48 | +0 | +0 | +0 | +0 | 20 | 20 | half:HOLY | - | - | - |
| $119 | Ashguard | Terra/Cyan/Edgar/Celes/Setzer | 58 | 42 | +0 | +0 | +0 | +0 | 0 | 0 | absorb:FIRE;weak:ICE | - | - | - |
| $11A | Runic Crest | Celes | 0 | 0 | +0 | +0 | +0 | +5 | 0 | 20 | - | - | - | - |
| $11B | Maduin's Locket | Terra | 0 | 0 | +0 | +0 | +3 | +6 | 0 | 0 | - | - | MP_PLUS_25 | - |
| $11C | Doma Crest | Cyan | 0 | 0 | +5 | +2 | +5 | +0 | 0 | 0 | - | - | - | - |
| $11D | Keepsake Ring | Shadow/Relm | 0 | 0 | +0 | +3 | +0 | +3 | 0 | 0 | - | CONDEMNED;ZOMBIE;DEAD | - | - |
| $11E | Darill's Coin | Setzer | 0 | 0 | +0 | +5 | +0 | +0 | 0 | 20 | - | - | - | - |
| $11F | Memorial Band | Terra/Locke/Cyan/Shadow/Edgar/Sabin/Celes/Strago/Relm/Setzer/Mog/Gau/Gogo/Umaro | 0 | 0 | +0 | +0 | +4 | +0 | 0 | 0 | - | BERSERK;CONFUSE | - | - |
| $120 | Gale Pin | Terra/Locke/Cyan/Shadow/Edgar/Sabin/Celes/Strago/Relm/Setzer/Mog/Gau/Gogo/Umaro | 0 | 0 | +0 | +3 | +0 | +0 | 0 | 0 | half:WIND | - | - | - |
| $121 | Beastheart | Gau | 0 | 0 | +4 | +0 | +4 | +0 | 0 | 0 | - | - | - | - |
| $122 | Painter's Lens | Relm | 0 | 0 | +0 | +0 | +0 | +5 | 0 | 0 | - | - | INC_SKETCH_RATE | - |
| $123 | Elder's Seal | Strago | 0 | 0 | +0 | +0 | +0 | +5 | 0 | 0 | - | SILENCE | MP_PLUS_12 | - |
| $124 | Engineer's Badge | Edgar | 0 | 0 | +3 | +3 | +0 | +0 | 0 | 0 | - | - | - | - |
| $125 | Master's Cord | Sabin | 0 | 0 | +5 | +0 | +5 | +0 | 0 | 0 | - | - | - | - |
| $126 | Legacy of the Magi | Terra/Celes/Strago/Relm/Gogo | 0 | 0 | +0 | +0 | +0 | +7 | 0 | 30 | - | - | MP_PLUS_25 | - |

## Derived (not given by the locked stat line)

Every derivation, per item:

* **$100 Tempered Edge** — locked: `Atk 188; Vigor +2; Eva +10`. hit_rate: family default (vanilla sword hit 150); weapon_flags: family default (vanilla sword: RUNIC, TWO_HAND, BUSHIDO); throw: not throwable (Throw excluded under Option C); animation: vanilla Falchion ($15) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$101 Imperial Saber** — locked: `Atk 205; Magic +3; M.Eva +20`. hit_rate: family default (vanilla sword hit 150); weapon_flags: family default (vanilla sword: RUNIC, TWO_HAND, BUSHIDO); throw: not throwable (Throw excluded under Option C); animation: vanilla Enhancer ($13) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$102 Leo's Blade** — locked: `Atk 218; Vigor +3; Stamina +3; Holy`. hit_rate: family default (vanilla sword hit 150); weapon_flags: family default (vanilla sword: RUNIC, TWO_HAND, BUSHIDO); throw: not throwable (Throw excluded under Option C); animation: vanilla Excalibur ($18) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$103 Raider Knife** — locked: `Atk 198; Speed +5; steal-on-hit`. hit_rate: family default (vanilla knife hit 180); weapon_flags: family default (vanilla knife: RUNIC, TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla ThiefKnife ($04) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$104 Sandpiercer** — locked: `Atk 210; Wind; Speed +2`. hit_rate: family default (vanilla spear hit 150); weapon_flags: family default (vanilla spear: RUNIC, TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Partisan ($20) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$105 Duncan Claw** — locked: `Atk 214; Vigor +5; Stamina +3`. hit_rate: family default (vanilla claw hit 200); weapon_flags: family default (vanilla claw: none); throw: not throwable (Throw excluded under Option C); animation: vanilla Tiger Fangs ($59) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$106 Moonless** — locked: `Atk 216; Speed +7; Eva +30`. hit_rate: family default (vanilla ninja blade hit 180); weapon_flags: family default (vanilla ninja blade: RUNIC, TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Hardened ($28) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$107 Doma Edge** — locked: `Atk 222; Vigor +5; Stamina +4`. hit_rate: family default (vanilla katana hit 150); weapon_flags: family default (vanilla katana: RUNIC, TWO_HAND, BUSHIDO); throw: not throwable (Throw excluded under Option C); animation: vanilla Sky Render ($32) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$108 Darill's Dirk** — locked: `Atk 202; Speed +4; Eva +20`. hit_rate: family default (vanilla knife hit 180); weapon_flags: family default (vanilla knife: RUNIC, TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Graedus ($08) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$109 Magister Rod** — locked: `Atk 190; Magic +7; M.Eva +20`. hit_rate: family default (vanilla rod hit 135); weapon_flags: family default (vanilla rod: TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Magus Rod ($3C) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$10A Concord Brush** — locked: `Atk 184; Magic +7; Speed +3`. hit_rate: family default (vanilla brush hit 135); weapon_flags: family default (vanilla brush: TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Rainbow Brsh ($40) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$10B Gale Lance** — locked: `Atk 218; Wind; Speed +4`. hit_rate: family default (vanilla spear hit 150); weapon_flags: family default (vanilla spear: RUNIC, TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Aura Lance ($23) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$10C Echo Dagger** — locked: `Atk 200; Vigor/Magic/Speed +3`. hit_rate: family default (vanilla knife hit 180); weapon_flags: family default (vanilla knife: RUNIC, TWO_HAND); throw: not throwable (Throw excluded under Option C); animation: vanilla Man Eater ($06) weapon animation, icon, block graphic; merit_award: MERIT equip flag off: signature gear keeps its locked users
* **$10D Royal Gear** — locked: `Def 84; MDef 60; Vig +4; Spd +2; Sta +3; Fire null`. merit_award: MERIT equip flag off; icon: vanilla Genji Armor ($9A) icon / block graphic; evade_unspecified: 0 unless locked
* **$10E Imperial Mantle** — locked: `Def 78; MDef 72; Mag +4; M.Eva +20`. merit_award: MERIT equip flag off; icon: vanilla Light Robe ($91) icon / block graphic; evade_unspecified: 0 unless locked
* **$10F Magister Robe** — locked: `Def 70; MDef 82; Mag +6; MP-oriented`. merit_award: MERIT equip flag off; icon: vanilla Tao Robe ($97) icon / block graphic; evade_unspecified: 0 unless locked; relic_effects: 'MP-oriented' -> MP +1/8 (vanilla Bard's Hat bit), the smaller of the two options named in the v0.7 audit
* **$110 Ashen Mail** — locked: `Def 88; MDef 52; Fire absorb; Ice weak`. merit_award: MERIT equip flag off; icon: vanilla Crystal Mail ($98) icon / block graphic; evade_unspecified: 0 unless locked
* **$111 Concord Vest** — locked: `Def 76; MDef 62; Spd +4; Eva +20`. merit_award: MERIT equip flag off; icon: vanilla Dark Gear ($96) icon / block graphic
* **$112 Doma Plate** — locked: `Def 92; MDef 58; Sta +5`. merit_award: MERIT equip flag off; icon: vanilla DiamondArmor ($95) icon / block graphic; evade_unspecified: 0 unless locked
* **$113 Falcon Jacket** — locked: `Def 74; MDef 60; Spd +5; Wind resist`. merit_award: MERIT equip flag off; icon: vanilla Mirage Vest ($8E) icon / block graphic; evade_unspecified: 0 unless locked; elements: 'resist' -> half damage (armor element byte 15, as Force Armor)
* **$114 Child's Ribbon** — locked: `Def 34; MDef 38; Mag +3; Sta +3; status resist subset`. merit_award: MERIT equip flag off; icon: vanilla Coronet ($70) icon / block graphic; evade_unspecified: 0 unless locked; immune_status: 'status resist subset' -> 4 of Ribbon's 10 (Blind, Poison, Silence, Sleep): no instant-death / Petrify / Zombie protection
* **$115 Doma Kabuto** — locked: `Def 42; MDef 32; Vig +4; Sta +4`. merit_award: MERIT equip flag off; icon: vanilla Diamond Helm ($7C) icon / block graphic; evade_unspecified: 0 unless locked
* **$116 Engineer Goggles** — locked: `Def 36; MDef 30; Blind immunity; Spd +2`. merit_award: MERIT equip flag off; icon: vanilla Diamond Helm ($7C) icon / block graphic; evade_unspecified: 0 unless locked
* **$117 Magi Circlet** — locked: `Def 36; MDef 44; Mag +5; M.Eva +10`. merit_award: MERIT equip flag off; icon: vanilla Mystery Veil ($79) icon / block graphic; evade_unspecified: 0 unless locked; users: 'magic users' -> the five-character magic set of Legacy of the Magi / Magister Robe
* **$118 Concord Shield** — locked: `Def 54; MDef 48; Eva +20; M.Eva +20; Holy resist`. merit_award: MERIT equip flag off; icon: vanilla Genji Shld ($64) icon / block graphic; users: 'broad' -> every character except Gau and Umaro (engine rule R8: no extended shield for Gau/Umaro); elements: 'resist' -> half damage (armor element byte 15, as Force Armor)
* **$119 Ashguard** — locked: `Def 58; MDef 42; Fire absorb; Ice weak`. merit_award: MERIT equip flag off; icon: vanilla Crystal Shld ($63) icon / block graphic; evade_unspecified: 0 unless locked; users: 'heavy users' -> vanilla heavy-shield set (Crystal/Diamond Shld: Terra, Cyan, Edgar, Celes, Setzer)
* **$11A Runic Crest** — locked: `Mag +5; M.Eva +20; enhanced Runic (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$11B Maduin's Locket** — locked: `Mag +6; Sta +3; longer Trance (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic); relic_effects: BAL-18 fallback named in the v0.7 audit: MP +25% (vanilla Minerva bit)
* **$11C Doma Crest** — locked: `Vig +5; Sta +5; Spd +2; faster Bushido (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$11D Keepsake Ring** — locked: `blocks Doom/Zombie/instant death; Mag +3; Spd +3`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic); immune_status: Doom = Condemned, Zombie, instant death = Dead immunity (Memento Ring mechanism)
* **$11E Darill's Coin** — locked: `Spd +5; M.Eva +20; improved Slots (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$11F Memorial Band** — locked: `Sta +4; prevents Berserk/Confuse`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic); immune_status: Berserk + Confuse (Peace Ring mechanism)
* **$120 Gale Pin** — locked: `Spd +3; Wind resistance`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic); elements: 'Wind resistance' -> half wind damage
* **$121 Beastheart** — locked: `Vig +4; Sta +4; Rage enhancement (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$122 Painter's Lens** — locked: `Mag +5; Sketch accuracy increase`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$123 Elder's Seal** — locked: `Mag +5; MP +12.5%; Silence immunity`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$124 Engineer's Badge** — locked: `Vig +3; Spd +3; Tools +10% (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$125 Master's Cord** — locked: `Vig +5; Sta +5; Blitz +10% (ASM, optional)`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)
* **$126 Legacy of the Magi** — locked: `Mag +7; M.Eva +30; MP +25%`. icon: vanilla relic icon ($B0 Goggles template; no Goggles property copied); merit_award: n/a (relic)

Common to all 39: price field 2 (vanilla value for unsold items; Sell excludes $1xx), no spell cast / proc, not throwable, no MERIT / IMP equip flag, no auto-status, no field effect, unique.
